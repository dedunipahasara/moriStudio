
import torch

from app.ai.neural_networks import Cute3DImageGenerator


def main():
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)

    model = Cute3DImageGenerator(
        vocab_size=100,
        embedding_dim=64,
        num_heads=4,
        num_layers=2,
        max_length=32,
        noise_dim=32,
        image_size=32,
        padding_idx=0,
    ).to(device)

    token_ids = torch.tensor(
        [[2, 4, 5, 6, 7, 3]],
        dtype=torch.long,
        device=device,
    )

    model.train()

    generated_image = model(token_ids)

    print("Input Shape:", token_ids.shape)
    print("Output Shape:", generated_image.shape)

    loss = generated_image.mean()
    loss.backward()

    print("Backward Pass: Successful")

    generated_image = model.generate(
        token_ids,
        seed=42,
    )

    print("Generation Shape:", generated_image.shape)
    print("Image Generator Test Passed!")


if __name__ == "__main__":
    main()
