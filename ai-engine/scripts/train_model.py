
import csv
import torch

from pathlib import Path

from app.ai.text_processing.tokenizer import Tokenizer
from app.ai.text_processing.prompt_encoder import PromptEncoder
from app.ai.text_processing.text_features import TextFeatureExtractor

from app.ai.image_processing.image_preprocessing import ImagePreprocessor

from app.ai.generation.diffusion_model import DiffusionModel

from app.ai.training import (
    create_train_val_dataloaders,
    create_optimizer,
    create_scheduler,
    CheckpointManager,
    Trainer,
)


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

IMAGE_SIZE = 32
IMAGE_CHANNELS = 3
MAX_LENGTH = 32

EMBEDDING_DIM = 64
TEXT_FEATURE_DIM = 128

BATCH_SIZE = 1
EPOCHS = 20
LEARNING_RATE = 1e-4

NUM_TIMESTEPS = 100
BASE_CHANNELS = 16

TRAIN_METADATA = Path("datasets/metadata/train.csv")
VAL_METADATA = Path("datasets/metadata/val.csv")
CAPTIONS_METADATA = Path("datasets/metadata/captions.csv")

IMAGE_DIRECTORY = Path("datasets/raw")
VOCABULARY_PATH = Path("datasets/metadata/vocabulary.json")

CHECKPOINT_DIRECTORY = Path("checkpoints/image_generator")


# --------------------------------------------------
# DEVICE CONFIGURATION
# --------------------------------------------------

def get_device():

    if torch.cuda.is_available():

        device = torch.device("cuda")

        print("CUDA is available.")
        print("GPU:", torch.cuda.get_device_name(0))

    else:

        device = torch.device("cpu")

        print("CUDA is not available.")
        print("Using CPU.")

    return device


# --------------------------------------------------
# VOCABULARY CREATION
# --------------------------------------------------

