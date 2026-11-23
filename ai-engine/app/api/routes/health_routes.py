from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    backend = getattr(request.app.state, "generation_pipeline", None)
    status = backend.status() if backend else {}
    return {
        "success": True,
        "status": "healthy",
        "service": "Cute3D AI Engine",
        "generation_backend": status,
    }
