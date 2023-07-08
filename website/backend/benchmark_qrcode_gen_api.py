import time
import json
import random
import qrcode_gen_api

qrcode_gen_api.setup_runpod("us92if08t5s7xt", "")
BASE_CONFIG = {
      "qr_code_content": "https://www.example.com",
      "prompt": "Girl with beautiful dress, in front of majestic mountain view landscape",
      "negative_prompt": "ugly, disfigured, low quality, blurry, nsfw, plain, mangled, weird",
      "strength": 0.95,
      "guidance_scale": 7.5,
      "controlnet_conditioning_scale": 1.4,
      "num_inference_steps": 40,
      "seed": 2313123,
}

data_file = "benchmark_results.json"
benchmark_results = []

while(True):
    interval = random.randint(5, 5*60)
    print("Requesting after %d seconds" % interval)
    time.sleep(interval)
    start = time.monotonic()
    print("Request start")
    _ = qrcode_gen_api.qrcode_gen_runpod(BASE_CONFIG)
    print("Request end")
    end = time.monotonic()
    api_call_duration =  end - start
    benchmark_results.append({"interval": interval,
                              "api_call_duration": api_call_duration})
    with open(data_file, "w") as f:
        json.dump(benchmark_results, f)
