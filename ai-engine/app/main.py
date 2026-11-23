import asyncio
import logging

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers

from app.services.stable_diffusion_cpp import (
    StableDiffusionCppBackend,
)

from app.services.upscaling_service import (
    UpscalingService,
)

from app.api.routes import (
    health_routes,
    generation_routes,
    training_routes,
    model_routes,
    style_routes,
)


# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------

setup_logging()

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Project Directories
# --------------------------------------------------

# app/main.py -> app -> ai-engine
PROJECT_ROOT = Path(__file__).resolve().parent.parent

REALESRGAN_DIR = (
    PROJECT_ROOT
    / "tools"
    / "realesrgan"
)

REALESRGAN_EXECUTABLE = (
    REALESRGAN_DIR
    / "realesrgan-ncnn-vulkan"
)

REALESRGAN_MODEL_DIR = (
    REALESRGAN_DIR
    / "models"
)


# --------------------------------------------------
# Stable Diffusion Backend Factory
# --------------------------------------------------

def create_generation_backend() -> StableDiffusionCppBackend:
    """
    Create the local Stable Diffusion backend.

    Uses the NVIDIA Vulkan configuration from settings.
    """

    backend = StableDiffusionCppBackend(
        executable=settings.SD_CPP_CLI,
        model_path=settings.SD_MODEL_PATH,
        output_dir=settings.OUTPUT_DIR / "images",

        host=settings.SD_SERVER_HOST,
        port=settings.SD_SERVER_PORT,

        startup_timeout=settings.SD_STARTUP_TIMEOUT,
        request_timeout=settings.SD_REQUEST_TIMEOUT,

        threads=settings.SD_THREADS,

        server_log=settings.LOG_DIR / "sd-server.log",

        # NVIDIA Vulkan configuration
        backend=getattr(
            settings,
            "SD_BACKEND",
            "vulkan0",
        ),

        auto_fit=getattr(
            settings,
            "SD_AUTO_FIT",
            True,
        ),

        max_vram=getattr(
            settings,
            "SD_MAX_VRAM",
            "1.5",
        ),

        params_backend=getattr(
            settings,
            "SD_PARAMS_BACKEND",
            "diffusion=disk,te=cpu,vae=cpu",
        ),

        vulkan_icd=getattr(
            settings,
            "VK_ICD_FILENAMES",
            "/usr/share/vulkan/icd.d/nvidia_icd.json",
        ),

        external_server_ok=True,
    )

    return backend


# --------------------------------------------------
# Real-ESRGAN Service Factory
# --------------------------------------------------

def create_upscaling_service() -> UpscalingService:
    """
    Create the local Real-ESRGAN Vulkan upscaling service.
    """

    service = UpscalingService(
        executable=REALESRGAN_EXECUTABLE,

        model_dir=REALESRGAN_MODEL_DIR,

        output_dir=settings.OUTPUT_DIR / "upscaled",

        # Vulkan GPU device index.
        gpu_id=0,

        # Suitable starting point for MX350 2GB VRAM.
        tile_size=128,

        timeout=600,
    )

    return service


