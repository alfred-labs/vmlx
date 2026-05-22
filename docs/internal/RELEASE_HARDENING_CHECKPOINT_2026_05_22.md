# Release Hardening Checkpoint - 2026-05-22

Scope: Python/Electron vMLX release hardening from
`/Users/eric/mlx/vllm-mlx-finite-launch-guard`.

This note tracks the no-heavy regression-suite hardening done after the v1.5.46
public release and before any v1.5.47 build/sign/publish action.

## Current Release State

- Public updater primary remains `1.5.46`.
- PyPI `vmlx` remains `1.5.46`.
- GitHub `jjang-ai/vmlx` release `v1.5.47` is not published.
- Do not start signing or publishing while the objective digest still reports:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## Hardened Rows

### Max Output vs Context

- Runner: `tests/cross_matrix/run_max_output_context_contract.py`.
- Added required marker enforcement so missing named rows fail the artifact.
- Pinned default profile behavior: clean new chats cannot inherit sticky
  `maxTokens`, sampler defaults, prompts, or thinking values from default
  profiles.
- Pinned coding-tool config behavior: huge context from `/health` stays
  context-only; missing output capabilities fall back to output `4096`, not
  the context value.
- Pinned chat override storage behavior: per-chat `maxTokens` remains a
  request-scoped output cap and cannot mutate session startup `maxTokens`,
  model settings, or prompt/context wiring. Session launch still reads
  `config.maxTokens` for `--max-tokens` and `config.maxContextLength` for
  `--max-prompt-tokens`.

Key artifacts:

- `build/current-max-output-context-contract-20260522-profile-max-green.json`
- `build/current-max-output-context-contract-20260522-coding-tools-final.json`
- `build/current-max-output-context-contract-20260522-chat-server-boundary.json`
- `build/current-regression-suite-20260522-coding-tools-boundary.json`
- `build/current-regression-suite-20260522-chat-server-boundary.json`

### Tool Calls, Parser Cleanup, And Panel Tool Loops

- Runner: `tests/cross_matrix/run_tool_call_contract.py`.
- Added required marker enforcement for DSV4 DSML repairs, Responses suppressed
  reasoning extraction, tool residue stripping, and panel tool-loop reset/cap
  rows.
- Added panel row: `panel max tool iterations caps tool loops`.
- No production behavior was changed in this row; the work prevents silent
  loss of already-covered DSV4/tool-loop regression tests.

Key artifacts:

- `build/current-tool-call-contract-20260522-marker-hardening.json`
- `build/current-regression-suite-20260522-tool-marker-hardening.json`

### DSV4 Cache Timing And Pool Quant Boundaries

- Runner: `tests/cross_matrix/run_cache_architecture_contract.py`.
- Added required marker enforcement for
  `test_dsv4_timing_probe_is_env_gated_and_covers_cache_boundaries`.
- Added an env-gated trace switch, `VMLINUX_DSV4_TRACE_TIMINGS=1`, covering
  DSV4 generator and scheduler cache boundaries. This is diagnostics only; it
  does not change sampler behavior, output caps, generation defaults, or cache
  policy.
- Timing markers cover:
  - generator: `prefill_head`, `prompt_snapshot`, `prefill_last`,
    `cache_hit_tail_prefill`, `decode_model`, `sample_materialize`;
  - scheduler: `reconstruct_cache`, `extract_cache_states`, `store_cache`.
- Live traced DSV4 default-cache tool loop with pool quant off produced a true
  prefix/paged/L2 cache hit:
  - result:
    `build/current-dsv4-default-cache-tool-loop-trace-pooloff-20260522/result.json`;
  - log:
    `build/current-dsv4-default-cache-tool-loop-trace-pooloff-20260522/logs/dsv4-default-cache-tool-loop-1779479242.log`;
  - cache hit round: `cached_tokens=231`, `cache_detail=paged+dsv4`, 83 output
    tokens in `3.906s` (~21.3 tok/s);
  - cache-hit reconstruct was `2.075ms`;
  - cache-hit tail prefill was `14.416ms`;
  - cold round 0 prompt snapshot was `13636.926ms`;
  - cold round 0 first sample/materialize was `6783.427ms`.
- Current read: true prefix-cache replay is not the measured 2-3 tok/s path
  when DSV4 pool quant is off. Cold prompt-boundary snapshot and first-token
  materialization dominate the slow first tool round. Pool quant remains
  release-off because append-only JANG fixed repeated requantization but did
  not remove the full-pool dequantize/concat read cost.
- The traced live tool loop is not a functional pass: status is `review`
  because `file_written=False`. Raw model output still degraded canonical DSML
  to forms such as `<｜DSML｜tool_ciles>`, `<｜DSML｜tool_ctools>`, and
  `<｜DSML｜inv>`. That syntax/file-generation quality issue happened with pool
  quant off and should not be attributed solely to UI spacing or pool quant.

Key artifacts:

- `build/current-cache-architecture-contract-20260522-dsv4-timing.json`
- `build/current-release-regression-manifest-20260522-dsv4-timing.json`
- `build/current-dsv4-default-cache-tool-loop-trace-pooloff-20260522/result.json`
- `build/current-dsv4-default-cache-tool-loop-trace-pooloff-20260522/logs/dsv4-default-cache-tool-loop-1779479242.log`
- `build/current-packaged-integrity-contract-20260522-dsv4-timing-clean-jang.json`
- `build/current-regression-suite-20260522-dsv4-timing-clean-jang.json`

### MCP Policy, Redaction, Gateway, And Panel Wiring

- Runner: `tests/cross_matrix/run_mcp_policy_contract.py`.
- Added required marker enforcement for:
  - MCP autodiscovery without CLI/env;
  - policy filtering before schema merge;
  - disabled tool execution rejection;
  - secret redaction;
  - command/env/header security;
  - panel policy flags and config import;
  - explicit-model gateway routing;
  - ambiguous multi-session gateway rejection;
  - built-in Electron tools remaining separate from MCP execution.
- Added `tests/test_mcp_policy_contract.py` so the runner fails if marker
  enforcement is removed.
- Wired the marker contract into `run_current_regression_suite.py`.

Key artifacts:

- `build/current-mcp-policy-contract-20260522-marker-hardening.json`
- `build/current-regression-suite-20260522-mcp-marker-hardening.json`
- `build/current-release-surface-contract-20260522-post-mcp-marker-hardening.json`

### Release Manifest Hygiene

- Added a manifest invariant that every relative Python entrypoint named in a
  release-gate command must exist in the tracked checkout.
- Fixed the DSV4 live-quality row so it no longer points at missing generated
  `build/run_dsv4_identifier_count_ablation.py` code. The row now points at
  the tracked production-family live runner:
  `tests/cross_matrix/run_production_family_audit.py --rows dsv4_jang_local --live`.
- This does not clear DSV4 quality; it makes the remaining live gate
  reproducible and keeps release docs from referencing zombie scripts.
- Added the no-heavy named model-family detection contract as its own durable
  release-manifest row. The current suite already ran it, but the release
  checklist now explicitly names the DSV4, ZAYA/ZAYA1-VL, Ling/Bailing,
  Nemotron, Qwen 3.6 VL/video/hybrid, MXFP4, MXFP8, native-MTP, MiniMax, and
  Hy3 parser/cache/modality compatibility proof.
- Added an executable-command invariant for Python runners in the release
  manifest and replaced the descriptive `model-family-live-multiturn-soak`
  command with a real scoped live command over Hy3, MiniMax, Qwen 3.6, ZAYA,
  ZAYA1-VL, Ling, Nemotron, and DSV4 rows.
- Added manifest guards against duplicate artifact entries and live-soak
  overclaims. The live soak row no longer implies Qwen MTP/VL/video live
  coverage from a command that only names Qwen 3.6 hybrid rows; those
  Qwen MTP/VL/video rows remain no-heavy family-detection coverage until
  dedicated live-audit rows exist.
- Added a concrete-artifact invariant so release rows cannot list directory
  placeholders as proof artifacts. The live multifamily soak row now points
  only at the generated JSON proof file, not `docs/internal/release-gates/`.
- Added a new-chat max-output inheritance guard so a previous chat or default
  profile cannot turn an old per-chat output cap into a sticky server/session
  cap. The test preserves model-owned `maxTokens` already derived for a new
  chat while refusing inherited `maxTokens=32768` and other sampler/prompt
  overrides from the previous chat.
- Updated the durable release-regression manifest so the
  `chat-settings-max-output-context-ui` row points at the current max-output
  proof artifact and explicitly names the new-chat model-owned maxTokens guard.
- Added a model-family speed-row guard so broad speed coverage cannot blur
  JANG-only MX matmul, JANGTQ/MXTQ TurboQuant, MXFP4, and MXFP8-MTP rows.
  Each distinct row class must keep explicit PP/decode thresholds and the
  release manifest now points at the current family artifact.
- Added a decode-speed parser-registration guard so every declared tool or
  reasoning parser in the family/speed matrix must be accepted by the engine
  registries, even when the model path is not present locally. This directly
  protects against MiniMax-style stale parser ids returning through another
  family row.

Key artifacts:

- `build/current-release-regression-manifest-20260522-live-entrypoint.json`
- `build/current-regression-suite-20260522-live-entrypoint.json`
- `build/current-model-family-detection-contract-20260522-manifest-row.json`
- `build/current-release-regression-manifest-20260522-family-row.json`
- `build/current-regression-suite-20260522-family-row.json`
- `build/current-release-regression-manifest-20260522-live-soak-command.json`
- `build/current-regression-suite-20260522-live-soak-command.json`
- `build/current-release-regression-manifest-20260522-live-overclaim.json`
- `build/current-regression-suite-20260522-live-overclaim.json`
- `build/current-release-regression-manifest-20260522-concrete-artifacts.json`
- `build/current-regression-suite-20260522-concrete-artifacts.json`
- `build/current-release-surface-contract-20260522-post-concrete-artifacts.json`
- `build/current-max-output-context-contract-20260522-new-chat-max-output.json`
- `build/current-regression-suite-20260522-new-chat-max-output.json`
- `build/current-release-surface-contract-20260522-post-new-chat-max-output.json`
- `build/current-release-regression-manifest-20260522-new-chat-max-output.json`
- `build/current-regression-suite-20260522-new-chat-manifest.json`
- `build/current-model-family-detection-contract-20260522-distinct-speed-rows.json`
- `build/current-release-regression-manifest-20260522-distinct-speed-rows.json`
- `build/current-regression-suite-20260522-distinct-speed-rows.json`
- `build/current-model-family-detection-contract-20260522-parser-registry-rows.json`
- `build/current-release-regression-manifest-20260522-parser-registry-rows.json`
- `build/current-regression-suite-20260522-parser-registry-rows.json`

## Latest Verification

```sh
uv run --extra dev python -m py_compile \
  tests/cross_matrix/run_max_output_context_contract.py \
  tests/cross_matrix/run_mcp_policy_contract.py \
  tests/cross_matrix/run_current_regression_suite.py \
  tests/cross_matrix/release_regression_manifest.py

git diff --check

uv run --extra dev python -m pytest -q \
  tests/test_max_output_context_contract.py \
  tests/test_mcp_policy_contract.py \
  tests/test_release_regression_manifest.py \
  tests/test_current_regression_suite.py

uv run --extra dev python tests/cross_matrix/release_regression_manifest.py \
  > build/current-release-regression-manifest-20260522-live-entrypoint.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-manifest-row.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-family-row.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-live-soak-command.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-live-overclaim.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-concrete-artifacts.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-new-chat-max-output.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-new-chat-max-output.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-distinct-speed-rows.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-parser-registry-rows.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-cli-parser-choices.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-distinct-speed-rows.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-parser-registry-rows.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-cli-parser-choices.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-chat-server-boundary.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-server-chat-boundary.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-server-chat-boundary.json

VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py \
  --out build/current-regression-suite-20260522-concrete-artifacts.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-new-chat-max-output.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-cli-parser-choices.json

uv run --extra dev python tests/cross_matrix/run_noheavy_panel_settings_contract.py \
  --out build/current-panel-settings-contract-proof-20260522-dsv4-cache-controls.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-dsv4-cache-controls.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-artifact-format-matrix.json

uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py \
  --out build/current-model-family-detection-contract-20260522-command-policy.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-command-policy.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-command-policy.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-artifact-format-matrix.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-legacy-completions.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-legacy-completions.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-legacy-completions.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-legacy-completions-streaming.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-legacy-completions-streaming.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-legacy-completions-streaming.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-chat-responses-streaming.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-chat-responses-streaming.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-chat-responses-streaming.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-anthropic-streaming.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-anthropic-streaming.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-anthropic-streaming.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-ollama-streaming.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-ollama-streaming.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-ollama-streaming.json

VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py \
  --out build/current-regression-suite-20260522-ollama-streaming.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-streaming-ollama.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-context-alias-clamp.json

uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py \
  --out build/current-api-surface-contract-20260522-context-alias-clamp.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-context-alias-clamp.json

VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py \
  --out build/current-regression-suite-20260522-context-alias-clamp.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-context-alias-clamp.json
```

Observed results:

- max-output gate: `status=pass`, `missing_markers=[]`, engine `14 passed`,
  panel `32 passed / 1 skipped`;
- focused max-output/current-suite/manifest tests: `49 passed`;
- manifest/current-suite tests after entrypoint hardening: `49 passed`;
- umbrella suite after entrypoint hardening: `status=pass`, `failed_steps=[]`;
- named model-family detection gate: `status=pass`, `missing_rows=[]`, engine
  `31 passed`, panel `40 passed / 12 skipped`;
- focused family/manifest/current-suite tests: `64 passed`;
- umbrella suite after family manifest row: `status=pass`, `failed_steps=[]`;
- manifest/current-suite tests after live-soak command hardening: `51 passed`;
- umbrella suite after live-soak command hardening: `status=pass`,
  `failed_steps=[]`;
- manifest/current-suite tests after live-overclaim guard: `53 passed`;
- umbrella suite after live-overclaim guard: `status=pass`, `failed_steps=[]`;
- focused concrete-artifact guard: red failed on `docs/internal/release-gates/`,
  then green after removing the directory artifact;
- manifest/current-suite tests after concrete-artifact guard: `54 passed`;
- manifest artifact after concrete-artifact guard: 17 rows, all artifacts are
  concrete paths;
- umbrella suite after concrete-artifact guard: `status=pass`,
  `failed_steps=[]`;
- max-output gate after new-chat inheritance guard: `status=pass`,
  `missing_markers=[]`, engine `14 passed`, panel `33 passed / 1 skipped`;
- max-output gate after server/chat boundary guard: `status=pass`,
  `missing_markers=[]`, engine `14 passed`, panel `34 passed / 1 skipped`;
- focused max-output/manifest/current-suite tests after new-chat guard:
  `55 passed`;
- focused max-output/manifest/current-suite tests after server/chat boundary
  guard: `58 passed`;
- umbrella suite after new-chat guard: `status=pass`, `failed_steps=[]`;
- umbrella suite after server/chat boundary guard: `status=pass`,
  `failed_steps=[]`;
- panel settings contract after DSV4-only cache-control guard: `status=pass`,
  `missing_source_markers=[]`, panel settings `281 passed`, panel typecheck
  passed, panel registry `52 passed`, engine registry `126 passed`;
- release manifest artifact after DSV4-only cache-control guard: 18 rows;
- umbrella suite after DSV4-only cache-control guard: `status=pass`,
  `failed_steps=[]`;
- manifest/current-suite tests after manifest row update: `55 passed`;
- release manifest artifact after row update: 17 rows;
- umbrella suite after manifest row update: `status=pass`, `failed_steps=[]`;
- model-family gate after distinct speed-row guard: `status=pass`,
  `missing_rows=[]`, engine `32 passed`, panel `40 passed / 12 skipped`;
- family/manifest/current-suite tests after distinct speed-row guard:
  `70 passed`;
- release manifest artifact after distinct speed-row guard: 17 rows;
- umbrella suite after distinct speed-row guard: `status=pass`,
  `failed_steps=[]`;
- model-family gate after parser-registration guard: `status=pass`,
  `missing_rows=[]`, engine `33 passed`, panel `40 passed / 12 skipped`;
- family/parser/manifest/current-suite tests after parser-registration guard:
  `72 passed`;
- release manifest artifact after parser-registration guard: 17 rows;
- umbrella suite after parser-registration guard: `status=pass`,
  `failed_steps=[]`;
- model-family gate after CLI parser-choice guard: `status=pass`,
  `missing_rows=[]`, engine `34 passed`, panel `40 passed / 12 skipped`;
- family/parser/manifest/current-suite tests after CLI parser-choice guard:
  `74 passed`;
- release manifest artifact after CLI parser-choice guard: 17 rows;
- umbrella suite after CLI parser-choice guard: `status=pass`,
  `failed_steps=[]`;
- model-family gate after decode-speed artifact-format matrix guard:
  `status=pass`, `missing_rows=[]`, engine `35 passed`, panel
  `40 passed / 12 skipped`;
- family/manifest/current-suite tests after artifact-format matrix guard:
  `77 passed`;
- release manifest artifact after artifact-format matrix guard: 18 rows;
- umbrella suite after artifact-format matrix guard: `status=pass`,
  `failed_steps=[]`;
- red proof for decode-speed command policy:
  `build/current-model-family-detection-contract-20260522-command-policy-red.json`
  failed only with
  `missing_rows=["decode_speed_build_command_parser_modality_policy"]`;
- focused decode-speed command policy test:
  `test_decode_speed_gate_build_command_preserves_row_parser_modality_policy`
  passed;
- model-family gate after command policy guard: `status=pass`,
  `missing_rows=[]`, engine `36 passed`, panel `40 passed / 12 skipped`;
- release manifest artifact after command policy guard: 18 rows;
- focused family/manifest/current-suite tests after command policy guard:
  `62 passed`;
