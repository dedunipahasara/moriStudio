from pathlib import Path
from PIL import Image, UnidentifiedImageError


class ImageService:

    ALLOWED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    def __init__(self, output_directory="outputs/images"):
        self.output_directory = Path(output_directory).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, filename):
        """
        Prevent directory traversal and access outside output folder.
        """

        if not filename or Path(filename).name != filename:
            raise ValueError("Invalid filename.")

        file_path = (self.output_directory / filename).resolve()

        if file_path.parent != self.output_directory:
            raise ValueError("Invalid file path.")

        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported image format.")

        return file_path

    def list_images(self):
        """
        Return all generated images.
        """

        images = []

        for file_path in self.output_directory.iterdir():

            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.ALLOWED_EXTENSIONS
            ):
                images.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                })

        return images

    def get_image(self, filename):
        """
        Open an image safely.
        """

        file_path = self._get_safe_path(filename)

        if not file_path.is_file():
            raise FileNotFoundError("Image not found.")

        try:
            with Image.open(file_path) as image:
                image.load()
                return image.copy()

        except (UnidentifiedImageError, OSError) as error:
            raise ValueError("Invalid or corrupted image.") from error

    def get_image_details(self, filename):

        file_path = self._get_safe_path(filename)

        if not file_path.is_file():
            raise FileNotFoundError("Image not found.")

        with Image.open(file_path) as image:
            return {
                "filename": file_path.name,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "size_bytes": file_path.stat().st_size,
            }

    def delete_image(self, filename):

        file_path = self._get_safe_path(filename)

        if not file_path.is_file():
            raise FileNotFoundError("Image not found.")

        file_path.unlink()

        return {
            "success": True,
            "message": "Image deleted successfully.",
            "filename": filename,
        }
