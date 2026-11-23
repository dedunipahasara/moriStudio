from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image


class ExportService:

    ALLOWED_FORMATS = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WEBP": ".webp",
    }

    def __init__(self, export_directory="outputs/exports"):
        self.export_directory = Path(export_directory).resolve()
        self.export_directory.mkdir(parents=True, exist_ok=True)

    def export_image(
        self,
        image,
        filename,
        image_format="PNG",
        quality=95,
    ):
        """
        Export a PIL image to PNG, JPEG or WEBP.
        """

        image_format = image_format.upper()

        if image_format not in self.ALLOWED_FORMATS:
            raise ValueError("Unsupported export format.")

        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if not filename or Path(filename).name != filename:
            raise ValueError("Invalid filename.")

        extension = self.ALLOWED_FORMATS[image_format]
        output_path = self.export_directory / filename

        if output_path.suffix.lower() != extension:
            output_path = output_path.with_suffix(extension)

        save_image = image.copy()

        if image_format == "JPEG" and save_image.mode not in ("RGB", "L"):
            save_image = save_image.convert("RGB")

        save_options = {}

        if image_format in ("JPEG", "WEBP"):
            quality = max(1, min(int(quality), 100))
            save_options["quality"] = quality

        save_image.save(
            output_path,
            format=image_format,
            **save_options,
        )

        return {
            "success": True,
            "filename": output_path.name,
            "path": str(output_path),
            "format": image_format,
            "size_bytes": output_path.stat().st_size,
        }

    def create_zip(self, image_paths, zip_filename="generated_images.zip"):
        """
        Export multiple image files into one ZIP archive.
        """

        if not zip_filename or Path(zip_filename).name != zip_filename:
            raise ValueError("Invalid ZIP filename.")

        zip_path = self.export_directory / zip_filename

        valid_paths = []

        for path in image_paths:

            image_path = Path(path).resolve()

            if not image_path.is_file():
                raise FileNotFoundError(f"Image not found: {image_path}")

            if image_path.suffix.lower() not in {
                ".png", ".jpg", ".jpeg", ".webp"
            }:
                raise ValueError(f"Unsupported image: {image_path.name}")

            valid_paths.append(image_path)

        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:

            for image_path in valid_paths:
                archive.write(
                    image_path,
                    arcname=image_path.name,
                )

        return {
            "success": True,
            "filename": zip_path.name,
            "path": str(zip_path),
            "image_count": len(valid_paths),
            "size_bytes": zip_path.stat().st_size,
        }
