# JANGTQ MPP/NAX Runtime Integration

Date: 2026-05-12

## What Changed

vMLX now has an explicit startup, UI, and health surface for the JANGTQ/MXTQ
MPP/NAX TensorOps lane.

- CLI: `--jangtq-mpp-nax off|auto|on`
- Panel session config: `jangtqMppNax`, default `auto`
- Session launch: emits `--jangtq-mpp-nax <mode>`
- `/health`: reports `acceleration.jangtq_mpp_nax`
- Performance panel: shows `JANGTQ MPP/NAX`

This is not the same as MLX affine quantized matmul. JANGTQ still uses the
TurboQuant codebook path; the new lane is the custom JANGTQ kernel using MPP/NAX
directly. MXFP4/NVFP4/FP4-style bundles are kept on the native MLX affine path.

## Startup Semantics

`auto` is the app default. The CLI sets `JANGTQ_MPP_NAX=auto` before model load.
The jang-tools kernels decide per dispatch shape whether the MPP/NAX path is
faster.

`off` sets `JANGTQ_MPP_NAX=off` and preserves the legacy custom kernels.

`on` sets `JANGTQ_MPP_NAX=1` and forces the path for diagnostics.

## Health Semantics

`quantization.codec` remains the weight codec:

- `turboquant_codebook`: JANGTQ/MXTQ routed codebook tensors
- `affine_quantized_matmul`: MLX affine/MXFP-style tensors
- `full_precision_or_unknown`: no quantized matmul evidence

`acceleration.kernel_type` reports:

- `turboquant_codebook_mpp_nax` when JANGTQ MPP/NAX is active
- `turboquant_codebook` when JANGTQ is present but MPP/NAX is off/unavailable
- `affine_quantized_matmul` for MLX affine/MXFP-style bundles

`acceleration.jangtq_mpp_nax` reports:

- `mode`
- `requested`
- `available`
- `active`
- `uses_mlx_quantized_matmul=false`
- `reason`

## Cache Boundary

This change does not alter prefix cache, paged cache, block-L2, typed ZAYA CCA,
hybrid SSM companion state, DSV4 composite cache, or TurboQuant KV cache policy.
It only controls the JANGTQ weight-matmul dispatch lane.

Cache correctness must still be validated per family. Do not use an MPP/NAX
health win as proof of cache reuse or multi-turn coherency.

## Verification

Focused checks run after the integration patch:

```sh
cd /Users/eric/mlx/vllm-mlx
.venv/bin/python -m pytest -q \
  tests/test_engine_audit.py::TestJangTqMppNaxCliPolicy \
  tests/test_engine_audit.py::TestTurboQuantKVTelemetry

cd panel
npx vitest run tests/settings-flow.test.ts
npm run typecheck

cd /Users/eric/mlx/vllm-mlx
.venv/bin/python -B -m py_compile vmlx_engine/server.py vmlx_engine/cli.py
.venv/bin/python -m vmlx_engine.cli serve --help | rg -n "jangtq-mpp-nax|JANGTQ/MXTQ"
JANGTQ_MPP_NAX=auto .venv/bin/python - <<'PY'
from vmlx_engine.server import _jangtq_mpp_nax_runtime_status
print(_jangtq_mpp_nax_runtime_status({"supported": True, "brand": "Apple M5 Max"}))
PY
```

Observed runtime status on this machine:

```text
{'mode': 'auto', 'requested': True, 'available': True, 'active': True,
 'uses_mlx_quantized_matmul': False, 'reason': None}
```

## Bundled Live Gate

After syncing the local `jang-tools` prototype into `panel/bundled-python`, the
bundled server path was tested directly with a real Qwen JANGTQ model:

```sh
cd /Users/eric/mlx/vllm-mlx
panel/bundled-python/python/bin/python3 -B -s -m vmlx_engine.cli serve \
  /Volumes/EricsLLMDrive/jangq-ai/Qwen3.6-35B-A3B-JANGTQ4 \
  --host 127.0.0.1 --port 8137 \
  --max-num-seqs 1 \
  --prefill-batch-size 512 \
  --prefill-step-size 2048 \
  --completion-batch-size 512 \
  --continuous-batching \
  --tool-call-parser qwen \
  --enable-auto-tool-choice \
  --reasoning-parser qwen3 \
  --use-paged-cache \
  --paged-cache-block-size 64 \
  --max-cache-blocks 1000 \
  --enable-block-disk-cache \
  --block-disk-cache-max-gb 10 \
  --stream-interval 1 \
  --max-tokens 512 \
  --default-temperature 0.0 \
  --default-top-p 1.0 \
  --default-repetition-penalty 1.0 \
  --jangtq-mpp-nax auto
```

