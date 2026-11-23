from fastapi import APIRouter, Request
from app.api.schemas.model_schema import ModelInfo, ModelStatusResponse

router = APIRouter()


@router.get("/models/status", response_model=ModelStatusResponse)
async def get_model_status(request: Request):
    backend = getattr(request.app.state, "generation_pipeline", None)
    status = backend.status() if backend else {}
    configured = bool(status.get("configured"))
    running = bool(status.get("running"))
    return ModelStatusResponse(
        available=configured and running,
        message=(
            "Local Stable Diffusion 1.5 is ready."
            if configured and running
            else "Local model/runtime is not ready. Check model path, runtime path, and server log."
        ),
        model=ModelInfo(
            name="Stable Diffusion 1.5 GGUF Q4_K",
            model_type="Pretrained latent diffusion model",
            version="1.5",
            framework="stable-diffusion.cpp",
            device="CPU",
            loaded=running,
            trained=True,
        ),
    )
