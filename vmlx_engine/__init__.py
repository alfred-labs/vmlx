# SPDX-License-Identifier: Apache-2.0
"""
vmlx-engine: Apple Silicon MLX backend for vLLM

This package provides native Apple Silicon GPU acceleration for vLLM
using Apple's MLX framework, mlx-lm for LLMs, and mlx-vlm for
vision-language models.

Features:
- Continuous batching via vLLM-style scheduler
- OpenAI-compatible API server
- Support for LLM and multimodal models
"""

__version__ = "1.5.48"

# mlx_lm 0.31.x changed create_attention_mask() to require return_array and
# window_size positional args.  mlx_vlm's qwen3_5/language.py calls
# create_ssm_mask(h, cache) which calls cache.make_mask(N) without those args.
# KVCache.make_mask passes them through to the local create_attention_mask()
# in cache.py which now requires all 4 positional args -> TypeError.
# Patch create_ssm_mask to always pass defaults for the new args.
try:
    import mlx_lm.models.base as _base

    if hasattr(_base, "create_ssm_mask"):
        _orig_ssm_mask = _base.create_ssm_mask

        def _patched_ssm_mask(h, cache=None):
            if cache is not None and hasattr(cache, "make_mask"):
                try:
                    return cache.make_mask(h.shape[1])
                except TypeError:
                    return cache.make_mask(
                        h.shape[1], return_array=False, window_size=None
                    )
            return None

        _base.create_ssm_mask = _patched_ssm_mask
except Exception:
    pass

# Also patch KVCache.make_mask to provide defaults for the new positional args
# in mlx_lm.models.cache.create_attention_mask(N, offset, return_array, window_size).
try:
    import mlx_lm.models.cache as _cache_mod

    if hasattr(_cache_mod, "KVCache") and hasattr(_cache_mod.KVCache, "make_mask"):
        _orig_kv_make_mask = _cache_mod.KVCache.make_mask
        _cache_create_attention_mask = getattr(
            _cache_mod, "create_attention_mask", None
        )

        def _patched_kv_make_mask(self, *args, **kwargs):
            kwargs.setdefault("return_array", False)
            kwargs.setdefault("window_size", None)
            if _cache_create_attention_mask is not None:
                return _cache_create_attention_mask(*args, offset=self.offset, **kwargs)
            return _orig_kv_make_mask(self, *args, **kwargs)

        _cache_mod.KVCache.make_mask = _patched_kv_make_mask
except Exception:
    pass

# mlx_vlm registry patches (gemma4 + kimi_k25) — DEFERRED to first VLM
# load instead of import time. Importing `mlx_vlm.prompt_utils` /
# `mlx_vlm.utils` transitively pulls in `mlx_vlm.generate` which has
# a module-level `mx.new_stream(mx.default_device())`. That stream is
# then bound to the importing thread (uvicorn MainThread) and becomes
# inaccessible to the `llm-worker` thread that scheduler.step()
# eventually runs on — DSV4-Flash + JANGTQ bundles crash with
# `RuntimeError: There is no Stream(gpu, N) in current thread.` mid-
# prefill (mlxstudio#119 follow-up, 2026-05-02). Calling
# `_install_mlx_vlm_registry_patches()` from the loader executor right
# before the first VLM load keeps the patches idempotent + ensures
# any thread-bound MLX stream is created on the load thread.
def _install_mlx_vlm_registry_patches() -> None:
    """Install gemma4 / kimi_k25 entries in mlx_vlm's MODEL_CONFIG /
    MODEL_REMAPPING. Idempotent. Safe to call from any thread; should
    be called from the same thread that will later run the VLM load
    so any module-level `mx.new_stream(...)` ends up bound to that
    thread."""
    try:
        from mlx_vlm.prompt_utils import (
            MODEL_CONFIG as _VLM_MODEL_CONFIG,
            MessageFormat as _VLMMF,
        )
        _VLM_MODEL_CONFIG.setdefault("gemma4", _VLMMF.LIST_WITH_IMAGE_TYPE)
        _VLM_MODEL_CONFIG.setdefault("gemma4_text", _VLMMF.LIST_WITH_IMAGE_TYPE)
    except Exception:
        pass
    try:
        from mlx_vlm import utils as _mlx_vlm_utils
        _mapping = getattr(_mlx_vlm_utils, "MODEL_REMAPPING", None)
        if _mapping is not None:
            _mapping.setdefault("kimi_k25", "kimi_vl")
    except Exception:
        pass
    try:
        from mlx_vlm.prompt_utils import MODEL_CONFIG as _KV_MODEL_CONFIG
        if "kimi_k25" not in _KV_MODEL_CONFIG and "kimi_vl" in _KV_MODEL_CONFIG:
            _KV_MODEL_CONFIG["kimi_k25"] = _KV_MODEL_CONFIG["kimi_vl"]
    except Exception:
        pass


