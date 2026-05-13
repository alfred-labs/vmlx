# vMLX 2026-05-13 Engine/Cache/App Gate

This note records the release-gate boundary for the Python/Electron vMLX
engine/app work on 2026-05-13. Raw private artifacts are under
`docs/internal/release-gates/20260513_installed_app_full_model_gate/`.

## Runtime Fixes

- `SimpleEngine` now loads and runs direct/no-continuous-batching model work on
  a dedicated single worker thread. MLX streams are thread-local; loading on
  one thread and later generating on arbitrary default-executor threads caused
  direct JANG/JANGTQ/VLM/hybrid rows to fail with missing `Stream(gpu,N)`.
- Direct streaming usage accounting now falls back to formatted prompt token
  counts when mlx-lm or mlx-vlm stream chunks report `prompt_tokens=0`.
- Direct MLLM thinking-off prompts now consult the real bundle/template
  contract before appending a synthetic `<think></think>` sentinel. Reasoning
  capability and `think_in_template` are separate; ZAYA/ZAYA-VL can support
  reasoning without starting the default/off prompt inside a think rail.

## Live Installed-App Evidence

The installed app was rebuilt and installed from source commit `27d1ce5f`
(`Fix direct engine thread affinity`) using
`bash panel/scripts/build-and-install.sh`. The installed bundle reports
`vmlx_engine 1.5.33`, imports `jang_tools.turboquant.mpp_nax_kernel`, opens as
`/Applications/vMLX.app`, and its gateway responds on `127.0.0.1:8080`.

Post-build verification:

- `codesign --verify --deep --strict --verbose=2 /Applications/vMLX.app`
  passed.
- The installed app bundled Python smoke passed for Qwen3.6-27B JANG_4M and
  ZAYA1-VL-8B JANGTQ4 after the clean rebuild.
- No model servers or image servers were left running after the final gates.

Representative all-cache-mode rows passed:

- Qwen3.6-27B JANG_4M: direct, prefix, paged L1, paged L2.
- Gemma-4-26B JANG_4M: direct, prefix, paged L1, paged L2.
- ZAYA1-VL-8B JANGTQ4: direct, prefix, paged L1, paged L2.
- Ling-2.6-flash JANGTQ2: direct, prefix, paged L1, paged L2.

Additional direct plus paged-L2 rows passed:

- ZAYA1-8B JANGTQ_K and MXFP4.
- ZAYA1-VL-8B JANGTQ_K.
- Qwen3.6-27B MXFP4.
- Qwen3.6-35B-A3B 4bit and JANGTQ.
- Nemotron-Omni-Nano JANGTQ, JANGTQ4, and MXFP4.
- MiniMax-M2.7 Small JANGTQ.
- Hy3-preview JANGTQ2.
- DeepSeek-V4-Flash JANGTQ_K.
- Laguna-XS.2 JANGTQ.
- Ling-2.6-flash JANGTQ and MXFP4.
- MiniMax-M2.7 JANGTQ and JANGTQ_K, both JANGQ and dealign package layouts.
- DeepSeek-V4-Flash JANGTQ_K upload-staging layouts for JANGQ and Osaurus.

The remaining direct/L2 sweep produced 18/18 passing result files and no
tracebacks, stream-affinity failures, OOMs, or working-set rejections.

Installed-app API parity passed after the clean rebuild:

- Core families: Qwen3.6-27B JANG_4M, Gemma-4-26B JANG_4M,
  ZAYA1-VL-8B JANGTQ4, Ling-2.6-flash JANGTQ2, Laguna-XS.2 JANGTQ,
  Nemotron-Omni-Nano JANGTQ4, and MiniMax-M2.7 Small JANGTQ.
- Heavy rows: Hy3-preview JANGTQ2 and DeepSeek-V4-Flash JANGTQ_K.
- Surfaces covered for those rows: OpenAI Chat Completions stream and
  non-stream, OpenAI Responses stream and non-stream with
  `previous_response_id`, Anthropic Messages stream and non-stream with
  thinking explicitly disabled, Ollama `/api/chat` stream and non-stream, and
  Ollama `/api/generate`.
- Exact outputs included `CERULEAN 45` recall and `READY` one-turn responses
  with no flags. DSV4 reported `DSV4BatchGenerator`, `engine_path=dsv4`,
  `block_size=256`, and `paged+dsv4` cache behavior. Hy3 reported
  `SingleBatchGenerator`, paged cache, block-disk writes/hits, and active
  `turboquant_codebook_mpp_nax`.

Installed-app media and image gates were rerun after the clean rebuild:

- `ZAYA1-VL-8B-JANGTQ4`, `Qwen3.6-35B-A3B-JANGTQ-CRACK`, and
  `Nemotron-Omni-Nano-JANGTQ-CRACK` answered image color correctly through
  Chat Completions, Responses, Anthropic Messages, and Ollama.
- `Nemotron-Omni-Nano-JANGTQ-CRACK` also exercised the packaged Omni
  RADIO/Nemotron-H encoder view path.
- `flux-schnell-4bit` and `z-image-turbo-4bit` returned valid PNGs from
  `/v1/images/generations`.
- `qwen-image-edit` returned a valid PNG from `/v1/images/edits`.

## Cache/Detection Notes

- DSV4 rows used the DSV4-specific path: `DSV4_LONG_CTX=1`,
  `DSV4_POOL_QUANT=0`, DSV4 chat-template shim, `DeepseekV4Cache` layers,
  block size 256, and `deepseek_v4_v7` nested-state block-L2 serialization.
- MiniMax JANGTQ_K rows logged the mixed projection bit map
  `gate_proj=2`, `up_proj=2`, `down_proj=4` rather than relying on the folder
  name.
- MiniMax/Ling rows retained their parser/tool contracts and safety-floor
  repetition handling while exercising direct and scheduler paths.
- JANGTQ startup used `--jangtq-mpp-nax on` in the live matrix so `/health`
  and logs could prove the custom TensorOps lane was available on applicable
  JANGTQ rows.

## Boundaries

- This gate does not claim Kimi-sized bundles or source-sized DSV4 are locally
  tested; they exceed the current 128 GB machine budget for this pass.
- `ZAYA1-VL-8B-MXFP4` remains a text-only review row: cache mechanics and
  prompt-processing speed are working, but strict text recall output was not
  clean enough to mark as fully cleared.
- The matrix is installed-app API/server evidence. Computer Use could not attach
  to the Electron window because macOS denied the automation event, so visual
  click-through proof is still manual/user-side until that permission is fixed.
- Sleep/wake, JIT toggling, and long-context/max-reasoning DSV4 qualification
  were not exhaustively rerun in this final pass. DSV4 is proven coherent for
  short multi-turn/API/cache rows here, not fully qualified for every long-tail
  reasoning/context scenario.
