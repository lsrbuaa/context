#!/usr/bin/env python3
"""Run the long-context experiment using the local WorkBuddy login.

This helper must run as the same Windows user that is logged into WorkBuddy.
It decrypts WorkBuddy's Electron SecretStorage in memory, sets
WORKBUDDY_API_TOKEN for this process only, then calls run_experiment.py.
The token is never printed and never written to disk.
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import ctypes.wintypes
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from run_experiment import apply_cli_overrides, load_config, run_experiment


APPDATA = Path(os.environ.get("APPDATA", r"C:\Users\lsr_buaa\AppData\Roaming"))
WORKBUDDY_USER_DATA = APPDATA / "WorkBuddy"
LOCAL_STATE = WORKBUDDY_USER_DATA / "Local State"
GLOBAL_STATE = WORKBUDDY_USER_DATA / "User" / "globalStorage" / "state.vscdb"
SECRET_KEY = 'secret://{"extensionId":"tencent-cloud.coding-copilot","key":"planning-genie.new.accessTokencn"}'
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config.workbuddy.local.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "runs"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def dpapi_unprotect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    in_buf = ctypes.create_string_buffer(data)
    in_blob = DATA_BLOB(len(data), ctypes.cast(in_buf, ctypes.POINTER(ctypes.c_char)))
    out_blob = DATA_BLOB()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def decrypt_chromium_v10(encrypted: bytes, aes_key: bytes) -> str:
    if not encrypted.startswith(b"v10"):
        raise RuntimeError("Unsupported WorkBuddy secret format; expected Chromium v10.")
    nonce = encrypted[3:15]
    ciphertext_and_tag = encrypted[15:]
    return AESGCM(aes_key).decrypt(nonce, ciphertext_and_tag, None).decode("utf-8")


def read_secret_blob() -> bytes:
    if not GLOBAL_STATE.exists():
        raise RuntimeError(f"WorkBuddy global state DB not found: {GLOBAL_STATE}")
    con = sqlite3.connect(str(GLOBAL_STATE))
    try:
        row = con.execute("select value from ItemTable where key=?", (SECRET_KEY,)).fetchone()
    finally:
        con.close()
    if not row:
        raise RuntimeError("WorkBuddy access token secret was not found. Please log into WorkBuddy first.")
    value = json.loads(row[0])
    return bytes(value["data"])


def read_aes_key() -> bytes:
    if not LOCAL_STATE.exists():
        raise RuntimeError(f"WorkBuddy Local State not found: {LOCAL_STATE}")
    state = json.loads(LOCAL_STATE.read_text(encoding="utf-8"))
    encrypted_key_b64 = state.get("os_crypt", {}).get("encrypted_key")
    if not encrypted_key_b64:
        raise RuntimeError("WorkBuddy Local State does not contain os_crypt.encrypted_key.")
    encrypted_key = base64.b64decode(encrypted_key_b64)
    if encrypted_key.startswith(b"DPAPI"):
        encrypted_key = encrypted_key[5:]
    return dpapi_unprotect(encrypted_key)


def extract_token(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        preferred_keys = [
            "accessToken",
            "access_token",
            "token",
            "bearerToken",
            "authorization",
            "Authorization",
        ]
        for key in preferred_keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate:
                return candidate.removeprefix("Bearer ").strip()
        for nested in value.values():
            try:
                return extract_token(nested)
            except RuntimeError:
                pass
    if isinstance(value, list):
        for nested in value:
            try:
                return extract_token(nested)
            except RuntimeError:
                pass
    raise RuntimeError("Could not locate an access token in the decrypted WorkBuddy secret.")


def load_workbuddy_token() -> str:
    aes_key = read_aes_key()
    plain = decrypt_chromium_v10(read_secret_blob(), aes_key)
    try:
        return extract_token(json.loads(plain))
    except json.JSONDecodeError:
        return extract_token(plain)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run long-context decay tests using the local WorkBuddy login."
    )
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    p.add_argument(
        "--mode",
        choices=["smoke", "pilot", "full"],
        default="smoke",
        help="smoke: 1 call; pilot: small all-tier run; full: config defaults.",
    )
    p.add_argument("--samples-per-tier", type=int)
    p.add_argument("--repeats", type=int)
    p.add_argument("--tiers", nargs="+", type=float)
    p.add_argument("--prepared-cases-path")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        token = load_workbuddy_token()
    except Exception as exc:
        print(
            "Unable to use the local WorkBuddy login from this process. "
            "Run this helper from the same Windows user that is logged into WorkBuddy.",
            file=sys.stderr,
        )
        print(f"Reason: {exc}", file=sys.stderr)
        return 1

    os.environ["WORKBUDDY_API_TOKEN"] = token
    config = load_config(args.config)

    if args.mode == "smoke":
        config["tiers"] = [0.30]
        config["samples_per_tier"] = 1
        config["repeats"] = 1
    elif args.mode == "pilot":
        config["tiers"] = [0.30, 0.50, 0.70, 0.80, 0.90, 0.95]
        config["samples_per_tier"] = 5
        config["repeats"] = 1

    class _Args:
        provider = None
        model = None
        context_window_tokens = None
        reserved_output_tokens = None
        fixed_system_overhead_tokens = None
        seed = None
        save_prompts = False
        real_tasks_path = None
        prepared_cases_path = None

    overrides = _Args()
    overrides.samples_per_tier = args.samples_per_tier
    overrides.repeats = args.repeats
    overrides.tiers = args.tiers
    overrides.prepared_cases_path = args.prepared_cases_path
    config = apply_cli_overrides(config, overrides)

    run_dir = run_experiment(config, Path(args.output_dir).resolve())
    print(f"Run artifacts written to: {run_dir}")
    print(f"Report: {run_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
