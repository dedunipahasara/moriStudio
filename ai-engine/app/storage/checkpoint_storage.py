from pathlib import Path
from typing import Any, Dict, Optional

import torch


class CheckpointStorage:
    """
    Save and load PyTorch model checkpoints.
    """

    def __init__(self, checkpoint_directory="checkpoints"):
        self.root = Path(checkpoint_directory).resolve()

        self.text_encoder_dir = self.root / "text_encoder"
        self.image_generator_dir = self.root / "image_generator"

        self.text_encoder_dir.mkdir(parents=True, exist_ok=True)
        self.image_generator_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, filename: str, checkpoint_type="image_generator"):
        directories = {
            "text_encoder": self.text_encoder_dir,
            "image_generator": self.image_generator_dir,
        }

        if checkpoint_type not in directories:
            raise ValueError("Invalid checkpoint type.")

        if not filename or Path(filename).name != filename:
            raise ValueError("Invalid checkpoint filename.")

        if Path(filename).suffix not in (".pt", ".pth"):
            raise ValueError("Checkpoint must use .pt or .pth extension.")

        return directories[checkpoint_type] / filename

    def save(
        self,
        checkpoint: Dict[str, Any],
        filename="latest.pth",
        checkpoint_type="image_generator",
    ) -> str:
        if not isinstance(checkpoint, dict):
            raise TypeError("Checkpoint must be a dictionary.")

        path = self._get_path(filename, checkpoint_type)

        torch.save(checkpoint, path)

        return str(path)

    def load(
        self,
        filename="latest.pth",
        checkpoint_type="image_generator",
        map_location="cpu",
    ) -> Dict[str, Any]:
        path = self._get_path(filename, checkpoint_type)

        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {filename}")

        try:
            checkpoint = torch.load(
                path,
                map_location=map_location,
                weights_only=True,
            )
        except TypeError:
            # Compatibility with older PyTorch versions.
            checkpoint = torch.load(
                path,
                map_location=map_location,
            )

        return checkpoint

    def list_checkpoints(self, checkpoint_type="image_generator"):
        directories = {
            "text_encoder": self.text_encoder_dir,
            "image_generator": self.image_generator_dir,
        }

        if checkpoint_type not in directories:
            raise ValueError("Invalid checkpoint type.")

        directory = directories[checkpoint_type]

        return sorted(
            file.name
            for file in directory.iterdir()
            if file.is_file() and file.suffix in (".pt", ".pth")
        )

    def delete(self, filename, checkpoint_type="image_generator"):
        path = self._get_path(filename, checkpoint_type)

        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {filename}")

        path.unlink()

        return True

    def get_checkpoint_info(
        self,
        filename,
        checkpoint_type="image_generator",
    ):
        path = self._get_path(filename, checkpoint_type)

        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {filename}")

        return {
            "filename": path.name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
        }
