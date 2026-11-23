from app.ai.inference.generation_engine import GenerationEngine


class Cute3DPredictor:
    def __init__(self, generation_engine):
        self.generation_engine = generation_engine

    def predict(
        self,
        prompt,
        num_images=1,
        seed=None,
    ):
        result = self.generation_engine.generate(
            prompt=prompt,
            num_images=num_images,
            seed=seed,
            save=True,
        )

        return {
            "success": True,
            "prompt": result["prompt"],
            "image_count": len(result["images"]),
            "images": result["images"],
            "image_paths": result["paths"],
        }

    def predict_one(self, prompt, seed=None):
        result = self.predict(
            prompt=prompt,
            num_images=1,
            seed=seed,
        )

        return result["images"][0]

