import torch

from app.ai.generation import DiffusionModel, sample_images


def main():
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)

    model = DiffusionModel(
        text_dim=128,
        image_channels=3,
        image_size=32,
        num_timesteps=100,
        base_channels=16,
        device=str(device),
    ).to(device)

    # Temporary test text features.
    # Later connect this to your TextFeatureExtractor.
    text_features = torch.randn(1, 128, device=device)

    # Test training loss
    clean_images = torch.randn(
        1, 3, 32, 32, device=device
    ).clamp(-1, 1)

    loss = model.training_loss(
        clean_images,
        text_features,
    )

    print("Training Loss:", loss.item())

    loss.backward()
    print("Backward Pass: Successful")

    # Test image sampling
    generated_images = sample_images(
        model=model,
        text_features=text_features,
        num_images=1,
        image_size=32,
        device=device,
        seed=42,
    )

    print("Generated Image Shape:", generated_images.shape)
    print("Generation Test: Successful")


if __name__ == "__main__":
    main()
