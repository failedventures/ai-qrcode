#!/usr/bin/env python3

import os
import sys
import logging
import argparse

from app import create_pipe

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser("Download model weights from HuggingFace")
    parser.add_argument("--diffusion-models", nargs="+",
                        default=["Lykon/DreamShaper"],
                        help="List of diffusion models to download")
    # parser.add_argument("--controlnet-models", nargs="+",
    #                     default=["DionTimmer/controlnet_qrcode-control_v1p_sd15"],
    #                     help="List of controlnet models to download")
    parser.add_argument("--model-cache-dir", default="diffusers-cache",
                        help="Directory to download models in")
    return parser.parse_args()


def mkdir_p(path):
    os.makedirs(path, exist_ok=True)


def main():
    args = parse_args()
    model_cache_dir = args.model_cache_dir
    log.info(f"Downloading models to {model_cache_dir}")
    mkdir_p(model_cache_dir)
    for model in args.diffusion_models:
        log.info(f"Downloading diffusion model {model}...")
        create_pipe(model)


if __name__ == "__main__":
    sys.exit(main())