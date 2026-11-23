import torch
import torch.nn as nn

from app.ai.neural_networks.embeddings import TokenPositionEmbedding
from app.ai.neural_networks.transformer import TransformerBlock


class TextEncoder(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        max_length: int = 32,
        dropout: float = 0.1,
        padding_idx: int = 0,
    ):
        super().__init__()

        self.padding_idx = padding_idx

        self.embeddings = TokenPositionEmbedding(
            vocab_size=vocab_size,
            embedding_dim=embedding_dim,
            max_length=max_length,
            padding_idx=padding_idx,
        )

        self.transformer_layers = nn.ModuleList([
            TransformerBlock(
                embedding_dim=embedding_dim,
                num_heads=num_heads,
                feedforward_dim=embedding_dim * 2,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(embedding_dim)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [batch, sequence].")

        padding_mask = token_ids.ne(self.padding_idx)

        x = self.embeddings(token_ids)

        for layer in self.transformer_layers:
            x = layer(x, padding_mask=padding_mask)

        x = self.final_norm(x)

        # Masked mean pooling: ignore PAD tokens.
        mask = padding_mask.unsqueeze(-1).to(x.dtype)

        pooled = (x * mask).sum(dim=1)
        token_counts = mask.sum(dim=1).clamp(min=1.0)

        return pooled / token_counts