Observed `/health` fields:

```json
{
  "acceleration": {
    "kernel_type": "turboquant_codebook_mpp_nax",
    "metal_na_capable": true,
    "metal_na_active_on_host": true,
    "jangtq_mpp_nax": {
      "mode": "auto",
      "requested": true,
      "available": true,
      "active": true,
      "uses_mlx_quantized_matmul": false,
      "reason": null
    }
  },
  "quantization": {
    "codec": "turboquant_codebook",
    "weight_format": "mxtq",
    "mxtq_bits": 4,
    "routed_expert_bits": 4,
    "target_bits": 4
  }
}
```

Real `/v1/chat/completions` output with `enable_thinking=false`:

```text
READY
45
CERULEAN
```

The server log also confirmed Qwen3.6 JANGTQ4 loaded through the JANGTQ VLM fast
path, patched `SwitchGLU`, started paged cache plus block disk cache plus SSM
companion L2, and stored a paged prefix cache entry after generation.

## Packaging Requirement

The vMLX integration assumes the packaged `jang_tools` contains
`jang_tools.turboquant.mpp_nax_kernel` plus the `JANGTQ_MPP_NAX` call sites in
the TurboQuant kernels. If a DMG bundles an older jang-tools wheel/source tree,
health will report `available=false` and fall back to the legacy custom kernels.

The live bundled gate above proves the local development bundle after a manual
`pip install --force-reinstall --no-deps /Users/eric/jang/jang-tools`. It is not
by itself proof that a clean checkout or future DMG contains the same
`jang-tools` files. The release lane must still make the jang-tools helper
module and call-site changes part of the packaged source/wheel.

## 2026-05-12 Follow-Up Packaging Audit

Codex rechecked the JANG source/package boundary after the initial live proof.

Problem found:

- The parent `/Users/eric/jang/.gitignore` ignored `jang-tools/jang_tools/turboquant/`
  and broad `test_*` files, so `mpp_nax_kernel.py`, `mpp_dense_kernel.py`, and
  their tests were hidden from normal Git status.
- A clean checkout would therefore miss the helper modules unless they were
  force-added. That would make vMLX's bundled verifier and runtime health
  surface regress to `available=false` or import failure.

Fix applied locally:

- `.gitignore` now keeps the private TurboQuant scratch area ignored while
  explicitly surfacing:
  - `jang-tools/jang_tools/turboquant/mpp_nax_kernel.py`
  - `jang-tools/jang_tools/turboquant/mpp_dense_kernel.py`
  - `jang-tools/tests/test_turboquant_mpp_nax_kernel.py`
  - `jang-tools/tests/test_turboquant_mpp_dense_kernel.py`

Fresh verification:

```sh
cd /Users/eric/jang/jang-tools
/Users/eric/mlx/vllm-mlx/.venv/bin/python -m pytest -q \
  tests/test_turboquant_mpp_nax_kernel.py \
  tests/test_turboquant_mpp_dense_kernel.py \
  tests/test_turboquant_kernel_source_contract.py \
  tests/test_turboquant_cache.py
# 47 passed

/Users/eric/mlx/vllm-mlx/.venv/bin/python -B -m py_compile \
  jang_tools/turboquant/mpp_nax_kernel.py \
  jang_tools/turboquant/mpp_dense_kernel.py \
  jang_tools/turboquant/tq_kernel.py \
  jang_tools/turboquant/gather_tq_kernel.py \
  jang_tools/turboquant/fused_gate_up_kernel.py

cd /Users/eric/jang
git diff --check
```

```sh
cd /Users/eric/mlx/vllm-mlx
.venv/bin/python -m pytest -q \
  tests/test_engine_audit.py::TestJangTqMppNaxCliPolicy \
  tests/test_engine_audit.py::TestTurboQuantKVTelemetry
# 75 passed

cd panel
npx vitest run tests/settings-flow.test.ts
# 197 passed
npm run typecheck
```

