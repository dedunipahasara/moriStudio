import asyncio
import logging

from pathlib import Path
from uuid import UUID
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from pydantic import BaseModel, Field

from app.api.schemas.generation_schema import (
    GenerationRequest,
    GenerationResponse,
)
from app.dependencies import get_generation_pipeline


logger = logging.getLogger(__name__)

router = APIRouter()


class UpscaleRequest(BaseModel):
    scale: Literal[2, 3, 4] = Field(
        default=2,
        description="Upscaling factor: 2x, 3x, or 4x.",
    )

    model: Literal[
        "realesrgan-x4plus",
        "realesrgan-x4plus-anime",
        "realesr-animevideov3",
    ] = Field(
        default="realesrgan-x4plus",
        description="Real-ESRGAN upscaling model.",
    )


@router.post(
    "/generations",
    response_model=GenerationResponse,
)
async def generate_image(
    request: GenerationRequest,
    pipeline=Depends(get_generation_pipeline),
):
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Image generation backend is not configured.",
        )

    try:
        result = await asyncio.to_thread(
            pipeline.generate,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            seed=request.seed,
            style=request.style,
        )

        return GenerationResponse(
            success=True,
            generation_id=result["generation_id"],
            status="COMPLETED",
            message="Image generated successfully.",
            image_base64=result["image_base64"],
            mime_type=result.get("mime_type", "image/png"),
            seed=result.get("seed"),
            style=result.get("style", request.style),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        logger.exception("Stable Diffusion generation error.")

        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Unexpected image generation error.")

        raise HTTPException(
            status_code=500,
            detail="Image generation failed. Check application logs.",
        ) from error


@router.post(
    "/generations/{generation_id}/upscale",
)
async def upscale_generated_image(
    generation_id: UUID,
    upscale_request: UpscaleRequest,
    request: Request,
):
    pipeline = getattr(
        request.app.state,
        "generation_pipeline",
        None,
    )

    upscaling_service = getattr(
        request.app.state,
        "upscaling_service",
        None,
    )

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Image generation backend is not configured.",
        )

    if upscaling_service is None:
        raise HTTPException(
            status_code=503,
            detail="Image upscaling service is not configured.",
        )

    try:
        # Locate the original generated image using its UUID.
        image_directory = Path(pipeline.output_dir).resolve()

        original_image = (
            image_directory / f"{generation_id}.png"
        ).resolve()

        # Ensure the requested image belongs to the image directory.
        if original_image.parent != image_directory:
            raise HTTPException(
                status_code=400,
                detail="Invalid generation ID.",
            )

        if not original_image.is_file():
            raise HTTPException(
                status_code=404,
                detail="Generated image not found.",
            )

        # Run Real-ESRGAN without blocking the API event loop.
        result = await asyncio.to_thread(
            upscaling_service.upscale,
            image_path=original_image,
            scale=upscale_request.scale,
            model=upscale_request.model,
        )

        return {
            "success": True,
            "message": "Image upscaled successfully.",
            "generation_id": str(generation_id),
            "original_image": result["original_image"],
            "upscaled_image": result["upscaled_image"],
            "scale": result["scale"],
            "model": result["model"],
            "gpu_id": result["gpu_id"],
            "file_size": result["file_size"],
        }

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        logger.exception("Image upscaling error.")

        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Unexpected image upscaling error.")

        raise HTTPException(
            status_code=500,
            detail="Image upscaling failed. Check application logs.",
        ) from error