- py-compile and `git diff --check` after command policy guard: pass;
- umbrella suite after command policy guard: `status=pass`,
  `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- pushed `f7f852ea test: pin decode speed command policy` to `origin/main`;
- release surface contract after pushing `f7f852ea`: `status=pass`;
- max-output gate after legacy `/v1/completions` output-cap guard:
  `status=pass`, `missing_markers=[]`, engine `15 passed`, panel
  `34 passed / 1 skipped`;
- API/cache surface after legacy `/v1/completions` output-cap guard:
  `status=pass`, `missing_markers=[]`, API route contracts `16 passed`;
- API surface after legacy `/v1/completions` output-cap guard:
  `status=pass`, `missing_nested_checks=[]`, `missing_panel_markers=[]`;
- release manifest artifact after legacy `/v1/completions` guard: 18 rows;
- focused legacy completions/API/manifest/current-suite tests: `64 passed`;
- umbrella suite after legacy `/v1/completions` guard: `status=pass`,
  `failed_steps=[]`;
- max-output gate after streaming legacy `/v1/completions` output-cap guard:
  `status=pass`, `missing_markers=[]`, engine `16 passed`, panel
  `34 passed / 1 skipped`;
- API surface after streaming legacy `/v1/completions` output-cap guard:
  `status=pass`, server API surface `17 passed`;
- release manifest artifact after streaming legacy `/v1/completions` guard:
  18 rows;
- focused streaming legacy completions/API/manifest/current-suite tests:
  `65 passed`;
- umbrella suite after streaming legacy `/v1/completions` guard:
  `status=pass`, `failed_steps=[]`;
- max-output gate after streaming Chat/Responses output-cap guard:
  `status=pass`, `missing_markers=[]`, engine `17 passed`, panel
  `34 passed / 1 skipped`;
- API surface after streaming Chat/Responses output-cap guard:
  `status=pass`, server API surface `18 passed`;
- release manifest artifact after streaming Chat/Responses guard: 18 rows;
- focused streaming Chat/Responses/API/manifest/current-suite tests:
  `64 passed`;
- umbrella suite after streaming Chat/Responses guard: `status=pass`,
  `failed_steps=[]`;
- max-output gate after streaming Anthropic Messages output-cap guard:
  `status=pass`, `missing_markers=[]`, engine `18 passed`, panel
  `34 passed / 1 skipped`;
- API surface after streaming Anthropic Messages output-cap guard:
  `status=pass`, server API surface `19 passed`;
- release manifest artifact after streaming Anthropic Messages guard: 18 rows;
- focused streaming Anthropic/API/manifest/current-suite tests: `64 passed`;
- umbrella suite after streaming Anthropic Messages guard: `status=pass`,
  `failed_steps=[]`;
- red proof for streaming Ollama `num_predict`:
  `build/current-max-output-context-contract-20260522-ollama-streaming-red.json`
  failed because the new marker was required but not yet present in the max-output
  command list;
- focused streaming Ollama route test:
  `test_ollama_streaming_num_predict_overrides_server_default_without_touching_context_cap`
  passed;
- max-output gate after streaming Ollama guard: `status=pass`,
  `missing_markers=[]`, engine `19 passed`, panel `34 passed / 1 skipped`;
- API surface after streaming Ollama guard: `status=pass`,
  `missing_nested_checks=[]`, `missing_nested_markers=[]`,
  `missing_panel_markers=[]`, server API surface `20 passed`, panel request
  builders `64 passed`;
- release manifest artifact after streaming Ollama guard: 18 rows;
- focused streaming Ollama/API/manifest/current-suite tests: `64 passed`;
- py-compile and `git diff --check` after streaming Ollama guard: pass;
- umbrella suite after streaming Ollama guard: `status=pass`,
  `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- pushed `204cf38c test: pin streaming ollama output caps` to `origin/main`;
- release surface contract after pushing `204cf38c`: `status=pass`;
- red proof for prompt/context alias clamp:
  `build/current-max-output-context-contract-20260522-context-alias-clamp-red.json`
  failed only with
  `missing_markers=["test_prompt_context_aliases_clamp_without_rewriting_output_caps"]`;
- focused prompt/context alias clamp test:
  `test_prompt_context_aliases_clamp_without_rewriting_output_caps` passed;
- max-output gate after prompt/context alias clamp guard: `status=pass`,
  `missing_markers=[]`, engine `20 passed`, panel `34 passed / 1 skipped`;
- API surface after prompt/context alias clamp guard: `status=pass`,
  `missing_nested_checks=[]`, `missing_nested_markers=[]`,
  `missing_panel_markers=[]`, server API surface `21 passed`, panel request
  builders `64 passed`;
- release manifest artifact after prompt/context alias clamp guard: 18 rows;
- focused prompt/context alias/API/manifest/current-suite tests: `64 passed`;
- py-compile and `git diff --check` after prompt/context alias clamp guard:
  pass;
- umbrella suite after prompt/context alias clamp guard: `status=pass`,
  `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- pushed `16e57192 test: pin context alias output cap boundaries` to
  `origin/main`;
- release surface contract after pushing `16e57192`: `status=pass`;
- umbrella suite: `status=pass`, `failed_steps=[]`;
- release surface contract after pushing `cdb7d0f0`: `status=pass`;
- release surface contract after pushing `177b9cd4`: `status=pass`;
- release surface contract after pushing `c36e7ace`: `status=pass`;
- release surface contract after pushing `68d5823b`: `status=pass`;
- release surface contract after pushing `943e21d0`: `status=pass`;
- release surface contract after pushing `b4fc7fa0`: `status=pass`;
- release surface contract after pushing `3391ab70`: `status=pass`;
- release surface contract after pushing `6f4ccaec`: `status=pass`;
- public updater primary/fallback remain `1.5.46`, PyPI `vmlx` remains
  `1.5.46`, and GitHub `jjang-ai/vmlx` release `v1.5.47` is not published;
- known open objective remains only DSV4 long-output/code quality.

## 2026-05-22 03:57 PDT - Large External Decode-Speed Rows

Added the no-heavy model-family row:

- `decode_speed_large_external_jangtq_mxfp_gptoss_rows`

This pins the large external rows that are too expensive to rely on for every
quick gate, but risky enough that their launch policy must not drift:

- `mistral_medium_jangtq_ext`
  - path:
    `/Volumes/EricsLLMDrive/jangq-ai/Mistral-Medium-3.5-128B-JANGTQ`
  - parser policy: `--tool-call-parser mistral`,
    `--reasoning-parser mistral`, `--is-mllm`
  - no startup `--max-tokens`
- `mistral_medium_mxfp4_ext`
  - path:
    `/Volumes/EricsLLMDrive/jangq-ai/Mistral-Medium-3.5-128B-mxfp4`
  - parser policy: `--tool-call-parser mistral`,
    `--reasoning-parser mistral`, `--is-mllm`
  - no startup `--max-tokens`
- `gpt_oss_ext`
  - path:
    `/Volumes/EricsLLMDrive/dealignai/GPT-OSS-120B-MLX-CRACK`
  - parser policy: `--tool-call-parser glm47`,
    `--reasoning-parser openai_gptoss`
  - no `--is-mllm`, no startup `--max-tokens`

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-large-external-red.json`
- result: `status=fail`, `failed=[]`,
  `missing_rows=["decode_speed_large_external_jangtq_mxfp_gptoss_rows"]`;
  existing engine/panel commands stayed green with engine `36 passed`, panel
  `40 passed / 12 skipped`.

Green proof:

- focused row test:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_has_large_external_mistral_gptoss_rows`
  -> `1 passed`;
- model-family gate:
  `uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-large-external.json`
  -> `status=pass`, `missing_rows=[]`, engine `37 passed`, panel
  `40 passed / 12 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-large-external.json`
  -> 18 rows;
- focused family/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_has_large_external_mistral_gptoss_rows tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-large-external.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed `357026ec test: pin large external speed rows` to `origin/main`;
- post-push release surface:
  `build/current-release-surface-contract-20260522-post-large-external.json`
  -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 04:07 PDT - Ollama `num_predict` Malformed Output-Cap Guard

Closed a panel API-gateway edge in the max-output/context lane:

- Ollama `options.num_predict` is the Ollama-compatible output cap.
- Valid positive values map to OpenAI `max_tokens`.
- `0`, negative, unset, malformed, or non-finite values must not become a
  poisoned `max_tokens` value at the OpenAI backend boundary.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-ollama-malformed-red.json`
- result: `status=fail`, `failed=[]`,
  `missing_markers=["omits malformed Ollama num_predict values instead of poisoning max_tokens"]`;
  existing engine and panel output/context commands stayed green.

Fix:

- `panel/src/main/api-gateway.ts`
  - `applyOllamaNumPredict(...)` now forwards only finite positive values;
  - forwarded values are normalized with `Math.floor(parsed)`;
  - malformed strings like `"not-a-number"` and non-finite strings like
    `"Infinity"` are omitted.

Green proof:

- focused panel test:
  `cd panel && npx vitest run tests/api-gateway-ollama-behavior.test.ts --testNamePattern "malformed Ollama num_predict" --reporter=verbose`
  -> `1 passed / 1 skipped`;
- max-output/context contract:
  `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-ollama-malformed.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `35 passed / 289 skipped`;
- API surface contract:
  `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-ollama-malformed.json`
  -> `status=pass`, `missing_nested_checks=[]`,
  `missing_nested_markers=[]`, `missing_panel_markers=[]`, server API surface
  `21 passed`, panel request builders `65 passed`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-ollama-malformed.json`
  -> 18 rows;
- focused API/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py::test_api_surface_contract_pins_named_public_surface_edges tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `61 passed`;
- full gateway behavior test:
  `cd panel && npx vitest run tests/api-gateway-ollama-behavior.test.ts --reporter=verbose`
  -> `2 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-ollama-malformed.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed `33d4b277 fix: drop malformed ollama output caps` to `origin/main`;
- post-push release surface:
  `build/current-release-surface-contract-20260522-post-ollama-malformed.json`
  -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 04:15 PDT - Ollama Context Malformed Prompt-Cap Guard

Closed the paired panel API-gateway edge for prompt/context caps:

- Ollama `options.num_ctx`, `options.max_context_tokens`, and related context
  aliases map to OpenAI `max_prompt_tokens`.
- Valid positive values remain prompt/context caps.
- Malformed, non-finite, `0`, negative, or unset values must not become a
  poisoned `max_prompt_tokens` value at the OpenAI backend boundary.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-ollama-context-malformed-red.json`
- result: `status=fail`, `failed=[]`,
  `missing_markers=["omits malformed Ollama context values instead of poisoning max_prompt_tokens"]`;
  existing engine and panel output/context commands stayed green.

Fix:

- `panel/src/main/api-gateway.ts`
  - `applyOllamaPromptContextLimit(...)` now forwards only finite positive
    values;
  - forwarded values are normalized with `Math.floor(parsedValue)`;
  - malformed strings like `"not-a-number"` and non-finite strings like
    `"Infinity"` are omitted.

Green proof:

- focused panel test:
  `cd panel && npx vitest run tests/api-gateway-ollama-behavior.test.ts --testNamePattern "malformed Ollama context" --reporter=verbose`
  -> `1 passed / 2 skipped`;
- max-output/context contract:
  `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-ollama-context-malformed.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `35 passed / 290 skipped`;
- API surface contract:
  `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-ollama-context-malformed.json`
  -> `status=pass`, `missing_nested_checks=[]`,
  `missing_nested_markers=[]`, `missing_panel_markers=[]`, server API surface
  `21 passed`, panel request builders `66 passed`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-ollama-context-malformed.json`
  -> 18 rows;
- focused API/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py::test_api_surface_contract_pins_named_public_surface_edges tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `61 passed`;
- full gateway behavior test:
  `cd panel && npx vitest run tests/api-gateway-ollama-behavior.test.ts --reporter=verbose`
  -> `3 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-ollama-context-malformed.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed `0dab0346 fix: drop malformed ollama context caps` to `origin/main`;
- post-push release surface:
  `build/current-release-surface-contract-20260522-post-ollama-context-malformed.json`
  -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 04:24 PDT - External Nemotron 3 Speed Row Guard

Closed a no-heavy model-family coverage gap in the decode-speed matrix:

- `nemotron3_jangtq2_ext` already existed in
  `tests/cross_matrix/run_decode_speed_gate.py` for
  `/Volumes/EricsLLMDrive/jangq-ai/Nemotron-3-Nano-Omni-30B-A3B-JANGTQ2`;
- `nemotron3_mxfp4_ext` already existed for
  `/Volumes/EricsLLMDrive/jangq-ai/Nemotron-3-Nano-Omni-30B-A3B-MXFP4`;
- the release family contract did not name those rows directly, so a future
  edit could remove their parser/modality/startup-command coverage without the
  named release gate noticing.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-nemotron3-external-red.json`
- result: `status=fail`, `failed=[]`,
  `missing_rows=["decode_speed_external_nemotron3_jangtq_mxfp_rows"]`;
  engine family detection and panel family detection were otherwise green.

Fix:

- `tests/cross_matrix/run_model_family_detection_contract.py`
  - added required row
    `decode_speed_external_nemotron3_jangtq_mxfp_rows`;
  - marker points at
    `test_decode_speed_gate_has_external_nemotron3_jangtq_mxfp_rows`.
- `tests/test_model_family_detection_contract.py`
  - pins both external Nemotron 3 paths;
  - proves JANGTQ2 vs MXFP4 format separation;
  - proves `tool_parser="nemotron"` and
    `reasoning_parser="deepseek_r1"`;
  - proves no `--max-tokens` is added to speed launch commands;
  - proves no `--is-mllm` flag is added for these text rows.
- `tests/cross_matrix/release_regression_manifest.py`
  - model-family row now points at
    `build/current-model-family-detection-contract-20260522-nemotron3-external.json`;
  - manifest text explicitly records external Nemotron 3 JANGTQ2/MXFP4 parser
    and reasoning launch policy coverage.

Green proof:

- focused family test:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_has_external_nemotron3_jangtq_mxfp_rows tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> `2 passed`;
- full model-family contract:
  `uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-nemotron3-external.json`
  -> `status=pass`, `missing_rows=[]`, engine `38 passed`, panel
  `40 passed / 12 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-nemotron3-external.json`
  -> 18 rows;
- focused family/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_has_external_nemotron3_jangtq_mxfp_rows tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-nemotron3-external.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed `c93df9d0 test: pin external nemotron speed rows` to `origin/main`;
- post-push release surface:
  `build/current-release-surface-contract-20260522-post-nemotron3-external.json`
  -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 04:34 PDT - Auto Chat Max Tokens / Server Default Boundary

Closed the direct edge Eric called out around separate Chat Max Tokens vs
Server Default Max Output Tokens:

- Chat Max Tokens set to Auto/disabled must omit per-request output caps.
- When omitted, the server startup `--max-tokens` default or model-owned
  generation metadata remains responsible for the response budget.
- Explicit chat caps still override per request; this row only protects the
  Auto path from accidentally sending `max_tokens`, `max_output_tokens`,
  prompt/context caps, or DSV4 synthetic budgets.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-chat-auto-server-default-red.json`
- result: `status=fail`, `failed=[]`,
  `missing_markers=["Auto chat maxTokens omits per-request output caps so server default can apply"]`;
  existing engine and panel rows stayed green.
- `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-chat-auto-server-default-red.json`
  reported the same missing panel marker. During this red check, the API
  runner still returned top-level `status=pass`, which exposed a gate bug.

Fix:

- `panel/tests/request-builder.test.ts`
  - added
    `Auto chat maxTokens omits per-request output caps so server default can apply`;
  - proves Chat Completions Auto, disabled `maxTokens: 0`, DSV4 Max thinking
    with Auto budget, Responses Auto, and Responses disabled all omit
    `max_tokens`, `max_output_tokens`, `max_prompt_tokens`,
    `max_context_tokens`, and `max_context`;
  - preserves DSV4 `reasoning_effort="max"` while still leaving the output
    budget to the server/model default.
- `tests/cross_matrix/run_api_surface_contract.py`
  - added `all_required_panel_api_markers_present`, so missing required panel
    request-builder markers fail the top-level API surface gate.
- `tests/cross_matrix/release_regression_manifest.py`
  - chat settings row now points at
    `build/current-max-output-context-contract-20260522-chat-auto-server-default.json`;
  - API surface row now points at
    `build/current-api-surface-contract-20260522-chat-auto-server-default.json`.

Green proof:

- focused panel test:
  `cd panel && npx vitest run tests/request-builder.test.ts --testNamePattern "Auto chat maxTokens omits per-request output caps" --reporter=verbose`
  -> `1 passed / 51 skipped`;
- focused API contract tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py::test_api_surface_contract_pins_named_public_surface_edges tests/test_api_surface_contract.py::test_api_surface_contract_status_fails_when_required_panel_markers_are_missing`
  -> `2 passed`;
- max-output/context contract:
  `uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-chat-auto-server-default.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `36 passed / 290 skipped`;
- API surface contract:
  `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-chat-auto-server-default.json`
  -> `status=pass`, `missing_panel_markers=[]`, server API surface
  `21 passed`, panel request builders `67 passed`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-chat-auto-server-default.json`
  -> 18 rows;
- focused API/max-output/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py tests/test_max_output_context_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `64 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-chat-auto-server-default.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 04:43 PDT - Reasoning Parser Dropdown / Registry Parity

Closed another MiniMax-style release regression edge:

- The engine and panel registry already had parser parity tests for emitted
  tool/reasoning parser ids.
- The UI dropdown had coverage for tool parsers, but it did not have an
  exhaustive guard proving every `reasoningParser` emitted by
  `model-config-registry.ts` is selectable in `SessionConfigForm`.
- That missing guard could allow a future family autodetect row to emit a
  parser that backend/CLI accepts while the settings UI cannot display or
  preserve it.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_parser_registry_contract.py --out build/current-parser-registry-contract-20260522-reasoning-dropdown-red.json`
  initially reported missing marker
  `reasoning parser dropdown covers every parser the panel registry can emit`;
- that red run also exposed a gate bug: missing required parser markers did not
  fail top-level status;
- after adding `all_required_parser_markers_present`, the status-red artifact
  `build/current-parser-registry-contract-20260522-reasoning-dropdown-status-red.json`
  failed on the same missing marker.

Fix:

- `panel/tests/settings-flow.test.ts`
  - added
    `reasoning parser dropdown covers every parser the panel registry can emit`;
  - parses panel registry `reasoningParser: '...'` literals and asserts every
    emitted parser exists in the settings form dropdown values.
- `tests/cross_matrix/run_parser_registry_contract.py`
  - added the required marker;
  - added top-level gate check
    `all_required_parser_markers_present`.
- `tests/test_parser_registry_contract.py`
  - pins the required marker;
  - pins that missing parser markers fail the parser contract status.
- `tests/cross_matrix/release_regression_manifest.py`
  - parser row now points at
    `build/current-parser-registry-contract-20260522-reasoning-dropdown.json`;
  - manifest text explicitly records reasoning parser dropdown coverage.

Green proof:

- focused panel test:
  `cd panel && npx vitest run tests/settings-flow.test.ts --testNamePattern "reasoning parser dropdown covers every parser" --reporter=verbose`
  -> `1 passed / 231 skipped`;
- focused parser contract tests:
  `uv run --extra dev python -m pytest -q tests/test_parser_registry_contract.py`
  -> `2 passed`;
