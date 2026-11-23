from pathlib import Path
from datetime import datetime
from PIL import Image


class OutputStorage:
    """
    Manage generated images and output files.
    """

    SUPPORTED_FORMATS = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WEBP": ".webp",
    }

    def __init__(self, output_directory="outputs"):
        self.root = Path(output_directory).resolve()

        self.images_dir = self.root / "images"
        self.thumbnails_dir = self.root / "thumbnails"
        self.logs_dir = self.root / "logs"

        for directory in (
            self.images_dir,
            self.thumbnails_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _safe_filename(self, filename):
        if not filename or Path(filename).name != filename:
            raise ValueError("Invalid filename.")

        return filename

    def save_image(
        self,
        image: Image.Image,
        filename=None,
        image_format="PNG",
        quality=95,
    ):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        image_format = image_format.upper()

        if image_format not in self.SUPPORTED_FORMATS:
            raise ValueError("Unsupported image format.")

        if not isinstance(quality, int) or isinstance(quality, bool):
            raise TypeError("Quality must be an integer.")

        if not 1 <= quality <= 100:
            raise ValueError("Quality must be between 1 and 100.")

        extension = self.SUPPORTED_FORMATS[image_format]

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"generated_{timestamp}{extension}"

        filename = self._safe_filename(filename)

        path = self.images_dir / filename

        if path.suffix.lower() != extension:
            raise ValueError("Filename extension does not match image format.")

        save_image = image.copy()
        options = {}

        if image_format == "JPEG":
            if save_image.mode not in ("RGB", "L"):
                save_image = save_image.convert("RGB")

            options = {
                "quality": quality,
                "optimize": True,
            }

        elif image_format == "WEBP":
            options = {
                "quality": quality,
            }

        elif image_format == "PNG":
            options = {
                "optimize": True,
            }

        save_image.save(
            path,
            format=image_format,
            **options,
        )

        return {
            "success": True,
            "filename": filename,
            "path": str(path),
            "format": image_format,
            "width": save_image.width,
            "height": save_image.height,
            "size_bytes": path.stat().st_size,
        }

    def save_thumbnail(
        self,
        image: Image.Image,
        filename,
        size=(256, 256),
    ):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        filename = self._safe_filename(filename)

        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("Thumbnail dimensions must be positive.")

        thumbnail = image.copy()

        thumbnail.thumbnail(
            size,
            Image.Resampling.LANCZOS,
        )

        path = self.thumbnails_dir / filename

        thumbnail.save(path, format="PNG", optimize=True)

        return str(path)

    def list_images(self):
        extensions = {".png", ".jpg", ".jpeg", ".webp"}

        return sorted(
            file.name
            for file in self.images_dir.iterdir()
            if file.is_file()
            and file.suffix.lower() in extensions
        )

    def get_image_path(self, filename):
        filename = self._safe_filename(filename)

        path = self.images_dir / filename

        if not path.is_file():
            raise FileNotFoundError(f"Generated image not found: {filename}")

        return path

    def delete_image(self, filename):
        path = self.get_image_path(filename)

        path.unlink()

        return True

    def get_storage_summary(self):
        images = [
            file for file in self.images_dir.iterdir()
            if file.is_file()
        ]

        total_size = sum(
            file.stat().st_size for file in images
        )

        return {
            "image_count": len(images),
            "total_size_bytes": total_size,
            "images_directory": str(self.images_dir),
            "thumbnails_directory": str(self.thumbnails_dir),
        }
