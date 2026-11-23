
import torch


class NoiseScheduler:
    def __init__(
        self,
        num_timesteps: int = 100,
        beta_start: float = 0.0001,
        beta_end: float = 0.2,
        device: str = "cpu",
    ):
        if num_timesteps < 2:
            raise ValueError("num_timesteps must be at least 2")

        if not (0 < beta_start < beta_end < 1):
            raise ValueError("Invalid beta schedule")

        self.num_timesteps = num_timesteps
        self.device = torch.device(device)

        self.betas = torch.linspace(
            beta_start,
            beta_end,
            num_timesteps,
            dtype=torch.float32,
            device=self.device,
        )

        self.alphas = 1.0 - self.betas
        self.alpha_cumprod = torch.cumprod(
            self.alphas, dim=0
        )

        self.sqrt_alpha_cumprod = torch.sqrt(
            self.alpha_cumprod
        )

        self.sqrt_one_minus_alpha_cumprod = torch.sqrt(
            1.0 - self.alpha_cumprod
        )

        self.sqrt_recip_alphas = torch.sqrt(
            1.0 / self.alphas
        )

        alpha_cumprod_previous = torch.cat([
            torch.ones(1, device=self.device),
            self.alpha_cumprod[:-1],
        ])

        self.posterior_variance = (
            self.betas
            * (1.0 - alpha_cumprod_previous)
            / (1.0 - self.alpha_cumprod)
        )

    def extract(self, values, timesteps, shape):
        values = values.to(timesteps.device)
        result = values.gather(0, timesteps.long())

        return result.reshape(
            timesteps.shape[0],
            *([1] * (len(shape) - 1)),
        )

    def add_noise(self, clean_images, noise, timesteps):
        sqrt_alpha = self.extract(
            self.sqrt_alpha_cumprod,
            timesteps,
            clean_images.shape,
        )

        sqrt_one_minus = self.extract(
            self.sqrt_one_minus_alpha_cumprod,
            timesteps,
            clean_images.shape,
        )

        return (
            sqrt_alpha * clean_images
            + sqrt_one_minus * noise
        )

    def get_posterior_variance(self, timesteps, shape):
        return self.extract(
            self.posterior_variance,
            timesteps,
            shape,
        )

    def get_beta(self, timesteps, shape):
        return self.extract(self.betas, timesteps, shape)

    def get_alpha(self, timesteps, shape):
        return self.extract(self.alphas, timesteps, shape)

    def get_alpha_cumprod(self, timesteps, shape):
        return self.extract(
            self.alpha_cumprod,
            timesteps,
            shape,
        )

