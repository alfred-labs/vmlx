# SPDX-License-Identifier: Apache-2.0
"""Regression tests for the RotatingKVCache max_size widening patch.

The patch installs a wrapper around ``mlx_lm.models.cache.RotatingKVCache.__init__``
at vmlx_engine import time. The wrapper enlarges ``max_size`` to at least
``ROTATING_KV_DEFAULT_MAX`` (32 768) — or the integer value of the
``VMLX_ROTATING_KV_MAX_TOKENS`` env var if larger.

The patch is required because upstream's ``_truncate_hybrid_cache`` bails on
``offset > max_size`` for any prompt past the trained ``sliding_window``
(e.g. Gemma 4's ``sliding_window=512``), silently disabling every prefix-cache
layer for long-prompt sessions.

These tests run in <1s, do not require model weights, and catch the most
common regression vectors:

1. The patch source actually lives in ``vmlx_engine/__init__.py``.
2. The wrapper widens small ``max_size`` values.
3. The env var override widens ``max_size`` past the default.
4. The wrapper leaves already-large ``max_size`` values alone.
5. The wrapper is idempotent (re-importing the module never chains wrappers).
6. Both positional and keyword ``max_size`` call forms are honoured.
"""
from __future__ import annotations

import importlib
import inspect
import os
from pathlib import Path
from unittest import mock

import pytest

# Skip the whole suite when mlx_lm is not importable (CI on Linux, etc.).
pytest.importorskip("mlx_lm.models.cache", reason="mlx_lm is required for RotatingKVCache patching")

import vmlx_engine
from mlx_lm.models.cache import RotatingKVCache


# ---------------------------------------------------------------------------
# Source-level checks: the patch lives in the package init
# ---------------------------------------------------------------------------


class TestPatchSourcePresence:
    """The patch must live in ``vmlx_engine/__init__.py``."""

    def test_init_module_contains_default_constant(self):
        init_path = Path(inspect.getfile(vmlx_engine))
        source = init_path.read_text()
        assert "ROTATING_KV_DEFAULT_MAX" in source
        assert "32768" in source

    def test_init_module_references_override_env(self):
        init_path = Path(inspect.getfile(vmlx_engine))
        source = init_path.read_text()
        assert "VMLX_ROTATING_KV_MAX_TOKENS" in source
        assert "ROTATING_KV_OVERRIDE_ENV" in source

    def test_init_module_patches_rotating_kv_init(self):
        init_path = Path(inspect.getfile(vmlx_engine))
        source = init_path.read_text()
        assert "RotatingKVCache.__init__" in source
        assert "_patched_rkv_init" in source

    def test_default_constant_exported_for_inspection(self):
        # Tests and operators rely on importing the default to compare or
        # mutate at runtime — surface it as a module attribute.
        assert hasattr(vmlx_engine, "ROTATING_KV_DEFAULT_MAX")
        assert vmlx_engine.ROTATING_KV_DEFAULT_MAX == 32768

    def test_override_env_name_exported_for_inspection(self):
        assert hasattr(vmlx_engine, "ROTATING_KV_OVERRIDE_ENV")
        assert vmlx_engine.ROTATING_KV_OVERRIDE_ENV == "VMLX_ROTATING_KV_MAX_TOKENS"


# ---------------------------------------------------------------------------
# Behaviour: the wrapper enlarges max_size to the configured floor
# ---------------------------------------------------------------------------


class TestSmallMaxSizeWidened:
    """A ``max_size`` below the floor is widened to at least the floor."""

    def test_kwarg_form_small_max_size_widened(self):
        cache = RotatingKVCache(max_size=512, keep=0)
        assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX

    def test_positional_form_small_max_size_widened(self):
        cache = RotatingKVCache(512)
        assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX

    def test_zero_max_size_widened_to_default(self):
        cache = RotatingKVCache(max_size=0)
        assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX


class TestLargeMaxSizeUntouched:
    """A ``max_size`` already at or above the floor must stay untouched."""

    def test_max_size_well_above_default_preserved(self):
        target = vmlx_engine.ROTATING_KV_DEFAULT_MAX * 2
        cache = RotatingKVCache(max_size=target)
        assert cache.max_size == target

    def test_max_size_exactly_default_preserved(self):
        target = vmlx_engine.ROTATING_KV_DEFAULT_MAX
        cache = RotatingKVCache(max_size=target)
        assert cache.max_size == target


# ---------------------------------------------------------------------------
# Behaviour: VMLX_ROTATING_KV_MAX_TOKENS env override
# ---------------------------------------------------------------------------


class TestEnvOverride:
    """``VMLX_ROTATING_KV_MAX_TOKENS`` lifts the floor when larger than default."""

    def test_override_above_default_lifts_floor(self):
        target = vmlx_engine.ROTATING_KV_DEFAULT_MAX * 2
        with mock.patch.dict(os.environ, {vmlx_engine.ROTATING_KV_OVERRIDE_ENV: str(target)}):
            cache = RotatingKVCache(max_size=512)
            assert cache.max_size >= target

    def test_override_below_default_ignored(self):
        # The wrapper takes max(default, override), so a tiny override does
        # not shrink the floor.
        with mock.patch.dict(os.environ, {vmlx_engine.ROTATING_KV_OVERRIDE_ENV: "100"}):
            cache = RotatingKVCache(max_size=512)
            assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX

    def test_unparseable_override_falls_back_to_default(self):
        with mock.patch.dict(os.environ, {vmlx_engine.ROTATING_KV_OVERRIDE_ENV: "not-a-number"}):
            cache = RotatingKVCache(max_size=512)
            assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX

    def test_unset_override_uses_default(self):
        # Explicitly remove the env var even if the test runner set it.
        env = {k: v for k, v in os.environ.items() if k != vmlx_engine.ROTATING_KV_OVERRIDE_ENV}
        with mock.patch.dict(os.environ, env, clear=True):
            cache = RotatingKVCache(max_size=512)
            assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX


# ---------------------------------------------------------------------------
# Idempotency: re-importing the module never chains wrappers
# ---------------------------------------------------------------------------


class TestPatchIdempotency:
    """Reloading vmlx_engine must not re-wrap RotatingKVCache.__init__."""

    def test_init_carries_patch_flag(self):
        # The wrapper itself must mark the bound init so a second import
        # detects an already-installed patch and skips re-wrapping.
        assert getattr(RotatingKVCache.__init__, "_vmlx_rotating_kv_widened", False) is True

    def test_reimport_does_not_double_wrap(self):
        first = RotatingKVCache.__init__
        importlib.reload(vmlx_engine)
        second = RotatingKVCache.__init__
        # Either the same callable object survives (preferred), or both still
        # widen correctly without chaining. The flag guarantees we don't chain.
        cache = RotatingKVCache(max_size=512)
        assert cache.max_size >= vmlx_engine.ROTATING_KV_DEFAULT_MAX
        assert getattr(second, "_vmlx_rotating_kv_widened", False) is True
        # The wrapper survives reload — chaining would set _vmlx_… on a new
        # function while keeping the old one referenced by closure.
        # Cheap proof: the bound init resolves the same object before and
        # after reload when the guard is honoured.
        assert first is second
