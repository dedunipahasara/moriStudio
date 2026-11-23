
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class SinusoidalTimeEmbedding(nn.Module):
    def __init__(self, embedding_dim: int):
        super().__init__()
        self.embedding_dim = embedding_dim

    def forward(self, timesteps):
        half_dim = self.embedding_dim // 2

        scale = math.log(10000) / max(half_dim - 1, 1)

        frequencies = torch.exp(
            torch.arange(
                half_dim,
                device=timesteps.device,
                dtype=torch.float32,
            ) * -scale
        )

        angles = timesteps.float().unsqueeze(1) * frequencies.unsqueeze(0)

        embedding = torch.cat(
            [torch.sin(angles), torch.cos(angles)],
            dim=1,
        )

        if embedding.shape[1] < self.embedding_dim:
            embedding = F.pad(
                embedding,
                (0, self.embedding_dim - embedding.shape[1]),
            )

        return embedding


class ConditionalResidualBlock(nn.Module):
    def __init__(
        self,
        channels: int,
        condition_dim: int,
        groups: int = 8,
    ):
        super().__init__()

        self.norm1 = nn.GroupNorm(groups, channels)
        self.conv1 = nn.Conv2d(
            channels, channels, kernel_size=3, padding=1
        )

        self.condition_projection = nn.Linear(
            condition_dim,
            channels * 2,
        )

        self.norm2 = nn.GroupNorm(groups, channels)
        self.conv2 = nn.Conv2d(
            channels, channels, kernel_size=3, padding=1
        )

    def forward(self, x, condition):
        residual = x

        x = self.norm1(x)
        x = F.silu(x)
        x = self.conv1(x)

        scale, shift = self.condition_projection(condition).chunk(
            2, dim=1
        )

        scale = scale.unsqueeze(-1).unsqueeze(-1)
        shift = shift.unsqueeze(-1).unsqueeze(-1)

        x = self.norm2(x)
        x = x * (1.0 + scale) + shift
        x = F.silu(x)
        x = self.conv2(x)

        return x + residual


class DenoisingNetwork(nn.Module):
    def __init__(
        self,
        image_channels: int = 3,
        text_dim: int = 128,
        base_channels: int = 32,
        time_dim: int = 128,
    ):
        super().__init__()

        if base_channels % 8 != 0:
            raise ValueError("base_channels must be divisible by 8")

        self.time_embedding = SinusoidalTimeEmbedding(time_dim)

        self.time_mlp = nn.Sequential(
            nn.Linear(time_dim, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim),
        )

        self.text_projection = nn.Sequential(
            nn.Linear(text_dim, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim),
        )

        self.input_conv = nn.Conv2d(
            image_channels,
            base_channels,
            kernel_size=3,
            padding=1,
        )

        self.block1 = ConditionalResidualBlock(
            base_channels, time_dim
        )

        self.downsample = nn.Conv2d(
            base_channels,
            base_channels * 2,
            kernel_size=4,
            stride=2,
            padding=1,
        )

        self.block2 = ConditionalResidualBlock(
            base_channels * 2, time_dim
        )

        self.middle = ConditionalResidualBlock(
            base_channels * 2, time_dim
        )

        self.upsample = nn.ConvTranspose2d(
            base_channels * 2,
            base_channels,
            kernel_size=4,
            stride=2,
            padding=1,
        )

        self.block3 = ConditionalResidualBlock(
            base_channels, time_dim
        )

        self.output_norm = nn.GroupNorm(8, base_channels)

        self.output_conv = nn.Conv2d(
            base_channels,
            image_channels,
            kernel_size=3,
            padding=1,
        )

    def forward(self, noisy_images, timesteps, text_features):
        time_emb = self.time_embedding(timesteps)
        time_emb = self.time_mlp(time_emb)

        text_emb = self.text_projection(text_features)

        condition = time_emb + text_emb

        x = self.input_conv(noisy_images)

        x = self.block1(x, condition)

        x = self.downsample(x)
        x = self.block2(x, condition)

        x = self.middle(x, condition)

        x = self.upsample(x)
        x = self.block3(x, condition)

        x = self.output_norm(x)
        x = F.silu(x)

        predicted_noise = self.output_conv(x)

        return predicted_noise