def _patch_loaded_mlx_vlm_registry_module(module_name: str, module) -> None:
    """Patch mlx_vlm registry modules without importing them eagerly."""
    try:
        if module_name == "mlx_vlm.utils":
            _mapping = getattr(module, "MODEL_REMAPPING", None)
            if _mapping is not None:
                _mapping.setdefault("kimi_k25", "kimi_vl")
        elif module_name == "mlx_vlm.prompt_utils":
            _model_config = getattr(module, "MODEL_CONFIG", None)
            _message_format = getattr(module, "MessageFormat", None)
            if _model_config is not None and _message_format is not None:
                _model_config.setdefault("gemma4", _message_format.LIST_WITH_IMAGE_TYPE)
                _model_config.setdefault("gemma4_text", _message_format.LIST_WITH_IMAGE_TYPE)
                if "kimi_k25" not in _model_config and "kimi_vl" in _model_config:
                    _model_config["kimi_k25"] = _model_config["kimi_vl"]
    except Exception:
        pass


def _install_mlx_vlm_registry_import_hook() -> None:
    """Patch mlx_vlm registries lazily when callers import those modules.

    This preserves the no-eager-mlx_vlm-import rule above: importing
    vmlx_engine alone must not create mlx_vlm's thread-bound MLX stream.
    """
    import importlib.abc
    import importlib.machinery
    import sys

    targets = {"mlx_vlm.utils", "mlx_vlm.prompt_utils"}

    class _VLMRegistryPatchLoader(importlib.abc.Loader):
        def __init__(self, wrapped):
            self._wrapped = wrapped

        def create_module(self, spec):
            create = getattr(self._wrapped, "create_module", None)
            if create is not None:
                return create(spec)
            return None

        def exec_module(self, module):
            self._wrapped.exec_module(module)
            _patch_loaded_mlx_vlm_registry_module(module.__name__, module)

    class _VLMRegistryPatchFinder(importlib.abc.MetaPathFinder):
        _vmlx_vlm_registry_patch_finder = True

        def find_spec(self, fullname, path, target=None):
            if fullname not in targets:
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            if spec is None or spec.loader is None:
                return spec
            if not isinstance(spec.loader, _VLMRegistryPatchLoader):
                spec.loader = _VLMRegistryPatchLoader(spec.loader)
            return spec

    for _name in targets:
        if _name in sys.modules:
            _patch_loaded_mlx_vlm_registry_module(_name, sys.modules[_name])

    if not any(getattr(f, "_vmlx_vlm_registry_patch_finder", False) for f in sys.meta_path):
        sys.meta_path.insert(0, _VLMRegistryPatchFinder())


_install_mlx_vlm_registry_import_hook()

# Install tracked runtime patches for upstream model dispatch/numeric fixes.
# This is intentionally after the lightweight mlx_lm compatibility shims and
# before lazy exports so importing vmlx_engine prepares the process for model
# loads without requiring each loader to remember patch bootstrap order.
try:
    from vmlx_engine import runtime_patches as _runtime_patches  # noqa: F401
except Exception:
    pass

