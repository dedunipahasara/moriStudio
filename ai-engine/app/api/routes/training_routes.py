from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.training_schema import (
    TrainingRequest,
    TrainingResponse,
    TrainingStatusResponse
)

from app.dependencies import get_training_service

router = APIRouter()


@router.post(
    "/training/start",
    response_model=TrainingResponse
)
async def start_training(
    request: TrainingRequest,
    service=Depends(get_training_service)
):

    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Training service is not implemented yet."
        )

    try:
        result = await service.start_training(
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate
        )

        return TrainingResponse(
            success=True,
            status="PENDING",
            message="Training request submitted.",
            training_id=result["training_id"]
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Training request failed: {str(error)}"
        )


@router.get(
    "/training/status",
    response_model=TrainingStatusResponse
)
async def training_status(
    service=Depends(get_training_service)
):

    if service is None:
        return TrainingStatusResponse(
            status="NOT_INITIALIZED",
            message="Training service is not ready."
        )

    return await service.get_status()