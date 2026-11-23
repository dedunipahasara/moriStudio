
import csv
import json
import random
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "datasets/raw"
PROCESSED_DIR = ROOT / "datasets/processed"
ANNOTATIONS_FILE = ROOT / "datasets/annotations/captions.json"
METADATA_DIR = ROOT / "datasets/metadata"

IMAGE_SIZE = 32
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}
SEED = 42


def load_captions():
    if not ANNOTATIONS_FILE.exists():
        raise FileNotFoundError(ANNOTATIONS_FILE)

    with open(ANNOTATIONS_FILE, encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = value.get("caption", "")
            else:
                result[key] = value
        return result

    if isinstance(data, list):
        return {
            item.get("filename", item.get("image", "")):
                item.get("caption", "")
            for item in data
            if isinstance(item, dict)
        }

    raise ValueError("Unsupported captions.json format")


def prepare_dataset():
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw folder not found: {RAW_DIR}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    captions = load_captions()
    records = []
    failures = []

    image_files = sorted(
        path for path in RAW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS
    )

    print(f"Found {len(image_files)} raw images.")

    for path in image_files:
        try:
            caption = captions.get(path.name, "")

            if not isinstance(caption, str) or not caption.strip():
                print(f"Skipped (missing caption): {path.name}")
                continue

            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image)
                image = image.convert("RGB")
                image = image.resize(
                    (IMAGE_SIZE, IMAGE_SIZE),
                    Image.Resampling.LANCZOS
                )

                output_name = f"{path.stem}.png"
                output_path = PROCESSED_DIR / output_name
                image.save(output_path, format="PNG")

            records.append({
                "image": output_name,
                "caption": caption.strip()
            })

            print(f"Processed: {path.name}")

        except Exception as error:
            failures.append({
                "filename": path.name,
                "error": str(error)
            })
            print(f"Failed: {path.name}: {error}")

    if len(records) < 2:
        raise ValueError(
            "At least two valid image-caption pairs are required "
            "to create training and validation datasets."
        )

    random.Random(SEED).shuffle(records)

    split_index = max(1, int(len(records) * 0.8))
    split_index = min(split_index, len(records) - 1)

    train_records = records[:split_index]
    val_records = records[split_index:]

    for filename, data in [
        ("train.csv", train_records),
        ("val.csv", val_records),
        ("captions.csv", records),
    ]:
        with open(
            METADATA_DIR / filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["image", "caption"]
            )
            writer.writeheader()
            writer.writerows(data)

    with open(
        METADATA_DIR / "preparation_report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump({
            "total_images": len(image_files),
            "processed_images": len(records),
            "training_images": len(train_records),
            "validation_images": len(val_records),
            "failed_images": failures
        }, file, indent=4)

    print("\nDataset preparation completed.")
    print(f"Processed: {len(records)}")
    print(f"Training: {len(train_records)}")
    print(f"Validation: {len(val_records)}")
    print(f"Output: {PROCESSED_DIR}")


if __name__ == "__main__":
    prepare_dataset()

