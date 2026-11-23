import torch
import torch.nn as nn


class ImageDecoder(nn.Module):
    def __init__(
        self,
        condition_dim: int = 64,
        noise_dim: int = 32,
        image_channels: int = 3,
        base_channels: int = 32,
        image_size: int = 32,
    ):
        super().__init__()

        if image_size != 32:
            raise ValueError("This prototype decoder supports 32x32 images.")

        self.noise_dim = noise_dim
        self.image_size = image_size

        input_dim = condition_dim + noise_dim

        self.project = nn.Sequential(
            nn.Linear(input_dim, base_channels * 4 * 4 * 4),
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
            nn.GroupNorm(8, base_channels * 2),
            nn.ReLU(inplace=True),

            # 8 x 8 -> 16 x 16
            nn.ConvTranspose2d(
                base_channels * 2,
                base_channels,
                kernel_size=4,
                stride=2,
                padding=1,
            ),
            nn.GroupNorm(8, base_channels),
            nn.ReLU(inplace=True),

            # 16 x 16 -> 32 x 32
            nn.ConvTranspose2d(
                base_channels,
                image_channels,
                kernel_size=4,
                stride=2,
                padding=1,
            ),

            nn.Tanh(),
        )

    def forward(
        self,
        text_features: torch.Tensor,
        noise: torch.Tensor = None,
    ) -> torch.Tensor:

        batch_size = text_features.shape[0]
        device = text_features.device
        dtype = text_features.dtype

        if noise is None:
            noise = torch.randn(
                batch_size,
                self.noise_dim,
                device=device,
                dtype=dtype,
            )

        if noise.shape != (batch_size, self.noise_dim):
            raise ValueError(
                f"Noise must have shape [{batch_size}, {self.noise_dim}]."
            )

        combined = torch.cat([text_features, noise], dim=1)

        x = self.project(combined)

        x = x.view(
            batch_size,
            -1,
            4,
            4,
        )

        return self.decoder(x)
