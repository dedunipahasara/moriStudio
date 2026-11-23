
import torch

from app.ai.generation.noise_generator import NoiseGenerator


@torch.no_grad()
def sample_images(
    model,
    text_features,
    num_images: int = 1,
    image_size: int = 32,
    image_channels: int = 3,
    device=None,
    seed=None,
):
    """
    Generate images using reverse diffusion.

    model:
        Trained DiffusionModel.

    text_features:
        TextFeatureExtractor output with shape [B, 128].

    Returns:
        Generated images with shape [B, 3, 32, 32].
        Values are in the range [-1, 1].
    """

    model.eval()

    if device is None:
        device = next(model.parameters()).device

    device = torch.device(device)

    text_features = text_features.to(device)

    if text_features.shape[0] == 1 and num_images > 1:
        text_features = text_features.repeat(num_images, 1)

    if text_features.shape[0] != num_images:
        raise ValueError(
            "text_features batch size must match num_images"
        )

    generator = None

    if seed is not None:
        generator = torch.Generator(device=device)
        generator.manual_seed(seed)

    noise_generator = NoiseGenerator(device=device)

    images = noise_generator.generate(
        batch_size=num_images,
        channels=image_channels,
        height=image_size,
        width=image_size,
        generator=generator,
        device=device,
    )

    scheduler = model.noise_scheduler
    total_steps = model.num_timesteps

    for step in reversed(range(total_steps)):
        timesteps = torch.full(
            (num_images,),
            step,
            device=device,
            dtype=torch.long,
        )

        predicted_noise = model(
            images,
            timesteps,
            text_features,
        )

        beta = scheduler.get_beta(timesteps, images.shape)
        alpha = scheduler.get_alpha(timesteps, images.shape)
        alpha_bar = scheduler.get_alpha_cumprod(
            timesteps,
            images.shape,
        )

        sqrt_recip_alpha = torch.rsqrt(alpha)

        predicted_mean = sqrt_recip_alpha * (
            images
            - beta * predicted_noise
            / torch.sqrt(1.0 - alpha_bar)
        )

        if step > 0:
            variance = scheduler.get_posterior_variance(
                timesteps,
                images.shape,
            )

            if generator is None:
                random_noise = torch.randn_like(images)
            else:
                random_noise = torch.randn(
                    images.shape,
                    device=device,
                    dtype=images.dtype,
                    generator=generator,
                )

            images = (
                predicted_mean
                + torch.sqrt(variance.clamp(min=1e-20))
                * random_noise
            )
        else:
            images = predicted_mean

    return images.clamp(-1.0, 1.0)
