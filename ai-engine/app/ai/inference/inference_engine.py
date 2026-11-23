
from pathlib import Path

import torch


class InferenceEngine:
    def __init__(
        self,
        tokenizer,
        prompt_encoder,
        text_feature_extractor,
        model,
        device=None,
    ):
        self.device = torch.device(
            device or (
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        )

        self.tokenizer = tokenizer

        self.prompt_encoder = prompt_encoder.to(
            self.device
        )

        self.text_feature_extractor = (
            text_feature_extractor.to(self.device)
        )

        self.model = model.to(self.device)

        self.is_loaded = False

    def load_checkpoint(self, checkpoint_path):
        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Checkpoint not found: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location=self.device,
        )

        required_keys = [
            "model_state_dict",
            "prompt_encoder_state_dict",
            "text_feature_extractor_state_dict",
        ]

        for key in required_keys:
            if key not in checkpoint:
                raise KeyError(
                    f"Checkpoint is missing required key: {key}"
                )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.prompt_encoder.load_state_dict(
            checkpoint["prompt_encoder_state_dict"]
        )

        self.text_feature_extractor.load_state_dict(
            checkpoint["text_feature_extractor_state_dict"]
        )

        self.model.eval()
        self.prompt_encoder.eval()
        self.text_feature_extractor.eval()

        self.is_loaded = True

        return {
            "epoch": checkpoint.get("epoch"),
            "best_loss": checkpoint.get("best_loss"),
            "checkpoint": str(checkpoint_path),
        }

    @torch.no_grad()
    def encode_prompt(self, prompt):
        if not self.is_loaded:
            raise RuntimeError(
                "Model is not loaded. Load a checkpoint first."
            )

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(
                "Prompt must be a non-empty string"
            )

        token_ids = self.tokenizer.encode(
            prompt,
            add_special_tokens=True,
            padding=True,
            truncation=True,
        )

        token_ids = torch.tensor(
            token_ids,
            dtype=torch.long,
            device=self.device,
        ).unsqueeze(0)

        embeddings = self.prompt_encoder(
            token_ids
        )

        text_features = self.text_feature_extractor(
            embeddings,
            token_ids,
        )

        return text_features

    def get_device(self):
        return str(self.device)

    def get_status(self):
        return {
            "loaded": self.is_loaded,
            "device": str(self.device),
        }

