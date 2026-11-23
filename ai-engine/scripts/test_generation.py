
from pathlib import Path
import torch

from app.ai.text_processing import (
    Vocabulary,
    Tokenizer,
    PromptEncoder,
    TextFeatureExtractor,
)

from app.ai.generation.diffusion_model import DiffusionModel

from app.ai.inference import (
    InferenceEngine,
    GenerationEngine,
)


# Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

IMAGE_SIZE = 32
MAX_LENGTH = 32
EMBEDDING_DIM = 64
TEXT_FEATURE_DIM = 128
NUM_TIMESTEPS = 100
BASE_CHANNELS = 16

CHECKPOINT = "checkpoints/image_generator/best_model.pt"
VOCABULARY = "datasets/metadata/vocabulary.json"


def main():

    print("Cute3D Studio - Image Generation Test")
    print("-------------------------------------")

    print(f"Device: {DEVICE}")

    # 1. Load vocabulary
    vocabulary = Vocabulary.load(VOCABULARY)

    tokenizer = Tokenizer(
        vocabulary=vocabulary,
        max_length=MAX_LENGTH,
    )

    print(f"Vocabulary size: {vocabulary.size}")

    # 2. Initialize prompt encoder
    prompt_encoder = PromptEncoder(
        vocab_size=vocabulary.size,
        embedding_dim=EMBEDDING_DIM,
        max_length=MAX_LENGTH,
        padding_idx=vocabulary.pad_id,
    )

    # 3. Initialize text feature extractor
    text_feature_extractor = TextFeatureExtractor(
        embedding_dim=EMBEDDING_DIM,
        feature_dim=TEXT_FEATURE_DIM,
        padding_idx=vocabulary.pad_id,
    )

    # 4. Initialize diffusion model
    model = DiffusionModel(
        text_dim=TEXT_FEATURE_DIM,
        image_channels=3,
        image_size=IMAGE_SIZE,
        num_timesteps=NUM_TIMESTEPS,
        base_channels=BASE_CHANNELS,
        device=DEVICE,
    )

    # 5. Initialize inference engine
    inference_engine = InferenceEngine(
        tokenizer=tokenizer,
        prompt_encoder=prompt_encoder,
        text_feature_extractor=text_feature_extractor,
        model=model,
        device=DEVICE,
    )

    # 6. Load trained checkpoint
    checkpoint_info = inference_engine.load_checkpoint(
        CHECKPOINT
    )

    print("Checkpoint loaded successfully!")
    print(checkpoint_info)

    # 7. Initialize generation engine
    generation_engine = GenerationEngine(
        inference_engine=inference_engine,
        output_dir="outputs/images",
        image_size=IMAGE_SIZE,
        image_channels=3,
    )

    # 8. Generate image
    prompt = "a cute robot"

    print(f"\nPrompt: {prompt}")
    print("Generating image...")

    result = generation_engine.generate(
        prompt=prompt,
        num_images=1,
        seed=42,
        save=True,
    )

    print("\nGeneration completed!")

    for path in result["paths"]:
        print(f"Saved image: {path}")

    print(f"Generated images: {len(result['images'])}")


if __name__ == "__main__":
    main()
