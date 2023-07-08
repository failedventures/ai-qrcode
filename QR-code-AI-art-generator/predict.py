# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from app import create_pipe, inference
from cog import BasePredictor, Input, Path

MODEL_ID = "Lykon/DreamShaper"

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        self.pipe = create_pipe(MODEL_ID)

    def predict(
        self,
        qr_code_content: str = Input(description="Content for the QR code"),
        prompt: str = Input(description="Prompt text"),
        negative_prompt: str = Input(description="Negative prompt text"),
        guidance_scale: float = Input(description="Guidance scale", ge=0.0, default=7.5),
        controlnet_conditioning_scale: float = Input(description="ControlNet conditioning scale", ge=0.0, default=1.4),
        strength: float = Input(description="Strength", ge=0.0, le=1.0, default=0.95),
        seed: int = Input(description="Seed for the random generator", default=-1),
        sampler: str = Input(description="Name of the sampler", default="DPM++ Karras SDE"),
        num_inference_steps: int = Input(description="Number of inference steps", ge=0, default=40),
    ) -> Path:
        """Run a single prediction on the model"""
        # processed_input = preprocess(image)
        # output = self.model(processed_image, scale)
        # return postprocess(output)
        img = inference(qr_code_content, prompt, negative_prompt,
                        guidance_scale=guidance_scale,
                        controlnet_conditioning_scale=controlnet_conditioning_scale,
                        strength=strength,
                        seed=seed,
                        sampler=sampler,
                        num_inference_steps=num_inference_steps,
                        _pipe = self.pipe)
        output_path = "/tmp/out.png"
        img.save(output_path)
        return Path(output_path)