- full parser registry contract:
  `uv run --extra dev python tests/cross_matrix/run_parser_registry_contract.py --out build/current-parser-registry-contract-20260522-reasoning-dropdown.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, engine
  `102 passed`, panel `40 passed / 244 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-reasoning-dropdown.json`
  -> 18 rows;
- focused parser/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_parser_registry_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-reasoning-dropdown.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed `0bda1673 test: pin reasoning parser dropdown coverage` to
  `origin/main`;
- post-push release surface:
  `build/current-release-surface-contract-20260522-post-reasoning-dropdown.json`
  -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 04:59 PDT - Plain KV Cache Health Guard

Closed another no-heavy cache-regression edge for non-DSV4 families:

- Previous live-health mismatch checks caught DSV4 native composite and ZAYA
  typed CCA rows, but plain KV rows did not reject a bad health report claiming
  `native_composite` or `typed_cca`.
- This matters because DSV4 native cache work must not bleed into normal
  JANG/JANGTQ/MXFP/KV rows or let a bad live health report appear compatible.
- The new check does not force TurboQuant KV off for plain KV rows; it only
  rejects the wrong cache architecture.

Red proof:

- `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_detects_plain_kv_cache_health_mismatches`
  initially failed because `cache_health_mismatches()` returned `[]` for a
  plain KV row with health `cache_type=native_composite`.

Fix:

- `tests/cross_matrix/run_decode_speed_gate.py`
  - plain `cache_type=kv` rows now accept only health `cache_type=kv` or
    `cache_type=paged_kv`;
  - they reject DSV4 native composite and ZAYA typed CCA live-health reports.
- `tests/cross_matrix/run_model_family_detection_contract.py`
  - added required row
    `decode_speed_plain_kv_cache_health_not_native`.
- `tests/test_model_family_detection_contract.py`
  - added focused regression coverage for plain KV health mismatch detection.
- `tests/cross_matrix/release_regression_manifest.py`
  - model-family row now records:
    `Decode-speed health checks reject DSV4 native or ZAYA typed cache health for plain KV JANG/JANGTQ/MXFP rows`.

Green proof:

- focused regression:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_detects_plain_kv_cache_health_mismatches`
  -> `1 passed`;
- family detection contract:
  `uv run --extra dev python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-plain-kv-cache-health.json`
  -> `status=pass`, `missing_rows=[]`, engine `39 passed`, panel
  `40 passed / 12 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-plain-kv-cache-health.json`
  -> 18 rows;
- focused pytest:
  `uv run --extra dev python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `82 passed`;
- py-compile for changed runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-plain-kv-cache-health.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- pushed:
  - `e9d86fbd test: pin plain kv cache health rows`;
  - post-push release surface
    `build/current-release-surface-contract-20260522-post-plain-kv-cache-health.json`
    -> `status=pass`, with updater/source consistency checks green.

## 2026-05-22 05:06 PDT - Launch Memory Admission Warning-Only Guard

Pinned the Python/Electron app behavior for the RAM launch issue Eric saw in a
dev build:

- The current `panel/src/main/sessions.ts` memory estimate path logs model size,
  free RAM, and warnings.
- It does not hard-block launch, does not require
  `VMLX_ALLOW_UNSAFE_MODEL_LAUNCH` / `VMLINUX_ALLOW_UNSAFE_MODEL_LAUNCH`, and
  does not set the session failed before launch.
- This is important for lazy-mmap JANG/JANGTQ bundles where macOS file cache
  pressure can make a resident estimate look too strict even though the model
  can still load.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_noheavy_panel_settings_contract.py --out build/current-panel-settings-contract-proof-20260522-launch-memory-red.json`
  failed with missing marker
  `launch memory admission is warning-only for lazy-mmap bundles`.

Fix:

- `panel/tests/settings-flow.test.ts`
  - added
    `launch memory admission is warning-only for lazy-mmap bundles`;
  - the test fences the actual session launch-memory block and asserts it keeps
    warning/log behavior without `Launch blocked`, unsafe env escape hatches,
    failed status, or thrown errors.
- `tests/cross_matrix/run_noheavy_panel_settings_contract.py`
  - requires the marker.
- `tests/cross_matrix/release_regression_manifest.py`
  - panel cache/settings row now points at the launch-memory artifact and
    records warning-only launch-memory admission for lazy-mmap bundles.

Green proof:

- focused panel marker:
  `cd panel && npx vitest run tests/settings-flow.test.ts --testNamePattern "launch memory admission is warning-only" --reporter=verbose`
  -> `1 passed / 232 skipped`;
- panel contract:
  `uv run --extra dev python tests/cross_matrix/run_noheavy_panel_settings_contract.py --out build/current-panel-settings-contract-proof-20260522-launch-memory-warning.json`
  -> `status=pass`, `missing_source_markers=[]`,
  `panel_settings_contracts` `283 passed`, panel model registry `52 passed`,
  engine model registry `126 passed`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-launch-memory-warning.json`
  -> 18 rows;
- focused pytest:
  `uv run --extra dev python -m pytest -q tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `60 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-launch-memory-warning.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 05:16 PDT - Config-Only Native MTP Suppression Guard

Pinned the native-MTP edge where a bundle name or config advertises MTP but the
actual safetensor index has no `mtp.*` tensors:

- Engine runtime status must not activate native MTP from config alone.
- Panel model detection must not expose Native MTP launch controls from config
  alone.
- For affine-JANG Qwen VL, config-only MTP keeps the existing text-only safety
  route; indexed MTP plus vision tensors is the path that can opt into the
  native-MTP VL route.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_native_mtp_contract.py --out build/current-native-mtp-contract-20260522-config-only-red.json`
  failed with missing markers:
  - `test_config_only_mtp_bundle_does_not_activate_native_runtime`
  - `does not expose Native MTP for config-only bundles without indexed mtp tensors`

Fix:

- `tests/test_native_mtp_autodetect.py`
  - added
    `test_config_only_mtp_bundle_does_not_activate_native_runtime`;
  - asserts config MTP layers plus no indexed `mtp.*` tensors yields
    `metadata_inconsistent`, no artifact availability, no runtime availability,
    no runtime active state, and no effective depth.
- `panel/tests/model-config-registry.test.ts`
  - added
    `does not expose Native MTP for config-only bundles without indexed mtp tensors`;
  - asserts the panel keeps that Qwen affine-JANG VL case text-only and leaves
    `nativeMtp` undefined.
- `tests/cross_matrix/run_native_mtp_contract.py`
  - now requires both markers and runs panel model-config MTP detection rows.
- `tests/cross_matrix/release_regression_manifest.py`
  - native-MTP row now records config-only MTP suppression and points at
    `build/current-native-mtp-contract-20260522-config-only.json`.

Green proof:

- focused engine marker:
  `uv run --extra dev python -m pytest -q tests/test_native_mtp_autodetect.py::TestNativeMtpAutodetect::test_config_only_mtp_bundle_does_not_activate_native_runtime`
  -> `1 passed`;
- focused panel marker:
  `cd panel && npx vitest run tests/model-config-registry.test.ts --testNamePattern "does not expose Native MTP for config-only" --reporter=verbose`
  -> `1 passed / 52 skipped`;
- native-MTP contract:
  `uv run --extra dev python tests/cross_matrix/run_native_mtp_contract.py --out build/current-native-mtp-contract-20260522-config-only.json`
  -> `status=pass`, `missing_markers=[]`, engine `116 passed`,
  panel controls `12 passed / 221 skipped`, panel detection
  `6 passed / 47 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-native-mtp-config-only.json`
  -> 18 rows;
- focused pytest:
  `uv run --extra dev python -m pytest -q tests/test_native_mtp_autodetect.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `131 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-native-mtp-config-only.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 05:23 PDT - VL Panel Family Detection Added To Media Gate

Strengthened the VL/media release gate so it covers panel-side family routing
for the user-called-out VL/video/Omni rows, not only engine media serialization
and tool follow-up:

- Qwen VL/video/hybrid panel detection is now part of the VL/media contract.
- ZAYA1-VL stale text stamps staying multimodal is now part of the contract.
- MXFP4/MXFP8 Qwen VLM panel detection is now part of the contract.
- Nemotron-H stale Omni sidecars not forcing text rows through MLLM is now part
  of the contract.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_vl_media_cache_contract.py --out build/current-vl-media-cache-contract-20260522-panel-family-red.json`
  first reported the new panel markers as missing while status still passed;
- `build/current-vl-media-cache-contract-20260522-panel-family-status-red.json`
  then failed top-level status after adding
  `all_required_panel_markers_present`.

Fix:

- `tests/cross_matrix/run_vl_media_cache_contract.py`
  - added panel model-config registry source hashing;
  - added required markers for ZAYA1-VL, Qwen JANGTQ/MXFP4/MXFP8 VLM,
    Qwen video metadata, and Nemotron stale-Omni sidecars;
  - added `panel_vlm_family_detection` command;
  - added `all_required_panel_markers_present`.
- `tests/test_vl_media_cache_contract.py`
  - pins the new markers and command.
- `tests/cross_matrix/release_regression_manifest.py`
  - VL row now records panel family detection coverage and points at
    `build/current-vl-media-cache-contract-20260522-panel-family.json`.

Green proof:

- VL/media contract:
  `uv run --extra dev python tests/cross_matrix/run_vl_media_cache_contract.py --out build/current-vl-media-cache-contract-20260522-panel-family.json`
  -> `status=pass`, no missing markers, engine `32 passed`,
  panel media `12 passed`, panel VLM settings `11 passed / 222 skipped`,
  panel family detection `11 passed / 42 skipped`;
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-vl-panel-family.json`
  -> 18 rows;
- focused pytest:
  `uv run --extra dev python -m pytest -q tests/test_vl_media_cache_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `63 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-vl-panel-family.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 05:37 PDT - Chat/Responses Streaming Cache Detail Usage Gate

Pinned the API-surface edge Eric called out around cache responses endpoint
visibility:

- Chat Completions streaming usage must preserve `cached_tokens` and
  `cache_detail`.
- Responses API streaming usage must preserve `cached_tokens` and
  `cache_detail`.
- Finish chunks must carry the same cache-detail label that non-streaming
  usage already exposes, so UI/API clients can distinguish `paged+dsv4`,
  `paged+zaya_cca`, `paged+ssm+disk`, `disk+tq`, and related typed cache
  paths.

Red proof:

- `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-stream-cache-detail-red.json`
  failed with nested missing markers:
  - `test_chat_stream_tracks_cache_detail_alongside_cached_tokens`
  - `test_chat_stream_finish_chunks_emit_cache_detail`
  - `test_responses_stream_tracks_cache_detail_alongside_cached`
  - `test_responses_stream_finish_emits_cache_detail`
- panel request builders stayed green during the red check.

Fix:

- `tests/cross_matrix/run_noheavy_api_cache_contract.py`
  - now requires and runs the four streaming cache-detail tests;
  - added the named check `streaming_cache_detail_usage`.
- `tests/cross_matrix/run_api_surface_contract.py`
  - now requires the nested `streaming_cache_detail_usage` check;
  - added the top-level check
    `chat_and_responses_streaming_cache_detail_usage`.
- `tests/cross_matrix/release_regression_manifest.py`
  - API surface row now points at
    `build/current-api-surface-contract-20260522-stream-cache-detail.json`;
  - manifest text explicitly records streaming `cache_detail` propagation for
    Chat Completions and Responses.

Green proof:

- API surface contract:
  `uv run --extra dev python tests/cross_matrix/run_api_surface_contract.py --out build/current-api-surface-contract-20260522-stream-cache-detail.json`
  -> `status=pass`, `missing_nested_checks=[]`,
  `missing_nested_markers=[]`, `server_api_surface` `25 passed`, panel request
  builders `67 passed`;
- focused API surface contract tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py`
  -> `3 passed`.
- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-stream-cache-detail.json`
  -> 18 rows;
- focused API/manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_api_surface_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `63 passed`;
- py-compile for changed Python runners and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-stream-cache-detail.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 05:49 PDT - Fresh DSV4 Live Quality Blocker Recheck

After pushing the stream cache-detail gate, reran the live DSV4 production row
from current source:

```sh
uv run --extra dev python tests/cross_matrix/run_production_family_audit.py \
  --rows dsv4_jang_local \
  --live \
  --out build/current-production-family-audit-live-dsv4-jang-local-20260522-after-stream-cache-detail.json
```

Result: `live: FAIL failures=5`.

Passed rows:

- DSV4 paged/native composite cache enabled;
- canonical encoder shim;
- multi-EOS;
- cache stats/model capabilities/native cache capabilities;
- runtime cache layout logging;
- basic thinking-off chat;
- thinking-on recall/toggle row;
- structured Responses auto-tool choice;
- Anthropic basic;
- Ollama basic;
- chat stream disconnect/done;
- cache second-turn coherence;
- no blocking runtime log findings.

Failed rows:

- `dsv4_thinking_mode_max`
  - `finish="length"`, content empty, reasoning chars `4145`;
  - still reasoning-only under max thinking for a simple arithmetic prompt.
- `dsv4_threejs_identifier_integrity`
  - deterministic request: thinking off, `temperature=0.0`, `top_p=1.0`,
    `repetition_penalty=1.0`;
  - output still added markdown fences and corrupted identifiers:
    `THREE.PPerspectiveCamera`, `THREE.MMeshBasicMaterial`.
- `dsv4_long_context_full_output_vc_project_plan`
  - `finish="length"`, incomplete tail despite low loop score.
- `dsv4_long_context_full_output_game_design_long_context`
  - skipped because identifier gate failed.
- `responses_tool_history_continuation`
  - returned `READEOM.md`, another exact-token/code-ish corruption symptom.

Static issue reported by the audit:

- `DSV4 output-head/final-norm precision boundary requires source-vs-quant or rebuilt-artifact clearance before long-output production claims (head=U32, norm=F16)`

No DSV4 server process was left running after the failed audit. This keeps the
release decision blocked unless the DSV4 long-output/code quality row is
explicitly descoped or a rebuilt/source-body artifact passes the live gate.

Verification around the evidence update:

- release manifest:
  `uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-dsv4-live-recheck.json`
  -> 18 rows;
- focused manifest/current-suite tests:
  `uv run --extra dev python -m pytest -q tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `61 passed`;
- py-compile for changed Python files and `git diff --check` -> pass;
- umbrella suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-dsv4-live-recheck.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## Release Decision

No release build has been started from this checkpoint. The next release action
is blocked unless Eric explicitly descopes the DSV4 long-output/code quality
row or that row gets real runtime evidence.

## 2026-05-22 05:53 PDT - Final Prebuild Gate Recheck

Fresh no-heavy prebuild verification from current source:

- max-output/context contract:
  `.venv/bin/python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-final-prebuild.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `36 passed / 292 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-final-prebuild.json`
  -> 18 rows across all required domains;
- focused max-output/release/current-suite tests:
  `.venv/bin/python -m pytest -q tests/test_max_output_context_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- umbrella current suite:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-final-prebuild.json`
  -> `status=pass`, `failed_steps=[]`, open requirements exactly
  `["DSV4 long-output/code/file-generation quality is release-cleared"]`;
- py-compile for the checked runners/tests and `git diff --check` -> pass;
- release-surface preflight:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-final-prebuild.json`
  -> `status=pass`;
- objective proof summary:
  `.venv/bin/python tests/cross_matrix/summarize_objective_proof.py --out build/current-objective-proof-summary-20260522-final-prebuild.json`
  -> 12 PASS / 1 OPEN.

Build/sign/release remains blocked unless Eric explicitly descopes the DSV4
long-output/code quality row or a rebuilt/source-body DSV4 artifact clears the
live quality gate. The fresh max-output/context evidence does not show a
remaining UI/server token-wiring blocker.

## 2026-05-22 05:59 PDT - Plain MLX 4bit Qwen Row Pinned

Added a named no-heavy release guard for the existing plain MLX 4-bit Qwen row
so it cannot be silently confused with JANG, JANGTQ/MXTQ, MXFP4, or MXFP8
families while parser/modality/speed rows are maintained.

New release row:

- `decode_speed_plain_mlx_4bit_qwen36_row`

What it pins:

- row `qwen35_4bit` points at `/Users/eric/models/Qwen3.6-35B-A3B-4bit`;
- path is not JANG, JANGTQ, or MXFP;
- launch policy remains Qwen tool parser + qwen3 reasoning parser;
- `--is-mllm` is present for the VLM row;
- no startup `--max-tokens` is emitted by the decode-speed launch command;
- decode/PP thresholds stay explicit and positive.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  failed before the required row existed;
- focused green:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows tests/test_model_family_detection_contract.py::test_decode_speed_gate_has_plain_mlx_qwen36_4bit_row tests/test_model_family_detection_contract.py::test_decode_speed_gate_artifact_format_coverage_matrix`
  -> `3 passed`;
- family gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-plain-mlx-4bit.json`
  -> `status=pass`, `missing_rows=[]`, engine `40 passed`, panel
  `41 passed / 12 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-plain-mlx-4bit.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `84 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-plain-mlx-4bit.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-plain-mlx-4bit.json`
  -> `status=pass`.

This is source/static launch-policy and matrix coverage. It does not claim live
output quality for the plain MLX 4-bit row.

## 2026-05-22 06:06 PDT - Plain MLX 4bit Artifact Detection Pinned

Extended the no-heavy model-artifact gate so plain MLX 4-bit Qwen artifacts are
explicitly covered alongside JANG, JANGTQ/MXTQ, MXFP4, MXFP8, dropped-MTP, and
preserved-MTP artifacts.

New artifact marker:

- `test_qwen36_plain_mlx_4bit_keeps_hybrid_cache_without_jang_or_mxfp`

What it pins:

- a `Qwen3.6-35B-A3B-4bit` artifact with config-declared
  `linear_attention`/`full_attention` uses hybrid cache;
- multimodal routing comes from `vision_config`;
- tool parser stays `qwen`;
- reasoning parser stays `qwen3`;
- the row does not require `jang_config.json`, JANGTQ/MXTQ, or MXFP metadata
  to pick the correct cache/parser/modality policy.

Verification:

- red:
  `.venv/bin/python tests/cross_matrix/run_model_artifact_format_contract.py --out build/current-model-artifact-format-contract-20260522-plain-mlx-4bit-red.json`
  -> `status=fail`, missing the new marker;
- focused registry marker:
  `.venv/bin/python -m pytest -q tests/test_model_config_registry.py -k qwen36_plain_mlx_4bit`
  -> `1 passed`;
- artifact gate:
  `.venv/bin/python tests/cross_matrix/run_model_artifact_format_contract.py --out build/current-model-artifact-format-contract-20260522-plain-mlx-artifact.json`
  -> `status=pass`, `missing_markers=[]`, `130 passed`;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `85 passed`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-plain-mlx-artifact-final.json`
  -> 18 rows;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-plain-mlx-artifact.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-plain-mlx-artifact.json`
  -> `status=pass`.

This is still source/static artifact detection proof. It does not claim live
output quality for the plain MLX 4-bit row.

