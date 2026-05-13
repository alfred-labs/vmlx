# vMLX 2026-05-13 Completion Audit

This is the tracked completion audit for the installed-app model/cache gate.
Raw local artifacts are intentionally kept under ignored
`docs/internal/release-gates/20260513_installed_app_full_model_gate/`.

## Objective

Prove the installed Python/Electron vMLX app is release-ready for as many local
`~/models` bundles as can fit on this M5 Max, covering:

- JANG, JANGTQ, MXFP4, affine/MLX, VL/media, and image-generation/edit
  detection and startup;
- coherent generation, multi-turn recall, and reasoning controls where
  relevant;
- prompt-processing speed and token-generation speed capture;
- direct, prefix/paged/L2, bypass, sleep/wake, and JIT fallback cache paths;
- Chat Completions, Responses, Anthropic, Ollama, image generation, and image
  edit API surfaces;
- source commit/push state, local installed-app sanity, and secret hygiene.

## Evidence Map

| Requirement | Evidence | Status |
| --- | --- | --- |
| Source pushed | `HEAD == origin/main == 82d7ab1973f794ca7956253fa2d0abdb7efa4c16` | Pass |
| Installed app | `/Applications/vMLX.app` rebuilt, opened, process running, gateway on `*:8080` | Pass |
| Codesign sanity | `codesign --verify --deep --strict --verbose=2 /Applications/vMLX.app` | Pass |
| Local model matrix | `cache_mode_matrix_all85_direct_l2_after_stream_reset/SUMMARY.json`: 52 rows, 26 model IDs | Partial |
| Matrix result | 50 pass, 2 review | Partial |
| Speed capture | PP `152.6..8321.5` tok/s, TG `5.4..62.7` tok/s | Pass |
| Direct and paged/L2 cache | Direct plus paged-L2 rows for every selected model | Pass |
| Core API parity | 7/7 pass in `api_parity_core_post_rebuild_thinking_off` | Pass |
| Heavy API parity | Hy3 and DSV4 pass in `api_parity_heavy_post_rebuild_thinking_off` | Pass |
| VL/media API | ZAYA-VL, Qwen3.6 VL/MoE, and Nemotron Omni image rows pass across Chat, Responses, Anthropic, and Ollama | Pass |
| Image generation | Flux Schnell and Z-Image-Turbo return valid PNGs | Pass |
| Image edit | Qwen image edit returns valid PNG | Pass |
| Sleep/wake | Qwen, ZAYA-VL, Hy3, and DSV4 lifecycle rows pass | Pass |
| JIT toggle/fallback | Qwen JIT pass, ZAYA safe fallback pass | Pass |
| MLLM prefix bypass | Normal repeat hit `paged+zaya_cca`; `skip_prefix_cache` and `cache_salt` did not | Pass |
| MLLM pixel bypass | Normal repeated blue image hit pixel cache; bypass/salt did not add hits/stores | Pass |
| ZAYA1-VL-MXFP4 Chat memory | Cached, skip-cache, and salted Chat Completions all returned `CERULEAN` and `45` | Pass |
| ZAYA1-VL-MXFP4 Responses memory | `instructions` and message-list `previous_response_id` forms returned `CERULEAN` and `45` | Pass |
| ZAYA exact plain-string harness | Exact `READY` plain-string row remains brittle | Review |
| DSV4 short gate | `DSV4BatchGenerator`, `engine_path=dsv4`, block size 256, `paged+dsv4` observed | Pass |
| DSV4 long-context/max-reasoning | Separate lane, not completed in this installed-app gate | Gap |
| Kimi/source DSV4 | Skipped by RAM budget | Gap |
| GUI visual click-through | Blocked by macOS automation: Computer Use `procNotFound` / Apple event `-1743`; `screencapture` failed | Gap |
| Leftover servers | No `vmlx_engine.cli`, `mflux`, `uvicorn`, or image server left after probes | Pass |
| Secret hygiene | Touched/staged diff scans found no HF/GitHub/OpenAI/private-key patterns | Pass |

## Decision

Do **not** claim every model in `~/models` is utterly proven. The installed app
has strong release-gate evidence for below-budget rows and the current engine
fixes, but the remaining unproven areas are:

- GUI visual click-through until macOS automation permission is fixed or a
  manual screen-recorded pass is supplied;
- Kimi-sized/source DSV4 rows that exceed this 128 GB local pass;
- DSV4 long-context/max-reasoning behavior;
- exact plain-string `READY` behavior for ZAYA harness prompts.

The current source is suitable to hand to release work with those boundaries
explicitly stated. The larger “utterly every model/function” goal remains open
unless those gaps are accepted out of scope.
