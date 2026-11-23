import csv
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "datasets" / "raw"
ANNOTATIONS_FILE = PROJECT_ROOT / "datasets" / "annotations" / "captions.json"
METADATA_DIR = PROJECT_ROOT / "datasets" / "metadata"

def main():
    if not ANNOTATIONS_FILE.exists():
        raise FileNotFoundError(f"Captions file not found: {ANNOTATIONS_FILE}")

    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw image folder not found: {RAW_DIR}")

    records = json.loads(ANNOTATIONS_FILE.read_text(encoding="utf-8"))
    valid_records = []

    for item in records:
        image_name = item.get("image", "").strip()
        caption = item.get("caption", "").strip()

        if not image_name or not caption:
            print(f"Skipping incomplete annotation: {item}")
            continue

        image_path = RAW_DIR / image_name
        if not image_path.is_file():
            print(f"Skipping missing image: {image_name}")
            continue

        valid_records.append({
            "image": image_name,
            "caption": caption
        })

    if len(valid_records) < 2:
        raise ValueError(
            "At least 2 valid image-caption pairs are required "
            "to create train and validation CSV files."
        )

    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save a combined CSV containing all valid image-caption pairs.
    write_csv(METADATA_DIR / "captions.csv", valid_records)

    # Deterministic shuffle so repeated runs produce the same split.
    shuffled = valid_records.copy()
    random.Random(42).shuffle(shuffled)

    # Keep at least one item in each split.
    val_count = max(1, round(len(shuffled) * 0.1))
    val_count = min(val_count, len(shuffled) - 1)

    val_records = shuffled[:val_count]
    train_records = shuffled[val_count:]

    write_csv(METADATA_DIR / "train.csv", train_records)
    write_csv(METADATA_DIR / "val.csv", val_records)

    print(f"Valid image-caption pairs: {len(valid_records)}")
    print(f"Training samples: {len(train_records)}")
    print(f"Validation samples: {len(val_records)}")
    print(f"Metadata saved in: {METADATA_DIR}")
    print("Note: vocabulary.json is created separately by your tokenizer.")

def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["image", "caption"])
        writer.writeheader()
        writer.writerows(records)

if __name__ == "__main__":
    main()