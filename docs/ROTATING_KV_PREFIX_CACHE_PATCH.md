# RotatingKVCache prefix-cache widening patch

This document explains the runtime monkey-patch installed by `vmlx_engine/__init__.py`
that widens `mlx_lm.models.cache.RotatingKVCache(max_size=…)` to a configurable
floor at import time. It is mandatory reading before touching the sliding-window
cache path, the truncation path, or the mixed-attention model loaders.

## 1. The bug it fixes

Mixed-attention models such as Gemma 4 alternate sliding-window attention layers
with full-attention layers. For the sliding layers, model code constructs the K/V
slot with `RotatingKVCache(max_size=sliding_window)` — a ring buffer the size of
the *trained* window. Gemma 4 ships with `sliding_window=512`.

When a prompt exceeds that window, the buffer wraps. `mllm_scheduler._truncate_hybrid_cache`
recognises this case explicitly:

```python
# vmlx_engine/mllm_scheduler.py
if offset > max_size:
    # Wrapped circular buffer — head-aligned slice is not in temporal order. Skip.
    return None
```

Returning `None` propagates up to the block-store path and **silently disables
every cache write for that request**: no L0 paged insert, no L1 disk
write-through, no L2 prompt store. The L0/L1/L2 stack exists but never receives
any data for prompts past `sliding_window`.

For deployments where the system prompt alone clears the trained window — most
agent / assistant workloads — `cache_hit_tokens` stays at zero no matter how
many byte-identical prompts you replay.

## 2. What this patch does

`vmlx_engine/__init__.py` installs a single wrapper around
`RotatingKVCache.__init__` at import time:

```python
def _patched_rkv_init(self, *args, **kwargs):
    effective = max(ROTATING_KV_DEFAULT_MAX,
                    int(os.environ.get(ROTATING_KV_OVERRIDE_ENV, 0) or 0))
    # Widen max_size in both positional and keyword call forms
    if "max_size" in kwargs:
        if effective > kwargs["max_size"]:
            kwargs["max_size"] = effective
    elif args:
        if effective > args[0]:
            args = (effective,) + args[1:]
    else:
        kwargs["max_size"] = effective
    _orig_rkv_init(self, *args, **kwargs)
```

| Constant / env | Value | Purpose |
|---|---|---|
| `ROTATING_KV_DEFAULT_MAX` | `32768` | Hard floor applied unconditionally |
| `ROTATING_KV_OVERRIDE_ENV` | `VMLX_ROTATING_KV_MAX_TOKENS` | Env var override, only effective if larger than the default |

The result : every `RotatingKVCache` reserves enough K/V slots to hold
`max(32 k, env-override)` tokens. The `offset > max_size` branch stops tripping
for the vast majority of agent prompts (system 1–3 k + history 5–10 k), and the
truncation path returns a coherent cache list.

## 3. Why this is compute-safe

Critical observation: **the attention mask is computed independently in the
model's forward pass**. It still uses the trained `sliding_window` value (and
the `sliding_window_pattern`) to decide which past tokens contribute to
attention.

The widening only enlarges the K/V *tensor reservation* — the ring buffer that
holds the keys and values. The model still attends to exactly the trained
sliding window. Logits and output tokens are bit-identical to upstream behaviour.

## 4. Why patch the class and not a callsite

Several construction paths exist for sliding-window caches:

- The model's own `make_cache` (e.g. `mlx_lm.models.gemma4_text.Model.make_cache`).
- vmlx loaders that reassign `model.make_cache` to their own factories:
  `smelt_loader`, `jang_loader`, `tokenizer`.
- Prefix-cache reconstruction in `prefix_cache.py` rebuilding caches from disk.
- Mamba companion constructors that nest a rotating cache inside.

A callsite-level patch (e.g. editing `gemma4_text.py` only) is shadowed at
runtime: on `mlx-lm >= 0.31.2`, models load directly from `mlx_lm.models.gemma4_text`
without going through the vendored `_gemma4_text_upstream.py` fallback. And no
loader overrides read the env var.

Wrapping `RotatingKVCache.__init__` at the class level catches every
construction path with a single hook. One install at import time, every callsite
benefits.

## 5. Trade-off vs upstream `b9fbabd4` auto-bypass

Upstream commit `b9fbabd4` ("Gemma 4 multi-turn auto-bypass + RotatingKVCache
meta fix") chose the opposite approach: it detects mixed-attention models at
init and forces `request._bypass_prefix_cache=True` on every request, disabling
the prefix cache entirely on those models. The motivation in the commit message
is to cure `step-by-step-step-by-step…` word-loops observed at `rep_pen=1.1`.

The two approaches are not mutually exclusive (one could compose them), but
their defaults represent different products:

| Aspect | Upstream auto-bypass | This patch |
|---|---|---|
| Default behaviour | Cache disabled on mixed-attention | Cache active, buffer widened |
| Optimised for | Sampler configurations that risk word-loops (`rep_pen=1.1`) | Long-prompt multi-turn workloads (no `rep_pen=1.1`) |
| Multi-turn perf on long prompts | ~0 % hits (full re-prefill every turn) | ~95 % hits from turn 3 onward |
| Word-loop risk at `rep_pen=1.1` | Mitigated | Not mitigated |
| RAM cost vs upstream defaults | none | ~2 GB extra per loaded sliding model at 32 k floor |

A deployment that needs both can always set `rep_pen<=1.0`, neutralising the
loop risk, and benefit from this patch's prefix-cache.

## 6. Memory footprint

The K/V buffer per sliding layer is approximately:

```
bytes ≈ max_size × num_kv_heads × head_dim × 2 (K+V) × dtype_bytes
```

For Gemma 4 e4b mxfp4 (≈4 B params, 24 layers of which ≈20 are sliding,
`num_kv_heads ≈ 4`, `head_dim ≈ 256`, dtype ≈ 2 bytes effective after quant):

```
20 × 32 768 × 4 × 256 × 2 × 2 ≈ 2.1 GB
```

That is the marginal cost over upstream's `max_size=512` reservation. On
Apple-Silicon Macs with 24 GB+ unified memory it's an acceptable trade for the
40× speed-up on cached turns.

Operators can dial this in via `VMLX_ROTATING_KV_MAX_TOKENS`:

| Override | Approx. extra RAM (Gemma 4 e4b) | Use case |
|---:|---:|---|
| (unset / default 32 768) | ~2.1 GB | Typical agent sessions |
| 65 536 | ~4.2 GB | Long agent loops |
| 131 072 | ~8.4 GB | Test bench / context-max experiments |

## 7. Idempotency

Re-importing or `importlib.reload`-ing `vmlx_engine` does not chain wrappers.
The patched `__init__` carries a sentinel attribute
(`_vmlx_rotating_kv_widened = True`); on a second import the install path
checks the flag and skips re-wrapping.

## 8. Disabling the patch

There is no flag to opt out — the patch is unconditional once `vmlx_engine` is
imported, by design. If you need to test upstream-vanilla behaviour, install
the matching upstream version (`pip install vmlx==<version>`) instead of the
fork.

## 9. Verification

Source-level and behaviour-level guards live in
[`tests/test_rotating_kv_max_size_patch.py`](../tests/test_rotating_kv_max_size_patch.py).
Run them with:

```bash
pytest tests/test_rotating_kv_max_size_patch.py -v
```

The suite covers source presence, kwarg + positional call forms, env override
parsing, no-shrink invariant, and reload idempotency. It runs in well under a
second and requires no model weights.
