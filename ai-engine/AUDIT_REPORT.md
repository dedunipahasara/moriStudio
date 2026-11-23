# Cute3D AI Engine — Audit and Change Report

## What was inspected
- 355 ZIP entries extracted and reviewed.
- 102 Python source files passed Python syntax compilation.
- 30 raw dataset images and 30 caption records were found; all caption image references exist.
- Existing custom tokenizer, prompt encoder, 32x32 diffusion model, trainer, pipelines, storage, API, and scripts were retained.

## Critical findings
1. The custom model preprocesses images at 32x32 and the bundled dataset contains only 30 image-caption pairs. It is not a capable general-purpose high-resolution text-to-image model.
2. The FastAPI lifespan previously left `generation_pipeline` as `None`, so the generation endpoint could not work.
3. The old generation route awaited a pipeline method that was synchronous and expected response fields the existing pipeline did not return.
4. Several old root-level test modules import a non-existent `TextTokenizer`, and duplicate test module names caused pytest collection conflicts.
5. The original custom diffusion training loss does not demonstrate image quality; a low loss is not proof of visually coherent generation.

## Changes made
- Added `StableDiffusionCppBackend`, which starts the local `sd-server`, calls its OpenAI-compatible image generation endpoint, validates the PNG response, and saves generated files.
- Wired the backend into FastAPI lifespan and model/health status routes.
- Fixed generation endpoint execution by running blocking generation calls in a worker thread.
- Added prompt, negative prompt, seed, and fixed 512x512 request validation.
- Added `.env` configuration, one-time model download script, API startup script, setup documentation, and backend unit tests.
- Kept the original custom PyTorch model and training implementation in the project; the new inference backend is a separate path.

## Verification performed
- Python syntax compilation: 102 files, zero syntax errors.
- Focused pytest suite: 2 passed.
- FastAPI smoke tests: health endpoint 200, model status endpoint 200, generation correctly returns 503 when model/runtime weights are not installed.
- Dataset integrity: 30 images, 30 annotation rows, zero missing image references.

## Not verified in this environment
The actual Stable Diffusion model weights and the user's locally compiled `sd-server` binary are not inside the uploaded ZIP or available in this audit container. Therefore a real 512x512 model inference could not be run here. The first real image-generation test must be run on the user's laptop after downloading the model weights. The ZIP does not claim that this hardware/model combination guarantees artifact-free output.

## Runtime/model notes
- Intended runtime: `stable-diffusion.cpp`, CPU backend.
- Intended model: Stable Diffusion 1.5 GGUF Q4_K.
- Expected model download: approximately 3.17 GB.
- Starting resolution: 512x512.
- 8 GB RAM may be tight; close other applications and monitor memory. If the process is killed due to memory pressure, try Q4_0 and update `SD_MODEL_PATH`.
- The model weights are not redistributed in this ZIP. Review the upstream CreativeML Open RAIL-M license before use or redistribution.


## Additional update: visual style presets
- Added six prompt presets: auto, photorealistic, 3d_cartoon, anime, digital_art, product_photo.
- Added `style` to the generation request; omitted style remains backward-compatible (`auto`).
- Added `GET /api/styles` to list available presets.
- Presets append positive and negative prompt guidance before sending the request to the same local SD 1.5 model.
- No new model weights are included. No claim is made that presets guarantee specialist-grade outputs.
- AI upscaling and image-to-image refinement remain future work; neither is represented as implemented.
