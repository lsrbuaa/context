#!/usr/bin/env python3
"""Create a local WorkBuddy config for the long-context experiment harness."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_PRODUCT_JSON = Path(
    r"D:\WorkBuddy\resources\app\extensions\genie\product.json"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "config.workbuddy.local.json"


def load_product(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def choose_model(product: dict[str, Any], requested: str | None) -> dict[str, Any]:
    models = list(product.get("models") or [])
    if requested:
        for model in models:
            if model.get("id") == requested or model.get("name") == requested:
                return model
        raise SystemExit(f"Model not found in WorkBuddy product.json: {requested}")

    text_models = [
        model
        for model in models
        if not model.get("tags")
        and not model.get("disabledMultimodal") is False
        and int(model.get("maxInputTokens") or 0) > 0
    ]
    if not text_models:
        raise SystemExit("No text model with maxInputTokens found in WorkBuddy product.json.")
    return max(text_models, key=lambda model: int(model.get("maxInputTokens") or 0))


def build_config(product: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    max_input = int(model.get("maxInputTokens") or model.get("maxAllowedSize") or 128000)
    max_output = int(model.get("maxOutputTokens") or 8192)
    endpoint = str(product.get("endpoint") or "https://copilot.tencent.com").rstrip("/")
    return {
        "experiment_name": "long_context_decay_workbuddy",
        "context_window_tokens": max_input,
        "reserved_output_tokens": min(max_output, max(2048, max_input // 20)),
        "fixed_system_overhead_tokens": 1200,
        "tiers": [0.3, 0.5, 0.7, 0.8, 0.9, 0.95],
        "samples_per_tier": 30,
        "repeats": 3,
        "seed": 20260625,
        "save_prompts": False,
        "provider": {
            "type": "workbuddy_api",
            "model": model["id"],
            "temperature": 0,
            "max_output_tokens": 512,
            "timeout_seconds": 180,
            "workbuddy_endpoint": endpoint,
            "workbuddy_api_key_env": "WORKBUDDY_API_TOKEN",
            "openai_base_url": f"{endpoint}/v1/chat/completions",
        },
        "score_weights": {
            "fact_recall": 0.4,
            "needle_position": 0.4,
            "instruction_following": 0.25,
            "multi_hop": 0.2,
            "distractor_resistance": 0.15,
            "real_workbuddy": 0.2,
        },
        "degradation_threshold": 0.1,
        "category_drop_threshold": 0.15,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a local WorkBuddy config for long-context decay runs."
    )
    parser.add_argument("--product-json", default=str(DEFAULT_PRODUCT_JSON))
    parser.add_argument("--model", help="WorkBuddy model id or name. Defaults to largest input window.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    product_path = Path(args.product_json)
    if not product_path.exists():
        raise SystemExit(f"WorkBuddy product.json not found: {product_path}")

    product = load_product(product_path)
    model = choose_model(product, args.model)
    config = build_config(product, model)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Endpoint: {config['provider']['workbuddy_endpoint']}")
    print(
        "Model: "
        f"{model.get('id')} ({model.get('name', model.get('id'))}), "
        f"maxInputTokens={model.get('maxInputTokens')}, "
        f"maxOutputTokens={model.get('maxOutputTokens')}"
    )
    print("Token env: WORKBUDDY_API_TOKEN")
    print("Note: the token is not read from WorkBuddy local storage and is not written to config.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
