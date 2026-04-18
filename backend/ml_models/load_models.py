#!/usr/bin/env python
"""
Download and cache all required models
Run once at startup
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer


def download_models():
    print("Downloading models (this may take a few minutes)...")

    # Download T5 for humanization
    print("Downloading T5-base...")
    T5ForConditionalGeneration.from_pretrained('t5-base')
    T5Tokenizer.from_pretrained('t5-base')

    print("✅ All models downloaded successfully!")
    print("Models cached in: ~/.cache/huggingface/hub/")


if __name__ == '__main__':
    download_models()
