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

uv run --extra dev python tests/cross_matrix/run_max_output_context_contract.py \
  --out build/current-max-output-context-contract-20260522-chat-server-boundary.json

VMLINUX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
VMLX_JANG_TOOLS_SOURCE=/Users/eric/jang/.worktrees/vmlx-release-clean-7f643ed/jang-tools \
uv run --extra dev python tests/cross_matrix/run_current_regression_suite.py \
  --out build/current-regression-suite-20260522-chat-server-boundary.json

uv run --extra dev python tests/cross_matrix/run_release_surface_contract.py \
  --out build/current-release-surface-contract-20260522-post-mcp-marker-hardening.json
```

Observed results:

- max-output gate: `status=pass`, `missing_markers=[]`, engine `14 passed`,
  panel `32 passed / 1 skipped`;
- focused max-output/current-suite/manifest tests: `49 passed`;
- umbrella suite: `status=pass`, `failed_steps=[]`;
- release surface contract: `status=pass`;
- known open objective remains only DSV4 long-output/code quality.

## Release Decision

No release build has been started from this checkpoint. The next release action
is blocked unless Eric explicitly descopes the DSV4 long-output/code quality
row or that row gets real runtime evidence.
