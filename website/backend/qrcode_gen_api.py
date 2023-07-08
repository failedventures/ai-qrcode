import time
import base64
import requests
import replicate
from typing import Dict

# TODO: Refactor into classes.

###############################################################################
# Replicate API ###############################################################
###############################################################################

REPLICATE_IMAGE = "dannypostma/cog-visual-qr:7653601d0571fa6342ba4fa93a0962adebd1169e9e2329eefeb5729cac645d42"


def setup_replicate(api_token: str, image=REPLICATE_IMAGE) -> None:
    global REPLICATE_IMAGE
    REPLICATE_IMAGE = image
    replicate.default_client.api_token = api_token


def qrcode_gen_replicate(config: Dict) -> bytes:
    input = {k: v for k, v in config.items()}
    output_url = replicate.run(
        # TODO: Replace with your own image
        REPLICATE_IMAGE,
        input=input
    )
    resp = requests.get(output_url)
    resp.raise_for_status()
    return resp.content


###############################################################################
# RunPod API ##################################################################
###############################################################################


RUNPOD_ENDPOINT = ""
RUNPOD_API_TOKEN = ""


def setup_runpod(endpoint: str, api_token: str) -> None:
    global RUNPOD_ENDPOINT
    global RUNPOD_API_TOKEN
    RUNPOD_ENDPOINT = endpoint
    RUNPOD_API_TOKEN = api_token


def qrcode_gen_runpod(config: Dict) -> bytes:
    global RUNPOD_ENDPOINT
    global RUNPOD_API_TOKEN
    api_run_url = "https://api.runpod.ai/v2/%s/run" % RUNPOD_ENDPOINT
    headers = {
        "Authorization": "Bearer %s" % RUNPOD_API_TOKEN,
        "Content-Type": "application/json",
    }
    body = {
        "input": config.copy(),
    }
    resp = requests.post(api_run_url, headers=headers, json=body)
    resp.raise_for_status()
    run_id = resp.json()["id"]
    api_status_url = ("https://api.runpod.ai/v2/%s/status/%s"
                      % (RUNPOD_ENDPOINT, run_id))
    retry_time_sec = 60*5
    retry_period_sec = 10
    for _ in range(retry_time_sec//retry_period_sec):
        resp = requests.get(api_status_url, headers=headers)
        resp.raise_for_status()
        if resp.json()["status"] == "COMPLETED":
            return base64.b64decode(resp.json()["output"].encode("ascii"))
        time.sleep(retry_period_sec)
