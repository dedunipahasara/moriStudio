
import torch


class NoiseGenerator:
    def __init__(self, device="cpu"):
        self.device = torch.device(device)

    def generate(
        self,
        batch_size: int,
        channels: int = 3,
        height: int = 32,
        width: int = 32,
        generator=None,
        device=None,
    ):
        target_device = torch.device(device) if device else self.device

        return torch.randn(
            batch_size,
            channels,
            height,
            width,
            device=target_device,
            generator=generator,
        )

    def generate_timesteps(
        self,
        batch_size: int,
        num_timesteps: int,
        device=None,
    ):
        target_device = torch.device(device) if device else self.device

        return torch.randint(
            low=0,
            high=num_timesteps,
            size=(batch_size,),
            device=target_device,
        )
