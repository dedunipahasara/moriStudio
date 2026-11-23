import torch
import torch.nn as nn

from app.ai.neural_networks.attention import MultiHeadSelfAttention


class TransformerBlock(nn.Module):
    def __init__(
        self,
        embedding_dim: int = 64,
        num_heads: int = 4,
        feedforward_dim: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.attention = MultiHeadSelfAttention(
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
        )

        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)

        self.feedforward = nn.Sequential(
            nn.Linear(embedding_dim, feedforward_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(feedforward_dim, embedding_dim),
        )

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        padding_mask: torch.Tensor = None,
    ) -> torch.Tensor:

        attention_output = self.attention(
            x,
            padding_mask=padding_mask,
        )

        x = self.norm1(x + self.dropout(attention_output))

        feedforward_output = self.feedforward(x)

        x = self.norm2(x + self.dropout(feedforward_output))

        return x
