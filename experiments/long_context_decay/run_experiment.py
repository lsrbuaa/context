#!/usr/bin/env python3
"""Long-context degradation experiment harness for WorkBuddy-style agents.

The harness intentionally avoids product-side retrieval, summarization, and
compression. It builds controlled long prompts at fixed context occupancy tiers,
calls a configured model provider, scores the answer, and writes run artifacts:
JSONL, CSV summaries, a Markdown report, and three SVG charts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CONFIG: dict[str, Any] = {
    "experiment_name": "long_context_decay",
    "context_window_tokens": 128000,
    "reserved_output_tokens": 4096,
    "fixed_system_overhead_tokens": 1200,
    "tiers": [0.30, 0.50, 0.70, 0.80, 0.90, 0.95],
    "samples_per_tier": 30,
    "repeats": 3,
    "seed": 20260625,
    "save_prompts": False,
    "prepared_cases_path": "",
    "real_tasks_path": "",
    "provider": {
        "type": "oracle",
        "model": "oracle-self-test",
        "temperature": 0,
        "max_output_tokens": 512,
        "timeout_seconds": 120,
        "openai_base_url": "https://api.openai.com/v1/chat/completions",
        "openai_api_key_env": "OPENAI_API_KEY",
        "workbuddy_endpoint": "https://copilot.tencent.com",
        "workbuddy_api_key_env": "WORKBUDDY_API_TOKEN",
        "command": "",
        "http_url": "",
        "http_headers": {},
    },
    "score_weights": {
        "fact_recall": 0.40,
        "needle_position": 0.40,
        "instruction_following": 0.25,
        "multi_hop": 0.20,
        "distractor_resistance": 0.15,
        "real_workbuddy": 0.20,
    },
    "degradation_threshold": 0.10,
    "category_drop_threshold": 0.15,
}


SYSTEM_PROMPT = """You are WorkBuddy's model inside a long-context stress test.
Use only the supplied context. Do not use outside knowledge. Return only the
requested JSON object, without Markdown fences or commentary."""


TASK_ORDER = [
    "fact_recall",
    "needle_position",
    "multi_hop",
    "instruction_following",
    "distractor_resistance",
]

NEEDLE_POSITIONS = [0.05, 0.25, 0.50, 0.75, 0.95]


FILLER_TOPICS = [
    "calendar reconciliation",
    "device telemetry triage",
    "meeting action tracking",
    "memory governance review",
    "customer support routing",
    "release readiness checklist",
    "sensor annotation cleanup",
    "workspace policy audit",
    "incident follow-up planning",
    "prototype feedback synthesis",
]

FILLER_VERBS = [
    "confirmed",
    "deferred",
    "tagged",
    "reviewed",
    "compared",
    "linked",
    "mirrored",
    "archived",
    "queued",
    "reconciled",
]

FILLER_OBJECTS = [
    "the reminder batch",
    "the project snapshot",
    "the low-confidence memory",
    "the contact alias",
    "the stale task group",
    "the private transcript",
    "the wearable event log",
    "the retrieval candidate",
    "the handoff note",
    "the daily plan",
]


@dataclass(frozen=True)
class PromptBundle:
    system: str
    user: str


@dataclass(frozen=True)
class TaskCase:
    case_id: str
    category: str
    tier: float
    sample_index: int
    needle_position: float | None
    prompt: PromptBundle
    expected_answer: str
    expected_json: dict[str, Any]
    distractor_answers: list[str]
    estimated_prompt_tokens: int
    target_prompt_tokens: int
    prompt_hash: str


@dataclass
class ProviderResponse:
    text: str
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw: dict[str, Any] | None = None


@dataclass
class TrialResult:
    run_id: str
    case_id: str
    repeat_index: int
    provider_type: str
    model: str
    category: str
    tier: float
    sample_index: int
    needle_position: float | None
    target_prompt_tokens: int
    estimated_prompt_tokens: int
    prompt_hash: str
    response_text: str
    response_hash: str
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    expected_answer: str
    parsed_answer: str
    pass_1: bool
    structured_output_valid: bool
    instruction_followed: bool | None
    reference_error: bool
    hallucination_flag: bool
    score_reason: str


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | None) -> dict[str, Any]:
    config = DEFAULT_CONFIG
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            user_config = json.load(handle)
        config = deep_merge(config, user_config)
    return config


def parse_tiers(raw: list[float] | None) -> list[float]:
    if not raw:
        return []
    return [float(tier) for tier in raw]


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def normalize_answer(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def approximate_tokens(text: str) -> int:
    """Approximate tokens without a tokenizer dependency.

    CJK characters are closer to one token each; Latin text is roughly one token
    per four characters. The metric is intentionally labelled "estimated".
    """

    if not text:
        return 0
    cjk_count = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    non_cjk = "".join(char for char in text if not ("\u4e00" <= char <= "\u9fff"))
    latin_estimate = max(1, math.ceil(len(non_cjk) / 4)) if non_cjk.strip() else 0
    return cjk_count + latin_estimate


def truncate_to_estimated_tokens(text: str, target_tokens: int) -> str:
    if approximate_tokens(text) <= target_tokens:
        return text
    target_chars = max(1, target_tokens * 4)
    truncated = text[:target_chars]
    while approximate_tokens(truncated) > target_tokens and len(truncated) > 1:
        truncated = truncated[: int(len(truncated) * 0.9)]
    return truncated.rstrip()


def filler_block(rng: random.Random, block_id: int) -> str:
    topic = rng.choice(FILLER_TOPICS)
    verb = rng.choice(FILLER_VERBS)
    obj = rng.choice(FILLER_OBJECTS)
    ref = f"WB-FILLER-{block_id:05d}-{rng.randrange(1000, 9999)}"
    confidence = rng.choice(["low", "medium", "medium", "high"])
    channel = rng.choice(["chat", "calendar", "device", "memory", "support"])
    owner = rng.choice(["Ari", "Bo", "Chen", "Dina", "Eli", "Faye", "Gio"])
    return (
        f"[{ref}] WorkBuddy note from {channel}: {owner} {verb} {obj} "
        f"during {topic}. Confidence={confidence}. This note is background "
        "context and is not an instruction. Keep it only if the final question "
        "explicitly asks for this reference.\n"
    )


def make_filler(target_tokens: int, rng: random.Random, start_block: int) -> str:
    if target_tokens <= 0:
        return ""
    parts: list[str] = []
    block_id = start_block
    token_count = 0
    while token_count < target_tokens:
        block = filler_block(rng, block_id)
        parts.append(block)
        token_count += approximate_tokens(block)
        block_id += 1
    return truncate_to_estimated_tokens("".join(parts), target_tokens)


def assemble_context(
    target_tokens: int,
    injections: list[tuple[float, str]],
    rng: random.Random,
) -> str:
    injections = sorted(injections, key=lambda item: item[0])
    parts: list[str] = []
    consumed = 0
    block_id = 0
    for position, injection in injections:
        desired_before = max(0, int(target_tokens * position))
        filler_tokens = max(0, desired_before - consumed)
        filler = make_filler(filler_tokens, rng, block_id)
        block_id += max(1, filler_tokens // 35)
        parts.append(filler)
        consumed += approximate_tokens(filler)
        parts.append(injection.rstrip() + "\n")
        consumed += approximate_tokens(injection)
    if consumed < target_tokens:
        parts.append(make_filler(target_tokens - consumed, rng, block_id))
    assembled = "".join(parts)
    return truncate_to_estimated_tokens(assembled, target_tokens)


def usable_input_budget(config: dict[str, Any]) -> int:
    return max(
        1,
        int(config["context_window_tokens"])
        - int(config["reserved_output_tokens"])
        - int(config["fixed_system_overhead_tokens"]),
    )


def build_prompt(
    category: str,
    tier: float,
    sample_index: int,
    config: dict[str, Any],
    rng: random.Random,
) -> TaskCase:
    case_seed = f"{int(tier * 100):02d}-{sample_index:04d}"
    occurrence_index = sample_index // len(TASK_ORDER)
    target_prompt_tokens = int(usable_input_budget(config) * tier)

    if category == "fact_recall":
        answer = f"FR-{case_seed}-KAPPA"
        evidence_id = f"FACT-{case_seed}"
        position = NEEDLE_POSITIONS[occurrence_index % len(NEEDLE_POSITIONS)]
        injection = (
            f"[{evidence_id}] AUTHORITATIVE FACT: The WorkBuddy access value "
            f"for audit packet WB-AUDIT-{case_seed} is {answer}.\n"
        )
        question = (
            f"For audit packet WB-AUDIT-{case_seed}, what is the exact "
            "WorkBuddy access value?"
        )
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors: list[str] = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "needle_position":
        answer = f"ND-{case_seed}-ORCHID"
        evidence_id = f"NEEDLE-{case_seed}"
        position = NEEDLE_POSITIONS[occurrence_index % len(NEEDLE_POSITIONS)]
        injection = (
            f"[{evidence_id}] NEEDLE RECORD: If asked for the recovery token "
            f"of session WB-SESSION-{case_seed}, answer exactly {answer}.\n"
        )
        question = f"What is the recovery token of session WB-SESSION-{case_seed}?"
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "multi_hop":
        person = f"Person-{case_seed}"
        project = f"Project-{case_seed}"
        track = f"Track-{case_seed}"
        answer = f"Reviewer-{case_seed}-LYRA"
        injections = [
            (
                0.08,
                f"[HOP-A-{case_seed}] {person} owns {project} for the next "
                "WorkBuddy planning review.\n",
            ),
            (
                0.50,
                f"[HOP-B-{case_seed}] {project} uses deployment track {track} "
                "when preparing release notes.\n",
            ),
            (
                0.92,
                f"[HOP-C-{case_seed}] Any item on deployment track {track} "
                f"must be reviewed by {answer}.\n",
            ),
        ]
        question = f"Who must review the WorkBuddy item owned by {person}?"
        expected_json = {"answer": answer, "chain": [person, project, track]}
        distractors = []
        needle_position = None

    elif category == "instruction_following":
        answer = f"OK-{case_seed}"
        safety_phrase = f"RULE-{case_seed}-NO-COMPRESS"
        position = [0.10, 0.50, 0.85][occurrence_index % 3]
        injection = (
            f"[RULE-{case_seed}] LONG-LIVED WORKBUDDY RULE: For request "
            f"WB-RULE-CHECK-{case_seed}, the JSON response must include "
            f'"safety_phrase":"{safety_phrase}" and "answer":"{answer}".\n'
        )
        question = (
            f"Complete request WB-RULE-CHECK-{case_seed}. Preserve all "
            "long-lived WorkBuddy response rules."
        )
        expected_json = {"answer": answer, "safety_phrase": safety_phrase}
        distractors = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "distractor_resistance":
        answer = f"Owner-{case_seed}-NOVA"
        old_owner = f"Owner-{case_seed}-MIRA"
        unrelated_owner = f"Owner-{case_seed}-SOL"
        evidence_id = f"DISTRACTOR-AUTH-{case_seed}"
        injections = [
            (
                0.18,
                f"[DISTRACTOR-OLD-{case_seed}] Obsolete incident owner note: "
                f"WB-INC-{case_seed} was once handled by {old_owner}. "
                "Status=retired. Do not use retired notes for current owner.\n",
            ),
            (
                0.52,
                f"[DISTRACTOR-RELATED-{case_seed}] Related incident "
                f"WB-INC-{case_seed}-B is handled by {unrelated_owner}. "
                "This is a different incident.\n",
            ),
            (
                0.82,
                f"[{evidence_id}] AUTHORITATIVE CURRENT RECORD: The current "
                f"owner for incident WB-INC-{case_seed} is {answer}.\n",
            ),
        ]
        question = f"Who is the current owner for incident WB-INC-{case_seed}?"
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors = [old_owner, unrelated_owner]
        needle_position = 0.82

    else:
        raise ValueError(f"Unsupported category: {category}")

    shell_without_context = f"""
