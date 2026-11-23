import torch


class ModelEvaluator:
    def __init__(
        self,
        model,
        prompt_encoder,
        text_feature_extractor,
        device,
    ):
        self.device = torch.device(device)

        self.model = model.to(self.device)

        self.prompt_encoder = prompt_encoder.to(
            self.device
        )

        self.text_feature_extractor = (
            text_feature_extractor.to(self.device)
        )

    @torch.no_grad()
    def evaluate(self, dataloader):

        self.model.eval()
        self.prompt_encoder.eval()
        self.text_feature_extractor.eval()

        total_loss = 0.0
        total_samples = 0

        for batch in dataloader:

            # Load images
            images = batch["images"].to(
                self.device,
                non_blocking=True,
            )

            # Load token IDs
            token_ids = batch["token_ids"].to(
                self.device,
                non_blocking=True,
            )

            # Encode text prompts
            embeddings = self.prompt_encoder(
                token_ids
            )

            # Extract text features
            # Padding tokens are excluded from mean pooling
            text_features = self.text_feature_extractor(
                embeddings,
                token_ids,
            )

            # Calculate validation loss
            loss = self.model.training_loss(
                images,
                text_features,
            )

            if not torch.isfinite(loss):
                raise RuntimeError(
                    f"Non-finite validation loss: {loss.item()}"
                )

            batch_size = images.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size

        if total_samples == 0:
            raise ValueError(
                "Validation dataloader is empty"
            )

        average_loss = total_loss / total_samples

        return average_loss
