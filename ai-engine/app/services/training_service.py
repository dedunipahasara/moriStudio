import logging
import threading

from datetime import datetime, timezone
from typing import Any, Optional


logger = logging.getLogger(__name__)


class TrainingService:
    """
    Manages model training in a background thread.

    Features:
    - Background model training
    - Thread-safe training status
    - Training lifecycle management
    - Error tracking
    - Training completion timestamps
    - Wait for training completion
    """

    def __init__(self, trainer: Any):

        if trainer is None:
            raise ValueError("Trainer instance cannot be None.")

        if not callable(getattr(trainer, "fit", None)):
            raise TypeError(
                "Trainer must provide a callable fit() method."
            )

        self.trainer = trainer

        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None

        self._status = self._initial_status()

    # --------------------------------------------------
    # Initial Status
    # --------------------------------------------------

    @staticmethod
    def _initial_status() -> dict:

        return {
            "status": "idle",
            "started_at": None,
            "finished_at": None,
            "error": None,
            "epochs": None,
        }

    # --------------------------------------------------
    # Current Timestamp
    # --------------------------------------------------

    @staticmethod
    def _current_timestamp() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()

    # --------------------------------------------------
    # Start Training
    # --------------------------------------------------

    def start_training(
        self,
        train_loader,
        val_loader,
        epochs: int = 10,
    ) -> dict:
        """
        Start model training in a background thread.

        Args:
            train_loader: Training data loader.
            val_loader: Validation data loader.
            epochs: Number of training epochs.

        Returns:
            dict: Current training status.
        """

        if train_loader is None:
            raise ValueError(
                "Training data loader cannot be None."
            )

        if val_loader is None:
            raise ValueError(
                "Validation data loader cannot be None."
            )

        if (
            not isinstance(epochs, int)
            or isinstance(epochs, bool)
            or epochs < 1
        ):
            raise ValueError(
                "Epochs must be a positive integer."
            )

        with self._lock:

            if (
                self._thread is not None
                and self._thread.is_alive()
            ):
                raise RuntimeError(
                    "Training is already running."
                )

            if self._status["status"] == "running":
                raise RuntimeError(
                    "Training is already running."
                )

            self._status = {
                "status": "running",
                "started_at": self._current_timestamp(),
                "finished_at": None,
                "error": None,
                "epochs": epochs,
            }

            self._thread = threading.Thread(
                target=self._run_training,
                args=(
                    train_loader,
                    val_loader,
                    epochs,
                ),
                name="ModelTrainingThread",
                daemon=True,
            )

            try:

                self._thread.start()

            except RuntimeError as error:

                self._status["status"] = "failed"
                self._status["error"] = str(error)
                self._status["finished_at"] = (
                    self._current_timestamp()
                )

                logger.exception(
                    "Failed to start training thread."
                )

                raise

            logger.info(
                "Training thread started. Epochs: %s",
                epochs,
            )

            return self.get_status()

    # --------------------------------------------------
    # Background Training
    # --------------------------------------------------

    def _run_training(
        self,
        train_loader,
        val_loader,
        epochs: int,
    ) -> None:
        """
        Execute trainer.fit() in the background thread.
        """

        try:

            logger.info(
                "Model training started. Epochs: %s",
                epochs,
            )

            self.trainer.fit(
                train_loader,
                val_loader,
                epochs=epochs,
            )

            with self._lock:

                self._status["status"] = "completed"

                self._status["finished_at"] = (
                    self._current_timestamp()
                )

                self._status["error"] = None

            logger.info(
                "Model training completed successfully."
            )

        except Exception as error:

            logger.exception(
                "Model training failed."
            )

            with self._lock:

                self._status["status"] = "failed"

                self._status["error"] = str(error)

                self._status["finished_at"] = (
                    self._current_timestamp()
                )

    # --------------------------------------------------
    # Get Training Status
    # --------------------------------------------------

    def get_status(self) -> dict:
        """
        Return a thread-safe copy of the training status.
        """

        with self._lock:

            return self._status.copy()

    # --------------------------------------------------
    # Check Training State
    # --------------------------------------------------

    def is_training(self) -> bool:
        """
        Check whether training is currently running.
        """

        with self._lock:

            return (
                self._thread is not None
                and self._thread.is_alive()
            )

    # --------------------------------------------------
    # Wait For Training
    # --------------------------------------------------

    def wait_for_training(
        self,
        timeout: Optional[float] = None,
    ) -> dict:
        """
        Wait until background training finishes.

        Args:
            timeout: Maximum waiting time in seconds.
                     None means wait indefinitely.

        Returns:
            dict: Latest training status.
        """

        if (
            timeout is not None
            and (
                isinstance(timeout, bool)
                or not isinstance(timeout, (int, float))
                or timeout < 0
            )
        ):
            raise ValueError(
                "Timeout must be a non-negative number or None."
            )

        with self._lock:
            thread = self._thread

        if thread is not None:

            thread.join(
                timeout=timeout
            )

        return self.get_status()

    # --------------------------------------------------
    # Reset Training Status
    # --------------------------------------------------

    def reset_status(self) -> dict:
        """
        Reset training status when no training is running.
        """

        with self._lock:

            if (
                self._thread is not None
                and self._thread.is_alive()
            ):
                raise RuntimeError(
                    "Cannot reset status while training is running."
                )

            self._status = self._initial_status()

            self._thread = None

            logger.info(
                "Training status has been reset."
            )

            return self.get_status()
