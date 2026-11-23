import torch
import torch.nn as nn

from app.ai.neural_networks.embeddings import TokenPositionEmbedding


class PromptEncoder(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 64,
        max_length: int = 32,
        padding_idx: int = 0,
    ):
        super().__init__()

        self.embedding = TokenPositionEmbedding(
            vocab_size=vocab_size,
            embedding_dim=embedding_dim,
            max_length=max_length,
            padding_idx=padding_idx,
        )

        self.embedding_norm = nn.LayerNorm(embedding_dim)

        self.padding_idx = padding_idx

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:

        if token_ids.ndim != 2:
            raise ValueError(
                "token_ids must have shape [batch, sequence]."
            )

        if token_ids.dtype != torch.long:
            raise TypeError("token_ids must use torch.long dtype.")

        embeddings = self.embedding(token_ids)

        embeddings = self.embedding_norm(embeddings)

        # Zero out padding token representations.
        padding_mask = token_ids.ne(
            self.padding_idx
        ).unsqueeze(-1)

        embeddings = embeddings * padding_mask.to(
            embeddings.dtype
        )

        return embeddings