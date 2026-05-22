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
