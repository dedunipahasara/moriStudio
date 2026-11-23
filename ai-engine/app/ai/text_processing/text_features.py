import torch
import torch.nn as nn


class TextFeatureExtractor(nn.Module):
    def __init__(
        self,
        embedding_dim: int = 64,
        feature_dim: int = 128,
        dropout: float = 0.1,
        padding_idx: int = 0,
    ):
        super().__init__()

        self.padding_idx = padding_idx

        self.feature_network = nn.Sequential(
            nn.Linear(embedding_dim, feature_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.LayerNorm(feature_dim),
        )

    def forward(
        self,
        embeddings: torch.Tensor,
        token_ids: torch.Tensor = None,
    ) -> torch.Tensor:

        if embeddings.ndim != 3:
            raise ValueError(
                "embeddings must have shape "
                "[batch, sequence, embedding_dim]."
            )

        if token_ids is not None:
            if token_ids.shape != embeddings.shape[:2]:
                raise ValueError(
                    "token_ids shape must match embedding batch "
                    "and sequence dimensions."
                )

            mask = token_ids.ne(
                self.padding_idx
            ).unsqueeze(-1).to(embeddings.dtype)

            pooled_features = (
                embeddings * mask
            ).sum(dim=1)

            token_count = mask.sum(dim=1).clamp(min=1.0)

            pooled_features = pooled_features / token_count

        else:
            pooled_features = embeddings.mean(dim=1)

        return self.feature_network(pooled_features)