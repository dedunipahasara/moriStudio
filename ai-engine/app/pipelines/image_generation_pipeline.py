import logging

logger = logging.getLogger(__name__)


class ImageGenerationPipeline:

    def __init__(self, text_to_image_pipeline):
        self.pipeline = text_to_image_pipeline

    def generate(self, prompt, num_images=1, seed=None):
        """
        Validate request and generate images.
        """

        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        prompt = prompt.strip()

        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        if len(prompt) > 1000:
            raise ValueError("Prompt cannot exceed 1000 characters.")

        if not isinstance(num_images, int) or isinstance(num_images, bool):
            raise TypeError("num_images must be an integer.")

        if not 1 <= num_images <= 4:
            raise ValueError(
                "num_images must be between 1 and 4."
            )

        try:
            return self.pipeline.generate(
                prompt=prompt,
                num_images=num_images,
                seed=seed,
            )

        except Exception:
            logger.exception("Image generation pipeline failed.")
            raise

    def get_status(self):
        return self.pipeline.get_status()
