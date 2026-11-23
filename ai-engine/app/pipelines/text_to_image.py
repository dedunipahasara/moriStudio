from app.ai.inference.inference_engine import InferenceEngine
from app.ai.inference.generation_engine import GenerationEngine


class TextToImagePipeline:
    def __init__(
        self,
        inference_engine: InferenceEngine,
        generation_engine: GenerationEngine,
    ):
        self.inference_engine = inference_engine
        self.generation_engine = generation_engine

    def load_model(self, checkpoint_path):
        return self.inference_engine.load_checkpoint(
            checkpoint_path
        )

    def generate(
        self,
        prompt,
        num_images=1,
        seed=None,
        save=True,
    ):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if num_images < 1:
            raise ValueError("num_images must be at least 1")

        result = self.generation_engine.generate(
            prompt=prompt,
            num_images=num_images,
            seed=seed,
            save=save,
        )

        return {
            "success": True,
            "prompt": prompt,
            "image_count": len(result["images"]),
            "images": result["images"],
            "paths": result["paths"],
        }

    def get_status(self):
        return self.inference_engine.get_status()
