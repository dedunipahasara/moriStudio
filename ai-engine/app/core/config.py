import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "Cute3D AI Engine"
    APP_VERSION: str = "0.2.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEVICE: str = "cpu"

    DATASET_DIR: Path = PROJECT_ROOT / "datasets"
    CHECKPOINT_DIR: Path = PROJECT_ROOT / "checkpoints"
    OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"
    LOG_DIR: Path = PROJECT_ROOT / "training" / "logs"

    MAX_PROMPT_LENGTH: int = 1000
    DEFAULT_IMAGE_WIDTH: int = 512
    DEFAULT_IMAGE_HEIGHT: int = 512

    SD_CPP_CLI: Path = (
        PROJECT_ROOT.parent
        / "local-image-runtime"
        / "build"
        / "bin"
        / "sd-server"
    )

    SD_MODEL_PATH: Path = (
        PROJECT_ROOT
        / "models"
        / "stable-diffusion"
        / "v1-5-pruned_Q4_K.gguf"
    )

    SD_SERVER_HOST: str = "127.0.0.1"
    SD_SERVER_PORT: int = 8082
    SD_STARTUP_TIMEOUT: int = 300
    SD_REQUEST_TIMEOUT: int = 1800
    SD_THREADS: int = 4

    SD_BACKEND: str = "vulkan0"
    SD_AUTO_FIT: bool = True
    SD_MAX_VRAM: str = "1.5"
    SD_PARAMS_BACKEND: str = "diffusion=disk,te=cpu,vae=cpu"

    VK_ICD_FILENAMES: str = (
        "/usr/share/vulkan/icd.d/nvidia_icd.json"
    )

    API_KEY: str = ""
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: tuple = (
        "http://localhost:3000",
        "http://localhost:5173",
    )

    def __post_init__(self):
        if not 1 <= self.PORT <= 65535:
            raise ValueError(
                "PORT must be between 1 and 65535."
            )

        if self.MAX_PROMPT_LENGTH < 3:
            raise ValueError(
                "MAX_PROMPT_LENGTH must be at least 3."
            )

        if self.LOG_LEVEL.upper() not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ValueError("Invalid LOG_LEVEL.")

        if not 1 <= self.SD_SERVER_PORT <= 65535:
            raise ValueError(
                "SD_SERVER_PORT must be between 1 and 65535."
            )


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _get_origins() -> tuple:
    value = os.getenv("CORS_ORIGINS")

    if not value:
        return (
            "http://localhost:3000",
            "http://localhost:5173",
        )

    return tuple(
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    )


@lru_cache
def get_settings() -> Settings:
    return Settings(
        APP_NAME=os.getenv(
            "APP_NAME",
            "Cute3D AI Engine",
        ),
        APP_VERSION=os.getenv(
            "APP_VERSION",
            "0.2.0",
        ),
        APP_ENV=os.getenv(
            "APP_ENV",
            "development",
        ),
        DEBUG=_get_bool("DEBUG", False),
        API_PREFIX=os.getenv(
            "API_PREFIX",
            "/api",
        ),
        HOST=os.getenv(
            "HOST",
            "127.0.0.1",
        ),
        PORT=int(os.getenv("PORT", "8000")),
        DEVICE=os.getenv("DEVICE", "cpu"),

        MAX_PROMPT_LENGTH=int(
            os.getenv("MAX_PROMPT_LENGTH", "1000")
        ),

        DEFAULT_IMAGE_WIDTH=int(
            os.getenv("DEFAULT_IMAGE_WIDTH", "512")
        ),

        DEFAULT_IMAGE_HEIGHT=int(
            os.getenv("DEFAULT_IMAGE_HEIGHT", "512")
        ),

        SD_CPP_CLI=Path(
            os.getenv(
                "SD_CPP_CLI",
                str(
                    PROJECT_ROOT.parent
                    / "local-image-runtime"
                    / "build"
                    / "bin"
                    / "sd-server"
                ),
            )
        ),

        SD_MODEL_PATH=Path(
            os.getenv(
                "SD_MODEL_PATH",
                str(
                    PROJECT_ROOT
                    / "models"
                    / "stable-diffusion"
                    / "v1-5-pruned_Q4_K.gguf"
                ),
            )
        ),

        SD_SERVER_HOST=os.getenv(
            "SD_SERVER_HOST",
            "127.0.0.1",
        ),

        SD_SERVER_PORT=int(
            os.getenv("SD_SERVER_PORT", "8082")
        ),

        SD_STARTUP_TIMEOUT=int(
            os.getenv("SD_STARTUP_TIMEOUT", "300")
        ),

        SD_REQUEST_TIMEOUT=int(
            os.getenv("SD_REQUEST_TIMEOUT", "1800")
        ),

        SD_THREADS=int(
            os.getenv("SD_THREADS", "4")
        ),

        SD_BACKEND=os.getenv(
            "SD_BACKEND",
            "vulkan0",
        ),

        SD_AUTO_FIT=_get_bool(
            "SD_AUTO_FIT",
            True,
        ),

        SD_MAX_VRAM=os.getenv(
            "SD_MAX_VRAM",
            "1.5",
        ),

        SD_PARAMS_BACKEND=os.getenv(
            "SD_PARAMS_BACKEND",
            "diffusion=disk,te=cpu,vae=cpu",
        ),

        VK_ICD_FILENAMES=os.getenv(
            "VK_ICD_FILENAMES",
            "/usr/share/vulkan/icd.d/nvidia_icd.json",
        ),

        API_KEY=os.getenv("API_KEY", ""),

        LOG_LEVEL=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ),

        CORS_ORIGINS=_get_origins(),
    )


settings = get_settings()