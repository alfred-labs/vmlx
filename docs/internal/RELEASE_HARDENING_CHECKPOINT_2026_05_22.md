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

## Release Decision

No release build has been started from this checkpoint. The next release action
is blocked unless Eric explicitly descopes the DSV4 long-output/code quality
row or that row gets real runtime evidence.
