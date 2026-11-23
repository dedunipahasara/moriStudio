import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadSelfAttention(nn.Module):
    def __init__(
        self,
        embedding_dim: int = 64,
        num_heads: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()

        if embedding_dim % num_heads != 0:
            raise ValueError(
                "embedding_dim must be divisible by num_heads."
            )

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads

        self.query = nn.Linear(embedding_dim, embedding_dim)
        self.key = nn.Linear(embedding_dim, embedding_dim)
        self.value = nn.Linear(embedding_dim, embedding_dim)

        self.output_projection = nn.Linear(
            embedding_dim,
            embedding_dim,
        )

        self.dropout = nn.Dropout(dropout)

    def split_heads(self, tensor: torch.Tensor) -> torch.Tensor:
        batch_size, sequence_length, _ = tensor.shape

        tensor = tensor.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        )

        return tensor.transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,
        padding_mask: torch.Tensor = None,
    ) -> torch.Tensor:

        queries = self.split_heads(self.query(x))
        keys = self.split_heads(self.key(x))
        values = self.split_heads(self.value(x))

        scores = torch.matmul(
            queries,
            keys.transpose(-2, -1),
        ) / (self.head_dim ** 0.5)

        if padding_mask is not None:
            # True indicates a valid token.
            valid_keys = padding_mask.bool()[:, None, None, :]
            scores = scores.masked_fill(
                ~valid_keys,
                torch.finfo(scores.dtype).min,
            )

        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        context = torch.matmul(attention_weights, values)

        context = context.transpose(1, 2).contiguous()

        batch_size, sequence_length, _, _ = context.shape

        context = context.view(
            batch_size,
            sequence_length,
            self.embedding_dim,
        )

        return self.output_projection(context)
