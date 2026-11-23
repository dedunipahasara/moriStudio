
import csv
from pathlib import Path

import torch
from torch.utils.data import Dataset
from PIL import Image


class Cute3DDataset(Dataset):
    def __init__(
        self,
        metadata_file,
        image_dir,
        tokenizer,
        image_preprocessor,
        max_length=32,
    ):
        self.metadata_file = Path(metadata_file)
        self.image_dir = Path(image_dir)
        self.tokenizer = tokenizer
        self.image_preprocessor = image_preprocessor
        self.max_length = max_length

        if not self.metadata_file.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {self.metadata_file}"
            )

        if not self.image_dir.exists():
            raise FileNotFoundError(
                f"Image directory not found: {self.image_dir}"
            )

        self.samples = []

        with open(
            self.metadata_file,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file is empty or invalid"
                )

            if "image" not in reader.fieldnames:
                raise ValueError(
                    "CSV must contain an 'image' column"
                )

            if "caption" not in reader.fieldnames:
                raise ValueError(
                    "CSV must contain a 'caption' column"
                )

            for row in reader:
                image_name = (row.get("image") or "").strip()
                caption = (row.get("caption") or "").strip()

                if not image_name or not caption:
                    continue

                image_path = self.image_dir / image_name

                if image_path.is_file():
                    self.samples.append({
                        "image_path": image_path,
                        "caption": caption,
                    })

        if not self.samples:
            raise ValueError(
                "No valid image-caption pairs found "
                "in the dataset"
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample = self.samples[index]

        with Image.open(sample["image_path"]) as img:
            image = img.convert("RGB")

        image_tensor = self.image_preprocessor.preprocess(
            image
        )

        token_ids = self.tokenizer.encode(
            sample["caption"],
            add_special_tokens=True,
            padding=True,
            truncation=True,
        )

        token_ids = torch.tensor(
            token_ids,
            dtype=torch.long,
        )

        return {
            "images": image_tensor,
            "token_ids": token_ids,
            "captions": sample["caption"],
        }