## 2026-05-22 06:11 PDT - Ling/Bailing Hybrid Loader Repair Gate Pinned

Extended the no-heavy model-artifact gate so Ling/Bailing hybrid loader repairs
are required explicitly, not only selected incidentally through broad MXFP/JANG
patterns.

Required markers:

- `test_sanitize_repairs_flat_2d_switch_mlp_to_3d`
- `test_sanitize_no_op_on_correct_3d_shape`
- `test_sanitize_restores_dwq_split_mla_kv_b_proj`
- `test_sanitize_trims_absent_mtp_layer_before_strict_load`

What this protects:

- older Ling/Bailing MXFP4 artifacts with flat 2D `switch_mlp` tensors are
  repaired back to 3D before strict load;
- already-correct JANGTQ 3D `switch_mlp` tensors are left unchanged;
- DWQ split `embed_q` / `unembed_out` MLA projection tensors are rebuilt into
  `kv_b_proj`;
- configs that advertise absent MTP tail layers trim those layers before
  strict load;
- the artifact runner selector now explicitly includes `bailing` and
  `switch_mlp`.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py`
  failed until the runner selector explicitly included `bailing`;
- artifact gate:
  `.venv/bin/python tests/cross_matrix/run_model_artifact_format_contract.py --out build/current-model-artifact-format-contract-20260522-bailing-loader.json`
  -> `status=pass`, `missing_markers=[]`, `130 passed`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-bailing-loader.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-bailing-loader.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-bailing-loader.json`
  -> `status=pass`.

This is source/static loader repair coverage. It does not claim live output
quality for Ling/Bailing rows.

## 2026-05-22 06:17 PDT - Qwen Indexed-MTP VLM Routing Pinned

Extended the VLM media/cache release gate so Qwen3.6 VL JANG bundles with
indexed MTP tensors are explicitly selected and required in the panel family
detection pass. This keeps native-MTP/VLM routing covered in the same gate as
video/media/tool-follow-up behavior, not only in the generic family/native-MTP
gates.

Required panel marker:

- `marks Qwen3.6 VL JANG bundles with indexed MTP tensors as native MTP capable`

What it pins:

- Qwen3.6 VL JANG bundles with indexed `mtp.*` tensors stay multimodal;
- the panel marks them native-MTP capable;
- this row is intentionally selected by `indexed MTP` in the VLM family
  detection command;
- it is checked alongside Qwen video, JANGTQ/MXTQ, MXFP4, MXFP8, ZAYA-VL, and
  Nemotron-H stale-sidecar rows.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_vl_media_cache_contract.py::test_vl_media_cache_contract_pins_named_panel_rows`
  failed until the VLM family detection selector included `indexed MTP`;
- VLM media gate:
  `.venv/bin/python tests/cross_matrix/run_vl_media_cache_contract.py --out build/current-vl-media-cache-contract-20260522-qwen-indexed-mtp.json`
  -> `status=pass`, no missing markers, engine `32 passed / 6 skipped`,
  panel family detection `13 passed / 40 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-qwen-indexed-mtp-vl.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_vl_media_cache_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `64 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-qwen-indexed-mtp-vl.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-qwen-indexed-mtp-vl.json`
  -> `status=pass`.

This is source/static panel routing coverage. It does not claim live Qwen
indexed-MTP VLM output quality.

## 2026-05-22 06:25 PDT - Nemotron-H Stale Omni Engine Routing Pinned

Extended the model-family detection gate so Nemotron-H stale Omni sidecars are
proved in both engine and panel routing, not only in the panel test. This keeps
text-only Nemotron-H/Nemotron-H v2 extracts from being routed through MLLM just
because a stale `jang_config.json` says `capabilities.modality=omni` or a
`preprocessor_config.json` sidecar exists.

Required engine marker:

- `test_nemotron_h_stale_omni_stamp_without_media_stays_text_hybrid`

What it pins:

- `config.json` with `model_type=nemotron_h_v2` and no real media config stays
  text-only even when `jang_config.json` says `modality=omni`;
- `preprocessor_config.json` alone is not enough to enable MLLM routing;
- hybrid SSM/attention cache routing remains `hybrid`;
- parser policy remains `tool_parser=nemotron` and
  `reasoning_parser=deepseek_r1`.

Verification:

- red:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-nemotron-stale-omni-red.json`
  -> `status=fail`, `missing_rows=["nemotron_h_hybrid_text_not_stale_omni"]`;
- focused green:
  `.venv/bin/python -m pytest -q tests/test_model_config_registry.py::TestModelConfigs::test_nemotron_h_stale_omni_stamp_without_media_stays_text_hybrid`
  -> `1 passed`;
- family gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-nemotron-stale-omni.json`
  -> `status=pass`, `missing_rows=[]`, engine `41 passed`, panel
  `41 passed / 12 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-nemotron-stale-omni.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `84 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-nemotron-stale-omni.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-nemotron-stale-omni.json`
  -> `status=pass`.

This is no-heavy engine/panel routing coverage. It does not claim live
Nemotron-H output quality.

## 2026-05-22 06:33 PDT - Chat Output Cap vs Server Startup Default Edge Pinned

Extended the max-output/context gate for Eric's concern that separating
per-chat Max Tokens from Server Default Max Output Tokens could accidentally
turn the server startup value into a ceiling or rewrite prompt/context caps.

Required panel marker:

- `per-chat maxTokens below or above the server startup default remain request scoped`

What it pins:

- Chat Completions request building keeps a per-chat `maxTokens=512` below a
  hypothetical `4096` server startup default as `max_tokens=512`;
- Chat Completions request building keeps `maxTokens=8192` above that default
  as `max_tokens=8192`;
- Responses request building keeps the same values as `max_output_tokens`;
- neither path writes `max_prompt_tokens`, `max_context_tokens`, or
  `max_context` from per-chat output settings;
- the existing engine-side gate still proves server startup `--max-tokens` is
  an omitted-request default, not a hard ceiling.

Verification:

- red:
  `.venv/bin/python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-chat-cap-startup-red.json`
  -> `status=fail`,
  `missing_markers=["per-chat maxTokens below or above the server startup default remain request scoped"]`;
- focused panel:
  `cd panel && npx vitest run tests/request-builder.test.ts --testNamePattern "per-chat maxTokens below or above" --reporter=verbose`
  -> `2 passed / 52 skipped`;
- max-output/context gate:
  `.venv/bin/python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-chat-cap-startup.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `38 passed / 292 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-chat-cap-startup.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_max_output_context_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `62 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-chat-cap-startup.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-chat-cap-startup.json`
  -> `status=pass`.

This is no-heavy request-builder/API-contract coverage. It does not claim live
model output quality.

## 2026-05-22 06:39 PDT - Reasoning Parser CLI Choice Parity Pinned

Extended the parser registry gate with the reasoning-parser equivalent of the
existing tool-parser CLI choice guard. This targets the MiniMax class of
regression where panel/family autodetection emits a parser id that the packaged
engine CLI rejects before the model can start.

Required engine marker:

- `test_cli_reasoning_parser_choices_cover_family_registry_parsers`

What it pins:

- every `reasoning_parser` emitted by registered model families is present in
  the runtime reasoning parser registry used by CLI choices;
- `serve --reasoning-parser` builds choices from `list_parsers()` plus
  `auto`/`none`;
- `minimax_m2` stays CLI-selectable for MiniMax M2/M2.7 sessions;
- this sits beside the existing tool-parser CLI parity guard for DSML, ZAYA,
  Hy3/Hunyuan, Gemma, MiniMax, Nemotron, and other parser families.

Verification:

- red:
  `.venv/bin/python tests/cross_matrix/run_parser_registry_contract.py --out build/current-parser-registry-contract-20260522-reasoning-cli-red.json`
  -> `status=fail`,
  `missing_markers=["test_cli_reasoning_parser_choices_cover_family_registry_parsers"]`;
- focused green:
  `.venv/bin/python -m pytest -q tests/test_engine_audit.py::TestStartupCompatibilityGuards::test_cli_reasoning_parser_choices_cover_family_registry_parsers tests/test_parser_registry_contract.py::test_parser_registry_contract_pins_named_parser_edges`
  -> `2 passed`;
- parser gate:
  `.venv/bin/python tests/cross_matrix/run_parser_registry_contract.py --out build/current-parser-registry-contract-20260522-reasoning-cli.json`
  -> `status=pass`, `missing_markers=[]`, engine `103 passed`, panel
  `40 passed / 246 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-reasoning-cli.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_parser_registry_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `63 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-reasoning-cli.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-reasoning-cli.json`
  -> `status=pass`.

This is no-heavy parser/CLI contract coverage. It does not claim live parser
quality for every model family.

## 2026-05-22 06:46 PDT - Qwen Affine-JANG VLM Text-Loader Policy Pinned

Extended the VLM media/cache gate with an engine-side registry marker for the
Qwen affine-JANG/M-RoPE boundary. Panel tests already covered this path, but
the release VLM gate did not execute the engine registry row.

Required engine marker:

- `test_qwen36_affine_jang_vlm_stays_text_loader_until_mrope_fixed`

What it pins:

- a Qwen3.6 affine-JANG artifact with `vision_config`, image/video token ids,
  and `capabilities.modality=vision` remains `is_mllm=False`;
- the same artifact still keeps `cache_type=hybrid`, `tool_parser=qwen`, and
  `reasoning_parser=qwen3`;
- this is scoped to explicit affine-JANG, not JANGTQ/MXTQ or plain MLX/MXFP
  Qwen VLM rows, which remain covered as multimodal elsewhere;
- the VLM gate now runs `tests/test_model_config_registry.py` for the selected
  Qwen affine-JANG marker.

Verification:

- red:
  `.venv/bin/python tests/cross_matrix/run_vl_media_cache_contract.py --out build/current-vl-media-cache-contract-20260522-qwen-affine-text-red.json`
  -> `status=fail`,
  `missing_engine_markers=["test_qwen36_affine_jang_vlm_stays_text_loader_until_mrope_fixed"]`;
- focused green:
  `.venv/bin/python -m pytest -q tests/test_model_config_registry.py::TestModelConfigs::test_qwen36_affine_jang_vlm_stays_text_loader_until_mrope_fixed tests/test_vl_media_cache_contract.py::test_vl_media_cache_contract_pins_named_engine_rows`
  -> `2 passed`;
- VLM media/cache gate:
  `.venv/bin/python tests/cross_matrix/run_vl_media_cache_contract.py --out build/current-vl-media-cache-contract-20260522-qwen-affine-text.json`
  -> `status=pass`, no missing engine/panel markers, engine
  `42 passed / 6 skipped`, panel follow-up `12 passed`, panel settings
  `11 passed / 222 skipped`, panel family detection `13 passed / 40 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-qwen-affine-text.json`
  -> 18 rows;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_vl_media_cache_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `64 passed`;
- py-compile and `git diff --check` -> pass;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-qwen-affine-text.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-qwen-affine-text.json`
  -> `status=pass`.

This is no-heavy engine/panel routing coverage. It does not claim live Qwen
video/VLM output quality.

## 2026-05-22 06:55 PDT - MXFP VLM Loader Quant Mode Pinned

Extended the model-artifact-format gate with a required marker for the MXFP
VLM loader quantization path.

Required marker:

- `test_mxfp_vlm_loader_quantizes_with_declared_mode`

What it pins:

- Qwen3.6 MXFP4 VLM/MTP bundles pass `mode=mxfp4`, `bits=4`, and
  `group_size=32` into MLX quantization;
- Qwen3.6 MXFP8 VLM/MTP bundles pass `mode=mxfp8`, `bits=8`, and
  `group_size=32` into MLX quantization;
- VLM loader routing does not silently fall back to affine mode or drift into
  JANGTQ/TurboQuant handling for MXFP bundles;
- the release manifest now names this exact row through
  `build/current-model-artifact-format-contract-20260522-mxfp-vlm-loader.json`.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py`
  -> failed before the marker was listed in
  `REQUIRED_ARTIFACT_TEST_MARKERS`;
- focused MXFP loader checks:
  `.venv/bin/python -m pytest -q -vv tests/test_native_mtp_autodetect.py -k "test_mxfp_vlm_loader_quantizes_with_declared_mode or test_jang_quant_mode_supports_mxfp8_metadata or test_uint32_post_load_upgrade_preserves_mxfp8_mode"`
  -> `4 passed / 67 deselected`;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `63 passed`;
- py-compile and `git diff --check` -> pass;
- artifact gate:
  `.venv/bin/python tests/cross_matrix/run_model_artifact_format_contract.py --out build/current-model-artifact-format-contract-20260522-mxfp-vlm-loader.json`
  -> `status=pass`, `missing_markers=[]`, `131 passed`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-mxfp-vlm-loader.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-mxfp-vlm-loader.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-mxfp-vlm-loader.json`
  -> `status=pass`.

This is no-heavy loader/artifact coverage. It does not claim live Qwen VLM
output quality.

## 2026-05-22 07:02 PDT - Affine JANG Loader Acceptance Pinned

Extended the model-artifact-format gate with a required marker for generic
affine JANG loader acceptance.

Required marker:

- `test_load_jang_model_accepts_affine_weight_format`

What it pins:

- a bundle with `jang_config.json` declaring `weight_format=affine` continues
  through `load_jang_model`;
- the loader does not reject that artifact shape or accidentally route it as
  JANGTQ/MXTQ, MXFP, or plain MLX;
- this complements the existing JANGTQ mixed-bit, MXFP4/8, Bailing/Ling, and
  plain MLX 4-bit rows.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py`
  -> failed before the marker was listed in
  `REQUIRED_ARTIFACT_TEST_MARKERS`;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_artifact_format_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `64 passed`;
- py-compile and `git diff --check` -> pass;
- artifact gate:
  `.venv/bin/python tests/cross_matrix/run_model_artifact_format_contract.py --out build/current-model-artifact-format-contract-20260522-affine-jang-loader.json`
  -> `status=pass`, `missing_markers=[]`, `131 passed`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-affine-jang-loader.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-affine-jang-loader.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-affine-jang-loader.json`
  -> `status=pass`.

This is no-heavy loader/artifact coverage. It does not claim live affine-JANG
model output quality.

## 2026-05-22 07:10 PDT - ZAYA Stale-Stamp Reasoning Policy Pinned

Extended the model-family-detection gate with a required row for stale ZAYA
converter stamps.

Required row:

- `zaya_stale_stamp_reasoning_policy`

Required marker:

- `test_zaya_stale_stamp_cannot_disable_reasoning_or_reenable_think_seed`

What it pins:

- stale `jang_config.json` capability stamps cannot disable ZAYA reasoning;
- stale stamps cannot swap ZAYA off the `qwen3` reasoning parser;
- stale stamps cannot reenable `think_in_template=True`;
- ZAYA keeps `zaya_xml` tools, `zaya_cca` cache subtype, and default
  thinking-off policy.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> failed before the required row existed;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `87 passed`;
- py-compile and `git diff --check` -> pass;
- family gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-zaya-stale-stamp.json`
  -> `status=pass`, `missing_rows=[]`, engine `41 passed`, panel
  `41 passed / 12 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-zaya-stale-stamp.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-zaya-stale-stamp.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-zaya-stale-stamp.json`
  -> `status=pass`.

This is no-heavy registry/family-policy coverage. It does not claim live ZAYA
output quality.

## 2026-05-22 07:17 PDT - Qwen/Nemotron Hybrid Cache Rows Pinned

Extended the model-family-detection gate with required engine-side rows for
Qwen and Nemotron hybrid-cache classification that were previously present as
individual tests but not mandatory release rows.

Required rows:

- `nemotron_h_registry_hybrid_cache`
- `qwen36_dense_linear_attention_hybrid_cache`
- `qwen36_moe_text_linear_attention_hybrid_cache`

Required markers:

- `test_nemotron_hybrid_cache`
- `test_nemotron_h_v2_config`
- `test_qwen3_5_linear_attention_config_uses_hybrid_cache`
- `test_qwen3_5_moe_text_linear_attention_uses_hybrid_cache`

What it pins:

- Qwen dense linear-attention wrappers keep `cache_type=hybrid` through the
  engine registry, not only through panel matching;
- Qwen MoE text linear-attention wrappers keep `cache_type=hybrid` through the
  engine registry;
- base Nemotron-H/Nemotron-H-v2 registry rows stay hybrid before stale Omni
  sidecar handling is considered;
- the release manifest now points at the new family artifact instead of an
  older ZAYA-only checkpoint.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> failed before the required rows existed;
- red:
  `.venv/bin/python -m pytest -q tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_qwen_nemotron_hybrid_cache_rows`
  -> failed before the release manifest referenced this checkpoint;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `88 passed`;
- py-compile and `git diff --check` -> pass;
- family gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-qwen-nemotron-hybrid-cache.json`
  -> `status=pass`, `missing_rows=[]`, engine `41 passed / 111 deselected`,
  panel `41 passed / 12 skipped`;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-qwen-nemotron-hybrid-cache.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-qwen-nemotron-hybrid-cache.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-qwen-nemotron-hybrid-cache.json`
  -> `status=pass`.

This is no-heavy registry/family-policy coverage. It does not claim live Qwen
or Nemotron output quality. No release build/signing started.

## 2026-05-22 07:27 PDT - New-Chat Output Cap Non-Stickiness Pinned

Tightened the max-output/max-context contract so the artifact has a named
check for the exact compatibility concern: per-chat output caps must not become
server startup defaults, inherited new-chat caps, or sticky model defaults.

New named check:

- `new_chat_output_caps_are_not_inherited_or_made_sticky`

Required markers behind that check:

- `default profiles cannot make maxTokens sticky on clean new chats`
- `new chats preserve model-owned maxTokens while refusing inherited output caps`
- `chat maxTokens save path cannot mutate session startup maxTokens`

What it pins:

- per-chat `maxTokens` remains a request override;
- default profiles cannot copy stale `maxTokens` into a clean new chat;
- same-model new chats preserve model-owned startup defaults while refusing
  inherited output caps;
- the chat override save path cannot mutate session startup `maxTokens`;
- the release manifest now points at the new max-output artifact instead of an
  older checkpoint.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_max_output_context_contract.py::test_max_output_context_contract_covers_all_public_api_surfaces`
  -> failed before the named check existed;
- red:
  `.venv/bin/python -m pytest -q tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_server_chat_max_output_boundary`
  -> failed before the release manifest referenced this checkpoint;
- max-output gate:
  `.venv/bin/python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-new-chat-output-cap-nonsticky.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `38 passed / 292 skipped`;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_max_output_context_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `66 passed`;
