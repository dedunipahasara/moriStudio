import torch
import torch.nn as nn


class ImageDecoder(nn.Module):
    def __init__(
        self,
        feature_dim: int = 128,
        output_channels: int = 3,
        base_channels: int = 32,
        image_size: int = 32,
    ):
        super().__init__()

        if image_size != 32:
            raise ValueError(
                "This image decoder currently supports 32x32 images."
            )

        self.image_size = image_size

        self.project = nn.Sequential(
            nn.Linear(
                feature_dim,
                base_channels * 4 * 4 * 4,
            ),
            nn.ReLU(inplace=True),
        )

        self.decoder = nn.Sequential(
            # 4 x 4 -> 8 x 8
            nn.ConvTranspose2d(
                base_channels * 4,
                base_channels * 2,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.BatchNorm2d(base_channels * 2),
            nn.ReLU(inplace=True),

            # 8 x 8 -> 16 x 16
            nn.ConvTranspose2d(
                base_channels * 2,
                base_channels,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(inplace=True),

            # 16 x 16 -> 32 x 32
            nn.ConvTranspose2d(
                base_channels,
                output_channels,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.Tanh(),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        if features.ndim != 2:
            raise ValueError(
                "Features must have shape [batch, feature_dim]."
            )

        x = self.project(features)

        x = x.view(
            x.shape[0],
            -1,
            4,
            4,
        )

        return self.decoder(x)
