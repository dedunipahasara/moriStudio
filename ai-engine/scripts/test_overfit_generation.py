import torch
from pathlib import Path

from app.ai.text_processing.tokenizer import Tokenizer
from app.ai.text_processing.prompt_encoder import PromptEncoder
from app.ai.text_processing.text_features import TextFeatureExtractor
from app.ai.generation.diffusion_model import DiffusionModel
from app.ai.generation.sampling import sample_images
from app.ai.generation.noise_scheduler import NoiseScheduler
from app.ai.inference.inference_engine import InferenceEngine
from app.ai.image_processing.image_postprocessing import ImagePostprocessor


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

IMAGE_SIZE = 32
EMBEDDING_DIM = 64
TEXT_DIM = 128
TIMESTEPS = 100
BASE_CHANNELS = 16

CHECKPOINT = Path(
    "checkpoints/overfit_test_beta020/overfit_model.pt"
)

OUTPUT_DIR = Path(
    "outputs/overfit_test_beta020"
)

PROMPT = "A cute 3D cartoon boy wearing a blue jacket and backpack."

SEED = 42

print("Device:", DEVICE)


# --------------------------------------------------
# Check checkpoint
# --------------------------------------------------

if not CHECKPOINT.exists():
    raise FileNotFoundError(
        f"Checkpoint not found: {CHECKPOINT}"
    )


# --------------------------------------------------
# Load vocabulary
# --------------------------------------------------

tokenizer = Tokenizer(max_length=32)

tokenizer.load_vocabulary(
    "datasets/metadata/vocabulary.json"
)

print("Vocabulary size:", tokenizer.vocabulary.size)


# --------------------------------------------------
# Initialize model components
# --------------------------------------------------

prompt_encoder = PromptEncoder(
    vocab_size=tokenizer.vocabulary.size,
    embedding_dim=EMBEDDING_DIM,
    max_length=32,
)

text_extractor = TextFeatureExtractor(
    embedding_dim=EMBEDDING_DIM,
    feature_dim=TEXT_DIM,
)

model = DiffusionModel(
    text_dim=TEXT_DIM,
    image_channels=3,
    image_size=IMAGE_SIZE,
    num_timesteps=TIMESTEPS,
    base_channels=BASE_CHANNELS,
    device=str(DEVICE),
)


# --------------------------------------------------
# Ensure generation uses the training noise schedule
# --------------------------------------------------

model.noise_scheduler = NoiseScheduler(
    num_timesteps=TIMESTEPS,
    beta_start=0.0001,
    beta_end=0.2,
    device=str(DEVICE),
)


# --------------------------------------------------
# Initialize inference engine
# --------------------------------------------------

engine = InferenceEngine(
    tokenizer=tokenizer,
    prompt_encoder=prompt_encoder,
    text_feature_extractor=text_extractor,
    model=model,
    device=DEVICE,
)


# --------------------------------------------------
# Load trained checkpoint
# --------------------------------------------------

result = engine.load_checkpoint(str(CHECKPOINT))

print("Checkpoint loaded:", result)


# --------------------------------------------------
# Encode prompt
# --------------------------------------------------

print("Prompt:", PROMPT)

text_features = engine.encode_prompt(PROMPT)

print("Text features shape:", text_features.shape)


# --------------------------------------------------
# Generate image
# --------------------------------------------------

engine.model.eval()
engine.prompt_encoder.eval()
engine.text_feature_extractor.eval()

with torch.no_grad():
    images = sample_images(
        model=engine.model,
        text_features=text_features,
        num_images=1,
        image_size=IMAGE_SIZE,
        image_channels=3,
        device=DEVICE,
        seed=SEED,
    )


# --------------------------------------------------
# Save generated image
# --------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

postprocessor = ImagePostprocessor()

output_path = OUTPUT_DIR / "overfit_boy_beta020.png"

postprocessor.save_image(
    images[0].detach().cpu(),
    str(output_path),
)

print("Generated image saved:", output_path)
print("Generation completed.")