- py-compile and `git diff --check` -> pass;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-new-chat-output-cap-nonsticky.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-new-chat-output-cap-nonsticky.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-new-chat-output-cap-nonsticky.json`
  -> `status=pass`.

This is no-heavy UI/API/server wiring coverage. It does not claim live DSV4
quality clearance. No release build/signing started.

## 2026-05-22 07:35 PDT - JANG-Only MX Matmul Speed Rows Pinned

Extended the model-family/decode-speed gate with a required row for the
JANG-only MX matmul launch policy.

Required row:

- `decode_speed_jang_only_mx_matmul_policy`

Required marker:

- `test_decode_speed_gate_jang_only_rows_keep_text_mx_matmul_launch_policy`

Rows covered:

- `qwen27_jang4m`
- `qwen27_jang4m_mtp`
- `qwen35_jang4k_ext`
- `minimax_jang2l_crack`

What it pins:

- JANG-only speed rows stay `JANG_` rows, not `JANGTQ` or `MXFP`;
- those rows stay text launch rows and do not emit `--is-mllm`;
- those rows do not emit startup `--max-tokens`;
- parser policy stays row-owned (`qwen/qwen3` or `minimax/minimax_m2`);
- no forced JANGTQ acceleration or DSV4-disable environment knobs leak into
  the launch command.

Verification:

- red:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> failed before the required row existed;
- focused row tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows tests/test_model_family_detection_contract.py::test_decode_speed_gate_jang_only_rows_keep_text_mx_matmul_launch_policy`
  -> `2 passed`;
- family gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-jang-only-mx-matmul-policy.json`
  -> `status=pass`, `missing_rows=[]`, engine `42 passed / 111 deselected`,
  panel `41 passed / 12 skipped`;
- red:
  `.venv/bin/python -m pytest -q tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_decode_speed_artifact_format_matrix`
  -> failed before the release manifest referenced this checkpoint;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py tests/test_release_regression_manifest.py tests/test_current_regression_suite.py`
  -> `89 passed`;
- py-compile and `git diff --check` -> pass;
- release manifest:
  `.venv/bin/python tests/cross_matrix/run_release_regression_manifest.py --out build/current-release-regression-manifest-20260522-jang-only-mx-matmul-policy.json`
  -> 18 rows;
- umbrella:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-jang-only-mx-matmul-policy.json`
  -> `status=pass`, `failed_steps=[]`, open requirement remains
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `.venv/bin/python tests/cross_matrix/run_release_surface_contract.py --out build/current-release-surface-contract-20260522-jang-only-mx-matmul-policy.json`
  -> `status=pass`.

This is no-heavy launch-policy and speed-row coverage. It does not claim live
JANG speed output quality or DSV4 quality clearance. No release build/signing
started.

## 2026-05-22 07:45 PDT - Release Gate Now Enforces Objective Digest

Found a release-preflight gap while preparing for the build step: the umbrella
suite caught the open DSV4 quality row, but a direct
`panel/scripts/release-gate-python-app.py --skip-app --skip-gui` run could
return success because the script did not refresh/read the objective-proof
digest itself.

Fix:

- added `check_objective_proof_digest()` to the release gate;
- the gate now runs
  `tests/cross_matrix/summarize_objective_proof.py --out build/current-objective-proof-audit-20260521.json`;
- if any digest requirement is not `pass`, the release gate records
  `[FAIL] objective proof digest: ...`;
- added tests proving the DSV4 open row blocks direct release-gate runs;
- indexed the enforced packaged-integrity artifact in the release manifest.

Red:

- `tests/test_release_gate_python_app.py::test_release_gate_objective_digest_fails_on_open_requirement`
  and `tests/test_release_gate_python_app.py::test_release_gate_static_runs_objective_digest_gate`
  failed before the function/call existed;
- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_packaged_integrity_with_runner_artifact`
  failed before the objective-gate-enforced artifact was indexed.

Green:

- `.venv/bin/python -m pytest -q tests/test_release_gate_python_app.py`
  -> `36 passed`;
- with clean JANG source:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools .venv/bin/python tests/cross_matrix/run_packaged_integrity_contract.py --out build/current-packaged-integrity-contract-20260522-objective-gate-enforced.json`
  -> `status=pass`, `failed=[]`, `release_gate_skip_app: rc=1`;
- the release-gate tail now shows:
  `[FAIL] objective proof digest: DSV4 long-output/code/file-generation quality is release-cleared`.

This is a release-safety fix. It does not clear the DSV4 model-quality row or
start build/signing.

## 2026-05-22 07:52 PDT - Persisted Chat Output Caps Cannot Relaunch Server Caps

Added a targeted max-output/context edge-case guard for the concern that a
separate Chat Max Output Tokens override could accidentally mutate or conflict
with Server Default Max Output Tokens on a later server launch.

New required marker:

- `persisted chat maxTokens cannot relaunch server with a new startup maxTokens`

What it pins:

- `chat_overrides.max_tokens` is written only through the chat override table;
- `chat:setOverrides` still does not touch session config, model settings, or
  session save paths;
- `model_settings.max_tokens` remains deliberately stored as `NULL`;
- server launch still reads only `sessions.config.maxTokens` for `--max-tokens`;
- the session launch block does not query `chat_overrides` or
  `overrides.maxTokens`.

Red:

- max-output/context gate failed with
  `missing_markers=["persisted chat maxTokens cannot relaunch server with a new startup maxTokens"]`
  before the test existed.
- release manifest boundary test failed before this artifact/proof text was
  indexed.

Green:

- focused panel test:
  `cd panel && npx vitest run tests/chat-override-policy.test.ts --testNamePattern "persisted chat maxTokens cannot relaunch server with a new startup maxTokens|chat maxTokens save path cannot mutate session startup maxTokens|server startup maxTokens and chat maxTokens remain independent" --reporter=verbose`
  -> `3 passed`;
- max-output/context gate:
  `build/current-max-output-context-contract-20260522-persisted-chat-output-cap.json`
  -> `status=pass`, `missing_markers=[]`, engine `20 passed`, panel
  `39 passed / 292 skipped`;
- focused release tests:
  `.venv/bin/python -m pytest -q tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_server_chat_max_output_boundary tests/test_max_output_context_contract.py::test_max_output_context_contract_covers_all_public_api_surfaces`
  -> `2 passed`.

This is no-heavy persisted-state and launch-wiring proof. It does not claim
live model output quality or clear the DSV4 long-output/code row.

## 2026-05-22 08:07 PDT - DSV4 Additional Args Cannot Reenable Native MTP

Added a targeted cross-feature guard for stale `additionalArgs` in DSV4
sessions. The bug class is dangerous because `additionalArgs` sits after the
structured settings builder and can otherwise reintroduce flags that the DSV4
family gate deliberately suppresses.

New required marker:

- `DSV4 additional args cannot reenable native MTP or deterministic sampling policy`

What it pins:

- DSV4 launch preview and real launch filtering both block
  `--native-mtp-depth`;
- both block `--native-mtp-sampling-policy deterministic-defaults`;
- both block `--disable-native-mtp`;
- both block stale `--dsv4-enable-prefix-cache` from additional args, so the
  structured DSV4 diagnostic toggle owns that flag;
- both block hidden `--default-temperature` and stale `--max-tokens` in DSV4
  additional args;
- non-DSV4 additional args still pass ordinary allowed flags such as
  `--log-level DEBUG`.

Red:

- focused panel test failed before the preview/filter fix with raw
  `--native-mtp-depth`, `--native-mtp-sampling-policy deterministic-defaults`,
  `--disable-native-mtp`, `--dsv4-enable-prefix-cache`,
  `--default-temperature 0`, and `--max-tokens 32768` still present.

Green:

- focused panel test:
  `cd panel && npx vitest run tests/settings-flow.test.ts --testNamePattern "DSV4 additional args cannot reenable native MTP or deterministic sampling policy|appends additional args to command|omits additional args when empty" --reporter=verbose`
  -> `3 passed / 231 skipped`.

This is a wiring/compatibility fix only. It does not clear DSV4
long-output/code/file-generation quality.

## 2026-05-22 08:38 PDT - Release Gates Use Clean JANG Source

Fixed a release-harness false failure where the umbrella suite and packaged
integrity wrapper could compare bundled `jang_tools` against dirty
`/Users/eric/jang` instead of the clean release worktree. The bundled runtime
already matched:

- `/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools`

but the wrapper call lacked explicit `VMLX_JANG_TOOLS_SOURCE` /
`VMLINUX_JANG_TOOLS_SOURCE` propagation, so unrelated dirty tracked JANG files
could make the release suite look broken.

New behavior:

- `tests/cross_matrix/run_packaged_integrity_contract.py` accepts
  `--jang-tools-source`;
- `tests/cross_matrix/run_current_regression_suite.py` accepts
  `--jang-tools-source`;
- each wrapper scopes both env vars while running child gates;
- no runtime code, sampler behavior, cache behavior, model config, or bundle
  contents were changed.

Red:

- `test_current_regression_suite_sets_clean_jang_source_env_for_release_children`
  failed because `build_suite_artifact()` had no `jang_tools_source` argument.
- `test_packaged_integrity_sets_clean_jang_source_env_for_bundle_checks` failed
  because `build_artifact()` had no `jang_tools_source` argument.

Green:

- focused harness tests:
  `.venv/bin/python -m pytest -q tests/test_current_regression_suite.py::test_current_regression_suite_sets_clean_jang_source_env_for_release_children tests/test_packaged_integrity_contract.py::test_packaged_integrity_sets_clean_jang_source_env_for_bundle_checks`
  -> `2 passed`;
- full harness tests:
  `.venv/bin/python -m pytest -q tests/test_current_regression_suite.py tests/test_packaged_integrity_contract.py`
  -> `32 passed`;
- packaged integrity gate with clean JANG source:
  `build/current-packaged-integrity-contract-20260522-clean-jang-source-env.json`
  -> `status=pass`, `failed=[]`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-clean-jang-source-env.json`
  -> `status=pass`, `failed_steps=[]`, with the only known open requirement:
  `DSV4 long-output/code/file-generation quality is release-cleared`;
- release surface:
  `build/current-release-surface-contract-20260522-release-finalization-refresh.json`
  -> `status=pass`;
- max-output/context audit:
  `build/current-max-output-context-contract-20260522-request-output-isolation-audit.json`
  -> `status=pass`, `missing_markers=[]`.

Release implication: packaging/source parity is no longer blocked by incidental
dirty JANG working state. A production release is still not cleared until the
DSV4 long-output/code/file-generation quality objective is closed or Eric
explicitly decides to ship with that limitation documented.

## 2026-05-22 08:49 PDT - Family Contract Pins Panel Launch Wiring

Added a no-heavy family-detection row that ties registry/decode-speed policy
back to the actual app launch builder. This closes the gap where
`run_model_family_detection_contract.py` could pass on registry and
decode-speed rows without directly exercising the `sessions.ts` launch-preview
boundary.

New required row:

- `panel_session_launch_parser_modality_policy`

What it pins:

- MiniMax launches with `--tool-call-parser minimax` and
  `--reasoning-parser minimax_m2`;
- Qwen3.6 hybrid cache forces paged cache over stale saved `usePagedCache=false`;
- ZAYA keeps the `qwen3` reasoning parser while startup thinking defaults stay
  model-owned, not emitted as hidden `--default-enable-thinking`;
- DSV4 stale cache config and additional args cannot reenable generic cache,
  native MTP, deterministic MTP sampling, hidden sampler defaults, or startup
  max-token overrides;
- native-MTP-capable rows launch with measured D3 policy through the panel path.

Red:

- `test_family_detection_contract_pins_named_release_rows` failed because the
  new row did not exist;
- `test_family_detection_contract_hashes_app_and_engine_sources` failed because
  `panel/src/main/sessions.ts` and `panel/tests/settings-flow.test.ts` were not
  hashed by the family contract;
- `test_family_detection_contract_runs_verbose_engine_and_panel_rows` failed
  because no focused `panel_session_launch_wiring` command existed;
- release manifest boundary test failed before the new proof artifact and
  scope were indexed.

Green:

- targeted family-contract tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows tests/test_model_family_detection_contract.py::test_family_detection_contract_hashes_app_and_engine_sources tests/test_model_family_detection_contract.py::test_family_detection_contract_runs_verbose_engine_and_panel_rows`
  -> `3 passed`;
- family detection gate:
  `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-panel-launch-wiring.json`
  -> `status=pass`, `missing_rows=[]`, engine `42 passed / 111 deselected`,
  panel registry `41 passed / 12 skipped`, panel launch wiring
  `6 passed / 228 skipped`.

This is launch-wiring compatibility proof only. It does not change runtime
behavior or clear live model output quality.

## 2026-05-22 08:53 PDT - Cache Architecture Gate Pins Panel Launch Policy

Strengthened `run_cache_architecture_contract.py` so cache-family proof now
includes the app launch builder, not only engine/API internals. This closes the
gap where DSV4, hybrid SSM/Mamba, regular KV, prefix cache, paged cache, block
disk L2, and stored KV quantization could be tested in backend units while the
panel launch command drifted.

New coverage:

- hashes `panel/src/main/sessions.ts`,
  `panel/src/shared/cacheControlPolicy.ts`,
  `panel/tests/settings-flow.test.ts`, and
  `panel/tests/cache-control-policy.test.ts`;
- runs focused panel vitest rows through `panel_cache_launch_policy`;
- requires DSV4 composite prefix cache to stay disabled by default;
- requires DSV4 diagnostic cache opt-in to emit native paged/L2 policy with
  256-token blocks;
- requires generic KV quantization to stay suppressed for DSV4 native cache;
- requires DSV4-only native controls not to leak onto non-DSV4 JANG/JANGTQ/MXFP
  rows;
- requires Qwen3.6 hybrid and Mamba cache detection to force paged cache over
  stale saved `usePagedCache=false`;
- requires regular KV rows to respect stale saved `usePagedCache=false`;
- requires prefix-cache and continuous-batching master switches to suppress
  dependent paged, L2, legacy disk, and stored KV quantization flags.

Red:

- `tests/test_cache_architecture_contract.py` failed because the gate had no
  `REQUIRED_PANEL_CACHE_MARKERS`, did not hash panel launch/cache files, and
  had no `panel_cache_launch_policy` command.

Green:

- cache architecture contract unit:
  `.venv/bin/python -m pytest -q tests/test_cache_architecture_contract.py`
  -> `2 passed`;
- cache architecture gate:
  `build/current-cache-architecture-contract-20260522-panel-cache-launch.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`,
  `missing_panel_markers=[]`;
- panel cache-launch proof inside that gate:
  `75 passed / 168 skipped`;
- release manifest:
  `build/current-release-regression-manifest-20260522-panel-cache-launch.json`
  -> `18 rows`;
- focused manifest/cache tests:
  `39 passed`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-panel-cache-launch.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

This is no-heavy launch-policy proof. It does not force sampler defaults,
change cache behavior, or clear DSV4 live long-output/code/file-generation
quality.

## 2026-05-22 08:59 PDT - Responses Output Boundary Is Required In Max-Token Gate

Tightened the max-output/context gate around the exact concern that a separate
per-chat output cap could interfere with server startup `--max-tokens`.

The existing panel tests already covered these behaviors, but the release gate
did not require their exact marker names. That made the proof too broad: the
gate could pass without proving the Responses-specific edge where per-chat
`maxTokens` maps to `max_output_tokens`, stays request-scoped above/below the
server default, and Auto omits output-budget fields so the server/model default
can apply.

New required markers:

- `per-chat maxTokens below or above the server startup default remain request scoped for Responses`
- `does not invent Responses sampler or output-budget values when chat overrides are absent`

Red:

- `tests/test_max_output_context_contract.py` failed because those markers were
  not required by `run_max_output_context_contract.py`;
- release-manifest boundary test failed because the
  `chat-settings-max-output-context-ui` row still referenced older artifacts.

Green:

- max-output contract unit:
  `.venv/bin/python -m pytest -q tests/test_max_output_context_contract.py`
  -> `1 passed`;
- max-output/context gate:
  `build/current-max-output-context-contract-20260522-responses-output-boundary.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`,
  engine `20 passed`, panel `39 passed / 293 skipped`;
- focused manifest/max-output tests:
  `38 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-responses-output-boundary.json`
  -> `18 rows`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-responses-output-boundary.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

No runtime behavior changed and no hidden output cap was added. This only makes
the existing server-default versus per-chat/API override boundary mandatory in
the release proof.

## 2026-05-22 10:20 PDT - Request Output Caps Cannot Mutate Later Auto Defaults

Added the edge Eric asked us to keep questioning after release: a per-chat/API
output cap below or above the server startup default must not become the new
server default for the next Auto request.

New required marker:

- `test_request_output_caps_do_not_mutate_server_default_across_later_omitted_requests`

Red:

- `.venv/bin/python tests/cross_matrix/run_max_output_context_contract.py --out build/current-max-output-context-contract-20260522-request-default-mutation-red.json`
  -> `status=fail`, `failed=[]`,
  `missing_markers=["test_request_output_caps_do_not_mutate_server_default_across_later_omitted_requests"]`.

Green:

- focused route/gate test:
  `.venv/bin/python -m pytest -q tests/test_engine_audit.py::TestServerSamplingResolution::test_request_output_caps_do_not_mutate_server_default_across_later_omitted_requests tests/test_max_output_context_contract.py`
  -> `2 passed`;
- max-output/context gate:
  `build/current-max-output-context-contract-20260522-request-default-mutation.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`,
  engine `21 passed`, panel `39 passed / 293 skipped`.

This is still no-heavy route-level proof. It does not add a hidden cap, clamp,
or sampler default. It proves Chat Completions and Responses explicit output
caps stay request-scoped and the later omitted requests still resolve to the
server startup default.

## 2026-05-22 10:22 PDT - Release Surface Gate Handles Post-Release Updater State

The umbrella suite exposed a real contract drift after the release shipped:
`run_release_surface_contract.py` still required `latest.json` to be behind the
source version. That was correct for pre-release staging, but false once
`latest.json` legitimately equals the source version after publication.

Red:

- umbrella suite:
  `build/current-regression-suite-20260522-request-default-mutation.json`
  -> `failed_steps=["release_surface_contracts"]`;
- focused new post-release updater test:
  `.venv/bin/python -m pytest -q tests/test_release_surface_contract.py::test_release_surface_contract_allows_complete_post_release_updater`
  -> failed because artifact status was `fail`.

Green:

- release-surface unit tests:
  `.venv/bin/python -m pytest -q tests/test_release_surface_contract.py`
  -> `4 passed`;
- release-surface artifact:
  `build/current-release-surface-contract-20260522-post-release-updater.json`
  -> `status=pass`, with `local_updater_release_state_valid=true` and
  `staged_source_version_not_public=false`.

The gate now accepts both safe pre-release state (`latest.json` behind source)
and complete post-release state (`latest.json` equals source with matching URL,
SHA256, and notes). It still rejects updater-ahead and incomplete bumped
manifests.

## 2026-05-22 10:28 PDT - Local High-Risk Artifact Registry Rows Are Pinned

Added a no-heavy static guard that reads the current local high-risk model
artifact metadata through the engine registry and compares it to the
decode-speed row policy. This does not load model weights.

Rows covered:

- DSV4: `dsv4_k`
- Qwen 3.6: JANG, JANG+MTP, MXFP4, MXFP8+MTP, JANGTQ, plain MLX 4bit
- Hy3: `Hy3-preview-JANGTQ2`
- Nemotron Omni/Nano: JANGTQ, JANGTQ4, MXFP4

Red:

- `.venv/bin/python tests/cross_matrix/run_model_family_detection_contract.py --out build/current-model-family-detection-contract-20260522-local-artifact-registry-red.json`
  -> `status=fail`, `failed=[]`,
  `missing_rows=["decode_speed_local_high_risk_rows_match_engine_registry"]`.

Green:

- focused local row tests:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_local_high_risk_rows_match_current_engine_registry tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> `2 passed`;
- model-family gate:
  `build/current-model-family-detection-contract-20260522-local-artifact-registry.json`
  -> `status=pass`, `failed=[]`, `missing_rows=[]`, engine `43 passed`,
  panel `41 passed / 12 skipped`, launch wiring `6 passed / 228 skipped`.

This pins parser/cache/modality policy against real local metadata for the
formats Eric called out: JANG, JANGTQ/MXTQ, MXFP4, MXFP8, plain MLX 4bit, and
native-MTP rows. It is not a live generation or speed clearance.

## 2026-05-22 10:39 PDT - Panel Local-Path Detection Matches Engine/API Policy

The new panel local-path guard exposed a real mismatch:

- panel/API already route indexed native-MTP Qwen affine-JANG VL artifacts as
  multimodal/VLM;
- the engine registry and decode-speed row still treated
  `qwen27_jang4m_mtp` as text-only.

Root cause:

- `vmlx_engine.model_config_registry._try_jang_stamp()` kept every affine-JANG
  Qwen VL-looking bundle on the text-loader guard used for plain affine-JANG
  M-RoPE safety;
- it did not exempt indexed native-MTP VL artifacts, even though
  `tests/test_native_mtp_autodetect.py` already proves those use the VLM path.

Fix:

- added `_is_native_mtp_qwen_vl_artifact_ready()` in the engine registry;
- plain affine-JANG Qwen VL still stays text-only;
- indexed native-MTP Qwen VL with real vision and MTP tensors now reports
  `is_mllm=True`;
- decode-speed row `qwen27_jang4m_mtp` now emits `--is-mllm`;
- panel local-path test pins the same policy across actual local DSV4, Qwen,
  Hy3, and Nemotron paths.

Red:

- panel focused test failed on `qwen27_jang4m_mtp`, expected text-only but
  detector returned multimodal;
- engine focused test
  `test_qwen36_affine_jang_native_mtp_vlm_uses_vlm_loader` failed because the
  engine registry returned `is_mllm=False`;
- model-family gate red:
  `build/current-model-family-detection-contract-20260522-panel-local-paths-red.json`
  -> missing only `panel_local_high_risk_rows_match_detector_policy`.

Green:

- engine focused guard:
  `.venv/bin/python -m pytest -q tests/test_model_config_registry.py::TestModelConfigs::test_qwen36_affine_jang_native_mtp_vlm_uses_vlm_loader tests/test_model_config_registry.py::TestModelConfigs::test_qwen36_affine_jang_vlm_stays_text_loader_until_mrope_fixed`
  -> `2 passed`;
- panel focused local-path guard:
  `cd panel && npx vitest run tests/model-config-registry.test.ts --testNamePattern "matches current local high-risk" --reporter=verbose`
  -> `1 passed / 53 skipped`;
- combined focused family rows:
  `.venv/bin/python -m pytest -q tests/test_model_config_registry.py::TestModelConfigs::test_qwen36_affine_jang_native_mtp_vlm_uses_vlm_loader tests/test_model_config_registry.py::TestModelConfigs::test_qwen36_affine_jang_vlm_stays_text_loader_until_mrope_fixed tests/test_model_family_detection_contract.py::test_decode_speed_local_high_risk_rows_match_current_engine_registry tests/test_model_family_detection_contract.py::test_decode_speed_gate_jang_only_rows_keep_text_mx_matmul_launch_policy tests/test_model_family_detection_contract.py::test_decode_speed_gate_artifact_format_coverage_matrix`
  -> `5 passed`;
- full model-family gate:
  `build/current-model-family-detection-contract-20260522-panel-local-paths.json`
  -> `status=pass`, `failed=[]`, `missing_rows=[]`, engine `43 passed`,
  panel `42 passed / 12 skipped`, launch wiring `6 passed / 228 skipped`.

This is a real policy alignment fix for native-MTP Qwen VL routing. It does
not add sampler forcing and does not claim live speed/generation clearance.

Follow-up packaging verification:

- first umbrella run exposed bundled Python drift after
  `vmlx_engine/model_config_registry.py` changed:
  `build/current-regression-suite-20260522-panel-local-paths.json`
  initially failed `packaged_integrity_contracts` and `release_gate_skip_app`;
- root cause was source/bundle hash mismatch for
  `vmlx_engine/model_config_registry.py`, not a model/runtime failure;
- reran `panel/scripts/bundle-python.sh` with clean JANG source:
  `/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools`;
- packaged integrity artifact:
  `build/current-packaged-integrity-contract-20260522-panel-local-paths.json`
  -> `status=pass`, `failed=[]`;
- umbrella artifact:
  `build/current-regression-suite-20260522-panel-local-paths.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

