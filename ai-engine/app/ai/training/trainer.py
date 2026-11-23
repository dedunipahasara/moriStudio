import logging
import math

import torch

from app.ai.training.evaluation import ModelEvaluator
from app.ai.training.checkpoint import CheckpointManager


logger = logging.getLogger(__name__)


class Trainer:
    """
    PyTorch training pipeline for the experimental
    text-conditioned image model.

    The model must implement:

        model.training_loss(images, text_features)

    This trainer does not train the external
    stable-diffusion.cpp GGUF checkpoint.
    """

    def __init__(
        self,
        model,
        prompt_encoder,
        text_feature_extractor,
        optimizer,
        scheduler=None,
        device=None,
        checkpoint_manager=None,
        max_grad_norm=1.0,
    ):

        # --------------------------------------------------
        # Validate Components
        # --------------------------------------------------

        if model is None:
            raise ValueError("Model cannot be None.")

        if prompt_encoder is None:
            raise ValueError(
                "Prompt encoder cannot be None."
            )

        if text_feature_extractor is None:
            raise ValueError(
                "Text feature extractor cannot be None."
            )

        if optimizer is None:
            raise ValueError("Optimizer cannot be None.")

        if not callable(
            getattr(model, "training_loss", None)
        ):
            raise TypeError(
                "Model must implement training_loss()."
            )

        if (
            isinstance(max_grad_norm, bool)
            or not isinstance(max_grad_norm, (int, float))
            or not math.isfinite(max_grad_norm)
            or max_grad_norm <= 0
        ):
            raise ValueError(
                "max_grad_norm must be a positive finite number."
            )

        # --------------------------------------------------
        # Device Configuration
        # --------------------------------------------------

        if device is None:

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        self.device = torch.device(device)

        if (
            self.device.type == "cuda"
            and not torch.cuda.is_available()
        ):
            raise RuntimeError(
                "CUDA device requested but CUDA is unavailable."
            )

        # --------------------------------------------------
        # Model Initialization
        # --------------------------------------------------

        self.model = model.to(self.device)

        self.prompt_encoder = (
            prompt_encoder.to(self.device)
        )

        self.text_feature_extractor = (
            text_feature_extractor.to(self.device)
        )

        self.optimizer = optimizer
        self.scheduler = scheduler

        self.checkpoint_manager = (
            checkpoint_manager
            if checkpoint_manager is not None
            else CheckpointManager()
        )

        self.max_grad_norm = float(max_grad_norm)

        self.best_loss = float("inf")

        self.history = []

        # --------------------------------------------------
        # Evaluator
        # --------------------------------------------------

        self.evaluator = ModelEvaluator(
            model=self.model,
            prompt_encoder=self.prompt_encoder,
            text_feature_extractor=(
                self.text_feature_extractor
            ),
            device=self.device,
        )

        logger.info(
            "Trainer initialized successfully. Device: %s",
            self.device,
        )

    # --------------------------------------------------
    # Model Parameters
    # --------------------------------------------------

    def _get_trainable_parameters(self):
        """
        Return unique trainable parameters from all components.
        """

        parameters = []
        seen = set()

        modules = [
            self.model,
            self.prompt_encoder,
            self.text_feature_extractor,
        ]

        for module in modules:

            for parameter in module.parameters():

                if (
                    parameter.requires_grad
                    and id(parameter) not in seen
                ):

                    parameters.append(parameter)
                    seen.add(id(parameter))

        if not parameters:
            raise RuntimeError(
                "No trainable model parameters found."
            )

        return parameters

    # --------------------------------------------------
    # Batch Validation
    # --------------------------------------------------

    def _prepare_batch(self, batch):
        """
        Validate and move batch tensors to the selected device.
        """

        if not isinstance(batch, dict):
            raise TypeError(
                "Each training batch must be a dictionary."
            )

        if "images" not in batch:
            raise KeyError(
                "Training batch is missing 'images'."
            )

        if "token_ids" not in batch:
            raise KeyError(
                "Training batch is missing 'token_ids'."
            )

        images = batch["images"]
        token_ids = batch["token_ids"]

        if not isinstance(images, torch.Tensor):
            raise TypeError(
                "Batch images must be a PyTorch tensor."
            )

        if not isinstance(token_ids, torch.Tensor):
            raise TypeError(
                "Batch token_ids must be a PyTorch tensor."
            )

        if images.ndim < 2:
            raise ValueError(
                "Images tensor must contain a batch dimension."
            )

        if token_ids.ndim != 2:
            raise ValueError(
                "token_ids must have shape [batch, sequence_length]."
            )

        if images.size(0) != token_ids.size(0):
            raise ValueError(
                "Images and token_ids batch sizes do not match."
            )

        if images.size(0) == 0:
            raise ValueError(
                "Training batch cannot be empty."
            )

        images = images.to(
            self.device,
            non_blocking=True,
        )

        token_ids = token_ids.to(
            self.device,
            dtype=torch.long,
            non_blocking=True,
        )

        return images, token_ids

    # --------------------------------------------------
    # Forward Pass
    # --------------------------------------------------

    def _calculate_loss(
        self,
        images,
        token_ids,
    ):
        """
        Generate text features and calculate model loss.
        """

        # Encode text tokens.
        embeddings = self.prompt_encoder(
            token_ids
        )

        # Extract text features.
        text_features = (
            self.text_feature_extractor(
                embeddings,
                token_ids,
            )
        )

        # Calculate model training loss.
        loss = self.model.training_loss(
            images,
            text_features,
        )

        if not isinstance(loss, torch.Tensor):
            raise TypeError(
                "Model training_loss() must return a tensor."
            )

        if loss.numel() != 1:
            raise ValueError(
                "Training loss must be a scalar tensor."
            )

        if not torch.isfinite(loss).all().item():
            raise RuntimeError(
                "Non-finite training loss detected."
            )

        return loss

    # --------------------------------------------------
    # Train One Epoch
    # --------------------------------------------------

    def train_one_epoch(self, dataloader):
        """
        Train the model for one epoch.

        Returns:
            float: Average training loss.
        """

        self.model.train()
        self.prompt_encoder.train()
        self.text_feature_extractor.train()

        total_loss = 0.0
        total_samples = 0

        trainable_parameters = (
            self._get_trainable_parameters()
        )

        for batch_index, batch in enumerate(
            dataloader,
            start=1,
        ):

            images, token_ids = (
                self._prepare_batch(batch)
            )

            # Reset gradients.
            self.optimizer.zero_grad(
                set_to_none=True
            )

            # Forward pass.
            loss = self._calculate_loss(
                images,
                token_ids,
            )

            # Backpropagation.
            loss.backward()

            # Gradient clipping.
            grad_norm = (
                torch.nn.utils.clip_grad_norm_(
                    trainable_parameters,
                    self.max_grad_norm,
                    error_if_nonfinite=True,
                )
            )

            if not torch.isfinite(grad_norm).all().item():

                self.optimizer.zero_grad(
                    set_to_none=True
                )

                raise RuntimeError(
                    "Non-finite gradient norm detected."
                )

            # Update model parameters.
            self.optimizer.step()

            batch_size = images.size(0)

            total_loss += (
                loss.detach().item() * batch_size
            )

            total_samples += batch_size

            logger.debug(
                "Training batch %s | Loss: %.6f | "
                "Gradient norm: %.6f",
                batch_index,
                loss.detach().item(),
                grad_norm.detach().item(),
            )

        if total_samples == 0:
            raise ValueError(
                "Training dataloader is empty."
            )

        average_loss = (
            total_loss / total_samples
        )

        return average_loss

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def validate(self, val_loader):
        """
        Evaluate model using the validation dataloader.
        """

        if val_loader is None:
            return None

        val_loss = self.evaluator.evaluate(
            val_loader
        )

        if val_loss is None:
            raise RuntimeError(
                "Evaluator returned no validation loss."
            )

        if isinstance(val_loss, torch.Tensor):

            if val_loss.numel() != 1:
                raise ValueError(
                    "Validation loss must be scalar."
                )

            val_loss = val_loss.detach().item()

        val_loss = float(val_loss)

        if not math.isfinite(val_loss):
            raise RuntimeError(
                "Non-finite validation loss detected."
            )

        return val_loss

    # --------------------------------------------------
    # Learning Rate Scheduler
    # --------------------------------------------------

    def _step_scheduler(self, current_loss):
        """
        Update learning rate scheduler.
        """

        if self.scheduler is None:
            return

        if isinstance(
            self.scheduler,
            torch.optim.lr_scheduler.ReduceLROnPlateau,
        ):

            self.scheduler.step(current_loss)

        else:

            self.scheduler.step()

    # --------------------------------------------------
    # Learning Rate
    # --------------------------------------------------

    def _get_learning_rate(self) -> float:

        if not self.optimizer.param_groups:
            return 0.0

        return float(
            self.optimizer.param_groups[0]["lr"]
        )

    # --------------------------------------------------
    # Save Checkpoint
    # --------------------------------------------------

    def _save_checkpoint(
        self,
        filename,
        epoch,
        best_loss,
    ):
        """
        Save all trainable components and optimizer state.
        """

        self.checkpoint_manager.save(
            filename=filename,
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            epoch=epoch,
            best_loss=best_loss,
            prompt_encoder=self.prompt_encoder,
            text_feature_extractor=(
                self.text_feature_extractor
            ),
        )

        logger.info(
            "Checkpoint saved: %s",
            filename,
        )

    # --------------------------------------------------
    # Fit
    # --------------------------------------------------

    def fit(
        self,
        train_loader,
        val_loader=None,
        epochs=20,
        save_every=1,
    ):
        """
        Train the model for multiple epochs.

        Args:
            train_loader: Training dataloader.
            val_loader: Optional validation dataloader.
            epochs: Number of training epochs.
            save_every: Save latest checkpoint every N epochs.
                        Use 0 to disable periodic latest saves.

        Returns:
            list: Training history.
        """

        if train_loader is None:
            raise ValueError(
                "Training dataloader cannot be None."
            )

        if (
            not isinstance(epochs, int)
            or isinstance(epochs, bool)
            or epochs < 1
        ):
            raise ValueError(
                "Epochs must be a positive integer."
            )

        if (
            not isinstance(save_every, int)
            or isinstance(save_every, bool)
            or save_every < 0
        ):
            raise ValueError(
                "save_every must be a non-negative integer."
            )

        history = []

        logger.info(
            "Training started | Epochs: %s | Device: %s",
            epochs,
            self.device,
        )

        try:

            for epoch in range(1, epochs + 1):

                # ------------------------------------------
                # Training
                # ------------------------------------------

                train_loss = self.train_one_epoch(
                    train_loader
                )

                # ------------------------------------------
                # Validation
                # ------------------------------------------

                val_loss = self.validate(
                    val_loader
                )

                current_loss = (
                    val_loss
                    if val_loss is not None
                    else train_loss
                )

                # ------------------------------------------
                # Learning Rate Scheduling
                # ------------------------------------------

                self._step_scheduler(
                    current_loss
                )

                learning_rate = (
                    self._get_learning_rate()
                )

                # ------------------------------------------
                # Record Progress
                # ------------------------------------------

                epoch_result = {
                    "epoch": epoch,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "learning_rate": learning_rate,
                }

                history.append(epoch_result)

                self.history.append(
                    epoch_result.copy()
                )

                logger.info(
                    "Epoch [%s/%s] | "
                    "Train Loss: %.6f | "
                    "Val Loss: %s | "
                    "LR: %.8f",
                    epoch,
                    epochs,
                    train_loss,
                    (
                        f"{val_loss:.6f}"
                        if val_loss is not None
                        else "N/A"
                    ),
                    learning_rate,
                )

                # ------------------------------------------
                # Save Best Model
                # ------------------------------------------

                if current_loss < self.best_loss:

                    self.best_loss = current_loss

                    self._save_checkpoint(
                        filename="best_model.pt",
                        epoch=epoch,
                        best_loss=self.best_loss,
                    )

                    logger.info(
                        "New best model saved. Loss: %.6f",
                        self.best_loss,
                    )

                # ------------------------------------------
                # Save Latest Model
                # ------------------------------------------

                if (
                    save_every > 0
                    and epoch % save_every == 0
                ):

                    self._save_checkpoint(
                        filename="latest_model.pt",
                        epoch=epoch,
                        best_loss=self.best_loss,
                    )

            logger.info(
                "Training completed successfully. "
                "Best loss: %.6f",
                self.best_loss,
            )

            return history

        except Exception:

            logger.exception(
                "Training process failed."
            )

            raise

    # --------------------------------------------------
    # Get Training History
    # --------------------------------------------------

    def get_history(self) -> list:
        """
        Return a copy of the training history.
        """

        return [
            item.copy()
            for item in self.history
        ]

    # --------------------------------------------------
    # Get Best Loss
    # --------------------------------------------------

    def get_best_loss(self) -> float:
        """
        Return the best validation/training loss.
        """

        return self.best_loss
