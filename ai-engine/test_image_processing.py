import torch
from PIL import Image

from app.ai.image_processing import (
    ImageEncoder,
    ImageDecoder,
    ImageFeatureExtractor,
    ImagePreprocessor,
    ImagePostprocessor,
)


def main():
    print("Testing Cute3D Image Processing...")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)

    # 1. Create sample image
    sample_image = Image.new(
        "RGB",
        (128, 128),
        color=(120, 180, 220),
    )

    # 2. Preprocess image
    preprocessor = ImagePreprocessor(image_size=32)

    image_tensor = preprocessor.preprocess(sample_image)

    image_batch = image_tensor.unsqueeze(0).to(device)

    print("Preprocessed Shape:", image_batch.shape)

    # 3. Image Encoder
    encoder = ImageEncoder(
        input_channels=3,
        feature_dim=128,
    ).to(device)

    encoded_features = encoder(image_batch)

    print("Encoded Features:", encoded_features.shape)

    # 4. Image Feature Extractor
    feature_extractor = ImageFeatureExtractor(
        input_dim=128,
        feature_dim=128,
    ).to(device)

    image_features = feature_extractor(encoded_features)

    print("Image Features:", image_features.shape)

    # 5. Image Decoder
    decoder = ImageDecoder(
        feature_dim=128,
        image_size=32,
    ).to(device)

    reconstructed_image = decoder(image_features)

    print("Reconstructed Shape:", reconstructed_image.shape)

    # 6. Backpropagation test
    loss = reconstructed_image.mean()
    loss.backward()

    print("Backward Pass: Successful")

    # 7. Postprocess image
    postprocessor = ImagePostprocessor()

    output_path = postprocessor.save_image(
        reconstructed_image[0],
        "outputs/images/image_processing_test.png",
    )

    print("Saved Image:", output_path)

    # 8. Convert back to PIL
    result_image = postprocessor.tensor_to_image(
        reconstructed_image[0]
    )

    print("Final Image Size:", result_image.size)
    print("Image Processing Test Passed!")


if __name__ == "__main__":
    main()