Bundled boundary:

```sh
cd /Users/eric/mlx/vllm-mlx
VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/jang-tools \
  panel/scripts/verify-bundled-python.sh
# all critical imports ok, including jang_tools.turboquant.mpp_nax_kernel
```

Release-build guard:

```sh
cd /Users/eric/mlx/vllm-mlx
panel/scripts/bundle-python.sh
# exits 1 before packaging because /Users/eric/jang/jang-tools is tracked-dirty
```

That failure is intentional. It prevents a DMG from silently bundling local
uncommitted JANG runtime edits. The fix is to commit/stash/drop the JANG lane or
point `VMLINUX_JANG_TOOLS_SOURCE` at a clean checkout.

Wheel/sdist package check:

```sh
cd /Users/eric/jang/jang-tools
/Users/eric/mlx/vllm-mlx/.venv/bin/python -m build \
  --wheel --sdist --outdir /tmp/jang-mpp-package-check
```

Direct archive inspection:

- wheel contains `jang_tools/turboquant/mpp_nax_kernel.py`
- wheel contains `jang_tools/turboquant/mpp_dense_kernel.py`
- sdist contains both runtime modules and both new tests
- wheel intentionally does not install top-level `tests/`

Installed-wheel import check:

```sh
rm -rf /tmp/jang-wheel-import-check
/Users/eric/mlx/vllm-mlx/.venv/bin/python -m pip install --no-deps \
  --target /tmp/jang-wheel-import-check \
  /tmp/jang-mpp-package-check/jang-2.5.28-py3-none-any.whl
cd /tmp
PYTHONPATH=/tmp/jang-wheel-import-check \
  /Users/eric/mlx/vllm-mlx/.venv/bin/python - <<'PY'
import sys
sys.path = [p for p in sys.path if not p.endswith('/Users/eric/jang/jang-tools') and p not in ('', '.')]
import jang_tools.turboquant.mpp_nax_kernel as nax
print(nax.__file__)
print(nax.mpp_nax_tensorops_available())
PY
# /tmp/jang-wheel-import-check/jang_tools/turboquant/mpp_nax_kernel.py
# True
```

Live speed/output parity gates:

| Model | Prompt | Mode | Approx PP tok/s | Decode tok/s after first | Output parity |
| --- | ---: | --- | ---: | ---: | --- |
| Qwen3.6-35B-A3B-JANGTQ4 | 2084 tokens | off | 1075.0 | 106.8 | same prefix |
| Qwen3.6-35B-A3B-JANGTQ4 | 2084 tokens | auto | 1902.3 | 106.7 | same prefix |
| Qwen3.6-35B-A3B-JANGTQ4 | 8244 tokens | off | 1056.6 | 101.9 | same prefix |
| Qwen3.6-35B-A3B-JANGTQ4 | 8244 tokens | auto | 1858.5 | 101.8 | same prefix |
| ZAYA1-8B-JANGTQ_K | 2092 tokens | off | 2394.9 | 71.9 | same prefix |
| ZAYA1-8B-JANGTQ_K | 2092 tokens | auto | 4292.3 | 72.4 | same prefix |
| MiniMax-M2.7-Small-JANGTQ | 2126 tokens | off | 161.8 | 40.5 | same prefix |
| MiniMax-M2.7-Small-JANGTQ | 2126 tokens | auto | 233.9 | 34.2 | same prefix |
| Hy3-preview-JANGTQ2 | 2099 tokens | off | 111.0 | 17.1 | same visible prefix |
| Hy3-preview-JANGTQ2 | 2099 tokens | auto | 202.9 | 15.8 | same visible prefix |

Notes:

- Qwen and ZAYA show prefill improvement with decode unchanged.
- MiniMax Small shows prefill improvement, but decode in this short run was
  lower under `auto`; treat MiniMax as needing deeper decode profiling before
  calling it an all-around speed win.
- Hy3-preview-JANGTQ2 shows prefill improvement and the same correct visible
  answer prefix, `READY CERULEAN 45`. The standalone probe continued sampling
  after the model emitted EOS, so post-EOS continuation is not counted as a
  runtime loop; app/API generation must stop at EOS.
