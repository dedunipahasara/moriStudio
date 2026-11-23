from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError


class ImageProcessor:
    SUPPORTED_FORMATS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
    }

    def load_image(self, image_path):
        image_path = Path(image_path)

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError("Unsupported image format.")

        try:
            with Image.open(image_path) as image:
                image.load()
                return image.copy()

        except (UnidentifiedImageError, OSError) as error:
            raise ValueError(
                "Invalid or corrupted image."
            ) from error

    def validate_image(self, image):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if image.width <= 0 or image.height <= 0:
            raise ValueError("Invalid image dimensions.")

        return True

    def convert_mode(self, image, mode="RGB"):
        self.validate_image(image)

        if mode not in ("RGB", "RGBA", "L"):
            raise ValueError("Unsupported image color mode.")

        return image.convert(mode)

    def rotate_image(self, image, angle):
        self.validate_image(image)

        return image.rotate(
            angle,
            expand=True,
            resample=Image.Resampling.BICUBIC,
        )

    def correct_orientation(self, image):
        self.validate_image(image)

        return ImageOps.exif_transpose(image)

    def get_image_info(self, image):
        self.validate_image(image)

        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }