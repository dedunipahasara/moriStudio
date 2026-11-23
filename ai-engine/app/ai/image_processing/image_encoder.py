import torch
import torch.nn as nn


class ImageEncoder(nn.Module):
    def __init__(
        self,
        input_channels: int = 3,
        feature_dim: int = 128,
        base_channels: int = 32,
    ):
        super().__init__()

        self.encoder = nn.Sequential(
            # 32 x 32 -> 16 x 16
            nn.Conv2d(
                input_channels,
                base_channels,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.BatchNorm2d(base_channels),
            nn.LeakyReLU(0.2, inplace=True),

            # 16 x 16 -> 8 x 8
            nn.Conv2d(
                base_channels,
                base_channels * 2,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.BatchNorm2d(base_channels * 2),
            nn.LeakyReLU(0.2, inplace=True),

            # 8 x 8 -> 4 x 4
            nn.Conv2d(
                base_channels * 2,
                base_channels * 4,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.BatchNorm2d(base_channels * 4),
            nn.LeakyReLU(0.2, inplace=True),

            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        self.projection = nn.Linear(
            base_channels * 4,
            feature_dim,
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        if images.ndim != 4:
            raise ValueError(
                "Images must have shape [batch, channels, height, width]."
            )

        features = self.encoder(images)

        return self.projection(features)