- `ZAYA1-VL-8B-JANGTQ4` could not be loaded by `jangtq_live_nax_probe.py`
  because that harness uses `load_jangtq_model`, not the VLM loader. This is a
  harness limitation, not evidence of a VLM runtime failure.

Live vMLX API gate:

- Server command used source vMLX plus `PYTHONPATH=/Users/eric/jang/jang-tools`
  and `--jangtq-mpp-nax auto` on Qwen3.6-35B-A3B-JANGTQ4.
- `/health` reported:
  - `acceleration.kernel_type=turboquant_codebook_mpp_nax`
  - `jangtq_mpp_nax.mode=auto`
  - `requested=true`, `available=true`, `active=true`
  - quantization `codec=turboquant_codebook`, `mxtq_bits=4`,
    `routed_expert_bits=4`
  - routing `trained_active_experts=8`, source `config.text_config.num_experts_per_tok`
- `/v1/responses` first turn returned `READY\n45` with no reasoning leak.
- `/v1/responses` second turn with `previous_response_id` returned `CERULEAN`
  and usage reported `cached_tokens=24`, `cache_detail=paged+ssm`.
- `/v1/chat/completions` returned `READY 42` with no `reasoning_content`.
- `/api/chat` returned `OLLAMA_OK`.
- `/v1/messages` returned `ANTHROPIC_OK`.
- Server was stopped after the gate; port 8137 had no listener.

Live vMLX ZAYA1-VL gate:

- Server command used source vMLX plus `PYTHONPATH=/Users/eric/jang/jang-tools`,
  `--is-mllm`, and `--jangtq-mpp-nax auto` on
  `/Users/eric/models/JANGQ/ZAYA1-VL-8B-JANGTQ4`.
- `/health` reported:
  - `acceleration.kernel_type=turboquant_codebook_mpp_nax`
  - `jangtq_mpp_nax.active=true`
  - model family `zaya1_vl`, `is_mllm=true`
  - `cache_subtype=zaya_cca`
- Single-turn `/v1/responses` returned `17 + 28 = 45`; scheduler telemetry
  showed `prompt_tps=180.8` and `generation_tps=77.7` for that short text-only
  MLLM request.
- Two-turn `/v1/responses` with `previous_response_id` returned `CERULEAN` on
  the second turn and usage reported `cached_tokens=25`,
  `cache_detail=paged+zaya_cca`.
- Server log confirmed JANGTQ VLM fast path, 40 fused `SwitchGLU` instances,
  paged cache, block disk write-through, and typed ZAYA CCA cache records.

JANG test hygiene fixed during this audit:

- `tests/test_inference.py` now inserts its optional fake `mlx_vlm` module via
  `monkeypatch.setitem`, so it cannot poison later real ZAYA-VL imports.
- `pyproject.toml` now constrains pytest discovery to `tests` and
  `jang_tools/dsv4/tests`, so manual smoke script
  `jang_tools/scripts/test_qwen36_python.py` is not executed as a pytest file.
- Fresh full JANG test roots result: `505 passed, 8 skipped`.

Repo-local packaged app gate:

- Built `panel/release/mac-arm64/vMLX.app` from vMLX `300dbe8b` plus JANG
  `2be5c5f`.
- Direct `codesign --deep --sign - vMLX.app` was insufficient: bundled
  `libpython3.12.dylib` remained unsigned at load time even though app-level
  strict verify passed.
- Correct local signing sequence is the one used by `build-and-install.sh`:
  sign bundled Python Mach-O files first, then seal the `.app`.
- After signing 499 bundled Python native files and resealing the app,
  `panel/scripts/release-gate-python-app.py --skip-sleep-wake --skip-gui`
  passed.
- The release gate now hashes `turboquant/mpp_nax_kernel.py` in the packaged
  `jang_tools` tree, so future packages cannot pass with the UI/CLI toggle but
  without the critical JANG runtime module.

Release boundary:

- Do not commit the vMLX `--jangtq-mpp-nax` UI/CLI/health wiring without the
  matching JANG kernel modules and call-site changes.
- Do not claim this as DSV4 correctness work. It only changes JANGTQ weight
  matmul dispatch. DSV4 cache/attention/coherency gates remain separate.
