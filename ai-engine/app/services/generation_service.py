import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GenerationService:

    def __init__(self, generation_pipeline):
        self.generation_pipeline = generation_pipeline

    def generate(self, prompt, num_images=1, seed=None):
        """
        Generate images and return generation information.
        """

        try:
            results = self.generation_pipeline.generate(
                prompt=prompt,
                num_images=num_images,
                seed=seed,
            )

            # GenerationEngine may return image paths,
            # PIL images, or a list of generated results.
            if results is None:
                image_paths = []

            elif isinstance(results, (str, Path)):
                image_paths = [str(results)]

            elif isinstance(results, (list, tuple)):
                image_paths = [
                    str(item) if isinstance(item, (str, Path)) else item
                    for item in results
                ]

            else:
                image_paths = [results]

            return {
                "success": True,
                "prompt": prompt,
                "image_count": len(image_paths),
                "images": image_paths,
            }

        except Exception:
            logger.exception("Generation service failed.")
            raise

    def get_status(self):
        return self.generation_pipeline.get_status()