The bundled app source is now in parity with this checkout for this hardening
increment. The remaining DSV4 long-output/code quality row is still open.

## 2026-05-22 11:04 PDT - v1.5.48 Release Prep Built, Notary Blocked

Prepared a patch release rather than replacing already-published v1.5.47
assets:

- bumped source version triple to `1.5.48`:
  `pyproject.toml`, `panel/package.json`, `panel/package-lock.json`,
  `vmlx_engine/__init__.py`;
- added `CHANGELOG.md` entry for Qwen native-MTP VL parity, panel local-path
  coverage, output-cap default mutation guard, and post-release updater gate;
- confirmed `v1.5.48` was not already present on GitHub or PyPI before build.

Built local DMGs:

- `panel/release/vMLX-1.5.48-sequoia-arm64.dmg`
  - sha256: `8637edbdcb261729c8013878ef606643915661ddd6c46a368d952d620efe9d6d`
  - size: `453M`;
- `panel/release/vMLX-1.5.48-tahoe-arm64.dmg`
  - sha256: `79adfba392ca534266acfad080718d6a392204c9f1ee60b831698c57a4edfedc`
  - size: `468M`.

Build facts:

- both lanes used clean JANG source:
  `/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools`;
- bundled verifier passed for `vmlx_engine==1.5.48`, source hash parity,
  JANG source hash parity, console-script relocatability, and critical imports;
- Electron app in `panel/release/mac-arm64/vMLX.app` is Developer-ID signed and
  passed `codesign --verify --deep --strict`;
- electron-builder skipped automatic notarization because notarize options were
  unavailable.

Verification:

- packaged integrity:
  `build/current-packaged-integrity-contract-20260522-v1548-release-prep.json`
  -> `status=pass`, `failed=[]`;
- release-surface pre-release gate:
  `build/current-release-surface-contract-20260522-v1548-pre-release.json`
  -> `status=pass`, `staged_source_version_not_public=true`;
- release gate + release surface focused tests:
  `41 passed`;
- umbrella:
  `build/current-regression-suite-20260522-v1548-release-prep.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Blocker before public release:

- default/build keychain is locked for notary credentials;
- do not upload or update `latest.json` with the current DMGs until both DMGs
  are submitted to Apple notarization, accepted, stapled, and validated with
  Gatekeeper.

## 2026-05-22 09:05 PDT - Family Gate Requires ZAYA/Hy3/Qwen VL Profile Rows

Strengthened `run_model_family_detection_contract.py` so existing high-risk
panel registry tests are mandatory family rows, not incidental output.

New required rows:

- `zaya1_vl_jangtq_profiles_reasoning_policy`
- `hy3_jangtq_k_reasoning_policy`
- `qwen36_affine_jang_native_mtp_vl_video`

What they pin:

- ZAYA1-VL JANGTQ_K, JANGTQ2, and JANGTQ4 keep the `qwen3` reasoning rail,
  multimodal/VL classification, and typed CCA cache detection;
- Hy3 JANGTQ_K keeps the Hunyuan tool parser and qwen3 Low/High reasoning
  contract;
- affine-JANG Qwen native-MTP VL/video bundles stay multimodal when indexed
  MTP and vision tensors exist.

Red:

- family contract unit failed because the new required rows were absent;
- release manifest test failed because the model-family row did not list the
  new artifact or proof scope.

Green:

- family contract unit:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_family_detection_contract_pins_named_release_rows`
  -> `1 passed`;
- family detection gate:
  `build/current-model-family-detection-contract-20260522-zaya-hy3-qwen-vl-profile-rows.json`
  -> `status=pass`, `failed=[]`, `missing_rows=[]`;
- focused family/manifest tests:
  `61 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-zaya-hy3-qwen-vl-profile-rows.json`
  -> `18 rows`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-zaya-hy3-qwen-vl-profile-rows.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

This is static/no-heavy family and launch-policy proof. It does not claim live
multi-turn quality or DSV4 long-output/code clearance.

## 2026-05-22 09:11 PDT - Parser Gate Requires Non-Reasoning Boundaries

Strengthened `run_parser_registry_contract.py` so parser parity now requires
negative reasoning-rail checks, not only positive parser availability.

New required markers:

- `test_qwen2_must_not_have_reasoning`
- `test_qwen2_vl_must_not_have_reasoning`
- `test_gemma3_reasoning_parser`
- `test_glm_flash_vs_base_reasoning_parser_differs`

Why:

- The MiniMax regression was a positive parser mismatch. A second class of
  parser regression is accidental reasoning-parser attachment to models that
  should stream visible content without reasoning extraction.
- These rows pin Qwen2/Qwen2-VL, Gemma 3, and GLM base/Flash separation so
  parser cleanup cannot silently classify ordinary output as reasoning.

Red:

- parser contract unit failed because these markers were not required;
- release manifest parser row failed because it still pointed at the older
  parser artifact.

Green:

- parser contract unit:
  `.venv/bin/python -m pytest -q tests/test_parser_registry_contract.py`
  -> `2 passed`;
- parser registry gate:
  `build/current-parser-registry-contract-20260522-non-reasoning-boundaries.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`,
  engine `120 passed / 425 deselected`, panel `40 passed / 247 skipped`;
- focused parser/manifest tests:
  `39 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-non-reasoning-boundaries.json`
  -> `18 rows`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-non-reasoning-boundaries.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

No runtime behavior changed. This is release-proof tightening for parser rails.

## 2026-05-22 13:22 PDT - DSV4 Pool Env Gate Added After Speed/Spacing Trace

Root-cause read from current artifacts:

- DSV4 native prefix/paged/L2 replay with pool quant off is not the 2-3 tok/s
  path. The traced cache-hit tool round generated 83 tokens in 3.906s and
  showed `cache_detail=paged+dsv4`.
- DSV4 pool quant on remains too slow after the append-only JANG fix because
  `PoolQuantizedV4Cache.update_pool()` still returns `state["pooled"]`, and
  that getter dequantizes and concatenates the whole historical CSA/HCA pool
  on attention reads during decode.
- Raw stream spacing artifacts did not show whitespace corruption:
  `has_spacing_suspect=false` for both pool-off and pool-on stream probes.
  UI spacing corruption is therefore still a separate boundary until raw SSE
  vs renderer assembly is captured from the failing app session.
- Malformed DSML syntax/file-write quality remains open and happened with pool
  quant off in the default-cache tool loop (`tool_ciles`, `tool_ctools`,
  `inv` variants), so it must not be blamed only on pool quant.

Changes:

- Added `panel/src/shared/dsv4Env.ts` and `panel/tests/dsv4-env.test.ts` to
  the cache architecture gate source hashes.
- Required the panel marker proving an old saved `dsv4PoolQuant=true` session
  still launches with `DSV4_POOL_QUANT=0`.
- Updated the DSV4 env helper comment to match the real current bottleneck:
  append-only writes are fixed, but full historical pool dequant/concat on
  attention read remains too slow.
- Updated release manifest cache row to point at:
  `build/current-cache-architecture-contract-20260522-dsv4-pool-env-gate.json`.

Red:

- `tests/test_cache_architecture_contract.py` failed because the DSV4 env helper
  and panel env test were not hashed, and the pool-quant-disabled marker was
  not required.
- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_cache_architecture_with_runner_artifact`
  failed because the manifest did not list the new artifact/proof.

Green:

- `.venv/bin/python -m pytest -q tests/test_cache_architecture_contract.py`
  -> `2 passed`;
- cache architecture gate:
  `build/current-cache-architecture-contract-20260522-dsv4-pool-env-gate.json`
  -> `status=pass`, `missing_markers=[]`, cache-family `108 passed`,
  panel cache launch `88 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-dsv4-pool-env-gate.json`
  -> `18 rows`;
- umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-dsv4-pool-env-gate.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Keep `DSV4_POOL_QUANT=0` for production app launches.
- DSV4 native prefix/paged/L2 can remain a diagnostic opt-in path with pool
  quant off, but DSML tool syntax/file-write quality and DSV4 long-output/code
  quality are still separate open rows.

## 2026-05-22 13:31 PDT - Max Output/Context Proof Hashes API Gateway + DSV4 Budget Paths

Scope:

- Eric asked again to make sure server default max output, chat max output,
  Responses/Chat/API request output caps, context caps, gateway adapters, DSV4
  request budgeting, and UI settings cannot conflict or regress separately.
- This checkpoint adds proof coverage only. It does not change runtime defaults
  and does not introduce hidden sampler, repetition, cache, or max-token
  forcing.

Changes:

- `run_max_output_context_contract.py` now source-hashes:
  - `panel/src/main/api-gateway.ts`;
  - `panel/src/shared/dsv4RequestBudget.ts`;
  - `panel/tests/chat-settings-compatibility.test.ts`.
- `test_max_output_context_contract.py` requires those files so the public API
  gateway and DSV4 request budget stay in the max-output/context boundary gate.
- Release manifest now names:
  - `API gateway output-budget and context-budget paths are source-hashed`;
  - `DSV4 request-budget helper is source-hashed with the max-output boundary gate`;
  - `build/current-max-output-context-contract-20260522-gateway-dsv4-budget-hash.json`.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_server_chat_max_output_boundary`
  failed until the new proof text and artifact were added to the manifest.

Green:

- max-output/context gate:
  `build/current-max-output-context-contract-20260522-gateway-dsv4-budget-hash.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, engine/API
  `22 passed`, panel output/context wiring `43 passed`;
- focused contract/manifest tests -> `2 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-gateway-dsv4-budget-hash.json`
  -> `18 rows`;
- umbrella suite:
  `build/current-regression-suite-20260522-gateway-dsv4-budget-hash.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

## 2026-05-22 13:53 PDT - DSV4 Pool-On Speed And Live Write File Tool Loop

Root-cause split:

- DSV4 pool-on slowdown was in JANG `PoolQuantizedV4Cache`: reading
  `state["pooled"]` dequantized and concatenated every historical CSA/HCA pool
  segment on every attention read.
- The live `write_file` failure was separate: raw DSV4 output contained the
  correct DSML path/content in a degraded
  `<｜DSML｜inv><｜DSML｜name>write_file</｜DSML｜>` form, but the canonical
  encoder parse returned bogus `" string="` argument values and blocked the
  regex repair path.

Changes:

- JANG commit pushed:
  `/Users/eric/jang/jang-tools` at
  `b5f66a7 fix: cache materialized dsv4 pool reads`.
- JANG pool cache now appends only newly produced quantized pool rows, reuses
  a materialized pooled view between appends, and includes that materialized
  live pool in `nbytes`.
- vMLX `DSMLToolParser` now repairs degraded named-invoke DSML and short DSML
  parameter close tags schema-safely.
- `run_cache_architecture_contract.py` now prepends
  `VMLX_JANG_TOOLS_SOURCE` / `VMLINUX_JANG_TOOLS_SOURCE` to child
  `PYTHONPATH`, so the cache gate cannot silently test installed stale
  `jang_tools` while a clean source path was requested.
- Release manifest now tracks:
  - `build/current-cache-architecture-contract-20260522-dsv4-pool-materialized-cache.json`;
  - `build/current-tool-call-contract-20260522-dsv4-live-write-file-repair.json`;
  - `build/current-dsv4-default-cache-tool-loop-poolon-materialized-parserfix-20260522/result.json`.

Green:

- JANG pool tests -> `3 passed`;
- focused vMLX DSV4 pool tests -> `2 passed`;
- cache architecture:
  `build/current-cache-architecture-contract-20260522-dsv4-pool-materialized-cache.json`
  -> `status=pass`, cache-family `109 passed`, panel `88 passed`;
- tool-call contract:
  `build/current-tool-call-contract-20260522-dsv4-live-write-file-repair.json`
  -> `status=pass`, engine DSML/tool `22 passed`, panel tool loop/security
  `11 passed`;
- live DSV4 default-cache pool-on tool loop:
  `build/current-dsv4-default-cache-tool-loop-poolon-materialized-parserfix-20260522/result.json`
  -> `status=pass`;
- packaged integrity after rebundling Python from clean JANG source:
  `build/current-packaged-integrity-contract-20260522-dsv4-pool-parserfix.json`
  -> `status=pass`;
- umbrella:
  `build/current-regression-suite-20260522-dsv4-pool-parserfix-bundled.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Live DSV4 evidence:

- `DSV4_POOL_QUANT=1`;
- native prefix/paged/L2 true;
- generic TQ KV off;
- cached tokens and `cache_detail=paged+dsv4` seen;
- ordered tool loop: `list_directory -> write_file -> DONE`;
- `write_file` args parsed correctly:
  `landing-p/proof.html`,
  `<html><body>dsv4-default-cache-tool-ok</body></html>`;
- round 1 generated 83 output tokens in 4.573s, about 18.2 tok/s.

Remaining limitation:

- This clears DSV4 default-cache/pool-on multi-tool execution and the pool-on
  speed regression. It does not clear the separate DSV4 long-output/code/file
  generation quality row.

## 2026-05-22 14:02 PDT - DSV4 Pool Quant App/UI Toggle Wired

Root-cause follow-up:

- The JANG materialized-pool fix made `DSV4_POOL_QUANT=1` viable again, but the
  panel still forced explicit `dsv4PoolQuant=true` to `DSV4_POOL_QUANT=0`.
- The settings UI also still displayed DSV4 Pool Quantization as a disabled,
  rejected option with stale full-pool dequant/concat language.

Changes:

- `dsv4EnvFromConfig()` now emits `DSV4_POOL_QUANT=1` only when
  `config.dsv4PoolQuant === true`.
- DSV4 family startup defaults initialize missing pool quant to false but
  preserve explicit true.
- The UI toggle is enabled and documents the materialized CSA/HCA pool reuse
  path.
- Generic TurboQuant KV remains suppressed for DSV4 native composite cache.
- No sampler, repetition, max-output, cache, or behavior forcing was added.

Red:

- `panel/tests/dsv4-env.test.ts` and `panel/tests/settings-flow.test.ts`
  failed because explicit pool quant still mapped to `0`, the UI was disabled,
  and sessions still cleared explicit true.
- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_cache_architecture_with_runner_artifact`
  failed until the release manifest named the new explicit app-wiring proof.

