import torch
from torch.utils.data import DataLoader

from app.ai.training.dataset import Cute3DDataset


def create_dataloader(
    metadata_file,
    image_dir,
    tokenizer,
    image_preprocessor,
    batch_size=2,
    shuffle=True,
    num_workers=0,
    max_length=32,
    drop_last=False,
):
    dataset = Cute3DDataset(
        metadata_file=metadata_file,
        image_dir=image_dir,
        tokenizer=tokenizer,
        image_preprocessor=image_preprocessor,
        max_length=max_length,
    )

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=drop_last,
    )

    return dataloader


def create_train_val_dataloaders(
    train_metadata,
    val_metadata,
    image_dir,
    tokenizer,
    image_preprocessor,
    batch_size=2,
    num_workers=0,
    max_length=32,
):
    train_loader = create_dataloader(
        metadata_file=train_metadata,
        image_dir=image_dir,
        tokenizer=tokenizer,
        image_preprocessor=image_preprocessor,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        max_length=max_length,
    )

    val_loader = create_dataloader(
        metadata_file=val_metadata,
        image_dir=image_dir,
        tokenizer=tokenizer,
        image_preprocessor=image_preprocessor,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        max_length=max_length,
    )

    return train_loader, val_loader
