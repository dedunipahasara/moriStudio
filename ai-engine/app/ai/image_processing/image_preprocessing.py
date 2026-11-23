from PIL import Image
import torch
from torchvision import transforms


class ImagePreprocessor:
    def __init__(
        self,
        image_size: int = 32,
        channels: int = 3,
    ):
        if image_size < 8:
            raise ValueError("Image size must be at least 8.")

        if channels != 3:
            raise ValueError("Only RGB images are supported.")

        self.image_size = image_size

        self.transform = transforms.Compose([
            transforms.Resize(
                (image_size, image_size),
                interpolation=transforms.InterpolationMode.BILINEAR,
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.5, 0.5, 0.5),
                std=(0.5, 0.5, 0.5),
            ),
        ])

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        image = image.convert("RGB")

        return self.transform(image)

    def preprocess_batch(self, images: list) -> torch.Tensor:
        if not images:
            raise ValueError("Image batch cannot be empty.")

        tensors = [
            self.preprocess(image)
            for image in images
        ]

        return torch.stack(tensors, dim=0)

    def load_and_preprocess(self, image_path: str) -> torch.Tensor:
        with Image.open(image_path) as image:
            return self.preprocess(image)
