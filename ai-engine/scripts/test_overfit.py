import torch
from pathlib import Path

from app.ai.text_processing.tokenizer import Tokenizer
from app.ai.text_processing.prompt_encoder import PromptEncoder
from app.ai.text_processing.text_features import TextFeatureExtractor
from app.ai.image_processing.image_preprocessing import ImagePreprocessor
from app.ai.generation.diffusion_model import DiffusionModel
from app.ai.training.dataset import Cute3DDataset


# Device configuration
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# Model configuration
IMAGE_SIZE = 32
EMBEDDING_DIM = 64
TEXT_DIM = 128
TIMESTEPS = 100
BASE_CHANNELS = 16
TRAINING_STEPS = 500

print("Device:", DEVICE)


# Load existing vocabulary
tokenizer = Tokenizer(max_length=32)

tokenizer.load_vocabulary(
    "datasets/metadata/vocabulary.json"
)


# Load one training sample
dataset = Cute3DDataset(
    metadata_file="datasets/metadata/train.csv",
    image_dir="datasets/raw",
    tokenizer=tokenizer,
    image_preprocessor=ImagePreprocessor(32, 3),
)

sample = dataset[0]

images = sample["images"].unsqueeze(0).to(DEVICE)
token_ids = sample["token_ids"].unsqueeze(0).to(DEVICE)

print("Caption:", sample["captions"])
print("Image shape:", images.shape)


# Initialize prompt encoder
prompt_encoder = PromptEncoder(
    vocab_size=tokenizer.vocabulary.size,
    embedding_dim=EMBEDDING_DIM,
    max_length=32,
).to(DEVICE)


# Initialize text feature extractor
text_extractor = TextFeatureExtractor(
    embedding_dim=EMBEDDING_DIM,
    feature_dim=TEXT_DIM,
).to(DEVICE)


# Initialize diffusion model
# Uses beta_end=0.2 from the updated NoiseScheduler
model = DiffusionModel(
    text_dim=TEXT_DIM,
    image_channels=3,
    image_size=IMAGE_SIZE,
    num_timesteps=TIMESTEPS,
    base_channels=BASE_CHANNELS,
    device=str(DEVICE),
).to(DEVICE)


# Create optimizer
trainable_parameters = (
    list(model.parameters())
    + list(prompt_encoder.parameters())
    + list(text_extractor.parameters())
)

optimizer = torch.optim.AdamW(
    trainable_parameters,
    lr=1e-4,
)


# Single-image overfit training
print("\nStarting single-image overfit test...")

for step in range(1, TRAINING_STEPS + 1):

    model.train()
    prompt_encoder.train()
    text_extractor.train()

    optimizer.zero_grad(set_to_none=True)

    embeddings = prompt_encoder(token_ids)

    text_features = text_extractor(
        embeddings,
        token_ids,
    )

    loss = model.training_loss(
        images,
        text_features,
    )

    loss.backward()

    torch.nn.utils.clip_grad_norm_(
        trainable_parameters,
        1.0,
    )

    optimizer.step()

    if step % 50 == 0:
        print(
            f"Step [{step}/{TRAINING_STEPS}] "
            f"Loss: {loss.item():.6f}"
        )


print("\nOverfit test completed.")


# Save checkpoint separately
checkpoint_dir = Path(
    "checkpoints/overfit_test_beta020"
)

checkpoint_dir.mkdir(
    parents=True,
    exist_ok=True,
)

checkpoint_path = (
    checkpoint_dir / "overfit_model.pt"
)


torch.save(
    {
        "model_state_dict": model.state_dict(),
        "prompt_encoder_state_dict": prompt_encoder.state_dict(),
        "text_feature_extractor_state_dict": (
            text_extractor.state_dict()
        ),
        "caption": sample["captions"],
        "image_size": IMAGE_SIZE,
        "timesteps": TIMESTEPS,
        "base_channels": BASE_CHANNELS,
        "vocab_size": tokenizer.vocabulary.size,
        "beta_start": 0.0001,
        "beta_end": 0.2,
    },
    checkpoint_path,
)


print(
    f"\nOverfit checkpoint saved: {checkpoint_path}"
)
print("Training and checkpoint saving completed.")
