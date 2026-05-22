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

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-distinct-speed-rows.json

uv run --extra dev python tests/cross_matrix/run_release_regression_manifest.py \
  --out build/current-release-regression-manifest-20260522-parser-registry-rows.json

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-chat-server-boundary.json

VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py \
  --out build/current-regression-suite-20260522-concrete-artifacts.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-new-chat-max-output.json
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
- focused max-output/manifest/current-suite tests after new-chat guard:
  `55 passed`;
- umbrella suite after new-chat guard: `status=pass`, `failed_steps=[]`;
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
- umbrella suite: `status=pass`, `failed_steps=[]`;
- release surface contract after pushing `cdb7d0f0`: `status=pass`;
- release surface contract after pushing `177b9cd4`: `status=pass`;
- public updater primary/fallback remain `1.5.46`, PyPI `vmlx` remains
  `1.5.46`, and GitHub `jjang-ai/vmlx` release `v1.5.47` is not published;
- known open objective remains only DSV4 long-output/code quality.

## Release Decision

No release build has been started from this checkpoint. The next release action
is blocked unless Eric explicitly descopes the DSV4 long-output/code quality
row or that row gets real runtime evidence.
