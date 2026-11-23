from pathlib import Path

import torch
from PIL import Image
from torchvision.transforms.functional import to_pil_image


class ImagePostprocessor:
    def __init__(self):
        pass

    def tensor_to_image(
        self,
        image_tensor: torch.Tensor,
    ) -> Image.Image:

        if image_tensor.ndim != 3:
            raise ValueError(
                "Expected image tensor shape [channels, height, width]."
            )

        if image_tensor.shape[0] != 3:
            raise ValueError("Expected a 3-channel RGB image.")

        # Model output is expected to be in the range [-1, 1].
        image_tensor = image_tensor.detach().float().cpu()

        image_tensor = (image_tensor + 1.0) / 2.0
        image_tensor = image_tensor.clamp(0.0, 1.0)

        return to_pil_image(image_tensor)

    def batch_to_images(
        self,
        image_batch: torch.Tensor,
    ) -> list[Image.Image]:

        if image_batch.ndim != 4:
            raise ValueError(
                "Expected batch shape [batch, channels, height, width]."
            )

        return [
            self.tensor_to_image(image)
            for image in image_batch
        ]

    def save_image(
        self,
        image_tensor: torch.Tensor,
        output_path: str,
    ) -> str:

        path = Path(output_path)

        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("Supported formats: PNG, JPG and JPEG.")

        path.parent.mkdir(parents=True, exist_ok=True)

        image = self.tensor_to_image(image_tensor)

        image.save(path)

        return str(path)

    def save_batch(
        self,
        image_batch: torch.Tensor,
        output_directory: str,
        prefix: str = "generated",
    ) -> list[str]:

        directory = Path(output_directory)
        directory.mkdir(parents=True, exist_ok=True)

        images = self.batch_to_images(image_batch)

        saved_paths = []

        for index, image in enumerate(images):
            path = directory / f"{prefix}_{index + 1:04d}.png"
            image.save(path)
            saved_paths.append(str(path))

        return saved_paths
