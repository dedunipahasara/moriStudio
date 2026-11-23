import torch
import torch.nn as nn


class TokenPositionEmbedding(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 64,
        max_length: int = 32,
        padding_idx: int = 0,
    ):
        super().__init__()

        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=padding_idx,
        )

        self.position_embedding = nn.Embedding(
            max_length,
            embedding_dim,
        )

        self.max_length = max_length

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        batch_size, sequence_length = token_ids.shape

        if sequence_length > self.max_length:
            raise ValueError(
                f"Sequence length cannot exceed {self.max_length}."
            )

        positions = torch.arange(
            sequence_length,
            device=token_ids.device,
        ).unsqueeze(0).expand(batch_size, -1)

        token_vectors = self.token_embedding(token_ids)
        position_vectors = self.position_embedding(positions)

        return token_vectors + position_vectors
