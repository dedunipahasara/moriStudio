import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatasetStorage:
    """
    Manage dataset files, captions and metadata.
    """

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
    }

    def __init__(self, dataset_directory="datasets"):
        self.root = Path(dataset_directory).resolve()

        self.raw_dir = self.root / "raw"
        self.processed_dir = self.root / "processed"
        self.annotations_dir = self.root / "annotations"
        self.metadata_dir = self.root / "metadata"

        for directory in (
            self.raw_dir,
            self.processed_dir,
            self.annotations_dir,
            self.metadata_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, directory: Path, filename: str) -> Path:
        if not filename or Path(filename).name != filename:
            raise ValueError("Invalid filename.")

        path = (directory / filename).resolve()

        if path.parent != directory.resolve():
            raise ValueError("Invalid storage path.")

        return path

    def list_images(self, dataset_type="raw") -> List[str]:
        directories = {
            "raw": self.raw_dir,
            "processed": self.processed_dir,
        }

        if dataset_type not in directories:
            raise ValueError("Dataset type must be raw or processed.")

        directory = directories[dataset_type]

        return sorted(
            file.name
            for file in directory.iterdir()
            if file.is_file()
            and file.suffix.lower() in self.IMAGE_EXTENSIONS
        )

    def save_annotation(
        self,
        filename: str,
        annotation: Dict[str, Any],
    ) -> str:
        path = self._safe_path(self.annotations_dir, filename)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                annotation,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return str(path)

    def load_annotation(self, filename: str) -> Dict[str, Any]:
        path = self._safe_path(self.annotations_dir, filename)

        if not path.is_file():
            raise FileNotFoundError(f"Annotation not found: {filename}")

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save_metadata_csv(
        self,
        filename: str,
        rows: List[Dict[str, Any]],
    ) -> str:
        if not rows:
            raise ValueError("Metadata rows cannot be empty.")

        path = self._safe_path(self.metadata_dir, filename)

        fieldnames = list(rows[0].keys())

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return str(path)

    def load_metadata_csv(self, filename: str) -> List[Dict[str, str]]:
        path = self._safe_path(self.metadata_dir, filename)

        if not path.is_file():
            raise FileNotFoundError(f"Metadata not found: {filename}")

        with path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def get_dataset_summary(self) -> Dict[str, Any]:
        return {
            "raw_images": len(self.list_images("raw")),
            "processed_images": len(self.list_images("processed")),
            "annotations": len(list(self.annotations_dir.glob("*.json"))),
            "metadata_files": len(list(self.metadata_dir.glob("*.csv"))),
        }