Green:

- panel focused tests:
  `npx vitest run tests/dsv4-env.test.ts tests/settings-flow.test.ts --reporter=verbose -t 'Dsv4Env|DSV4|deepseek-v4 family defaults'`
  -> `21 passed`;
- `tests/test_cache_architecture_contract.py` -> `2 passed`;
- cache architecture:
  `build/current-cache-architecture-contract-20260522-dsv4-pool-ui-wired.json`
  -> `status=pass`, cache-family `109 passed`, panel `88 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-dsv4-pool-ui-wired.json`
  -> `18 rows`;
- umbrella:
  `build/current-regression-suite-20260522-dsv4-pool-ui-wired.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- DSV4 native prefix/paged/L2 plus pool quant now has both runtime
  materialized-pool proof and app/UI env proof.
- The remaining release blocker is still the separate DSV4 long-output/code/file
  generation quality row.

## 2026-05-22 14:12 PDT - Casual Preset Server Output Cap Edge Gated

Scope:

- Eric flagged a specific risk that separate chat output caps could conflict
  with the server Max Output Tokens setting.
- The server/API request-resolution tests already cover explicit request caps
  below/above startup defaults, omitted Auto requests, legacy completions,
  Responses, Anthropic, Ollama, and mutation resistance.
- The weak edge was UI/preset wording: Casual mode intentionally sets
  `maxTokens=8192`, but the source comment still described that as preventing
  huge KV allocation, which blurs output length with context/cache behavior.

Changes:

- Added panel test marker:
  `casual preset maxTokens uses an explicit server output cap without changing model-owned defaults or context`.
- Changed the Casual preset comment to:
  `Explicit server output cap; limits runaway long replies without changing context.`
- Added the marker to `run_max_output_context_contract.py`.
- Updated the release manifest to track:
  `build/current-max-output-context-contract-20260522-casual-server-output-cap.json`.

Green:

- focused red/green panel test:
  `npx vitest run tests/settings-flow.test.ts --reporter=verbose -t 'casual preset maxTokens uses an explicit server output cap'`
  -> `1 passed`;
- max-output/context gate:
  `build/current-max-output-context-contract-20260522-casual-server-output-cap.json`
  -> `status=pass`, engine `22 passed`, panel `45 passed`,
  `missing_markers=[]`;
- release manifest:
  `build/current-release-regression-manifest-20260522-casual-server-output-cap.json`
  -> `18 rows`;
- umbrella:
  `build/current-regression-suite-20260522-casual-server-output-cap.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- No runtime default changed.
- Server Max Output Tokens, chat/API output caps, and Max Context Tokens remain
  separate in the gated proof.

## 2026-05-22 14:47 PDT - DSV4 Short-Prompt Prefix/Pool Speed Split

Scope:

- Eric reported DSV4 Flash around 2-3 tok/s and suspected prefix cache, pool
  quant, TurboQuant, or spacing corruption.
- The investigation separated raw stream spacing, pool quant, DSV4 prefix-cache
  snapshot/store, and cold compile/warmup.

Findings:

- Pool quant is not the current steady-state slowdown:
  - rebuilt repo-local packaged app now bundles the fixed JANG
    `dsv4/pool_quant_cache.py`;
  - source-hash integrity passes for both `scheduler.py` and
    `dsv4/pool_quant_cache.py`;
  - packaged pool-on and pool-off non-stream short cold requests were
    effectively identical, around 3.55 tok/s.
- Raw API/SSE spacing is not currently proven broken:
  - fresh pool-on/off stream captures had `has_spacing_suspect=false`;
  - do not change renderer spacing without a raw-stream-vs-UI diff.
- DSV4 prefix is diagnostic opt-in:
  - without `--dsv4-enable-prefix-cache`, there is no prompt snapshot at all;
  - with prefix explicitly enabled, short prompts now skip the synchronous
    composite prompt snapshot.
- Live timing with prefix+pool enabled:
  - first request is cold compile/warmup dominated:
    `prefill_head` about 14s and first `sample_materialize` about 7.5s;
  - second same request on the same server is back around 20.9 tok/s.

Changes:

- `vmlx_engine/utils/dsv4_batch_generator.py`
  - added `DEFAULT_DSV4_PROMPT_SNAPSHOT_MIN_TOKENS = 256`;
  - added `dsv4_prompt_snapshot_min_tokens()`;
  - DSV4 N-1 prompt keys below the threshold skip synchronous prompt-boundary
    snapshot;
  - override is available via `DSV4_PROMPT_SNAPSHOT_MIN_TOKENS` or legacy
    `VMLINUX_DSV4_PROMPT_SNAPSHOT_MIN_TOKENS`.
- `vmlx_engine/scheduler.py`
  - when a DSV4 short prompt skipped snapshot, cleanup skips donating a prefix
    block instead of immediately doing a synchronous clean prompt-only re-prefill
    store.
- `tests/cross_matrix/release_regression_manifest.py`
  - now tracks the short-prompt threshold proof and live two-turn DSV4 proof.

Red:

- `test_dsv4_generator_skips_prompt_snapshot_for_short_cache_store_prompt_by_default`
  failed on current code because every 2+ token prompt captured a snapshot.
- `test_dsv4_short_prompt_snapshot_skip_does_not_sync_reprefill_for_store`
  failed until scheduler cleanup knew about the same threshold.

Green:

- focused snapshot tests:
  `tests/test_dsv4_paged_cache.py -k 'prompt_snapshot or short_prompt_snapshot'`
  -> `4 passed`;
- full DSV4 paged/cache suite with fixed JANG source:
  `PYTHONPATH=/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools .venv/bin/python -m pytest -q tests/test_dsv4_paged_cache.py`
  -> `53 passed`;
- cache architecture gate:
  `build/current-cache-architecture-contract-20260522-dsv4-short-snapshot-threshold.json`
  -> `status=pass`, cache-family `111 passed`, panel cache launch `88 passed`;
- live DSV4 proof:
  `build/current-dsv4-prefix-enabled-two-turn-threshold-live-20260522.json`
  -> first request 32 tokens in 23.36s, second same request 32 tokens in 1.53s
  (~20.9 tok/s), `prompt_snapshot_skipped=true`,
  `has_short_store_skip=true`.

Environment caveat:

- The repo `.venv` still imports stale installed `jang_tools`; without fixed
  JANG on `PYTHONPATH`, the materialized-pool test fails.
- Packaged dev app was rebuilt with the clean fixed JANG worktree and passed
  packaged source-hash integrity.
- Direct isolated packaged behavior check passed from `/tmp`:
  `dequant_count=0`, `pool_shape=(1, 4, 16)`, and `nbytes_ok=True`.
- Source test runs must use the same JANG path or reinstall the venv dependency
  before treating a pool test failure as a runtime regression.

Release read:

- DSV4 prefix+pool steady behavior is now split from cold compile/warmup and
  has a live second-turn speed proof near the expected 20 tok/s.
- DSV4 first cold request latency is still open as a warmup/compile issue.
- DSV4 long-output/code/file-generation quality remains the release blocker.

## 2026-05-22 15:03 PDT - Cross-Family Output/Cache/MTP Recheck

Scope:

- Eric specifically worried that separate chat/API Max Output Tokens could
  interfere with Server Settings Max Output Tokens.
- The same pass rechecked family detection, parser/modality policy, MTP, API
  request building, DSV4 native cache/pool policy, generic TurboQuant KV
  suppression, hybrid/MLA/media cache contracts, and panel launch settings.

Max output/context evidence:

- `build/current-max-output-context-contract-20260522-recheck-chat-server-boundary.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`.
- Engine output/context resolution:
  - `22 passed`;
  - covers Chat Completions, Responses, legacy Completions, Anthropic, Ollama,
    startup defaults, explicit request caps above/below startup default, and
    request caps not mutating later omitted defaults.
- Panel output/context wiring:
  - `45 passed`, `295 skipped`;
  - covers settings UI separation, stale session migration, chat switching,
    invalid maxTokens omission, chat override persistence, and coding tool
    output-limit vs context fallback separation.

Cross-family evidence:

- `build/current-model-family-detection-contract-20260522-recheck-families.json`
  -> `status=pass`, engine `44 passed`, panel `43 passed`, launch `6 passed`.
- `build/current-native-mtp-contract-20260522-recheck.json`
  -> `status=pass`, engine `116 passed`, panel controls `13 passed`, panel
  detection `6 passed`.
- `build/current-api-surface-contract-20260522-recheck-output-cache.json`
  -> `status=pass`, server API `25 passed`, panel request builders
  `72 passed`.
- `build/current-cache-architecture-contract-20260522-recheck-family-cache.json`
  -> `status=pass`, cache family `111 passed`, panel cache launch
  `88 passed`.

Release manifest and umbrella:

- `build/current-release-regression-manifest-20260522-recheck-dsv4-threshold-output-boundary.json`
  -> `rows=18`.
- `build/current-regression-suite-20260522-recheck-dsv4-threshold-output-boundary.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- No-heavy compatibility is currently green for JANG/JANGTQ/MXFP4/MXFP8
  detection, DSV4 native cache/pool policy, Qwen 3.6 alias/MTP/VL/video rows,
  ZAYA, Ling, Nemotron, parser/modality launch policy, and API
  output/context boundaries.
- This does not clear the remaining live DSV4 long-output/code quality row.

## 2026-05-22 15:08 PDT - Parser And Tool Parity Recheck

Scope:

- Rechecked the prior MiniMax-style failure mode where panel auto-detection
  emitted a parser value the engine CLI did not accept.
- Rechecked DSV4 DSML parser repair/residue rejection because the DSV4 tool
  loop issue sits next to parser registry and Responses/tool-call assembly.

Evidence:

- `build/current-parser-registry-contract-20260522-recheck-parser-parity.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`;
  - engine parser registry: `121 passed`;
  - panel parser registry/dropdown/launch parity: `41 passed`.
- `build/current-tool-call-contract-20260522-recheck-parser-dsv4.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`;
  - DSV4 DSML/tool parser contracts: `22 passed`;
  - panel tool-loop/security contracts: `11 passed`.

Release read:

- Panel-emitted reasoning/tool parsers remain registered and CLI-accepted by
  the engine at no-heavy contract level.
- DSV4 DSML repair/residue rejection remains green at no-heavy contract level.
- This does not clear the remaining live DSV4 long-output/code quality row.

## 2026-05-22 15:15 PDT - Artifact Format And Decode-Speed Matrix Recheck

Scope:

- Rechecked the artifact-format and speed-matrix metadata for the families Eric
  called out: generic JANG/JANGTQ/MXTQ, DSV4, MXFP4/MXFP8, plain MLX 4bit,
  Qwen 3.6 VL/video/native-MTP rows, Ling/Bailing hybrid, Nemotron
  Omni/Nano/Nemotron3, Mistral, GPT-OSS, and ZAYA/ZAYA-VL policy edges.

Evidence:

- `build/current-model-artifact-format-contract-20260522-recheck-jang-mxfp.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`;
  - `model_artifact_format_pytest`: `132 passed`, `174 deselected`.
- `.venv/bin/python -m pytest -q -vv tests/test_model_family_detection_contract.py -k 'decode_speed_gate'`
  -> `17 passed`, `8 deselected`.

What this proves at no-heavy level:

- affine JANG is accepted by the JANG loader instead of being misclassified as
  JANGTQ/MXFP/plain MLX;
- JANGTQ/MXTQ mixed routed-bit metadata stays represented;
- MXFP4/MXFP8 VLM loader paths use declared quantization mode;
- plain MLX Qwen 3.6 4bit rows keep hybrid cache without JANG/MXFP inference;
- DSV4 dropped/no-runtime MTP state is explicit;
- native MTP detection is weight-index based, not path-name based;
- Ling/Bailing hybrid shape/MTP/MLA repairs remain covered;
- decode-speed rows keep JANG-only MX affine matmul text-only policy;
- decode-speed rows keep JANG, JANGTQ/MXTQ, plain MLX 4bit, MXFP4, and MXFP8
  thresholds and rows distinct;
- decode-speed rows declare registered/CLI-accepted parsers and preserve row
  parser/modality command policy;
- decode-speed health checks reject DSV4/ZAYA native-cache health for plain KV
  JANG/JANGTQ/MXFP rows.

Release read:

- This strengthens the no-heavy model-family compatibility ledger.
- It does not claim live speed for every row.
- It does not clear the remaining live DSV4 long-output/code quality row.

## 2026-05-22 15:11 PDT - Defaults, Reasoning Rails, And API Endpoint Assembly Recheck

Scope:

- Rechecked Eric's concern that no fix should secretly force sampler values,
  repetition floors, reasoning rails, or output caps while we are hardening max
  output/context, parser, Responses, and tool/cache paths.
- Updated the release-regression manifest so the durable rows point at current
  2026-05-22 recheck artifacts for generation defaults, reasoning/template
  rails, and API endpoint assembly instead of relying only on older artifact
  names.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a manifest guard requiring current generation-defaults,
    reasoning/template, and API-surface recheck artifacts.
- `tests/cross_matrix/release_regression_manifest.py`
  - generation defaults row now names the current no-hidden-forcing artifact
    and explicitly proves bundle `max_new_tokens`, request-scoped output caps,
    and no hidden sampler/repetition floor behavior;
  - reasoning/template row now names the current parser-rails artifact and
    explicitly proves DSV4 requested rails, MiniMax/Ling boundaries, and
    tool-followup reasoning reset behavior;
  - API surface row now names the current endpoint-assembly artifact and
    explicitly proves named server cache/DSV4 parser surfaces plus invalid
    persisted `maxTokens` omission in panel request builders.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_defaults_reasoning_api_rechecks`
  failed until the manifest named the current artifacts and edge-case text.

Green:

- generation defaults:
  `build/current-generation-defaults-contract-20260522-recheck-no-hidden-forcing.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, panel `13 passed`,
  engine `37 passed`;
- reasoning/template:
  `build/current-reasoning-template-contract-20260522-recheck-parser-rails.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, engine `126 passed`,
  panel `108 passed`;
- API surface:
  `build/current-api-surface-contract-20260522-recheck-endpoint-assembly.json`
  -> `status=pass`, no missing nested checks/markers/panel markers, server API
  `25 passed`, panel request builders `72 passed`;
- focused manifest tests:
  `tests/test_release_regression_manifest.py::{generation_defaults,reasoning_template,api_surface,current_defaults_reasoning_api_rechecks}`
  -> `4 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-defaults-reasoning-api.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-defaults-reasoning-api.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Current no-heavy proof now ties together model-owned generation defaults,
  explicit per-request output caps, reasoning/parser rails, Responses/Chat/API
  assembly, invalid persisted `maxTokens` omission, and DSV4 tool/cache surface
  naming.
- No runtime behavior changed in this slice.
- DSV4 long-output/code/file-generation quality remains the only open
  requirement in the umbrella suite.

## 2026-05-22 15:28 PDT - Packaged Integrity Recheck Pinned

Scope:

- Rechecked packaged-runtime integrity after the DSV4 materialized-pool JANG
  fix and the v1.5.48 local release prep work.
- This specifically guards against calling DSV4 pool/prefix behavior fixed in
  source while the bundled Python app still imports stale `jang_tools`.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a guard requiring the current packaged-integrity artifact and the
    clean JANG source path used for source-hash parity.
- `tests/cross_matrix/release_regression_manifest.py`
  - packaged-release-integrity now names
    `build/current-packaged-integrity-contract-20260522-recheck-bundled-release-gate.json`;
  - the row explicitly proves clean JANG source parity, critical bundled
    `jang_tools` file hash parity, relocatable console-script shebangs, and
    dry release-gate failure only on the known DSV4 objective row.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_packaged_integrity_recheck`
  failed until the manifest named the current packaged-integrity artifact and
  bundled-source edge cases.

Green:

- packaged integrity:
  `build/current-packaged-integrity-contract-20260522-recheck-bundled-release-gate.json`
  -> `status=pass`, `failed=[]`;
- packaged subchecks:
  - release gate unit contracts: `36 passed`;
  - bundled Python verifier: `rc=0`;
  - dry release gate with app build skipped: expected `rc=1` because the only
    open requirement is DSV4 long-output/code/file-generation quality;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-packaged-integrity.json`
  -> `18 rows`;
- focused tests:
  `tests/test_release_regression_manifest.py::{packaged_integrity_with_runner_artifact,current_packaged_integrity_recheck}` plus
  `tests/test_packaged_integrity_contract.py`
  -> `4 passed`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-packaged-integrity.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- DSV4 native prefix/paged/L2 plus pool quant has source, panel/env, live
  pool-on tool-loop, and packaged-source-parity coverage.
- Default app policy remains conservative: DSV4 native composite prefix cache
  is diagnostic/opt-in, and DSV4 pool quant defaults off unless explicitly
  enabled.
- This does not clear the separate DSV4 long-output/code/file-generation
  quality row.

## 2026-05-22 15:34 PDT - Server/Chat Output Compatibility Recheck Pinned

Scope:

- Rechecked Eric's specific concern that a separate per-chat/API Max Output
  Tokens override could conflict with Server Settings Max Output Tokens.
- Inspected the current gate before editing: it already covers Chat
  Completions, Responses, legacy Completions, Anthropic, Ollama, panel request
  builders, chat override persistence, session launch args, stale `32768`
  migration, wake/reload explicitness, and DSV4 request-budget paths.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a red-first guard requiring the current server/chat output
    compatibility artifact and explicit edge-case text.
- `tests/cross_matrix/release_regression_manifest.py`
  - updated the max-output/context row to point at
    `build/current-max-output-context-contract-20260522-recheck-server-chat-output-compat.json`;
  - explicitly names the above/below server-default override cases, later Auto
    request default preservation, and wake/reload plus CLI startup explicitness.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_server_chat_output_compat_recheck`
  failed until the release manifest named the current artifact and edge-case
  proof text.

Green:

