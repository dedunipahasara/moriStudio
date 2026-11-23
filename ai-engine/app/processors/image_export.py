from pathlib import Path
from PIL import Image


class ImageExporter:

    SUPPORTED_FORMATS = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WEBP": ".webp",
    }

    def export(
        self,
        image,
        output_path,
        image_format="PNG",
        quality=95,
    ):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        image_format = image_format.upper()

        if image_format not in self.SUPPORTED_FORMATS:
            raise ValueError("Unsupported export format.")

        if not isinstance(quality, int) or isinstance(quality, bool):
            raise TypeError("Quality must be an integer.")

        if not 1 <= quality <= 100:
            raise ValueError("Quality must be between 1 and 100.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        expected_extension = self.SUPPORTED_FORMATS[image_format]

        if output_path.suffix.lower() != expected_extension:
            output_path = output_path.with_suffix(expected_extension)

        export_image = image.copy()
        save_options = {}

        if image_format == "JPEG":
            if export_image.mode not in ("RGB", "L"):
                export_image = export_image.convert("RGB")

            save_options = {
                "quality": quality,
                "optimize": True,
            }

        elif image_format == "WEBP":
            save_options = {
                "quality": quality,
                "method": 6,
            }

        elif image_format == "PNG":
            save_options = {
                "optimize": True,
            }

        export_image.save(
            output_path,
            format=image_format,
            **save_options,
        )

        return {
            "success": True,
            "filename": output_path.name,
            "path": str(output_path),
            "format": image_format,
            "width": export_image.width,
            "height": export_image.height,
            "size_bytes": output_path.stat().st_size,
        }

    def export_batch(
        self,
        images,
        output_directory,
        image_format="PNG",
        quality=95,
    ):
        output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        results = []

        for index, image in enumerate(images, start=1):
            filename = f"generated_{index}"

            result = self.export(
                image=image,
                output_path=output_directory / filename,
                image_format=image_format,
                quality=quality,
            )

            results.append(result)

        return {
            "success": True,
            "image_count": len(results),
            "files": results,
        }