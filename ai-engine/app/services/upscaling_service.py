import logging
import os
import subprocess
import threading
import uuid

from pathlib import Path
from typing import Union

from PIL import Image, UnidentifiedImageError


logger = logging.getLogger(__name__)


class UpscalingService:
    """
    Local Real-ESRGAN image upscaling service.

    Features:
    - NVIDIA Vulkan GPU support
    - Multiple Real-ESRGAN models
    - 2x, 3x and 4x upscaling
    - Input image validation
    - Output image verification
    - GPU task synchronization
    - Timeout protection
    - Unique output filenames
    """

    # --------------------------------------------------
    # Supported Models
    # --------------------------------------------------

    SUPPORTED_MODELS = {
        "realesrgan-x4plus",
        "realesrgan-x4plus-anime",
        "realesr-animevideov3",
    }

    SUPPORTED_SCALES = (2, 3, 4)

    SUPPORTED_FORMATS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
    }

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def __init__(
        self,
        executable: Union[str, Path],
        model_dir: Union[str, Path],
        output_dir: Union[str, Path],
        gpu_id: int = 0,
        tile_size: int = 128,
        timeout: int = 600,
    ):

        self.executable = (
            Path(executable)
            .expanduser()
            .resolve()
        )

        self.model_dir = (
            Path(model_dir)
            .expanduser()
            .resolve()
        )

        self.output_dir = (
            Path(output_dir)
            .expanduser()
            .resolve()
        )

        self.gpu_id = gpu_id
        self.tile_size = tile_size
        self.timeout = timeout

        # Prevent simultaneous GPU upscaling processes.
        self._gpu_lock = threading.Lock()

        self._validate_configuration()

    # --------------------------------------------------
    # Configuration Validation
    # --------------------------------------------------

    def _validate_configuration(self) -> None:

        if (
            not isinstance(self.gpu_id, int)
            or isinstance(self.gpu_id, bool)
            or self.gpu_id < 0
        ):
            raise ValueError(
                "GPU ID must be a non-negative integer."
            )

        if (
            not isinstance(self.tile_size, int)
            or isinstance(self.tile_size, bool)
            or self.tile_size < 0
        ):
            raise ValueError(
                "Tile size must be a non-negative integer."
            )

        if (
            not isinstance(self.timeout, int)
            or isinstance(self.timeout, bool)
            or self.timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a positive integer."
            )

    # --------------------------------------------------
    # Configuration Status
    # --------------------------------------------------

    def is_configured(self) -> bool:
        """
        Check whether executable and model directory exist.
        """

        return (
            self.executable.is_file()
            and os.access(self.executable, os.X_OK)
            and self.model_dir.is_dir()
        )

    def get_status(self) -> dict:
        """
        Return upscaling service configuration status.
        """

        return {
            "configured": self.is_configured(),
            "executable": str(self.executable),
            "model_directory": str(self.model_dir),
            "output_directory": str(self.output_dir),
            "backend": "realesrgan-ncnn-vulkan",
            "device": "Vulkan GPU",
            "gpu_id": self.gpu_id,
            "tile_size": self.tile_size,
            "timeout": self.timeout,
            "supported_models": sorted(
                self.SUPPORTED_MODELS
            ),
            "supported_scales": list(
                self.SUPPORTED_SCALES
            ),
        }

    # --------------------------------------------------
    # Model Filename
    # --------------------------------------------------

    def _get_model_name(
        self,
        model: str,
        scale: int,
    ) -> str:
        """
        Resolve the actual model name used by Real-ESRGAN.

        AnimeVideoV3 uses separate model files for each scale.
        """

        if model == "realesr-animevideov3":

            return f"{model}-x{scale}"

        return model

    # --------------------------------------------------
    # Model Files
    # --------------------------------------------------

    def _get_model_files(
        self,
        model: str,
        scale: int,
    ) -> tuple[Path, Path]:

        model_name = self._get_model_name(
            model,
            scale,
        )

        param_file = (
            self.model_dir
            / f"{model_name}.param"
        )

        bin_file = (
            self.model_dir
            / f"{model_name}.bin"
        )

        return param_file, bin_file

    # --------------------------------------------------
    # Model Validation
    # --------------------------------------------------

    def _validate_model(
        self,
        model: str,
        scale: int,
    ) -> None:

        if model not in self.SUPPORTED_MODELS:

            raise ValueError(
                f"Unsupported Real-ESRGAN model: {model}. "
                f"Available models: "
                f"{', '.join(sorted(self.SUPPORTED_MODELS))}"
            )

        param_file, bin_file = (
            self._get_model_files(
                model,
                scale,
            )
        )

        missing_files = []

        if not param_file.is_file():
            missing_files.append(
                str(param_file)
            )

        if not bin_file.is_file():
            missing_files.append(
                str(bin_file)
            )

        if missing_files:

            raise FileNotFoundError(
                "Required Real-ESRGAN model files are missing: "
                + ", ".join(missing_files)
            )

    # --------------------------------------------------
    # Input Validation
    # --------------------------------------------------

    def _validate_input(
        self,
        image_path: Union[str, Path],
    ) -> tuple[Path, tuple[int, int]]:

        source = (
            Path(image_path)
            .expanduser()
            .resolve()
        )

        if not source.exists():

            raise FileNotFoundError(
                f"Original image not found: {source}"
            )

        if not source.is_file():

            raise ValueError(
                "Input path must point to a file."
            )

        if source.stat().st_size == 0:

            raise ValueError(
                "Input image is empty."
            )

        if source.suffix.lower() not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported image format: {source.suffix}"
            )

        try:

            with Image.open(source) as image:

                image.verify()

            with Image.open(source) as image:

                image.load()

                dimensions = image.size

                if (
                    dimensions[0] <= 0
                    or dimensions[1] <= 0
                ):
                    raise ValueError(
                        "Invalid input image dimensions."
                    )

        except (
            UnidentifiedImageError,
            OSError,
        ) as error:

            raise ValueError(
                "Input file is not a valid image."
            ) from error

        return source, dimensions

    # --------------------------------------------------
    # Output Validation
    # --------------------------------------------------

    def _validate_output(
        self,
        output_path: Path,
        original_dimensions: tuple[int, int],
        scale: int,
    ) -> dict:
        """
        Verify generated image and return image information.
        """

        if not output_path.is_file():

            raise RuntimeError(
                "Real-ESRGAN did not create an output image."
            )

        file_size = output_path.stat().st_size

        if file_size == 0:

            raise RuntimeError(
                "Generated output image is empty."
            )

        try:

            with Image.open(output_path) as image:

                image.verify()

            with Image.open(output_path) as image:

                image.load()

                output_width, output_height = image.size
                output_format = image.format

        except (
            UnidentifiedImageError,
            OSError,
        ) as error:

            raise RuntimeError(
                "Real-ESRGAN generated an invalid image."
            ) from error

        expected_width = (
            original_dimensions[0] * scale
        )

        expected_height = (
            original_dimensions[1] * scale
        )

        if (
            output_width != expected_width
            or output_height != expected_height
        ):

            raise RuntimeError(
                "Unexpected upscaled image dimensions. "
                f"Expected {expected_width}x{expected_height}, "
                f"received {output_width}x{output_height}."
            )

        return {
            "width": output_width,
            "height": output_height,
            "format": output_format,
            "file_size": file_size,
        }

    # --------------------------------------------------
    # Build Command
    # --------------------------------------------------

    def _build_command(
        self,
        source: Path,
        output_path: Path,
        scale: int,
        model: str,
    ) -> list[str]:

        model_name = self._get_model_name(
            model,
            scale,
        )

        return [
            str(self.executable),

            "-i",
            str(source),

            "-o",
            str(output_path),

            "-s",
            str(scale),

            "-n",
            model_name,

            "-m",
            str(self.model_dir),

            "-g",
            str(self.gpu_id),

            "-t",
            str(self.tile_size),

            "-f",
            "png",
        ]

    # --------------------------------------------------
    # Run Upscaling
    # --------------------------------------------------

    def upscale(
        self,
        image_path: Union[str, Path],
        scale: int = 2,
        model: str = "realesrgan-x4plus",
    ) -> dict:
        """
        Upscale an image using Real-ESRGAN.

        Args:
            image_path: Original image path.
            scale: Upscaling factor (2, 3 or 4).
            model: Real-ESRGAN model name.

        Returns:
            dict: Upscaling result and output information.
        """

        # Validate scale.
        if (
            not isinstance(scale, int)
            or isinstance(scale, bool)
            or scale not in self.SUPPORTED_SCALES
        ):

            raise ValueError(
                "Scale must be 2, 3, or 4."
            )

        # Validate model.
        if not isinstance(model, str):

            raise ValueError(
                "Model name must be a string."
            )

        model = model.strip().lower()

        # Validate input image.
        source, original_dimensions = (
            self._validate_input(image_path)
        )

        # Validate executable and model directory.
        if not self.is_configured():

            raise RuntimeError(
                "Real-ESRGAN is not configured. "
                "Check executable permissions and model directory."
            )

        # Validate model files.
        self._validate_model(
            model,
            scale,
        )

        # Create output directory.
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Generate unique output filename.
        request_id = uuid.uuid4().hex

        output_path = (
            self.output_dir
            / (
                f"{source.stem}_upscaled_"
                f"{scale}x_{request_id[:8]}.png"
            )
        )

        command = self._build_command(
            source=source,
            output_path=output_path,
            scale=scale,
            model=model,
        )

        logger.info(
            "Starting Real-ESRGAN upscaling | "
            "Request ID: %s | Image: %s | "
            "Scale: %sx | Model: %s | GPU: %s",
            request_id,
            source,
            scale,
            model,
            self.gpu_id,
        )

        # Run one GPU upscaling task at a time.
        try:

            with self._gpu_lock:

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False,
                )

            if result.stdout:

                logger.info(
                    "Real-ESRGAN output: %s",
                    result.stdout.strip(),
                )

            if result.stderr:

                logger.info(
                    "Real-ESRGAN messages: %s",
                    result.stderr.strip(),
                )

            if result.returncode != 0:

                logger.error(
                    "Real-ESRGAN failed | "
                    "Return code: %s | Error: %s",
                    result.returncode,
                    result.stderr.strip(),
                )

                raise RuntimeError(
                    "Real-ESRGAN upscaling failed. "
                    "Check application logs and Vulkan GPU configuration."
                )

            # Verify output image.
            output_info = self._validate_output(
                output_path=output_path,
                original_dimensions=original_dimensions,
                scale=scale,
            )

            logger.info(
                "Upscaling completed successfully | "
                "Request ID: %s | Output: %s",
                request_id,
                output_path,
            )

            return {
                "success": True,
                "request_id": request_id,
                "original_image": str(source),
                "upscaled_image": str(output_path),
                "original_width": original_dimensions[0],
                "original_height": original_dimensions[1],
                "width": output_info["width"],
                "height": output_info["height"],
                "scale": scale,
                "model": model,
                "gpu_id": self.gpu_id,
                "format": output_info["format"],
                "file_size": output_info["file_size"],
            }

        except subprocess.TimeoutExpired as error:

            output_path.unlink(
                missing_ok=True
            )

            logger.exception(
                "Real-ESRGAN timed out after %s seconds.",
                self.timeout,
            )

            raise RuntimeError(
                f"Real-ESRGAN upscaling timed out "
                f"after {self.timeout} seconds."
            ) from error

        except Exception:

            output_path.unlink(
                missing_ok=True
            )

            logger.exception(
                "An error occurred during image upscaling."
            )

            raise
