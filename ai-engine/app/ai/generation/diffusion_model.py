
import torch
import torch.nn as nn
import torch.nn.functional as F

from app.ai.generation.noise_scheduler import NoiseScheduler
from app.ai.generation.denoising_network import DenoisingNetwork
from app.ai.generation.noise_generator import NoiseGenerator


class DiffusionModel(nn.Module):
    def __init__(
        self,
        text_dim: int = 128,
        image_channels: int = 3,
        image_size: int = 32,
        num_timesteps: int = 100,
        base_channels: int = 32,
        device: str = "cpu",
    ):
        super().__init__()

        self.image_size = image_size
        self.image_channels = image_channels
        self.num_timesteps = num_timesteps

        self.denoising_network = DenoisingNetwork(
            image_channels=image_channels,
            text_dim=text_dim,
            base_channels=base_channels,
        )

        self.noise_scheduler = NoiseScheduler(
            num_timesteps=num_timesteps,
            device=device,
        )

        self.noise_generator = NoiseGenerator(device=device)

    def forward(self, noisy_images, timesteps, text_features):
        """
        Predict the noise present in noisy images.
        """
        return self.denoising_network(
            noisy_images,
            timesteps,
            text_features,
        )

    def training_loss(self, clean_images, text_features):
        """
        Calculate DDPM noise prediction loss.

        clean_images: [B, 3, 32, 32], normalized to [-1, 1]
        text_features: [B, 128]
        """
        batch_size = clean_images.shape[0]
        device = clean_images.device

        timesteps = self.noise_generator.generate_timesteps(
            batch_size=batch_size,
            num_timesteps=self.num_timesteps,
            device=device,
        )

        noise = torch.randn_like(clean_images)

        noisy_images = self.noise_scheduler.add_noise(
            clean_images,
            noise,
            timesteps,
        )

        predicted_noise = self.forward(
            noisy_images,
            timesteps,
            text_features,
        )

        loss = F.mse_loss(predicted_noise, noise)

        return loss

    def get_denoising_network(self):
        return self.denoising_network
