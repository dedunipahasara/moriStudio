import torch


def create_scheduler(
    optimizer,
    scheduler_type="cosine",
    epochs=20,
    step_size=5,
    gamma=0.5,
):
    if scheduler_type == "cosine":
        return torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=max(epochs, 1),
            eta_min=1e-6,
        )

    if scheduler_type == "step":
        return torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=step_size,
            gamma=gamma,
        )

    if scheduler_type == "plateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=gamma,
            patience=3,
            min_lr=1e-6,
        )

    raise ValueError(
        f"Unsupported scheduler type: {scheduler_type}"
    )
