
import base64
import json
import logging
import os
import secrets
import socket
import subprocess
import time
import uuid

from pathlib import Path
from typing import Optional, Union

import requests

from app.services.style_presets import (
    build_styled_prompts,
    get_style,
)

logger = logging.getLogger(__name__)


class StableDiffusionCppBackend:
    """
    Local image generation using stable-diffusion.cpp HTTP server.

    Features:
    - Local image generation
    - NVIDIA Vulkan backend support
    - VRAM auto-fit configuration
    - CPU and disk parameter offloading
    - Style preset integration
    - Positive and negative prompts
    - Reproducible seed handling
    - PNG validation and storage
    - API-managed and external server support
    """

    # --------------------------------------------------
    # Generation Configuration
    # --------------------------------------------------

    SUPPORTED_RESOLUTIONS = {(512, 512)}

    SAMPLE_STEPS = 25
    SAMPLE_METHOD = "dpm++2m"
    SCHEDULER = "karras"
    GUIDANCE_SCALE = 7.0

    MAX_SEED = 2**31 - 1

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def __init__(
        self,
        executable: Path,
        model_path: Path,
        output_dir: Path,
        host: str = "127.0.0.1",
        port: int = 8082,
        startup_timeout: int = 300,
        request_timeout: int = 1800,
        threads: int = 4,
        server_log: Optional[Path] = None,
        backend: str = "vulkan0",
        auto_fit: Union[bool, str] = True,
        max_vram: str = "1.5",
        params_backend: Optional[str] = (
            "diffusion=disk,te=cpu,vae=cpu"
        ),
        vulkan_icd: Optional[str] = (
            "/usr/share/vulkan/icd.d/nvidia_icd.json"
        ),
        external_server_ok: bool = True,
    ):

        self.executable = (
            Path(executable).expanduser().resolve()
        )

        self.model_path = (
            Path(model_path).expanduser().resolve()
        )

        self.output_dir = (
            Path(output_dir).expanduser().resolve()
        )

        self.host = host
        self.port = int(port)

        self.startup_timeout = int(startup_timeout)
        self.request_timeout = int(request_timeout)

        self.threads = max(1, int(threads))

        self.backend = str(backend).strip()

        # Support both boolean and string values.
        if isinstance(auto_fit, bool):
            self.auto_fit = "on" if auto_fit else "off"
        else:
            self.auto_fit = str(auto_fit).strip().lower()

        if self.auto_fit not in {"on", "off"}:
            raise ValueError(
                "auto_fit must be True, False, 'on' or 'off'."
            )

        # Accept both "1.5" and "vulkan0=1.5".
        max_vram = str(max_vram).strip()

        if max_vram and "=" not in max_vram:
            self.max_vram = (
                f"{self.backend}={max_vram}"
            )
        else:
            self.max_vram = max_vram

        self.params_backend = (
            params_backend.strip()
            if params_backend
            else None
        )

        self.vulkan_icd = vulkan_icd
        self.external_server_ok = bool(
            external_server_ok
        )

        self.server_log = Path(
            server_log
            or (
                self.output_dir.parent
                / "logs"
                / "sd-server.log"
            )
        ).expanduser().resolve()

        self.process = None
        self._log_handle = None

        self._externally_managed = False

        self.base_url = (
            f"http://{self.host}:{self.port}"
        )

    # --------------------------------------------------
    # Configuration Status
    # --------------------------------------------------

    def is_configured(self) -> bool:

        return (
            self.executable.is_file()
            and os.access(self.executable, os.X_OK)
            and self.model_path.is_file()
        )

    def status(self) -> dict:

        owned_running = (
            self.process is not None
            and self.process.poll() is None
        )

        listening = self._port_is_open()

        return {
            "backend": "stable-diffusion.cpp",
            "configured": self.is_configured(),
            "running": bool(
                owned_running or listening
            ),
            "process_managed_by_api": bool(
                owned_running
            ),
            "externally_managed": bool(
                self._externally_managed
                or (listening and not owned_running)
            ),
            "executable": str(self.executable),
            "model": str(self.model_path),
            "device": self.backend,
            "auto_fit": self.auto_fit,
            "max_vram": self.max_vram,
            "params_backend": self.params_backend,
            "supported_resolutions": [
                "512x512"
            ],
            "sampling": {
                "steps": self.SAMPLE_STEPS,
                "method": self.SAMPLE_METHOD,
                "scheduler": self.SCHEDULER,
                "guidance_scale": self.GUIDANCE_SCALE,
            },
            "url": self.base_url,
        }

    # --------------------------------------------------
    # Server Health Check
    # --------------------------------------------------

    def _port_is_open(self) -> bool:

        try:
            with socket.create_connection(
                (self.host, self.port),
                timeout=1,
            ):
                return True

        except OSError:
            return False

    # --------------------------------------------------
    # Server Command
    # --------------------------------------------------

    def _build_command(self) -> list[str]:

        command = [
            str(self.executable),
            "--model",
            str(self.model_path),
            "--listen-ip",
            self.host,
            "--listen-port",
            str(self.port),
            "--threads",
            str(self.threads),
        ]

        if self.backend:
            command.extend([
                "--backend",
                self.backend,
            ])

        command.extend([
            "--auto-fit",
            self.auto_fit,
        ])

        if self.max_vram:
            command.extend([
                "--max-vram",
                self.max_vram,
            ])

        if self.params_backend:
            command.extend([
                "--params-backend",
                self.params_backend,
            ])

        return command

    # --------------------------------------------------
    # Server Startup
    # --------------------------------------------------

    def start(self) -> bool:

        if (
            self.process is not None
            and self.process.poll() is None
        ):
            logger.info(
                "Stable Diffusion server is already running "
                "under this API process."
            )
            return True

        # Reuse an existing manually started server.
        if self._port_is_open():

            if not self.external_server_ok:
                raise RuntimeError(
                    f"Port {self.port} is already in use."
                )

            self._externally_managed = True

            logger.info(
                "Using existing Stable Diffusion server at %s",
                self.base_url,
            )

            return True

        if not self.executable.is_file():
            raise FileNotFoundError(
                f"Stable Diffusion executable not found: "
                f"{self.executable}"
            )

        if not os.access(self.executable, os.X_OK):
            raise PermissionError(
                f"Stable Diffusion executable is not executable: "
                f"{self.executable}"
            )

        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Stable Diffusion model not found: "
                f"{self.model_path}"
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.server_log.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._log_handle = self.server_log.open(
            "a",
            encoding="utf-8",
        )

        env = os.environ.copy()

        if self.vulkan_icd:
            env["VK_ICD_FILENAMES"] = (
                self.vulkan_icd
            )

        command = self._build_command()

        logger.info(
            "Starting Stable Diffusion server: %s",
            " ".join(command),
        )

        try:

            self.process = subprocess.Popen(
                command,
                cwd=str(
                    self.executable.parent.parent
                ),
                env=env,
                stdout=self._log_handle,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )

        except OSError:

            self._close_log_handle()

            logger.exception(
                "Failed to launch Stable Diffusion server."
            )

            raise

        deadline = (
            time.monotonic()
            + self.startup_timeout
        )

        while time.monotonic() < deadline:

            if self.process.poll() is not None:

                return_code = (
                    self.process.returncode
                )

                self.stop()

                raise RuntimeError(
                    "Stable Diffusion server exited unexpectedly. "
                    f"Exit code: {return_code}. "
                    f"Check log: {self.server_log}"
                )

            if self._port_is_open():

                logger.info(
                    "Stable Diffusion server is listening at %s",
                    self.base_url,
                )

                return True

            time.sleep(1)

        self.stop()

        raise TimeoutError(
            "Stable Diffusion server startup timed out "
            f"after {self.startup_timeout} seconds. "
            f"Check log: {self.server_log}"
        )

    # --------------------------------------------------
    # Log Handle Management
    # --------------------------------------------------

    def _close_log_handle(self) -> None:

        if self._log_handle is not None:

            if not self._log_handle.closed:
                self._log_handle.close()

            self._log_handle = None

    # --------------------------------------------------
    # Server Shutdown
    # --------------------------------------------------

    def stop(self) -> None:

        # Never terminate a manually managed server.
        if (
            self.process is not None
            and self.process.poll() is None
        ):

            logger.info(
                "Stopping API-managed Stable Diffusion server..."
            )

            self.process.terminate()

            try:

                self.process.wait(timeout=15)

            except subprocess.TimeoutExpired:

                logger.warning(
                    "Graceful shutdown timed out. "
                    "Killing Stable Diffusion server."
                )

                self.process.kill()
                self.process.wait(timeout=5)

        self.process = None

        self._externally_managed = False

        self._close_log_handle()

        logger.info(
            "Stable Diffusion backend stopped."
        )

    # --------------------------------------------------
    # Resolution Validation
    # --------------------------------------------------

    def _validate_resolution(
        self,
        width: int,
        height: int,
    ) -> None:

        resolution = (
            int(width),
            int(height),
        )

        if resolution not in self.SUPPORTED_RESOLUTIONS:

            raise ValueError(
                "Unsupported image resolution: "
                f"{width}x{height}. "
                "Currently supported: 512x512."
            )

    # --------------------------------------------------
    # Seed Generation
    # --------------------------------------------------

    def _resolve_seed(
        self,
        seed: Optional[int],
    ) -> int:

        if seed is None:
            return secrets.randbelow(
                self.MAX_SEED + 1
            )

        if isinstance(seed, bool):
            raise ValueError(
                "Seed must be an integer."
            )

        try:
            seed = int(seed)

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Seed must be an integer."
            ) from exc

        if not 0 <= seed <= self.MAX_SEED:

            raise ValueError(
                f"Seed must be between 0 and {self.MAX_SEED}."
            )

        return seed

    # --------------------------------------------------
    # Sampling Configuration
    # --------------------------------------------------

    def _build_sampling_args(
        self,
        seed: int,
    ) -> dict:

        return {
            "sample_params": {
                "sample_steps": self.SAMPLE_STEPS,
                "sample_method": self.SAMPLE_METHOD,
                "scheduler": self.SCHEDULER,
                "guidance": {
                    "txt_cfg": self.GUIDANCE_SCALE,
                },
            },
            "seed": seed,
        }

    # --------------------------------------------------
    # Prompt Preparation
    # --------------------------------------------------

    def _prepare_prompts(
        self,
        prompt: str,
        negative_prompt: str,
        style: str,
    ) -> tuple[str, str]:

        if not isinstance(prompt, str):
            raise ValueError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        if not isinstance(negative_prompt, str):
            raise ValueError(
                "Negative prompt must be a string."
            )

        get_style(style)

        styled_prompt, styled_negative = (
            build_styled_prompts(
                prompt=prompt.strip(),
                negative_prompt=negative_prompt.strip(),
                style=style,
            )
        )

        if not styled_prompt.strip():
            raise ValueError(
                "Processed generation prompt cannot be empty."
            )

        return (
            styled_prompt,
            styled_negative,
        )

    # --------------------------------------------------
    # Image Response Processing
    # --------------------------------------------------

    def _decode_image_response(
        self,
        response_data: dict,
    ) -> tuple[str, bytes, Optional[int]]:

        if not isinstance(response_data, dict):
            raise RuntimeError(
                "Invalid Stable Diffusion response."
            )

        image_items = response_data.get("data")

        if (
            not isinstance(image_items, list)
            or not image_items
            or not isinstance(image_items[0], dict)
        ):
            raise RuntimeError(
                "Stable Diffusion returned no image data."
            )

        image_item = image_items[0]

        image_base64 = image_item.get("b64_json")

        if (
            not isinstance(image_base64, str)
            or not image_base64
        ):
            raise RuntimeError(
                "Stable Diffusion returned invalid Base64 image data."
            )

        try:

            image_bytes = base64.b64decode(
                image_base64,
                validate=True,
            )

        except (ValueError, TypeError) as exc:

            raise RuntimeError(
                "Failed to decode generated image."
            ) from exc

        if not image_bytes.startswith(
            b"\x89PNG\r\n\x1a\n"
        ):
            raise RuntimeError(
                "Stable Diffusion returned an invalid PNG image."
            )

        returned_seed = image_item.get("seed")

        if (
            not isinstance(returned_seed, int)
            or isinstance(returned_seed, bool)
        ):
            returned_seed = None

        return (
            image_base64,
            image_bytes,
            returned_seed,
        )

    # --------------------------------------------------
    # Image Generation
    # --------------------------------------------------

    def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        seed: Optional[int] = None,
        negative_prompt: str = "",
        style: str = "auto",
    ) -> dict:

        # Validate dimensions.
        self._validate_resolution(
            width,
            height,
        )

        # Prepare prompts.
        prompt_text, negative_text = (
            self._prepare_prompts(
                prompt=prompt,
                negative_prompt=negative_prompt,
                style=style,
            )
        )

        # Resolve seed.
        actual_seed = self._resolve_seed(seed)

        # Check local model configuration.
        if not self.is_configured():

            raise RuntimeError(
                "Local image model is not configured. "
                "Check executable and model path."
            )

        # Start or reuse the server.
        if not self._port_is_open():

            self.start()

        elif (
            self.process is None
            or self.process.poll() is not None
        ):

            self._externally_managed = True

            logger.info(
                "Reusing externally managed Stable Diffusion server."
            )

        request_id = str(uuid.uuid4())

        preset = get_style(style)

        extra_args = self._build_sampling_args(
            actual_seed
        )

        prompt_with_settings = (
            f"{prompt_text} "
            f"<sd_cpp_extra_args>"
            f"{json.dumps(extra_args)}"
            f"</sd_cpp_extra_args>"
        )

        payload = {
            "model": "sd",
            "prompt": prompt_with_settings,
            "n": 1,
            "size": f"{width}x{height}",
            "response_format": "b64_json",
        }

        if negative_text.strip():

            payload["negative_prompt"] = (
                negative_text.strip()
            )

        logger.info(
            "Starting image generation | "
            "Request ID: %s | Style: %s | "
            "Resolution: %sx%s | Seed: %s | Steps: %s",
            request_id,
            preset.key,
            width,
            height,
            actual_seed,
            self.SAMPLE_STEPS,
        )

        # Send HTTP request.
        try:

            response = requests.post(
                f"{self.base_url}/v1/images/generations",
                json=payload,
                timeout=self.request_timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            (
                image_base64,
                image_bytes,
                returned_seed,
            ) = self._decode_image_response(
                response_data
            )

        except requests.RequestException as exc:

            logger.exception(
                "Stable Diffusion HTTP request failed. "
                "Request ID: %s",
                request_id,
            )

            raise RuntimeError(
                "Local Stable Diffusion server request failed. "
                f"Check server at {self.base_url} "
                f"and log {self.server_log}."
            ) from exc

        except ValueError as exc:

            logger.exception(
                "Invalid Stable Diffusion JSON response. "
                "Request ID: %s",
                request_id,
            )

            raise RuntimeError(
                "Stable Diffusion returned an invalid response."
            ) from exc

        except RuntimeError:

            logger.exception(
                "Image response processing failed. "
                "Request ID: %s",
                request_id,
            )

            raise

        final_seed = (
            returned_seed
            if returned_seed is not None
            else actual_seed
        )

        # Save image safely using a temporary file.
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        image_path = (
            self.output_dir
            / f"{request_id}.png"
        )

        temporary_path = image_path.with_suffix(
            ".tmp"
        )

        try:

            temporary_path.write_bytes(
                image_bytes
            )

            temporary_path.replace(
                image_path
            )

        except OSError:

            temporary_path.unlink(
                missing_ok=True
            )

            logger.exception(
                "Failed to save generated image: %s",
                image_path,
            )

            raise

        logger.info(
            "Image generation completed successfully | "
            "Request ID: %s | Image: %s | Seed: %s",
            request_id,
            image_path,
            final_seed,
        )

        return {
            "generation_id": request_id,
            "image_base64": image_base64,
            "mime_type": "image/png",
            "seed": final_seed,
            "style": preset.key,
            "image_path": str(image_path),
            "width": width,
            "height": height,
        }

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def get_status(self) -> dict:
        return self.status()