# =========================================================================
# RotatingKVCache max_size widening (mixed-attention prefix-cache fix)
# =========================================================================
#
# Why this exists
# ---------------
# Mixed-attention models (Gemma 4 sliding+full, gpt-oss, exaone-moe, cohere2,
# llama-with-sliding-window, etc.) build their sliding layers with
# ``RotatingKVCache(max_size=sliding_window)`` — typically 512 tokens. As soon
# as a prompt exceeds that window, ``mllm_scheduler._truncate_hybrid_cache``
# bails on ``offset > max_size`` and returns ``None``, which silently
# disables every prefix-cache write for the request: no L0 paged insert, no
# L1 block disk write-through, no L2 prompt store. The cache pyramid exists
# but never receives data for long-prompt sessions (agent-style system
# prompts of 1–3 k tokens plus multi-turn history easily clear the trained
# window).
#
# What this patch does
# --------------------
# Monkey-patch ``RotatingKVCache.__init__`` at import time. When a caller
# constructs the cache with ``max_size=N``, we enlarge ``max_size`` to at
# least ``ROTATING_KV_DEFAULT_MAX`` (32 768) — or higher if the env var
# ``VMLX_ROTATING_KV_MAX_TOKENS`` is set to a larger value.
#
# Why this is compute-safe
# ------------------------
# The attention mask is computed independently in the model's forward pass.
# It still uses the trained ``sliding_window`` to decide which past tokens
# contribute to attention. Only the K/V tensor reservation grows. Logits
# and output tokens are bit-identical to upstream — we just stop tripping
# the truncation guard.
#
# Why patch the class and not a callsite
# --------------------------------------
# vmlx loaders (``smelt_loader``, ``jang_loader``, ``tokenizer``) reassign
# ``model.make_cache`` to their own factories that do not read the env. And
# on ``mlx-lm >= 0.31.2`` models load via ``mlx_lm.models.gemma4_text.Model``
# directly, bypassing the vendored copy. Wrapping the class constructor is
# the only point that catches every construction path: the model's own
# ``make_cache``, smelt/jang/tq overrides, the prefix-cache reconstruction
# in ``prefix_cache.py``, and mamba companion constructors.
#
# Relation to upstream b9fbabd4
# -----------------------------
# Upstream's "Gemma 4 multi-turn auto-bypass" deliberately *disables* the
# prefix cache on mixed-attention models to cure ``step-by-step…`` word-loops
# at ``rep_pen=1.1``. That trade-off makes sense when the deployment can hit
# that sampler config. This patch takes the opposite stance: keep the cache
# active, trading the loop-protection (which deployments not using
# ``rep_pen=1.1`` do not benefit from anyway) for the multi-turn speedup.
#
# Idempotent
# ----------
# The patch is gated by a sentinel so re-importing or reloading the module
# never chains wrappers.
try:
    import os as _os
    from mlx_lm.models.cache import RotatingKVCache as _RotatingKVCache

    ROTATING_KV_DEFAULT_MAX = 32768
    ROTATING_KV_OVERRIDE_ENV = "VMLX_ROTATING_KV_MAX_TOKENS"
    _ROTATING_KV_PATCH_FLAG = "_vmlx_rotating_kv_widened"

    def _effective_rotating_kv_max_size():
        """Return the minimum max_size the patch should enforce.

        Picks the larger of ``ROTATING_KV_DEFAULT_MAX`` and the integer
        value of ``VMLX_ROTATING_KV_MAX_TOKENS`` if set and parseable.
        """
        override = 0
        raw = _os.environ.get(ROTATING_KV_OVERRIDE_ENV)
        if raw is not None:
            try:
                override = int(raw)
            except (TypeError, ValueError):
                override = 0
        return max(ROTATING_KV_DEFAULT_MAX, override)

    if not getattr(_RotatingKVCache.__init__, _ROTATING_KV_PATCH_FLAG, False):
        _orig_rkv_init = _RotatingKVCache.__init__

        def _patched_rkv_init(self, *args, **kwargs):
            effective = _effective_rotating_kv_max_size()

            if "max_size" in kwargs:
                if effective > kwargs["max_size"]:
                    kwargs["max_size"] = effective
            elif args:
                current = args[0]
                if effective > current:
                    args = (effective,) + args[1:]
            else:
                kwargs["max_size"] = effective

            _orig_rkv_init(self, *args, **kwargs)

        setattr(_patched_rkv_init, _ROTATING_KV_PATCH_FLAG, True)
        _RotatingKVCache.__init__ = _patched_rkv_init
