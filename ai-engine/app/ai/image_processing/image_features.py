import torch
import torch.nn as nn


class ImageFeatureExtractor(nn.Module):
    def __init__(
        self,
        input_dim: int = 128,
        feature_dim: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.feature_network = nn.Sequential(
            nn.Linear(input_dim, feature_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.LayerNorm(feature_dim),
        )

    def forward(self, image_features: torch.Tensor) -> torch.Tensor:
        if image_features.ndim != 2:
            raise ValueError(
                "Image features must have shape [batch, features]."
            )

        return self.feature_network(image_features)