- max-output/context contract:
  `build/current-max-output-context-contract-20260522-recheck-server-chat-output-compat.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, all `checks` true,
  engine `22 passed`, panel `45 passed / 295 skipped`;
- focused manifest/contract tests:
  `tests/test_release_regression_manifest.py::{max_output_context_with_runner_artifact,current_server_chat_output_compat_recheck}` plus
  `tests/test_max_output_context_contract.py`
  -> `3 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-server-chat-output-compat.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-server-chat-output-compat.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Server Max Output Tokens remains an omitted-request startup default.
- Explicit Chat/Responses output caps remain per-request overrides and can be
  lower or higher than that server default.
- Later Auto Chat/Responses requests still use the original server startup
  default; request overrides do not mutate it.
- Max Context Tokens remains prompt/context-only and maps separately.
- This does not clear the separate DSV4 long-output/code/file-generation
  quality row.

## 2026-05-22 15:39 PDT - JANG/MXFP/MTP Loader Recheck Pinned

Scope:

- Rechecked the no-heavy artifact-format gate for the loader/autodetect
  families Eric called out: JANG, JANGTQ/MXTQ, MXFP4, MXFP8, plain MLX 4bit,
  Ling/Bailing hybrid repairs, dropped/preserved MTP, and native-MTP
  detection from real indexed weights.
- This is source/static loader and registry coverage. It does not load model
  weights or claim live output quality.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a red-first guard requiring the current JANG/MXFP/MTP loader artifact
    and explicit edge-case proof text.
- `tests/cross_matrix/release_regression_manifest.py`
  - model-artifact-format row now points at
    `build/current-model-artifact-format-contract-20260522-recheck-jang-mxfp-mtp-loaders.json`;
  - explicitly names JANGTQ_K mixed routed-bit `gather_dn`, Ling/Bailing
    `switch_mlp` repair/no-op, Qwen plain MLX 4bit separation, and native-MTP
    indexed-weight detection.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_jang_mxfp_mtp_loader_recheck`
  failed until the release manifest named the current artifact and edge-case
  proof text.

Green:

- model artifact format:
  `build/current-model-artifact-format-contract-20260522-recheck-jang-mxfp-mtp-loaders.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, checks all true,
  `132 passed / 174 deselected`;
- focused manifest/contract tests:
  `tests/test_release_regression_manifest.py::{current_jang_mxfp_mtp_loader_recheck,model_artifact_detection_with_runner_artifact,mxfp_vlm_loader_quant_mode,affine_jang_loader_acceptance}` plus
  `tests/test_model_artifact_format_contract.py`
  -> `5 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-jang-mxfp-mtp-loaders.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-jang-mxfp-mtp-loaders.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- JANG/JANGTQ/MXTQ, MXFP4/8, plain MLX 4bit, and native-MTP loader
  classification are pinned to current source and cannot silently fall back to
  path-name-only detection.
- Ling/Bailing 2D/3D hybrid shape handling remains covered.
- DSV4 long-output/code/file-generation quality remains separate and open.

## 2026-05-22 15:45 PDT - Model-Family Launch Policy Matrix Recheck Pinned

Scope:

- Rechecked the full no-heavy model-family launch-policy matrix after the
  loader/artifact slice.
- The current gate runs three layers together:
  engine family detection, panel family detection, and panel session launch
  wiring.
- This targets the compatibility concerns around ZAYA/ZAYA1-VL, Ling/Bailing,
  Nemotron-H, Qwen 3.6 VL/video/hybrid/MXFP/MTP, MiniMax, Hy3, and DSV4 stale
  launch flags.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a red-first guard requiring the current family launch-policy artifact
    and explicit edge-case proof text.
- `tests/cross_matrix/release_regression_manifest.py`
  - model-family row now points at
    `build/current-model-family-detection-contract-20260522-recheck-launch-policy-matrix.json`;
  - explicitly records that engine, panel, and session launch wiring run in
    the same matrix;
  - explicitly names aligned parser/cache/modality policy and DSV4 stale
    `additionalArgs`/native-MTP D3 suppression.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_family_launch_policy_recheck`
  failed until the manifest named the current artifact and edge-case proof
  text.

Green:

- model-family detection:
  `build/current-model-family-detection-contract-20260522-recheck-launch-policy-matrix.json`
  -> `status=pass`, `failed=[]`, `missing_rows=[]`, engine
  `44 passed / 112 deselected`, panel `43 passed / 12 skipped`, launch wiring
  `6 passed / 230 skipped`;
- focused manifest/family tests:
  `tests/test_release_regression_manifest.py::{current_family_launch_policy_recheck,named_model_family_detection_with_runner_artifact,panel_family_launch_wiring,qwen_nemotron_hybrid_cache_rows}` plus
  `tests/test_model_family_detection_contract.py`
  -> `29 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-family-launch-policy.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-family-launch-policy.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Engine, panel, and launch builder policy are aligned for the high-risk
  families covered by this no-heavy gate.
- Session launch still strips stale DSV4 `additionalArgs` and preserves
  native-MTP D3 only where supported.
- This is source/static/launch-policy proof only. It does not replace the live
  multi-turn family soak or the DSV4 long-output/code quality row.

## 2026-05-22 15:16 PDT - MCP And VL/Media Recheck Pinned

Scope:

- Rechecked the user-called-out MCP, Qwen VL/video, ZAYA-VL, Nemotron stale
  Omni, hybrid SSM, video-tool, and media follow-up surfaces against current
  code.
- Updated the release-regression manifest so these rows point at current
  2026-05-22 artifacts and explicitly name the edge cases instead of relying
  only on older proof names.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a guard requiring current MCP and VL/media recheck artifacts and
    edge-case text.
- `tests/cross_matrix/release_regression_manifest.py`
  - MCP row now names current UI/gateway artifact and explicitly proves
    `mcp.json/jsonc` import, redaction, explicit model routing, ambiguous
    multi-session rejection, and built-in tool separation;
  - VL/media row now names current Qwen/ZAYA/media artifact and explicitly
    proves Qwen3.6 indexed-MTP VL routing, MXTQ/JANGTQ and MXFP4/MXFP8 Qwen
    VLM policy, hybrid SSM companion/deferred rederive/TQ suppression, and
    `read_video`/image-video tool-result follow-up behavior.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_mcp_and_vl_media_rechecks`
  failed until the manifest named the current artifacts and edge-case text.

Green:

- MCP:
  `build/current-mcp-policy-contract-20260522-recheck-ui-gateway.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`, engine `76 passed`,
  panel `13 passed`, `3 skipped`;
- VL/media:
  `build/current-vl-media-cache-contract-20260522-recheck-qwen-zaya-media.json`
  -> `status=pass`, `failed=[]`, no missing engine/panel markers, engine
  `44 passed`, `6 skipped`, `692 deselected`, panel media `12 passed`, panel
  VLM settings `11 passed`, `225 skipped`, panel VLM family detection
  `13 passed`, `42 skipped`;
- focused manifest tests:
  `tests/test_release_regression_manifest.py::{mcp_with_runner_artifact,vl_media_with_runner_artifact,current_mcp_and_vl_media_rechecks}`
  -> `3 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-mcp-vl-media.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-mcp-vl-media.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Current no-heavy proof now pins MCP import/routing/security and the
  Qwen/ZAYA/Nemotron/VL/video/media-cache/tool-follow-up edges in the durable
  release manifest.
- No runtime behavior changed in this slice.
- These checks are source/static and panel-contract coverage; they do not claim
  live video/Omni/VLM output quality.
- DSV4 long-output/code/file-generation quality remains the only open
  requirement in the umbrella suite.

## 2026-05-22 15:22 PDT - Updater Surface And Update Notice I18n Recheck Pinned

Scope:

- Rechecked the release-updater and "What's New" surfaces Eric called out:
  `latest.json`, source version parity, post-release updater completeness,
  and localized release notice copy mentioning MCP/MTP/cache/release-critical
  items.
- Updated the release-regression manifest so those current 2026-05-22 artifacts
  are named directly instead of relying only on older proof names.

Changes:

- `tests/test_release_regression_manifest.py`
  - added a guard requiring current updater and i18n/update-notice recheck
    artifacts and edge-case text.
- `tests/cross_matrix/release_regression_manifest.py`
  - panel/settings row now names the current update-notice/i18n artifact and
    explicitly proves all five locales mention MCP, MTP, `latest.json`,
    Developer ID, L2 disk cache, and `max_tokens`;
  - release-surface row now names the current updater artifact and explicitly
    proves source version parity plus complete post-release updater handling.

Red:

- `tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_current_updater_and_i18n_rechecks`
  failed until the manifest named the current artifacts and edge-case text.

Green:

- release surface:
  `build/current-release-surface-contract-20260522-recheck-updater-i18n.json`
  -> `status=pass`; source versions are `1.5.48` in `pyproject.toml` and
  `panel/package.json`; local `latest.json` is also `1.5.48` and the local
  updater checks are valid;
- panel settings / i18n:
  `build/current-panel-settings-contract-proof-20260522-recheck-update-notice-i18n.json`
  -> `status=pass`, `missing_source_markers=[]`, panel settings/i18n
  `286 passed`, panel typecheck `rc=0`, panel model registry `55 passed`,
  engine model registry `131 passed`;
- focused manifest tests:
  `tests/test_release_regression_manifest.py::{public_release_surface_preflight,panel_cache_family_gating,current_updater_and_i18n_rechecks}`
  -> `3 passed`;
- release manifest:
  `build/current-release-regression-manifest-20260522-recheck-updater-i18n.json`
  -> `18 rows`;
- umbrella with fixed JANG source:
  `build/current-regression-suite-20260522-recheck-updater-i18n.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly:
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- Current no-heavy proof now pins `latest.json`/source-version consistency and
  the localized "What's New" release notice in the durable release manifest.
- No runtime behavior changed in this slice.
- The release surface check is local-state only; public GitHub/PyPI/update-feed
  checks remain explicit operator checks before publishing.
- DSV4 long-output/code/file-generation quality remains the only open
  requirement in the umbrella suite.

## 2026-05-22 15:58 PDT - Qwen JANG_4M Live Speed/Cache Split

Scope:

- Followed up on the JANG-only MX matmul speed row with a real packaged-engine
  run for `qwen27_jang4m`.
- Model path:
  `/Users/eric/models/dealign.ai/Qwen3.6-27B-JANG_4M-CRACK`.

Artifact:

- `build/current-decode-speed-live-qwen27-jang4m-20260522-hybrid-tq-review.json`

Findings:

- The earlier live `fail` was partly a stale harness invariant. Qwen3.6
  hybrid/path-dependent cache intentionally keeps live TurboQuant active for
  attention KV layers only, while SSM/GatedDelta companion state remains native
  full precision.
- DSV4 and ZAYA still reject generic TurboQuant KV.
- Red/green guard:
  `tests/test_model_family_detection_contract.py::test_decode_speed_gate_detects_cache_health_mismatches`
  now accepts only the Qwen attention-only health shape and still rejects
  unsafe generic hybrid SSM TQ for non-Qwen rows.
- Fresh live row is `status=review`, not pass:
  - bundle decode: `25.76 tok/s`, above the row's `18 tok/s` decode floor;
  - coherency row: `19.47 tok/s`, no reasoning and no loopish output;
  - PP rows remain below the current `600 tok/s` floor:
    `283.95`, `289.03`, `251.06 tok/s`.
- The release manifest now has a live `performance` row named
  `qwen-jang-mx-live-speed-review` so broad JANG/MX speed claims cannot hide
  this PP review state.

Release read:

- This does not change runtime behavior.
- Qwen/JANG cache wiring is better represented in the gate.
- Qwen/JANG live decode is not the DSV4 2-3 tok/s decode issue, but its
  prefill speed is still under the current target and should remain review.

## 2026-05-22 16:14 PDT - SingleBatch Prefill Keep-Alloc Wiring

Scope:

- Followed up on the Qwen/JANG PP review row by checking the explicit
  prefill allocator reuse flag from PR #163.
- Root cause found: the existing `--prefill-keep-alloc` flag reached the
  environment, but only the MLLM batch generator honored it. The
  `qwen27_jang4m` speed row runs `SingleBatchGenerator` because
  `max_num_seqs=1`, so single-sequence JANG rows still cleared the allocator
  cache after every prefill chunk.

Change:

- `SingleBatchGenerator._prefill()` now honors
  `VMLINUX_PREFILL_KEEP_ALLOC=1` / `VMLX_PREFILL_KEEP_ALLOC=1`.
- Default behavior is unchanged: if the env/CLI flag is omitted, the prefill
  loop still calls `mx.clear_cache()` after each chunk.
- This is not a hidden sampler, max-token, cache-policy, or generation-default
  change.

Source proof:

- Red/green guard:
  `tests/test_perf_prefill_loop.py::test_single_batch_prefill_loop_env_gates_clear_cache`
  failed before the source change and passes after it.
- Harness guard:
  `tests/test_model_family_detection_contract.py::test_decode_speed_gate_extra_serve_arg_is_opt_in_without_mutating_row_defaults`
  failed red before `row_with_extra_serve_args()` existed, then passed after
  adding an explicit `--serve-extra-arg=...` harness path.
- Source live Qwen run with explicit `--prefill-keep-alloc`:
  `build/current-decode-speed-live-qwen27-jang4m-source-keepalloc-20260522.json`
  -> `status=pass`, decode `22.87 tok/s`, no notes.

Release read:

- This proves the source single-batch path now honors the explicit keep-alloc
  flag. It does not prove the currently packaged app has absorbed the source
  change until bundled Python is rebuilt and parity-checked.
- It does not clear the earlier packaged Qwen PP review row because the source
  artifact did not record the same PP measurements. Keep the release manifest
  row in review.
- Fresh max-output/context contract after this change:
  `build/current-max-output-context-contract-20260522-after-singlebatch-keepalloc.json`
  -> `status=pass`, `failed=[]`, `missing_markers=[]`. This rechecks the
  server startup max-output default vs per-chat/API output-cap edge cases after
  the prefill change.
- Fresh model-family detection contract after this change:
  `build/current-model-family-detection-contract-20260522-singlebatch-keepalloc.json`
  -> `status=pass`, `failed=[]`, `missing_rows=[]`.
- Fresh umbrella suite with clean JANG source:
  `build/current-regression-suite-20260522-singlebatch-keepalloc.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly
  `DSV4 long-output/code/file-generation quality is release-cleared`.
- DSV4 long-output/code/file-generation quality remains open.

## 2026-05-22 16:26 PDT - Bundled SingleBatch Hash Parity Gate

Scope:

- Closed the packaging gap left by the source `SingleBatchGenerator` fix.
- The existing bundled-source parity gates covered `mllm_batch_generator.py`
  but not `utils/single_batch_generator.py`, so a release build could have
  carried stale single-batch prefill behavior while still passing the older
  verifier.

Red failure:

- `tests/test_release_gate_python_app.py::test_packaged_bundled_hash_gate_covers_runtime_files_changed_for_release`
  and
  `tests/test_release_gate_python_app.py::test_verify_bundled_python_hash_gate_covers_release_runtime_files`
  failed until `utils/single_batch_generator.py` was added to both parity
  lists.
- The first packaged integrity run also failed exactly on bundled/source drift:
  `build/current-packaged-integrity-contract-20260522-singlebatch-hashgate.json`
  -> `status=fail`, bundled
  `vmlx_engine/utils/single_batch_generator.py` content drift.

Change:

- Added `utils/single_batch_generator.py` to:
  - `panel/scripts/release-gate-python-app.py::BUNDLED_SOURCE_HASH_PATHS`;
  - `panel/scripts/verify-bundled-python.sh::HASH_GATED_ENGINE_FILES`.
- Rebuilt `panel/bundled-python` from this checkout with clean JANG source:
  `/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools`.

Verification:

- Focused release-gate tests:
  `.venv/bin/python -m pytest -q tests/test_release_gate_python_app.py::test_packaged_bundled_hash_gate_covers_runtime_files_changed_for_release tests/test_release_gate_python_app.py::test_verify_bundled_python_hash_gate_covers_release_runtime_files`
  -> `2 passed`.
- Packaged integrity after rebundle:
  `build/current-packaged-integrity-contract-20260522-singlebatch-hashgate-after-bundle.json`
  -> `status=pass`, `failed=[]`, bundled engine hash parity true, bundled
  JANG tools hash parity true, bundled critical imports true.
- Clean-JANG umbrella after rebundle:
  `build/current-regression-suite-20260522-singlebatch-hashgate-bundled.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Release read:

- The packaged/bundled runtime now carries the single-batch prefill keep-alloc
  source fix and future release gates will fail if this file drifts.
- This still does not clear DSV4 long-output/code/file-generation quality.

Verification:

- Focused red/green guard:
  `.venv/bin/python -m pytest -q tests/test_model_family_detection_contract.py::test_decode_speed_gate_detects_cache_health_mismatches`
  -> `1 passed` after the red failure proved the old invariant was stale.
- Focused manifest guard:
  `.venv/bin/python -m pytest -q tests/test_release_regression_manifest.py::test_release_regression_manifest_tracks_qwen_jang_live_speed_review tests/test_release_regression_manifest.py::test_release_regression_manifest_covers_required_domains`
  -> passed.
- Release manifest artifact:
  `build/current-release-regression-manifest-20260522-qwen-live-speed-review.json`
  -> `rows=19`, includes new `performance` domain.
- Cache architecture with clean JANG source:
  `PYTHONPATH=/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools .venv/bin/python tests/cross_matrix/run_cache_architecture_contract.py --out build/current-cache-architecture-contract-20260522-qwen-live-speed-review.json`
  -> `status=pass`, `failed=[]`.
- Packaged integrity with clean JANG source:
  `VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools .venv/bin/python tests/cross_matrix/run_packaged_integrity_contract.py --out build/current-packaged-integrity-contract-20260522-qwen-live-speed-review.json`
  -> `status=pass`, `failed=[]`.
- Umbrella with clean JANG source:
  `PYTHONPATH=/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-b5f66a7/jang-tools .venv/bin/python tests/cross_matrix/run_current_regression_suite.py --out build/current-regression-suite-20260522-qwen-live-speed-review-clean-jang.json`
  -> `status=pass`, `failed_steps=[]`, open requirement exactly
  `DSV4 long-output/code/file-generation quality is release-cleared`.

Dirty-source caveat:

- `/Users/eric/jang/jang-tools` is currently tracked-dirty in
  `jang_tools/convert_hy3_jangtq.py` and `tests/test_hy3_capabilities.py`.
- Running the umbrella against that dirty source makes bundled hash parity fail
  because the packaged app matches clean `b5f66a7`, not dirty local edits.
- `.venv` still imports stale installed `jang_tools` unless the clean JANG
  worktree is placed on `PYTHONPATH`; the packaged app already contains the
  materialized-pool fix.
