from pathlib import Path

import torch
from PIL import Image

from app.ai.generation.sampling import sample_images


class GenerationEngine:
    def __init__(
        self,
        inference_engine,
        output_dir="outputs/images",
        image_size=32,
        image_channels=3,
    ):
        self.inference_engine = inference_engine

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.image_size = image_size
        self.image_channels = image_channels

    @torch.no_grad()
    def generate(
        self,
        prompt,
        num_images=1,
        seed=None,
        save=True,
    ):
        if not self.inference_engine.is_loaded:
            raise RuntimeError(
                "Load a trained model before generating images"
            )

        if num_images < 1:
            raise ValueError("num_images must be at least 1")

        text_features = self.inference_engine.encode_prompt(
            prompt
        )

        generated_images = sample_images(
            model=self.inference_engine.model,
            text_features=text_features,
            num_images=num_images,
            image_size=self.image_size,
            image_channels=self.image_channels,
            device=self.inference_engine.device,
            seed=seed,
        )

        pil_images = self.tensor_to_pil(generated_images)

        saved_paths = []

        if save:
            for index, image in enumerate(pil_images):
                filename = f"generated_{index + 1}.png"
                image_path = self.output_dir / filename

                image.save(image_path, format="PNG")
                saved_paths.append(str(image_path))

        return {
            "prompt": prompt,
            "images": pil_images,
            "paths": saved_paths,
        }

    @staticmethod
    def tensor_to_pil(image_batch):
        """
        Convert generated tensor values [-1, 1] into PIL RGB images.
        """
        image_batch = (
            (image_batch.detach().cpu().clamp(-1, 1) + 1.0)
            / 2.0
        )

        image_batch = (
            image_batch * 255.0
        ).round().byte()

        images = []

        for tensor in image_batch:
            array = tensor.permute(1, 2, 0).numpy()
            images.append(Image.fromarray(array, mode="RGB"))

        return images