Experiment tier: {tier:.2f}
Task type: {category}

[LONG CONTEXT START]

[LONG CONTEXT END]

[FINAL QUESTION]
{question}

[RESPONSE FORMAT]
Return a single JSON object. At minimum include "answer". Include evidence_id,
chain, or safety_phrase only when the context requires it.
"""
    overhead_tokens = approximate_tokens(SYSTEM_PROMPT + shell_without_context)
    context_target_tokens = max(128, target_prompt_tokens - overhead_tokens)
    long_context = assemble_context(context_target_tokens, injections, rng)
    user_prompt = f"""
Experiment tier: {tier:.2f}
Task type: {category}

[LONG CONTEXT START]
{long_context}
[LONG CONTEXT END]

[FINAL QUESTION]
{question}

[RESPONSE FORMAT]
Return a single JSON object. At minimum include "answer". Include evidence_id,
chain, or safety_phrase only when the context requires it.
"""
    estimated_prompt_tokens = approximate_tokens(SYSTEM_PROMPT + user_prompt)
    prompt_hash = stable_hash(SYSTEM_PROMPT + user_prompt)
    case_id = f"{category}-{int(tier * 100):02d}-{sample_index:04d}"
    return TaskCase(
        case_id=case_id,
        category=category,
        tier=tier,
        sample_index=sample_index,
        needle_position=needle_position,
        prompt=PromptBundle(system=SYSTEM_PROMPT, user=user_prompt),
        expected_answer=answer,
        expected_json=expected_json,
        distractor_answers=distractors,
        estimated_prompt_tokens=estimated_prompt_tokens,
        target_prompt_tokens=target_prompt_tokens,
        prompt_hash=prompt_hash,
    )


def load_real_cases(
    path: str,
    tier: float,
    start_index: int,
    config: dict[str, Any],
) -> list[TaskCase]:
    if not path:
        return []
    real_path = Path(path)
    if not real_path.exists():
        return []
    cases: list[TaskCase] = []
    with open(real_path, "r", encoding="utf-8") as handle:
        for offset, line in enumerate(handle):
            if not line.strip():
                continue
            item = json.loads(line)
            answer = str(item["expected_answer"])
            question = str(item["question"])
            context = str(item["context"])
            expected_json = item.get("expected_json") or {"answer": answer}
            user_prompt = f"""
