import io
import base64
import runpod

from app import create_pipe, inference

MODEL_ID = "Lykon/DreamShaper"

## load your model(s) into vram here
pipe = create_pipe(MODEL_ID)

def handler(event):
    # Event looks like this:
    # {
    #     'delayTime': 2534,
    #     'id': '2a16b881-830f-4d14-af5b-f7db7c0a96fc',
    #     'input': {
    #         'prompt': 'A beautiful painting of a singular lighthouse, shining its light across a tumultuous sea of blood by greg rutkowski and thomas kinkade, Trending on artstation.'
    #         },
    #     'status': 'IN_PROGRESS'
    # }
    print(event)
    qr_code_content = event["input"]["qr_code_content"]
    prompt = event["input"]["prompt"]
    negative_prompt = event["input"]["negative_prompt"]
    guidance_scale = event["input"]["guidance_scale"]
    controlnet_conditioning_scale = event["input"]["controlnet_conditioning_scale"]
    strength = event["input"]["strength"]
    seed = event["input"]["seed"]
    # sampler = event["input"]["sampler"]
    num_inference_steps = event["input"]["num_inference_steps"]

    img = inference(qr_code_content, prompt, negative_prompt,
                    guidance_scale=guidance_scale,
                    controlnet_conditioning_scale=controlnet_conditioning_scale,
                    strength=strength,
                    seed=seed,
                    sampler="DPM++ Karras SDE",
                    num_inference_steps=num_inference_steps,
                    _pipe = pipe)
    print("Generated QR Code!")
    # Return the image bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode("ascii")


runpod.serverless.start({
    "handler": handler
})