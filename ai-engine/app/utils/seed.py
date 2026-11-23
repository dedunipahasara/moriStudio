import random
import numpy as np
import torch


def set_seed(seed=42, deterministic=True):
    """
    Set random seeds for reproducible results.
    """

    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError("Seed must be an integer.")

    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    return seed


def get_generator(seed=42, device="cpu"):
    """
    Create a seeded PyTorch random generator.
    """

    generator = torch.Generator(device=device)
    generator.manual_seed(seed)

    return generator
