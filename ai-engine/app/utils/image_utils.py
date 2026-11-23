import torch
import numpy as np

from PIL import Image


class ImageUtils:
    """
    Utility functions for image and tensor operations.
    """

    @staticmethod
    def validate_image(image):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if image.width <= 0 or image.height <= 0:
            raise ValueError("Invalid image dimensions.")

        return True

    @staticmethod
    def get_dimensions(image):
        ImageUtils.validate_image(image)

        return {
            "width": image.width,
            "height": image.height,
            "channels": len(image.getbands()),
        }

    @staticmethod
    def get_aspect_ratio(image):
        ImageUtils.validate_image(image)

        return round(image.width / image.height, 4)

    @staticmethod
    def convert_to_rgb(image):
        ImageUtils.validate_image(image)

        return image.convert("RGB")

    @staticmethod
    def convert_to_grayscale(image):
        ImageUtils.validate_image(image)

        return image.convert("L")

    @staticmethod
    def image_to_tensor(image, normalize=True):
        ImageUtils.validate_image(image)

        image = image.convert("RGB")

        array = np.array(image, dtype=np.float32) / 255.0

        tensor = torch.from_numpy(array).permute(2, 0, 1)

        if normalize:
            tensor = (tensor * 2.0) - 1.0

        return tensor

    @staticmethod
    def tensor_to_image(tensor):
        if not isinstance(tensor, torch.Tensor):
            raise TypeError("Input must be a PyTorch tensor.")

        tensor = tensor.detach().cpu()

        if tensor.ndim == 4:
            if tensor.shape[0] != 1:
                raise ValueError(
                    "Expected a single image in the batch."
                )
            tensor = tensor.squeeze(0)

        if tensor.ndim != 3:
            raise ValueError(
                "Expected tensor shape [C, H, W]."
            )

        if tensor.shape[0] not in (1, 3, 4):
            raise ValueError("Unsupported number of image channels.")

        # Convert model range [-1, 1] to [0, 1].
        tensor = (tensor.clamp(-1, 1) + 1) / 2

        array = (
            tensor.permute(1, 2, 0).numpy() * 255
        ).round().astype(np.uint8)

        if array.shape[2] == 1:
            array = array.squeeze(2)
            return Image.fromarray(array, mode="L")

        return Image.fromarray(array)

    @staticmethod
    def normalize_tensor(tensor):
        if not isinstance(tensor, torch.Tensor):
            raise TypeError("Input must be a PyTorch tensor.")

        return (tensor - 0.5) / 0.5

    @staticmethod
    def denormalize_tensor(tensor):
        if not isinstance(tensor, torch.Tensor):
            raise TypeError("Input must be a PyTorch tensor.")

        return (tensor * 0.5 + 0.5).clamp(0, 1)