except Exception:
    # mlx_lm not available (e.g. non-Apple platforms during packaging),
    # or class signature changed — leave upstream behaviour in place.
    pass

# All imports are lazy to allow usage on non-Apple Silicon platforms
# (e.g., CI running on Linux) where mlx_lm is not available.


def __getattr__(name):
    """Lazy load all components to avoid mlx_lm import on non-Apple platforms."""
    # Request management
    if name in ("Request", "RequestOutput", "RequestStatus", "SamplingParams"):
        from vmlx_engine import request

        return getattr(request, name)

    # Scheduler
    if name in ("Scheduler", "SchedulerConfig", "SchedulerOutput"):
        from vmlx_engine import scheduler

        return getattr(scheduler, name)

    # Engine
    if name in ("EngineCore", "AsyncEngineCore", "EngineConfig"):
        from vmlx_engine import engine_core

        return getattr(engine_core, name)

    # Prefix cache
    if name in ("PrefixCacheManager", "PrefixCacheStats", "BlockAwarePrefixCache"):
        from vmlx_engine import prefix_cache

        return getattr(prefix_cache, name)

    # Paged cache
    if name in ("PagedCacheManager", "CacheBlock", "BlockTable", "CacheStats"):
        from vmlx_engine import paged_cache

        return getattr(paged_cache, name)

    # MLLM cache (with legacy VLM aliases)
    if name in (
        "MLLMCacheManager",
        "MLLMCacheStats",
        "VLMCacheManager",
        "VLMCacheStats",
    ):
        from vmlx_engine import mllm_cache

        # Map legacy VLM names to MLLM
        mllm_name = name.replace("VLM", "MLLM") if name.startswith("VLM") else name
        return getattr(mllm_cache, mllm_name)

    # Model registry
    if name in ("get_registry", "ModelOwnershipError"):
        from vmlx_engine import model_registry

        return getattr(model_registry, name)

    # Model config registry
    if name in ("get_model_config_registry", "ModelConfigRegistry", "ModelConfig"):
        from vmlx_engine import model_config_registry

        return getattr(model_config_registry, name)

    # vLLM integration components (require torch)
    if name == "MLXPlatform":
        from vmlx_engine.mlx_platform import MLXPlatform

        return MLXPlatform
    if name == "MLXWorker":
        from vmlx_engine.worker import MLXWorker

        return MLXWorker
    if name == "MLXModelRunner":
        from vmlx_engine.model_runner import MLXModelRunner

        return MLXModelRunner
    if name == "MLXAttentionBackend":
        from vmlx_engine.attention import MLXAttentionBackend

        return MLXAttentionBackend

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Core (lazy loaded, require torch)
    "MLXPlatform",
    "MLXWorker",
    "MLXModelRunner",
    "MLXAttentionBackend",
    # Request management
    "Request",
    "RequestOutput",
    "RequestStatus",
    "SamplingParams",
    # Scheduler
    "Scheduler",
    "SchedulerConfig",
    "SchedulerOutput",
    # Engine
    "EngineCore",
    "AsyncEngineCore",
    "EngineConfig",
    # Model registry
    "get_registry",
    "ModelOwnershipError",
    # Prefix cache (LLM)
    "PrefixCacheManager",
    "PrefixCacheStats",
    "BlockAwarePrefixCache",
    # Paged cache (memory efficiency)
    "PagedCacheManager",
    "CacheBlock",
    "BlockTable",
    "CacheStats",
    # MLLM cache (images/videos)
    "MLLMCacheManager",
    "MLLMCacheStats",
    # Legacy aliases
    "VLMCacheManager",
    "VLMCacheStats",
    # Version
    "__version__",
]
