
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs/exports"

FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP"
}


def export_image(input_path, output_dir, image_format, quality):
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.is_file():
        raise FileNotFoundError(f"Image not found: {input_path}")

    image_format = image_format.lower()

    if image_format not in FORMATS:
        raise ValueError("Unsupported image format")

    if not 1 <= quality <= 100:
        raise ValueError("Quality must be between 1 and 100")

    output_dir.mkdir(parents=True, exist_ok=True)

    extension = "jpg" if image_format == "jpeg" else image_format
    output_path = output_dir / f"{input_path.stem}.{extension}"

    with Image.open(input_path) as image:
        image = image.convert("RGB")

        options = {}
        if image_format in ("jpg", "jpeg", "webp"):
            options["quality"] = quality

        image.save(
            output_path,
            format=FORMATS[image_format],
            **options
        )

    print(f"Export completed: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Cute3D Image Export"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg", "webp"],
        default="png"
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--quality", type=int, default=95)

    args = parser.parse_args()

    export_image(
        args.input,
        args.output,
        args.format,
        args.quality
    )


if __name__ == "__main__":
    main()