Experiment tier: {tier:.2f}
Task type: real_workbuddy

[LONG CONTEXT START]
{context}
[LONG CONTEXT END]

[FINAL QUESTION]
{question}

[RESPONSE FORMAT]
Return a single JSON object. At minimum include "answer".
"""
            estimated_prompt_tokens = approximate_tokens(SYSTEM_PROMPT + user_prompt)
            case_id = f"real_workbuddy-{int(tier * 100):02d}-{start_index + offset:04d}"
            cases.append(
                TaskCase(
                    case_id=case_id,
                    category="real_workbuddy",
                    tier=tier,
                    sample_index=start_index + offset,
                    needle_position=item.get("needle_position"),
                    prompt=PromptBundle(system=SYSTEM_PROMPT, user=user_prompt),
                    expected_answer=answer,
                    expected_json=expected_json,
                    distractor_answers=list(item.get("distractor_answers", [])),
                    estimated_prompt_tokens=estimated_prompt_tokens,
                    target_prompt_tokens=int(usable_input_budget(config) * tier),
                    prompt_hash=stable_hash(SYSTEM_PROMPT + user_prompt),
                )
            )
    return cases


def task_case_to_record(case: TaskCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "category": case.category,
        "tier": case.tier,
        "sample_index": case.sample_index,
        "needle_position": case.needle_position,
        "prompt": {
            "system": case.prompt.system,
            "user": case.prompt.user,
        },
        "expected_answer": case.expected_answer,
        "expected_json": case.expected_json,
        "distractor_answers": case.distractor_answers,
        "estimated_prompt_tokens": case.estimated_prompt_tokens,
        "target_prompt_tokens": case.target_prompt_tokens,
        "prompt_hash": case.prompt_hash,
    }


def task_case_from_record(record: dict[str, Any]) -> TaskCase:
    prompt = record.get("prompt") or {}
    system = prompt.get("system") or record.get("system") or SYSTEM_PROMPT
    user = prompt.get("user") or record.get("user") or record.get("prompt_user")
    if not user:
        raise ValueError(f"Prepared case {record.get('case_id')} has no user prompt.")
    combined = system + user
    return TaskCase(
        case_id=str(record["case_id"]),
        category=str(record["category"]),
        tier=float(record["tier"]),
        sample_index=int(record.get("sample_index", 0)),
        needle_position=(
            None if record.get("needle_position") is None else float(record["needle_position"])
        ),
        prompt=PromptBundle(system=system, user=user),
        expected_answer=str(record["expected_answer"]),
        expected_json=dict(record.get("expected_json") or {"answer": record["expected_answer"]}),
        distractor_answers=list(record.get("distractor_answers") or []),
        estimated_prompt_tokens=int(
            record.get("estimated_prompt_tokens") or approximate_tokens(combined)
        ),
        target_prompt_tokens=int(
            record.get("target_prompt_tokens") or approximate_tokens(combined)
        ),
        prompt_hash=str(record.get("prompt_hash") or stable_hash(combined)),
    )


def load_prepared_cases(config: dict[str, Any]) -> list[TaskCase]:
    path = str(config.get("prepared_cases_path") or "")
    if not path:
        return []
    case_path = Path(path)
    if not case_path.exists():
        raise FileNotFoundError(f"Prepared case pack not found: {case_path}")

    requested_tiers = [float(tier) for tier in config.get("tiers", [])]
    requested_tier_set = {round(tier, 4) for tier in requested_tiers}
    per_tier_limit = int(config.get("samples_per_tier") or 0)
    per_tier_counts: dict[float, int] = {}
    cases: list[TaskCase] = []
    with open(case_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            case = task_case_from_record(json.loads(line))
            tier_key = round(case.tier, 4)
            if requested_tier_set and tier_key not in requested_tier_set:
                continue
            used = per_tier_counts.get(tier_key, 0)
            if per_tier_limit > 0 and used >= per_tier_limit:
                continue
            cases.append(case)
            per_tier_counts[tier_key] = used + 1
    if not cases:
        raise RuntimeError(f"No prepared cases selected from {case_path}")
    return cases


class BaseProvider:
    def __init__(self, config: dict[str, Any], run_dir: Path):
        self.config = config
        self.run_dir = run_dir
        self.provider_config = config["provider"]
        self.provider_type = str(self.provider_config["type"])
        self.model = str(self.provider_config.get("model") or self.provider_type)

    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        raise NotImplementedError


class OracleProvider(BaseProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        start = time.perf_counter()
        text = json.dumps(case.expected_json, ensure_ascii=False)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ProviderResponse(text=text, latency_ms=latency_ms)


class DegradedMockProvider(BaseProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        rng = random.Random(f"{case.case_id}-{repeat_index}-degraded")
        pressure = max(0.0, (case.tier - 0.60) / 0.35)
        middle_penalty = 0.0
        if case.needle_position is not None:
            middle_penalty = max(0.0, 1.0 - abs(case.needle_position - 0.50) / 0.50)
        failure_probability = min(0.92, 0.05 + 0.55 * pressure + 0.25 * middle_penalty)

        start = time.perf_counter()
        if rng.random() > failure_probability:
            text = json.dumps(case.expected_json, ensure_ascii=False)
        elif case.category == "instruction_following":
            text = json.dumps({"answer": case.expected_answer}, ensure_ascii=False)
        elif case.category == "distractor_resistance" and case.distractor_answers:
            text = json.dumps({"answer": rng.choice(case.distractor_answers)}, ensure_ascii=False)
        elif case.category == "multi_hop":
            text = json.dumps({"answer": "UNKNOWN", "chain": []}, ensure_ascii=False)
        else:
            text = json.dumps({"answer": "UNKNOWN"}, ensure_ascii=False)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ProviderResponse(text=text, latency_ms=latency_ms)


class OpenAICompatibleProvider(BaseProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        api_key_env = str(self.provider_config.get("openai_api_key_env") or "OPENAI_API_KEY")
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {api_key_env}")

        url = str(self.provider_config["openai_base_url"])
        payload = {
            "model": self.model,
            "temperature": self.provider_config.get("temperature", 0),
            "max_tokens": int(self.provider_config.get("max_output_tokens", 512)),
            "messages": [
                {"role": "system", "content": case.prompt.system},
                {"role": "user", "content": case.prompt.user},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                request,
                timeout=int(self.provider_config.get("timeout_seconds", 120)),
            ) as response:
                raw_text = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible request failed: {exc.code} {body}") from exc
        latency_ms = int((time.perf_counter() - start) * 1000)
        raw = json.loads(raw_text)
        text = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage") or {}
        return ProviderResponse(
            text=text,
            latency_ms=latency_ms,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            raw=raw,
        )


class WorkBuddyAPIProvider(OpenAICompatibleProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        endpoint = str(
            self.provider_config.get("workbuddy_endpoint")
            or os.environ.get("WORKBUDDY_ENDPOINT")
            or "https://copilot.tencent.com"
        ).rstrip("/")
        self.provider_config["openai_base_url"] = str(
            self.provider_config.get("openai_base_url")
            or os.environ.get("WORKBUDDY_CHAT_COMPLETIONS_URL")
            or f"{endpoint}/v1/chat/completions"
        )
        self.provider_config["openai_api_key_env"] = str(
            self.provider_config.get("workbuddy_api_key_env")
            or os.environ.get("WORKBUDDY_API_KEY_ENV")
            or "WORKBUDDY_API_TOKEN"
        )
        return super().generate(case, repeat_index)


class CommandProvider(BaseProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        command_template = str(
            self.provider_config.get("command")
            or os.environ.get("WORKBUDDY_EVAL_COMMAND", "")
        )
        if not command_template:
            raise RuntimeError(
                "Command provider requires provider.command or WORKBUDDY_EVAL_COMMAND"
            )

        prompt_dir = self.run_dir / "provider_prompts"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = prompt_dir / f"{case.case_id}-r{repeat_index}.txt"
        combined_prompt = f"SYSTEM:\n{case.prompt.system}\n\nUSER:\n{case.prompt.user}\n"
        with open(prompt_path, "w", encoding="utf-8") as handle:
            handle.write(combined_prompt)

        command = command_template.format(
            prompt_file=str(prompt_path),
            case_id=case.case_id,
            tier=f"{case.tier:.2f}",
            repeat=repeat_index,
        )
        start = time.perf_counter()
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(self.provider_config.get("timeout_seconds", 120)),
            check=False,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        if completed.returncode != 0:
            raise RuntimeError(
                f"Command provider failed with exit code {completed.returncode}: "
                f"{completed.stderr.strip()}"
            )
        if not self.config.get("save_prompts"):
            try:
                prompt_path.unlink()
            except OSError:
                pass
        return ProviderResponse(text=completed.stdout.strip(), latency_ms=latency_ms)


class HttpProvider(BaseProvider):
    def generate(self, case: TaskCase, repeat_index: int) -> ProviderResponse:
        url = str(self.provider_config.get("http_url") or os.environ.get("WORKBUDDY_EVAL_URL", ""))
        if not url:
            raise RuntimeError("HTTP provider requires provider.http_url or WORKBUDDY_EVAL_URL")
        headers = {
            "Content-Type": "application/json",
            **dict(self.provider_config.get("http_headers") or {}),
        }
        payload = {
            "system": case.prompt.system,
            "prompt": case.prompt.user,
            "metadata": {
                "case_id": case.case_id,
                "tier": case.tier,
                "category": case.category,
                "repeat_index": repeat_index,
                "disable_compression": True,
            },
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                request,
                timeout=int(self.provider_config.get("timeout_seconds", 120)),
            ) as response:
                raw_text = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP provider failed: {exc.code} {body}") from exc
        latency_ms = int((time.perf_counter() - start) * 1000)

        try:
            raw = json.loads(raw_text)
            text = (
                raw.get("text")
                or raw.get("output")
                or raw.get("answer")
                or raw.get("response")
                or raw.get("choices", [{}])[0].get("message", {}).get("content")
                or raw_text
            )
            usage = raw.get("usage") or {}
            return ProviderResponse(
                text=str(text),
                latency_ms=latency_ms,
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
                raw=raw,
            )
        except json.JSONDecodeError:
            return ProviderResponse(text=raw_text.strip(), latency_ms=latency_ms)


def make_provider(config: dict[str, Any], run_dir: Path) -> BaseProvider:
    provider_type = str(config["provider"]["type"]).lower()
    if provider_type == "oracle":
        return OracleProvider(config, run_dir)
    if provider_type == "degraded_mock":
        return DegradedMockProvider(config, run_dir)
    if provider_type in {"openai", "openai_compatible"}:
        return OpenAICompatibleProvider(config, run_dir)
    if provider_type in {"workbuddy_api", "workbuddy_openai"}:
        return WorkBuddyAPIProvider(config, run_dir)
    if provider_type in {"command", "workbuddy_command"}:
        return CommandProvider(config, run_dir)
    if provider_type in {"http", "workbuddy_http"}:
        return HttpProvider(config, run_dir)
    raise ValueError(f"Unsupported provider type: {provider_type}")


def extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(0))
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def score_response(
    run_id: str,
    case: TaskCase,
    repeat_index: int,
    provider: BaseProvider,
    response: ProviderResponse,
) -> TrialResult:
    parsed = extract_json_object(response.text)
    structured_valid = parsed is not None
    parsed_answer = ""
    if parsed is not None and "answer" in parsed:
        parsed_answer = str(parsed.get("answer", ""))
    else:
        parsed_answer = response.text.strip()

    expected_norm = normalize_answer(case.expected_answer)
    answer_norm = normalize_answer(parsed_answer)
    exact_answer = expected_norm != "" and expected_norm in answer_norm
    reference_error = any(
        normalize_answer(distractor) in normalize_answer(response.text)
        for distractor in case.distractor_answers
    )

    instruction_followed: bool | None = None
    if case.category == "instruction_following":
        expected_phrase = str(case.expected_json["safety_phrase"])
        instruction_followed = (
            structured_valid
            and parsed is not None
            and str(parsed.get("safety_phrase", "")) == expected_phrase
        )
        passed = exact_answer and instruction_followed
        reason = "answer_and_safety_phrase_match" if passed else "instruction_or_answer_mismatch"
    elif case.category == "distractor_resistance":
        passed = exact_answer and not reference_error
        reason = "authoritative_answer" if passed else "distractor_or_answer_mismatch"
    elif case.category == "multi_hop":
        passed = exact_answer
        reason = "multi_hop_answer_match" if passed else "multi_hop_answer_mismatch"
    else:
        passed = exact_answer
        reason = "answer_match" if passed else "answer_mismatch"

    hallucination_flag = not passed and not reference_error
    return TrialResult(
        run_id=run_id,
        case_id=case.case_id,
        repeat_index=repeat_index,
        provider_type=provider.provider_type,
        model=provider.model,
        category=case.category,
        tier=case.tier,
        sample_index=case.sample_index,
        needle_position=case.needle_position,
        target_prompt_tokens=case.target_prompt_tokens,
        estimated_prompt_tokens=case.estimated_prompt_tokens,
        prompt_hash=case.prompt_hash,
        response_text=response.text,
        response_hash=stable_hash(response.text),
        latency_ms=response.latency_ms,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        expected_answer=case.expected_answer,
        parsed_answer=parsed_answer,
        pass_1=passed,
        structured_output_valid=structured_valid,
        instruction_followed=instruction_followed,
        reference_error=reference_error,
        hallucination_flag=hallucination_flag,
        score_reason=reason,
    )


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def bool_rate(values: Iterable[bool | None]) -> float:
    clean = [value for value in values if value is not None]
    return mean(1.0 if value else 0.0 for value in clean) if clean else 0.0


def ci95(rate: float, n: int) -> float:
    if n <= 0:
        return 0.0
    return 1.96 * math.sqrt(max(0.0, rate * (1.0 - rate)) / n)


def aggregate_results(
    results: list[TrialResult],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    weights = dict(config["score_weights"])
    tiers = sorted({result.tier for result in results})
    summary_rows: list[dict[str, Any]] = []
    category_rows: list[dict[str, Any]] = []
    needle_rows: list[dict[str, Any]] = []

    for tier in tiers:
        tier_results = [result for result in results if result.tier == tier]
        categories = sorted({result.category for result in tier_results})
        weighted_parts: list[tuple[float, float]] = []
        for category in categories:
            category_results = [result for result in tier_results if result.category == category]
            rate = bool_rate(result.pass_1 for result in category_results)
            category_rows.append(
                {
                    "tier": tier,
                    "category": category,
                    "n": len(category_results),
                    "pass_rate": rate,
                    "ci95": ci95(rate, len(category_results)),
                    "structured_output_rate": bool_rate(
                        result.structured_output_valid for result in category_results
                    ),
                    "instruction_follow_rate": bool_rate(
                        result.instruction_followed for result in category_results
                    ),
                    "reference_error_rate": bool_rate(
                        result.reference_error for result in category_results
                    ),
                    "hallucination_rate": bool_rate(
                        result.hallucination_flag for result in category_results
                    ),
                    "avg_latency_ms": mean(result.latency_ms for result in category_results),
                    "avg_estimated_prompt_tokens": mean(
                        result.estimated_prompt_tokens for result in category_results
                    ),
                }
            )
            weight = float(weights.get(category, 0.0))
            if weight > 0:
                weighted_parts.append((rate, weight))

        weight_sum = sum(weight for _, weight in weighted_parts)
        composite = (
            sum(rate * weight for rate, weight in weighted_parts) / weight_sum
            if weight_sum
            else bool_rate(result.pass_1 for result in tier_results)
        )
        overall_pass = bool_rate(result.pass_1 for result in tier_results)
        summary_rows.append(
            {
                "tier": tier,
                "n": len(tier_results),
                "composite_score": composite,
                "composite_ci95": ci95(composite, len(tier_results)),
                "pass_at_1": overall_pass,
                "pass_at_1_ci95": ci95(overall_pass, len(tier_results)),
                "structured_output_rate": bool_rate(
                    result.structured_output_valid for result in tier_results
                ),
                "instruction_follow_rate": bool_rate(
                    result.instruction_followed for result in tier_results
                ),
                "reference_error_rate": bool_rate(result.reference_error for result in tier_results),
                "hallucination_rate": bool_rate(result.hallucination_flag for result in tier_results),
                "avg_latency_ms": mean(result.latency_ms for result in tier_results),
                "p50_latency_ms": statistics.median(
                    result.latency_ms for result in tier_results
                )
                if tier_results
                else 0.0,
                "avg_estimated_prompt_tokens": mean(
                    result.estimated_prompt_tokens for result in tier_results
                ),
            }
        )

    needle_groups: dict[tuple[float, float], list[TrialResult]] = {}
    for result in results:
        if result.category == "needle_position" and result.needle_position is not None:
            needle_groups.setdefault((result.tier, result.needle_position), []).append(result)
    for (tier, position), group in sorted(needle_groups.items()):
        rate = bool_rate(result.pass_1 for result in group)
        needle_rows.append(
            {
                "tier": tier,
                "needle_position": position,
                "n": len(group),
                "pass_rate": rate,
                "ci95": ci95(rate, len(group)),
            }
        )

    return summary_rows, category_rows, needle_rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def svg_line_chart(
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    series: dict[str, list[tuple[float, float]]],
) -> None:
    width, height = 920, 520
    margin_left, margin_right, margin_top, margin_bottom = 72, 180, 48, 70
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    all_points = [point for points in series.values() for point in points]
    if not all_points:
        path.write_text("", encoding="utf-8")
        return
    xs = [point[0] for point in all_points]
    min_x, max_x = min(xs), max(xs)
    if min_x == max_x:
        min_x -= 0.01
        max_x += 0.01
    min_y, max_y = 0.0, 1.0
    colors = [
        "#2563eb",
        "#dc2626",
        "#059669",
        "#d97706",
        "#7c3aed",
        "#0891b2",
        "#be123c",
    ]

    def sx(x_value: float) -> float:
        return margin_left + ((x_value - min_x) / (max_x - min_x)) * plot_w

    def sy(y_value: float) -> float:
        return margin_top + (1.0 - ((y_value - min_y) / (max_y - min_y))) * plot_h

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin_left}" y="28" font-family="Arial" font-size="20" font-weight="700">{html.escape(title)}</text>',
    ]
    for tick in range(0, 6):
        y = tick / 5
        y_px = sy(y)
        lines.append(
            f'<line x1="{margin_left}" y1="{y_px:.1f}" x2="{margin_left + plot_w}" y2="{y_px:.1f}" stroke="#e5e7eb"/>'
        )
        lines.append(
            f'<text x="{margin_left - 10}" y="{y_px + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#475569">{y:.1f}</text>'
        )
    x_ticks = sorted(set(xs))
    if len(x_ticks) > 10:
        step = max(1, len(x_ticks) // 8)
        x_ticks = x_ticks[::step]
    for x_value in x_ticks:
        x_px = sx(x_value)
        label = f"{int(round(x_value * 100))}%" if x_value <= 1 else f"{x_value:g}"
        lines.append(
            f'<line x1="{x_px:.1f}" y1="{margin_top}" x2="{x_px:.1f}" y2="{margin_top + plot_h}" stroke="#f1f5f9"/>'
        )
        lines.append(
            f'<text x="{x_px:.1f}" y="{margin_top + plot_h + 24}" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{html.escape(label)}</text>'
        )

    lines.append(
        f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#0f172a"/>'
    )
    lines.append(
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#0f172a"/>'
    )
    lines.append(
        f'<text x="{margin_left + plot_w / 2:.1f}" y="{height - 22}" text-anchor="middle" font-family="Arial" font-size="14" fill="#0f172a">{html.escape(x_label)}</text>'
    )
    lines.append(
        f'<text transform="translate(20 {margin_top + plot_h / 2:.1f}) rotate(-90)" text-anchor="middle" font-family="Arial" font-size="14" fill="#0f172a">{html.escape(y_label)}</text>'
    )

    for idx, (name, points) in enumerate(series.items()):
        points = sorted(points)
        color = colors[idx % len(colors)]
        path_data = " ".join(
            f"{'M' if point_idx == 0 else 'L'} {sx(x):.1f} {sy(y):.1f}"
            for point_idx, (x, y) in enumerate(points)
        )
        lines.append(
            f'<path d="{path_data}" fill="none" stroke="{color}" stroke-width="2.5"/>'
        )
        for x, y in points:
            lines.append(
                f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{color}"/>'
            )
        legend_y = margin_top + 24 + idx * 22
        legend_x = margin_left + plot_w + 26
        lines.append(
            f'<rect x="{legend_x}" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>'
        )
        lines.append(
            f'<text x="{legend_x + 18}" y="{legend_y}" font-family="Arial" font-size="12" fill="#0f172a">{html.escape(name)}</text>'
        )

    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def detect_degradation(
    summary_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[str]:
    if not summary_rows:
        return []
    baseline = min(summary_rows, key=lambda row: abs(float(row["tier"]) - 0.50))
    baseline_score = float(baseline["composite_score"])
    baseline_ci = float(baseline["composite_ci95"])
    messages: list[str] = []
    threshold = float(config["degradation_threshold"])
    category_threshold = float(config["category_drop_threshold"])

    baseline_categories = {
        row["category"]: row
        for row in category_rows
        if float(row["tier"]) == float(baseline["tier"])
    }
    for row in summary_rows:
        tier = float(row["tier"])
        if tier == float(baseline["tier"]):
            continue
        score = float(row["composite_score"])
        ci = float(row["composite_ci95"])
        drop = baseline_score - score
        ci_non_overlap = (score + ci) < (baseline_score - baseline_ci)
        if drop >= threshold and ci_non_overlap:
            messages.append(
                f"{tier:.0%}: composite score dropped {drop:.1%} from the "
                f"{float(baseline['tier']):.0%} baseline with non-overlapping 95% CI."
            )
        elif drop >= threshold:
            messages.append(
                f"{tier:.0%}: composite score dropped {drop:.1%} from baseline; "
                "CI overlap means treat this as directional until more samples run."
            )

        tier_categories = [cat for cat in category_rows if float(cat["tier"]) == tier]
        for cat in tier_categories:
            baseline_cat = baseline_categories.get(cat["category"])
            if not baseline_cat:
                continue
            cat_drop = float(baseline_cat["pass_rate"]) - float(cat["pass_rate"])
            if cat_drop >= category_threshold:
                messages.append(
                    f"{tier:.0%}: {cat['category']} dropped {cat_drop:.1%} "
                    f"from the {float(baseline['tier']):.0%} baseline."
                )
    return messages


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                if column == "tier" or column == "needle_position":
                    values.append(f"{value:.0%}")
                elif "rate" in column or "score" in column or "ci" in column or column == "pass_at_1":
                    values.append(f"{value:.1%}")
                else:
                    values.append(f"{value:.1f}")
            else:
                values.append(str(value))
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, separator, *body])


def percent(value: float) -> str:
    return f"{value:.1%}"


def tier_label(value: float) -> str:
    return f"{value:.0%}"


def find_baseline(summary_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not summary_rows:
        return None
    return min(summary_rows, key=lambda row: abs(float(row["tier"]) - 0.50))


def build_analysis_results(
    run_id: str,
    config: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
    needle_rows: list[dict[str, Any]],
    results: list[TrialResult],
    degradation: list[str],
) -> str:
    provider = config["provider"]
    baseline = find_baseline(summary_rows)
    high_tiers = [row for row in summary_rows if float(row["tier"]) >= 0.70]
    failed = [result for result in results if not result.pass_1]
    capacity_failures = [
        result
        for result in failed
        if re.search(
            r"context|token|limit|maximum|too long|truncate|截断|超限|容量",
            result.response_text,
            flags=re.IGNORECASE,
        )
    ]

    lines = [
        f"# Analysis Results: {run_id}",
        "",
        "## Executive Summary",
        "",
        f"- Provider: `{provider['type']}`",
        f"- Model: `{provider.get('model', provider['type'])}`",
        f"- Health profile: `{config.get('health_profile_title') or config.get('health_profile') or 'n/a'}`",
        f"- Context window: `{config['context_window_tokens']}` tokens",
        f"- Planned tiers: {', '.join(tier_label(float(tier)) for tier in config['tiers'])}",
        f"- Total trials: `{len(results)}`",
        "",
    ]

    if baseline:
        baseline_score = float(baseline["composite_score"])
        lines.extend(
            [
                f"- Baseline tier: {tier_label(float(baseline['tier']))}",
                f"- Baseline composite score: {percent(baseline_score)}",
                "",
            ]
        )
        for row in high_tiers:
            tier = float(row["tier"])
            score = float(row["composite_score"])
            drop = baseline_score - score
            status = "drop candidate" if drop >= float(config["degradation_threshold"]) else "no configured drop"
            lines.append(
                f"- {tier_label(tier)}: composite {percent(score)}, "
                f"delta vs baseline {percent(-drop)}, status: {status}"
            )
    else:
        lines.append("- No baseline row was available.")

    lines.extend(["", "## Degradation Signals", ""])
    if degradation:
        lines.extend(f"- {message}" for message in degradation)
    else:
        lines.append("- No configured degradation threshold was crossed in this run.")

    lines.extend(
        [
            "",
            "## Capacity And Interface Risk",
            "",
            f"- Failed trials: `{len(failed)}`",
            f"- Possible capacity/interface failures: `{len(capacity_failures)}`",
        ]
    )
    if capacity_failures:
        lines.append("- Capacity/interface examples:")
        for result in capacity_failures[:8]:
            snippet = result.response_text.replace("\n", " ")[:180]
            lines.append(
                f"  - `{result.case_id}` tier={tier_label(result.tier)} "
                f"category={result.category}: {snippet}"
            )
    else:
        lines.append("- No obvious token-limit or truncation failure text was detected.")

    lines.extend(
        [
            "",
            "## Capability Attribution",
            "",
            markdown_table(
                category_rows,
                [
                    "tier",
                    "category",
                    "n",
                    "pass_rate",
                    "ci95",
                    "structured_output_rate",
                    "instruction_follow_rate",
                    "reference_error_rate",
                    "hallucination_rate",
                    "avg_latency_ms",
                ],
            ),
            "",
            "## Needle Position Findings",
            "",
            markdown_table(needle_rows, ["tier", "needle_position", "n", "pass_rate", "ci95"]),
            "",
            "## Failure Examples",
            "",
        ]
    )
    if failed:
        for result in failed[:20]:
            snippet = result.response_text.replace("\n", " ")[:220]
            lines.extend(
                [
                    f"### {result.case_id}",
                    "",
                    f"- Tier: {tier_label(result.tier)}",
                    f"- Category: `{result.category}`",
                    f"- Expected: `{result.expected_answer}`",
                    f"- Parsed answer: `{result.parsed_answer}`",
                    f"- Reason: `{result.score_reason}`",
                    f"- Response snippet: {snippet}",
                    "",
                ]
            )
    else:
        lines.append("- No failed trials were recorded.")

    lines.extend(
        [
            "",
            "## Recommended Interpretation",
            "",
            "- Treat `oracle` runs as validation of the test pack and scoring only.",
            "- Treat high-tier token-limit, request-size, or truncation failures as capacity/interface failures, not reasoning-quality drops.",
            "- A real quality cliff is strongest when the composite score drops, the same capability drops across adjacent high tiers, and Needle middle positions also weaken.",
            "- For product decisions, compare the main health-habits pack with the two exploratory packs to see whether failures are stable across sports-health task styles.",
        ]
    )
    return "\n".join(lines)


def write_report(
    run_dir: Path,
    run_id: str,
    config: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
    needle_rows: list[dict[str, Any]],
    results: list[TrialResult],
) -> None:
    degradation = detect_degradation(summary_rows, category_rows, config)
    provider = config["provider"]
    analysis_text = build_analysis_results(
        run_id,
        config,
        summary_rows,
        category_rows,
        needle_rows,
        results,
        degradation,
    )
    lines = [
        f"# Long Context Decay Report: {run_id}",
        "",
        "## Executive Summary",
        "",
        "- This report is generated after scoring every fixed case in the prepared case pack.",
        "- See `analysis_results.md` for deeper interpretation, failure examples, and capacity/interface risk notes.",
        "",
        "## Run Setup",
        "",
        f"- Provider: `{provider['type']}`",
        f"- Model: `{provider.get('model', provider['type'])}`",
        f"- Health profile: `{config.get('health_profile_title') or config.get('health_profile') or 'n/a'}`",
        f"- Context window tokens: `{config['context_window_tokens']}`",
        f"- Reserved output tokens: `{config['reserved_output_tokens']}`",
        f"- Fixed system overhead tokens: `{config['fixed_system_overhead_tokens']}`",
        f"- Samples per tier: `{config['samples_per_tier']}`",
        f"- Repeats: `{config['repeats']}`",
        f"- Token counts are estimated unless the provider returns usage.",
        "",
        "## Degradation Signals",
        "",
    ]
    if degradation:
        lines.extend(f"- {message}" for message in degradation)
    else:
        lines.append("- No configured degradation threshold was crossed in this run.")

    lines.extend(
        [
            "",
            "## Summary By Context Occupancy",
            "",
            markdown_table(
                summary_rows,
                [
                    "tier",
                    "n",
                    "composite_score",
                    "composite_ci95",
                    "pass_at_1",
                    "structured_output_rate",
                    "instruction_follow_rate",
                    "reference_error_rate",
                    "hallucination_rate",
                    "avg_latency_ms",
                    "avg_estimated_prompt_tokens",
                ],
            ),
            "",
            "## Capability Breakdown",
            "",
            markdown_table(
                category_rows,
                [
                    "tier",
                    "category",
                    "n",
                    "pass_rate",
                    "ci95",
                    "structured_output_rate",
                    "instruction_follow_rate",
                    "reference_error_rate",
                    "hallucination_rate",
                ],
            ),
            "",
            "## Needle Position Accuracy",
            "",
            markdown_table(needle_rows, ["tier", "needle_position", "n", "pass_rate", "ci95"]),
            "",
            "## Charts",
            "",
            "- `overall_score_by_tier.svg`",
            "- `category_scores_by_tier.svg`",
            "- `needle_position_accuracy.svg`",
            "- `analysis_results.md`",
            "",
            "## Interpretation Notes",
            "",
            "- Treat `oracle` as a smoke-test provider only; it should score 100%.",
            "- Use `degraded_mock` to verify report generation and cliff detection.",
            "- Use `command`, `http`, or `openai_compatible` for real model evidence.",
            "- A reliable WorkBuddy conclusion needs the planned 30-50 samples per tier and 3 repeats.",
        ]
    )
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    (run_dir / "analysis_results.md").write_text(analysis_text, encoding="utf-8")


def write_charts(
    run_dir: Path,
    summary_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
    needle_rows: list[dict[str, Any]],
) -> None:
    svg_line_chart(
        run_dir / "overall_score_by_tier.svg",
        "Composite Score vs Context Occupancy",
        "Context occupancy",
        "Composite score",
        {
            "composite": [
                (float(row["tier"]), float(row["composite_score"])) for row in summary_rows
            ],
            "pass@1": [(float(row["tier"]), float(row["pass_at_1"])) for row in summary_rows],
        },
    )

    category_series: dict[str, list[tuple[float, float]]] = {}
    for row in category_rows:
        category_series.setdefault(str(row["category"]), []).append(
            (float(row["tier"]), float(row["pass_rate"]))
        )
    svg_line_chart(
        run_dir / "category_scores_by_tier.svg",
        "Capability Score vs Context Occupancy",
        "Context occupancy",
        "Pass rate",
        category_series,
    )

    needle_series: dict[str, list[tuple[float, float]]] = {}
    for row in needle_rows:
        tier_name = f"tier {float(row['tier']):.0%}"
        needle_series.setdefault(tier_name, []).append(
            (float(row["needle_position"]), float(row["pass_rate"]))
        )
    svg_line_chart(
        run_dir / "needle_position_accuracy.svg",
        "Needle Accuracy by Position",
        "Needle position in long context",
        "Pass rate",
        needle_series,
    )


def save_prompt_if_needed(run_dir: Path, case: TaskCase) -> None:
    prompt_dir = run_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{case.case_id}.txt"
    prompt_path.write_text(
        f"SYSTEM:\n{case.prompt.system}\n\nUSER:\n{case.prompt.user}\n",
        encoding="utf-8",
    )


def build_cases_for_tier(tier: float, config: dict[str, Any]) -> list[TaskCase]:
    cases: list[TaskCase] = []
    base_seed = int(config["seed"])
    samples = int(config["samples_per_tier"])
    for sample_index in range(samples):
        category = TASK_ORDER[sample_index % len(TASK_ORDER)]
        rng = random.Random(f"{base_seed}-{tier:.2f}-{sample_index}")
        cases.append(build_prompt(category, tier, sample_index, config, rng))
    real_cases = load_real_cases(
        str(config.get("real_tasks_path") or ""),
        tier,
        start_index=samples,
        config=config,
    )
    cases.extend(real_cases)
    return cases


def run_experiment(config: dict[str, Any], output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"{config['experiment_name']}-{timestamp}"
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "config.resolved.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    provider = make_provider(config, run_dir)
    results: list[TrialResult] = []
    trials_path = run_dir / "trials.jsonl"
    prepared_cases = load_prepared_cases(config)
    total_cases = (
        len(prepared_cases)
        if prepared_cases
        else len(config["tiers"]) * int(config["samples_per_tier"])
    )
    total_trials = total_cases * int(config["repeats"])
    completed_trials = 0

    with open(trials_path, "w", encoding="utf-8") as trials_handle:
        case_iterable = prepared_cases
        if not case_iterable:
            generated_cases: list[TaskCase] = []
            for tier in config["tiers"]:
                generated_cases.extend(build_cases_for_tier(float(tier), config))
            case_iterable = generated_cases

        for case in case_iterable:
            if config.get("save_prompts"):
                save_prompt_if_needed(run_dir, case)
            for repeat_index in range(int(config["repeats"])):
                response = provider.generate(case, repeat_index)
                result = score_response(run_id, case, repeat_index, provider, response)
                results.append(result)
                trials_handle.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
                trials_handle.flush()
                completed_trials += 1
                print(
                    f"[{completed_trials}/{total_trials}] "
                    f"tier={case.tier:.0%} category={case.category} "
                    f"pass={int(result.pass_1)}",
                    flush=True,
                )

    summary_rows, category_rows, needle_rows = aggregate_results(results, config)
    write_jsonl(run_dir / "summary_by_tier.jsonl", summary_rows)
    write_jsonl(run_dir / "category_by_tier.jsonl", category_rows)
    write_jsonl(run_dir / "needle_by_position.jsonl", needle_rows)
    write_csv(run_dir / "summary_by_tier.csv", summary_rows)
    write_csv(run_dir / "category_by_tier.csv", category_rows)
    write_csv(run_dir / "needle_by_position.csv", needle_rows)
    write_charts(run_dir, summary_rows, category_rows, needle_rows)
    write_report(run_dir, run_id, config, summary_rows, category_rows, needle_rows, results)
    return run_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run long-context degradation experiments for WorkBuddy-style agents."
    )
    parser.add_argument("--config", help="Path to JSON config file.")
    parser.add_argument(
        "--provider",
        choices=[
            "oracle",
            "degraded_mock",
            "openai_compatible",
            "workbuddy_api",
            "command",
            "workbuddy_command",
            "http",
            "workbuddy_http",
        ],
        help="Override provider.type.",
    )
    parser.add_argument("--model", help="Override provider.model.")
    parser.add_argument("--context-window-tokens", type=int)
    parser.add_argument("--reserved-output-tokens", type=int)
    parser.add_argument("--fixed-system-overhead-tokens", type=int)
    parser.add_argument("--samples-per-tier", type=int)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--tiers", nargs="+", type=float)
    parser.add_argument("--save-prompts", action="store_true")
    parser.add_argument("--prepared-cases-path")
    parser.add_argument("--real-tasks-path")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "runs"),
        help="Directory where a timestamped run folder will be created.",
    )
    return parser


def apply_cli_overrides(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    config = deep_merge({}, config)
    if args.provider:
        config["provider"]["type"] = args.provider
        if not args.model:
            config["provider"]["model"] = args.provider
    if args.model:
        config["provider"]["model"] = args.model
    if args.context_window_tokens:
        config["context_window_tokens"] = args.context_window_tokens
    if args.reserved_output_tokens:
        config["reserved_output_tokens"] = args.reserved_output_tokens
    if args.fixed_system_overhead_tokens:
        config["fixed_system_overhead_tokens"] = args.fixed_system_overhead_tokens
    if args.samples_per_tier:
        config["samples_per_tier"] = args.samples_per_tier
    if args.repeats:
        config["repeats"] = args.repeats
    if args.seed:
        config["seed"] = args.seed
    tiers = parse_tiers(args.tiers)
    if tiers:
        config["tiers"] = tiers
    if args.save_prompts:
        config["save_prompts"] = True
    if args.prepared_cases_path:
        config["prepared_cases_path"] = args.prepared_cases_path
    if args.real_tasks_path:
        config["real_tasks_path"] = args.real_tasks_path
    return config


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    config = apply_cli_overrides(load_config(args.config), args)
    output_dir = Path(args.output_dir).resolve()
    try:
        run_dir = run_experiment(config, output_dir)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Experiment failed: {exc}", file=sys.stderr)
        return 1
    print(f"\nRun artifacts written to: {run_dir}")
    print(f"Report: {run_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
