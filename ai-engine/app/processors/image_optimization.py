from pathlib import Path
from PIL import Image


class ImageOptimizer:

    SUPPORTED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
    }

    def optimize(
        self,
        image,
        output_path,
        image_format="WEBP",
        quality=85,
    ):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        image_format = image_format.upper()

        if image_format not in self.SUPPORTED_FORMATS:
            raise ValueError("Unsupported optimization format.")

        if not isinstance(quality, int) or isinstance(quality, bool):
            raise TypeError("Quality must be an integer.")

        if not 1 <= quality <= 100:
            raise ValueError("Quality must be between 1 and 100.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_image = image.copy()
        options = {}

        if image_format == "JPEG":
            if save_image.mode not in ("RGB", "L"):
                save_image = save_image.convert("RGB")

            options = {
                "quality": quality,
                "optimize": True,
                "progressive": True,
            }

        elif image_format == "WEBP":
            options = {
                "quality": quality,
                "method": 6,
            }

        elif image_format == "PNG":
            options = {
                "optimize": True,
            }

        save_image.save(
            output_path,
            format=image_format,
            **options,
        )

        return {
            "success": True,
            "path": str(output_path),
            "format": image_format,
            "size_bytes": output_path.stat().st_size,
        }

    def get_file_size(self, image_path):
        image_path = Path(image_path)

        if not image_path.is_file():
            raise FileNotFoundError("Image file not found.")

        return image_path.stat().st_size

    def calculate_size_reduction(
        self,
        original_size,
        optimized_size,
    ):
        if original_size <= 0:
            raise ValueError(
                "Original size must be greater than zero."
            )

        reduction = (
            (original_size - optimized_size) / original_size
        ) * 100

        return round(reduction, 2)