# --------------------------------------------------
# Application Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.

    Startup:
    - Initialize application services.
    - Register services in app.state.
    - Check Real-ESRGAN configuration.
    - Start Stable Diffusion backend.

    Shutdown:
    - Stop API-managed Stable Diffusion process.
    - Release application service references.
    """

    logger.info("=" * 60)
    logger.info("Starting Cute3D AI Engine...")
    logger.info("=" * 60)

    logger.info(
        "Project root: %s",
        PROJECT_ROOT,
    )

    backend = None

    # --------------------------------------------------
    # Initialize Services
    # --------------------------------------------------

    try:

        # Stable Diffusion backend
        backend = create_generation_backend()

        # Real-ESRGAN service
        upscaling_service = create_upscaling_service()

        # --------------------------------------------------
        # Register Application Services
        # --------------------------------------------------

        app.state.generation_pipeline = backend

        app.state.upscaling_service = (
            upscaling_service
        )

        # Training is unavailable until a PyTorch Trainer
        # instance and its data pipeline are configured.
        app.state.training_service = None

        logger.info(
            "Application services initialized."
        )

    except Exception:

        logger.exception(
            "Failed to initialize application services."
        )

        raise

    # --------------------------------------------------
    # Stable Diffusion Configuration
    # --------------------------------------------------

    logger.info("-" * 60)
    logger.info("Stable Diffusion Configuration")
    logger.info("-" * 60)

    backend_status = backend.status()

    logger.info(
        "Executable: %s",
        backend_status["executable"],
    )

    logger.info(
        "Model: %s",
        backend_status["model"],
    )

    logger.info(
        "Server URL: %s",
        backend_status["url"],
    )

    logger.info(
        "Backend: %s",
        backend_status["device"],
    )

    logger.info(
        "Auto-fit: %s",
        backend_status["auto_fit"],
    )

    logger.info(
        "Maximum VRAM: %s",
        backend_status["max_vram"],
    )

    logger.info(
        "Parameter offloading: %s",
        backend_status["params_backend"],
    )

    if not backend.is_configured():

        logger.error(
            "Stable Diffusion backend configuration is invalid."
        )

        logger.error(
            "Check executable and model paths."
        )

    # --------------------------------------------------
    # Real-ESRGAN Configuration
    # --------------------------------------------------

    logger.info("-" * 60)
    logger.info("Real-ESRGAN Configuration")
    logger.info("-" * 60)

    logger.info(
        "Executable: %s",
        REALESRGAN_EXECUTABLE,
    )

    logger.info(
        "Model directory: %s",
        REALESRGAN_MODEL_DIR,
    )

    upscaling_status = (
        upscaling_service.get_status()
    )

    logger.info(
        "GPU ID: %s",
        upscaling_status["gpu_id"],
    )

    logger.info(
        "Tile size: %s",
        upscaling_status["tile_size"],
    )

    if upscaling_service.is_configured():

        logger.info(
            "Real-ESRGAN executable and model directory found."
        )

        # Verify default model.
        default_param = (
            REALESRGAN_MODEL_DIR
            / "realesrgan-x4plus.param"
        )

        default_bin = (
            REALESRGAN_MODEL_DIR
            / "realesrgan-x4plus.bin"
        )

        if (
            default_param.is_file()
            and default_bin.is_file()
        ):

            logger.info(
                "Default Real-ESRGAN model is available."
            )

        else:

            logger.warning(
                "Default Real-ESRGAN model files are missing."
            )

            logger.warning(
                "Expected: %s",
                default_param,
            )

            logger.warning(
                "Expected: %s",
                default_bin,
            )

    else:

        logger.warning(
            "Real-ESRGAN is not configured. "
            "Upscaling endpoints will be unavailable."
        )

    # --------------------------------------------------
    # Start Stable Diffusion Backend
    # --------------------------------------------------

    logger.info("-" * 60)
    logger.info("Starting Stable Diffusion Backend")
    logger.info("-" * 60)

    try:

        await asyncio.to_thread(
            backend.start
        )

        logger.info(
            "Stable Diffusion backend started successfully."
        )

    except Exception:

        # Keep the API available for health checks and
        # other endpoints. Generation requests can retry
        # starting the backend through the backend service.
        logger.exception(
            "Stable Diffusion startup failed. "
            "Image generation may be temporarily unavailable."
        )

    # --------------------------------------------------
    # Application Ready
    # --------------------------------------------------

    logger.info("=" * 60)
    logger.info("Cute3D AI Engine startup completed.")
    logger.info("=" * 60)

    try:

        yield

    finally:

        # --------------------------------------------------
        # Application Shutdown
        # --------------------------------------------------

        logger.info("=" * 60)
        logger.info("Shutting down Cute3D AI Engine...")
        logger.info("=" * 60)

        if backend is not None:

            try:

                await asyncio.to_thread(
                    backend.stop
                )

                logger.info(
                    "Stable Diffusion backend stopped."
                )

            except Exception:

                logger.exception(
                    "Error while stopping Stable Diffusion backend."
                )

        # Release application references.
        app.state.generation_pipeline = None

        app.state.upscaling_service = None

        app.state.training_service = None

        logger.info(
            "Cute3D AI Engine shutdown completed."
        )


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,

    description=(
        "Local offline image generation powered by "
        "stable-diffusion.cpp and Real-ESRGAN AI upscaling, "
        "with experimental PyTorch training support."
    ),

    version=settings.APP_VERSION,

    debug=settings.DEBUG,

    lifespan=lifespan,
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=list(
        settings.CORS_ORIGINS
    ),

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

register_exception_handlers(app)


# --------------------------------------------------
# API Routes
# --------------------------------------------------

app.include_router(
    health_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Health"],
)

app.include_router(
    generation_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Image Generation"],
)

app.include_router(
    training_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Training"],
)

app.include_router(
    model_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Models"],
)

app.include_router(
    style_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Generation Styles"],
)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
async def root():

    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }
