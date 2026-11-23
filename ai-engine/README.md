# Cute3D AI Engine — Local Image Generation Edition

This ZIP preserves the original experimental PyTorch training code and adds a separate,
pretrained Stable Diffusion 1.5 inference backend using `stable-diffusion.cpp`.

## Important: model weights are not included

The GGUF model is approximately 3.2 GB and is downloaded by the included installer (it is not embedded in this ZIP):
`models/stable-diffusion/v1-5-pruned_Q4_K.gguf`.

The model is CreativeML Open RAIL-M licensed. Review the license before redistribution.
The runtime and model are separate projects with their own licenses.

## Hardware profile

The intended fallback for the bundled setup is CPU inference. The NVIDIA MX350 has 2 GB
VRAM, so this setup does not enable CUDA. 512x512 is the intended starting resolution.
On an 8 GB RAM laptop, generation can be slow and may still fail if memory pressure is high.
Do not expect instant generation or guaranteed artifact-free output on this hardware.

## Folder layout expected

```text
cute3d/
├── ai-engine/                 # this project
│   ├── app/
│   ├── models/stable-diffusion/
│   └── .venv/
└── local-image-runtime/
    └── build/bin/sd-server
```

The default executable path assumes this layout. Override `SD_CPP_CLI` and `SD_MODEL_PATH`
in `.env` if your folders differ.

## Setup

1. Keep your existing `.venv` and the already-built `local-image-runtime`.
2. From `ai-engine`, create the local environment file and install the API dependencies without reinstalling PyTorch:

   ```bash
   cp .env.example .env
   ```

   ```bash
   source .venv/bin/activate
   pip install -r requirements-local.txt
   ```

3. Check the local runtime and model paths, then download the model once:

   ```bash
   chmod +x scripts/download_model.sh scripts/check_local_setup.sh
   ./scripts/check_local_setup.sh
   ./scripts/download_model.sh
   ```

4. Start the API:

   ```bash
   chmod +x scripts/start_api.sh
   ./scripts/start_api.sh
   ```

   The first server startup loads the 3.17 GB model and may take several minutes.
   Logs are written to `training/logs/sd-server.log`.

5. Check readiness:

   - `http://127.0.0.1:8000/api/health`
   - `http://127.0.0.1:8000/api/models/status`
   - API docs: `http://127.0.0.1:8000/docs`

## Generate an image

POST `http://127.0.0.1:8000/api/generations`:

```json
{
  "prompt": "A cute 3D stylized baby fox, full body, soft studio lighting, detailed fur, clean composition, high quality",
  "negative_prompt": "blurry, low quality, noisy, distorted, deformed, extra limbs, text, watermark",
  "width": 512,
  "height": 512,
  "seed": 12345
}
```

The API returns a base64 PNG and saves the generated image under `outputs/images/`.
A fixed seed makes a run reproducible within the same runtime/model configuration.

## Original custom PyTorch model

The original tokenizer, prompt encoder, custom diffusion model, trainer, dataset, and
checkpoints are retained. They are still useful for experimentation and learning, but
the supplied 30-image dataset and 32x32 architecture are not a suitable foundation for
high-quality general-purpose text-to-image generation. The new inference backend does not
silently train or replace that model.

## Troubleshooting

- `model file not found`: run `./scripts/download_model.sh` from the `ai-engine` directory, then restart the API. The model is intentionally downloaded separately because it is a large third-party licensed weight file.
- `executable not found`: verify `local-image-runtime/build/bin/sd-server`, then set
  `SD_CPP_CLI` in `.env`.
- Port 8081 in use: change `SD_SERVER_PORT` in `.env`.
- Out of memory / killed process: close other applications, increase swap, and consider
  using the Q4_0 model variant instead (lower memory/quality tradeoff); update the model
  filename in `.env`.
- Generation errors: inspect `training/logs/sd-server.log` and `training/logs/cute3d.log`.

## Model source

`kostakoff/stable-diffusion-v1-5-GGUF` on Hugging Face. The Q4_K variant is a balanced
quantization for stable-diffusion.cpp. This project downloads it on the user's machine;
it does not bundle or redistribute the weights.


## Visual style presets (added in this update)

The API now accepts an optional `style` field. Existing clients that omit it continue
to work with `auto`.

Available values:
- `auto` — keeps the user's visual direction and adds general quality guidance.
- `photorealistic` — photography, natural materials, skin/hair texture and realistic light.
- `3d_cartoon` — stylized 3D characters, expressive forms and animation-style lighting.
- `anime` — polished 2D anime illustration, linework and expressive eyes.
- `digital_art` — concept art and painterly digital illustration.
- `product_photo` — commercial product photography and studio lighting.

List styles at `GET http://127.0.0.1:8000/api/styles`.

Example photorealistic request:

```json
{
  "prompt": "A close-up portrait of a woman in a sunlit garden, natural expression, detailed brown hair",
  "negative_prompt": "blurry, deformed face, extra fingers, watermark, text",
  "style": "photorealistic",
  "width": 512,
  "height": 512,
  "seed": 123
}
```

Example 3D cartoon request:

```json
{
  "prompt": "A cute baby panda sitting on a mossy hill in a lush forest, full body",
  "negative_prompt": "blurry, deformed paws, extra limbs, text, watermark",
  "style": "3d_cartoon",
  "width": 512,
  "height": 512,
  "seed": 42
}
```

### Important quality limitations

Style presets append carefully selected prompt and negative-prompt guidance. They do not
switch to separate specialist models, train the model, or add new visual knowledge.
All styles still use the same installed Stable Diffusion 1.5 GGUF Q4_K weights. The
result depends on the prompt, seed, quantization, model capability and CPU runtime.
Photorealistic faces, hands, small text, fine fur and complex anatomy can still contain
artifacts. Inspect results and iterate prompts.

This build intentionally keeps 512x512 as the supported resolution for the user's
8 GB RAM / 2 GB VRAM laptop. AI upscaling and image-to-image refinement are **not**
claimed as implemented in this release; they require compatible additional model
weights/runtime support and separate real-device testing.