def prepare_tokenizer():

    tokenizer = Tokenizer(max_length=MAX_LENGTH)

    if VOCABULARY_PATH.exists():

        print("\nLoading existing vocabulary...")

        tokenizer.load_vocabulary(
            str(VOCABULARY_PATH)
        )

    else:

        print("\nCreating vocabulary...")

        if not CAPTIONS_METADATA.exists():
            raise FileNotFoundError(
                f"Captions metadata not found: {CAPTIONS_METADATA}"
            )

        captions = []

        with CAPTIONS_METADATA.open(
            "r",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                caption = row.get("caption", "").strip()

                if caption:
                    captions.append(caption)

        if not captions:
            raise ValueError(
                "No valid captions found in captions.csv"
            )

        tokenizer.build_vocabulary(captions)

        tokenizer.save_vocabulary(
            str(VOCABULARY_PATH)
        )

        print("Vocabulary successfully created.")

    print("Vocabulary size:", tokenizer.vocabulary.size)

    return tokenizer


# --------------------------------------------------
# DATASET VALIDATION
# --------------------------------------------------

def validate_dataset():

    required_paths = [
        TRAIN_METADATA,
        VAL_METADATA,
        CAPTIONS_METADATA,
        IMAGE_DIRECTORY,
    ]

    for path in required_paths:

        if not path.exists():

            raise FileNotFoundError(
                f"Required dataset path not found: {path}"
            )

    print("\nDataset files verified.")


# --------------------------------------------------
# MODEL INITIALIZATION
# --------------------------------------------------

def initialize_models(tokenizer, device):

    print("\nInitializing image preprocessor...")

    image_preprocessor = ImagePreprocessor(
        image_size=IMAGE_SIZE,
        channels=IMAGE_CHANNELS,
    )

    print("Initializing prompt encoder...")

    prompt_encoder = PromptEncoder(
        vocab_size=tokenizer.vocabulary.size,
        embedding_dim=EMBEDDING_DIM,
        max_length=MAX_LENGTH,
    )

    print("Initializing text feature extractor...")

    text_feature_extractor = TextFeatureExtractor(
        embedding_dim=EMBEDDING_DIM,
        feature_dim=TEXT_FEATURE_DIM,
    )

    print("Initializing diffusion model...")

    model = DiffusionModel(
        text_dim=TEXT_FEATURE_DIM,
        image_channels=IMAGE_CHANNELS,
        image_size=IMAGE_SIZE,
        num_timesteps=NUM_TIMESTEPS,
        base_channels=BASE_CHANNELS,
        device=str(device),
    )

    return (
        image_preprocessor,
        prompt_encoder,
        text_feature_extractor,
        model,
    )


# --------------------------------------------------
# DATALOADER INITIALIZATION
# --------------------------------------------------

def initialize_dataloaders(
    tokenizer,
    image_preprocessor,
):

    print("\nPreparing training and validation datasets...")

    train_loader, val_loader = create_train_val_dataloaders(
        train_metadata=str(TRAIN_METADATA),
        val_metadata=str(VAL_METADATA),
        image_dir=str(IMAGE_DIRECTORY),
        tokenizer=tokenizer,
        image_preprocessor=image_preprocessor,
        batch_size=BATCH_SIZE,
        num_workers=0,
        max_length=MAX_LENGTH,
    )

    print("Training batches:", len(train_loader))
    print("Validation batches:", len(val_loader))

    return train_loader, val_loader


# --------------------------------------------------
# TRAINING SETUP
# --------------------------------------------------

def initialize_trainer(
    model,
    prompt_encoder,
    text_feature_extractor,
    device,
):

    print("\nInitializing optimizer...")

    optimizer = create_optimizer(
        model=model,
        prompt_encoder=prompt_encoder,
        text_feature_extractor=text_feature_extractor,
        learning_rate=LEARNING_RATE,
    )

    print("Initializing learning rate scheduler...")

    lr_scheduler = create_scheduler(
        optimizer,
        scheduler_type="plateau",
    )

    print("Initializing checkpoint manager...")

    checkpoint_manager = CheckpointManager(
        checkpoint_dir=str(CHECKPOINT_DIRECTORY)
    )

    trainer = Trainer(
        model=model,
        prompt_encoder=prompt_encoder,
        text_feature_extractor=text_feature_extractor,
        optimizer=optimizer,
        scheduler=lr_scheduler,
        device=device,
        checkpoint_manager=checkpoint_manager,
    )

    return trainer


# --------------------------------------------------
# MAIN TRAINING FUNCTION
# --------------------------------------------------

def main():

    print("=" * 55)
    print("             CUTE3D AI ENGINE")
    print("             MODEL TRAINING")
    print("=" * 55)

    # 1. Device
    device = get_device()

    # 2. Dataset validation
    validate_dataset()

    # 3. Tokenizer and vocabulary
    tokenizer = prepare_tokenizer()

    # 4. Initialize models
    (
        image_preprocessor,
        prompt_encoder,
        text_feature_extractor,
        model,
    ) = initialize_models(tokenizer, device)

    # 5. Prepare dataloaders
    train_loader, val_loader = initialize_dataloaders(
        tokenizer,
        image_preprocessor,
    )

    # 6. Initialize trainer
    trainer = initialize_trainer(
        model,
        prompt_encoder,
        text_feature_extractor,
        device,
    )

    # 7. Start training
    print("\nStarting model training...")
    print("Epochs:", EPOCHS)
    print("Batch size:", BATCH_SIZE)
    print("Learning rate:", LEARNING_RATE)

    history = trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=EPOCHS,
        save_every=1,
    )

    # 8. Training completed
    print("\n" + "=" * 55)
    print("TRAINING COMPLETED")
    print("=" * 55)

    print("Total epochs:", len(history))

    print(
        "Checkpoint directory:",
        CHECKPOINT_DIRECTORY.resolve()
    )

    if CHECKPOINT_DIRECTORY.exists():

        for checkpoint in CHECKPOINT_DIRECTORY.glob("*.pt"):
            print("Saved checkpoint:", checkpoint.name)


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print("\nTraining interrupted by user.")

    except Exception as error:

        print("\nTRAINING FAILED")
        print("Error:", error)

        raise

