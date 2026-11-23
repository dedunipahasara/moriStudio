import logging

from fastapi import HTTPException, Request, status

import torch


logger = logging.getLogger(__name__)


# --------------------------------------------------
# DEVICE DETECTION
# --------------------------------------------------

def get_device() -> torch.device:
    """
    Detect the available PyTorch computation device.

    Returns:
        torch.device: CUDA device if available,
                      otherwise CPU.
    """

    if torch.cuda.is_available():

        device = torch.device("cuda")

        logger.info(
            "PyTorch CUDA device selected: %s",
            torch.cuda.get_device_name(0),
        )

        return device

    logger.info(
        "PyTorch CUDA is unavailable. Using CPU."
    )

    return torch.device("cpu")


# --------------------------------------------------
# GENERATION PIPELINE
# --------------------------------------------------

def get_generation_pipeline(request: Request):
    """
    Retrieve the image generation pipeline
    from FastAPI application state.
    """

    pipeline = getattr(
        request.app.state,
        "generation_pipeline",
        None,
    )

    if pipeline is None:

        logger.error(
            "Generation pipeline has not been initialized."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image generation service is unavailable.",
        )

    return pipeline


# --------------------------------------------------
# TRAINING SERVICE
# --------------------------------------------------

def get_training_service(request: Request):
    """
    Retrieve the model training service
    from FastAPI application state.
    """

    training_service = getattr(
        request.app.state,
        "training_service",
        None,
    )

    if training_service is None:

        logger.error(
            "Training service has not been initialized."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model training service is unavailable.",
        )

    return training_service


# --------------------------------------------------
# UPSCALING SERVICE
# --------------------------------------------------

def get_upscaling_service(request: Request):
    """
    Retrieve the Real-ESRGAN upscaling service
    from FastAPI application state.
    """

    upscaling_service = getattr(
        request.app.state,
        "upscaling_service",
        None,
    )

    if upscaling_service is None:

        logger.error(
            "Upscaling service has not been initialized."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image upscaling service is unavailable.",
        )

    return upscaling_service
