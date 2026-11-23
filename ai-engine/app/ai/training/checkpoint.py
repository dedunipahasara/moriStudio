from pathlib import Path
import torch


class CheckpointManager:
    def __init__(self, checkpoint_dir="checkpoints/image_generator"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        filename,
        model,
        optimizer=None,
        scheduler=None,
        epoch=0,
        best_loss=float("inf"),
        prompt_encoder=None,
        text_feature_extractor=None,
    ):
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "best_loss": best_loss,
        }

        if optimizer is not None:
            checkpoint["optimizer_state_dict"] = optimizer.state_dict()

        if scheduler is not None:
            checkpoint["scheduler_state_dict"] = scheduler.state_dict()

        if prompt_encoder is not None:
            checkpoint["prompt_encoder_state_dict"] = (
                prompt_encoder.state_dict()
            )

        if text_feature_extractor is not None:
            checkpoint["text_feature_extractor_state_dict"] = (
                text_feature_extractor.state_dict()
            )

        save_path = self.checkpoint_dir / filename

        torch.save(checkpoint, save_path)

        return save_path

    def load(
        self,
        filename,
        model,
        optimizer=None,
        scheduler=None,
        prompt_encoder=None,
        text_feature_extractor=None,
        device="cpu",
    ):
        checkpoint_path = self.checkpoint_dir / filename

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Checkpoint not found: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location=device,
        )

        model.load_state_dict(checkpoint["model_state_dict"])

        if (
            optimizer is not None
            and "optimizer_state_dict" in checkpoint
        ):
            optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )

        if (
            scheduler is not None
            and "scheduler_state_dict" in checkpoint
        ):
            scheduler.load_state_dict(
                checkpoint["scheduler_state_dict"]
            )

        if (
            prompt_encoder is not None
            and "prompt_encoder_state_dict" in checkpoint
        ):
            prompt_encoder.load_state_dict(
                checkpoint["prompt_encoder_state_dict"]
            )

        if (
            text_feature_extractor is not None
            and "text_feature_extractor_state_dict" in checkpoint
        ):
            text_feature_extractor.load_state_dict(
                checkpoint["text_feature_extractor_state_dict"]
            )

        return {
            "epoch": checkpoint.get("epoch", 0),
            "best_loss": checkpoint.get("best_loss", float("inf")),
        }
