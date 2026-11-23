import torch
import torch.nn as nn

from app.ai.neural_networks.encoder import TextEncoder
from app.ai.neural_networks.decoder import ImageDecoder


class Cute3DImageGenerator(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        max_length: int = 32,
        noise_dim: int = 32,
        image_size: int = 32,
        padding_idx: int = 0,
    ):
        super().__init__()

        self.text_encoder = TextEncoder(
            vocab_size=vocab_size,
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            num_layers=num_layers,
            max_length=max_length,
            padding_idx=padding_idx,
        )

        self.image_decoder = ImageDecoder(
            condition_dim=embedding_dim,
            noise_dim=noise_dim,
            image_size=image_size,
        )

        self.image_size = image_size
        self.noise_dim = noise_dim

    def forward(
        self,
        token_ids: torch.Tensor,
        noise: torch.Tensor = None,
    ) -> torch.Tensor:

        text_features = self.text_encoder(token_ids)

        generated_image = self.image_decoder(
            text_features=text_features,
            noise=noise,
        )

        return generated_image

    def generate(
        self,
        token_ids: torch.Tensor,
        seed: int = None,
    ) -> torch.Tensor:

        self.eval()

        device = next(self.parameters()).device
        token_ids = token_ids.to(device)

        generator = None

        if seed is not None:
            generator = torch.Generator(device=device)
            generator.manual_seed(seed)

        with torch.no_grad():
            noise = torch.randn(
                token_ids.shape[0],
                self.noise_dim,
                device=device,
                generator=generator,
            )

            return self.forward(
                token_ids=token_ids,
                noise=noise,
            )
