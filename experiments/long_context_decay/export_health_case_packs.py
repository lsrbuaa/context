#!/usr/bin/env python3
"""Export sports-health long-context case packs.

The generated cases keep the same scoring categories as run_experiment.py, but
the context is messy daily sports-health material: workouts, sleep, meals,
wearables, chats, schedules, travel, recovery notes, and stale plans.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from run_experiment import (
    DEFAULT_CONFIG,
    PromptBundle,
    TaskCase,
    approximate_tokens,
    load_config,
    stable_hash,
    task_case_to_record,
    truncate_to_estimated_tokens,
    usable_input_budget,
)


TASK_ORDER = [
    "fact_recall",
    "needle_position",
    "multi_hop",
    "instruction_following",
    "distractor_resistance",
]

NEEDLE_POSITIONS = [0.05, 0.25, 0.50, 0.75, 0.95]

SYSTEM_PROMPT = """You are the model inside a sports-health long-context stress test.
Use only the supplied user daily context. Do not give medical advice. Return
only the requested JSON object, without Markdown fences or commentary."""


PACK_PROFILES: dict[str, dict[str, Any]] = {
    "habits": {
        "title": "运动健康日常习惯抽取",
        "description": "从杂乱日常记录中抽取用户稳定运动、睡眠、饮食和恢复习惯。",
        "case_pack_suffix": "health_habits_256k_main",
        "default_samples_per_tier": 25,
        "focus": "stable habit extraction",
        "answer_roots": ["AMRUN", "Z2BIKE", "YOGA", "MEALPREP", "SLEEPLOCK"],
    },
    "change_events": {
        "title": "运动健康习惯变更识别",
        "description": "在旧计划、新计划和日常噪声中识别当前有效习惯。",
        "case_pack_suffix": "health_change_events_256k_pilot",
        "default_samples_per_tier": 5,
        "focus": "current-state extraction from conflicting history",
        "answer_roots": ["CURRUN", "NEWSHOE", "LOADCAP", "TRAVELMOD", "RECENTPLAN"],
    },
    "safety_preferences": {
        "title": "运动健康约束与偏好记忆",
        "description": "从长期偏好、身体反馈和恢复约束中找到应遵守的健康规则。",
        "case_pack_suffix": "health_safety_preferences_256k_pilot",
        "default_samples_per_tier": 5,
        "focus": "personal constraints and recovery preferences",
        "answer_roots": ["KNEELOW", "SLEEPFIRST", "NOCAFFEINE", "SWIMOK", "DELOAD"],
    },
}

DAILY_EVENTS = [
    "morning weigh-in",
    "commute walk",
    "lunch photo",
    "watch sync",
    "calendar conflict",
    "team standup",
    "evening stretch",
    "grocery note",
    "weather alert",
    "shoe rotation note",
    "sleep diary",
    "hydration reminder",
    "recovery check-in",
    "bike maintenance",
    "family chat",
]

MOODS = ["calm", "busy", "sluggish", "focused", "restless", "steady"]
WORKOUTS = ["easy run", "zone-2 ride", "strength circuit", "pool swim", "mobility block"]
MEALS = ["oats", "rice bowl", "salad wrap", "noodle soup", "eggs", "yogurt"]
LOCATIONS = ["river path", "office gym", "home mat", "community pool", "hotel treadmill"]


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pre-generate sports-health case packs.")
    p.add_argument("--config", help="Base JSON config.")
    p.add_argument("--output-dir", required=True)
    p.add_argument(
        "--profile",
        choices=sorted(PACK_PROFILES),
        default="habits",
        help="Health case-pack direction.",
    )
    p.add_argument("--model-label", default="Hy3 preview")
    p.add_argument("--context-window-tokens", type=int, default=256000)
    p.add_argument("--reserved-output-tokens", type=int, default=8192)
    p.add_argument("--fixed-system-overhead-tokens", type=int, default=1500)
    p.add_argument("--samples-per-tier", type=int)
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument(
        "--tiers",
        nargs="+",
        type=float,
        default=[0.30, 0.50, 0.70, 0.80, 0.90, 0.95],
    )
    p.add_argument("--seed", type=int, default=20260625)
    return p


def build_config(args: argparse.Namespace, output_dir: Path) -> dict[str, Any]:
    profile = PACK_PROFILES[args.profile]
    config = load_config(args.config) if args.config else copy.deepcopy(DEFAULT_CONFIG)
    config["experiment_name"] = f"long_context_decay_{args.profile}_{args.model_label.lower().replace('-', '_')}"
    config["context_window_tokens"] = args.context_window_tokens
    config["reserved_output_tokens"] = args.reserved_output_tokens
    config["fixed_system_overhead_tokens"] = args.fixed_system_overhead_tokens
    config["samples_per_tier"] = args.samples_per_tier or profile["default_samples_per_tier"]
    config["repeats"] = args.repeats
    config["tiers"] = args.tiers
    config["seed"] = args.seed
    config["prepared_cases_path"] = str((output_dir / "cases.jsonl").resolve())
    config["health_profile"] = args.profile
    config["health_profile_title"] = profile["title"]
    config["provider"]["type"] = "workbuddy_api"
    config["provider"]["model"] = args.model_label
    config["provider"]["workbuddy_endpoint"] = "https://copilot.tencent.com"
    config["provider"]["workbuddy_api_key_env"] = "WORKBUDDY_API_TOKEN"
    config["provider"]["openai_base_url"] = "https://copilot.tencent.com/v1/chat/completions"
    return config


def health_filler_block(rng: random.Random, block_id: int, profile_key: str) -> str:
    date = f"2026-{rng.randrange(1, 7):02d}-{rng.randrange(1, 29):02d}"
    time = f"{rng.randrange(5, 23):02d}:{rng.randrange(0, 60):02d}"
    event = rng.choice(DAILY_EVENTS)
    workout = rng.choice(WORKOUTS)
    meal = rng.choice(MEALS)
    location = rng.choice(LOCATIONS)
    mood = rng.choice(MOODS)
    steps = rng.randrange(3200, 18800)
    sleep_h = rng.randrange(5, 9)
    sleep_m = rng.randrange(0, 60)
    rhr = rng.randrange(48, 74)
    hrv = rng.randrange(28, 92)
    ref = f"HLTH-NOISE-{profile_key.upper()}-{block_id:06d}-{rng.randrange(100, 999)}"
    return (
        f"[{ref}] {date} {time} daily context: event={event}; mood={mood}; "
        f"sleep={sleep_h}h{sleep_m:02d}m; resting_hr={rhr}; hrv={hrv}; "
        f"steps={steps}; possible workout={workout} at {location}; meal={meal}. "
        "This is ordinary user-life noise unless the final question asks for this exact reference. "
        "Notes may mention training, work, family, travel, snacks, soreness, weather, or calendar issues, "
        "but they are not authoritative habit records by themselves.\n"
    )


def make_filler(target_tokens: int, rng: random.Random, start_block: int, profile_key: str) -> str:
    if target_tokens <= 0:
        return ""
    parts: list[str] = []
    block_id = start_block
    token_count = 0
    while token_count < target_tokens:
        block = health_filler_block(rng, block_id, profile_key)
        parts.append(block)
        token_count += approximate_tokens(block)
        block_id += 1
    return truncate_to_estimated_tokens("".join(parts), target_tokens)


def assemble_context(
    target_tokens: int,
    injections: list[tuple[float, str]],
    rng: random.Random,
    profile_key: str,
) -> str:
    injections = sorted(injections, key=lambda item: item[0])
    parts: list[str] = []
    consumed = 0
    block_id = 0
    for position, injection in injections:
        desired_before = max(0, int(target_tokens * position))
        filler_tokens = max(0, desired_before - consumed)
        filler = make_filler(filler_tokens, rng, block_id, profile_key)
        block_id += max(1, filler_tokens // 55)
        parts.append(filler)
        consumed += approximate_tokens(filler)
        parts.append(injection.rstrip() + "\n")
        consumed += approximate_tokens(injection)
    if consumed < target_tokens:
        parts.append(make_filler(target_tokens - consumed, rng, block_id, profile_key))
    return truncate_to_estimated_tokens("".join(parts), target_tokens)


def answer_code(profile_key: str, category: str, case_seed: str, root: str) -> str:
    return f"{profile_key.upper()}-{category.upper()}-{case_seed}-{root}"


def profile_root(profile_key: str, occurrence_index: int) -> str:
    roots = PACK_PROFILES[profile_key]["answer_roots"]
    return str(roots[occurrence_index % len(roots)])


def build_health_prompt(
    profile_key: str,
    category: str,
    tier: float,
    sample_index: int,
    config: dict[str, Any],
    rng: random.Random,
) -> TaskCase:
    case_seed = f"{int(tier * 100):02d}-{sample_index:04d}"
    occurrence_index = sample_index // len(TASK_ORDER)
    target_prompt_tokens = int(usable_input_budget(config) * tier)
    root = profile_root(profile_key, occurrence_index)
    user_id = f"USER-{profile_key.upper()}-{case_seed}"

    if category == "fact_recall":
        answer = answer_code(profile_key, category, case_seed, root)
        evidence_id = f"HEALTH-HABIT-{case_seed}"
        position = NEEDLE_POSITIONS[occurrence_index % len(NEEDLE_POSITIONS)]
        injection = (
            f"[{evidence_id}] AUTHORITATIVE SPORTS-HEALTH HABIT RECORD: "
            f"For {user_id}, the current stable habit code is {answer}. "
            "Meaning: the user usually repeats this pattern when normal daily context is noisy. "
            "This record overrides ordinary diary noise.\n"
        )
        question = f"What is the exact current stable habit code for {user_id}?"
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors: list[str] = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "needle_position":
        answer = answer_code(profile_key, category, case_seed, root)
        evidence_id = f"HEALTH-NEEDLE-{case_seed}"
        position = NEEDLE_POSITIONS[occurrence_index % len(NEEDLE_POSITIONS)]
        injection = (
            f"[{evidence_id}] SPORTS-HEALTH NEEDLE: When asked for the user's "
            f"hidden routine anchor for {user_id}, answer exactly {answer}. "
            "Ignore similar daily notes around it.\n"
        )
        question = f"What is the hidden routine anchor for {user_id}?"
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "multi_hop":
        plan = f"PLAN-{profile_key.upper()}-{case_seed}"
        slot = f"SLOT-{profile_key.upper()}-{case_seed}"
        routine = f"ROUTINE-{profile_key.upper()}-{case_seed}"
        answer = answer_code(profile_key, category, case_seed, root)
        injections = [
            (
                0.08,
                f"[HOP-A-{case_seed}] Sports-health profile note: {user_id} "
                f"uses {plan} when the week contains mixed work stress and training noise.\n",
            ),
            (
                0.50,
                f"[HOP-B-{case_seed}] Plan mapping: {plan} maps to preferred "
                f"habit slot {slot} after checking sleep, steps, and soreness logs.\n",
            ),
            (
                0.92,
                f"[HOP-C-{case_seed}] Habit slot mapping: {slot} maps to "
                f"routine {routine}; the exact routine answer code is {answer}.\n",
            ),
        ]
        question = f"Using the scattered mappings, what exact routine answer code applies to {user_id}?"
        expected_json = {"answer": answer, "chain": [plan, slot, routine]}
        distractors = []
        needle_position = None

    elif category == "instruction_following":
        answer = answer_code(profile_key, category, case_seed, root)
        safety_phrase = f"HEALTH-RULE-{case_seed}-NO-MEDICAL-ADVICE"
        position = [0.10, 0.50, 0.85][occurrence_index % 3]
        injection = (
            f"[HEALTH-RULE-{case_seed}] LONG-LIVED USER HEALTH RESPONSE RULE: "
            f"For request HEALTH-RULE-CHECK-{case_seed}, return JSON with "
            f'"answer":"{answer}" and "safety_phrase":"{safety_phrase}". '
            "Do not add diagnosis, treatment, or generic coaching text.\n"
        )
        question = (
            f"Complete request HEALTH-RULE-CHECK-{case_seed}. Preserve the "
            "long-lived user health response rule."
        )
        expected_json = {"answer": answer, "safety_phrase": safety_phrase}
        distractors = []
        needle_position = position
        injections = [(position, injection)]

    elif category == "distractor_resistance":
        answer = answer_code(profile_key, category, case_seed, root)
        old_answer = f"OLD-{answer}"
        related_answer = f"RELATED-{answer}"
        evidence_id = f"HEALTH-CURRENT-{case_seed}"
        injections = [
            (
                0.16,
                f"[HEALTH-OLD-{case_seed}] Retired sports-health plan for {user_id}: "
                f"the old habit code was {old_answer}. Status=retired. Do not use it for current habit questions.\n",
            ),
            (
                0.53,
                f"[HEALTH-RELATED-{case_seed}] Similar user or adjacent training block mentions "
                f"{related_answer}. This is not the requested user's current record.\n",
            ),
            (
                0.84,
                f"[{evidence_id}] AUTHORITATIVE CURRENT SPORTS-HEALTH RECORD: "
                f"The current habit/constraint code for {user_id} is {answer}.\n",
            ),
        ]
        question = f"What is the current habit/constraint code for {user_id}?"
        expected_json = {"answer": answer, "evidence_id": evidence_id}
        distractors = [old_answer, related_answer]
        needle_position = 0.84

    else:
        raise ValueError(f"Unsupported category: {category}")

    shell_without_context = f"""
Experiment tier: {tier:.2f}
Sports-health pack: {PACK_PROFILES[profile_key]["title"]}
Task type: {category}

[MESSY USER DAILY CONTEXT START]

[MESSY USER DAILY CONTEXT END]

[FINAL QUESTION]
{question}

[RESPONSE FORMAT]
Return a single JSON object. At minimum include "answer". Include evidence_id,
chain, or safety_phrase only when the context requires it.
"""
    overhead_tokens = approximate_tokens(SYSTEM_PROMPT + shell_without_context)
    context_target_tokens = max(128, target_prompt_tokens - overhead_tokens)
    long_context = assemble_context(context_target_tokens, injections, rng, profile_key)
    user_prompt = f"""
Experiment tier: {tier:.2f}
Sports-health pack: {PACK_PROFILES[profile_key]["title"]}
Task type: {category}

[MESSY USER DAILY CONTEXT START]
{long_context}
[MESSY USER DAILY CONTEXT END]

[FINAL QUESTION]
{question}

[RESPONSE FORMAT]
Return a single JSON object. At minimum include "answer". Include evidence_id,
chain, or safety_phrase only when the context requires it.
"""
    estimated_prompt_tokens = approximate_tokens(SYSTEM_PROMPT + user_prompt)
    prompt_hash = stable_hash(SYSTEM_PROMPT + user_prompt)
    case_id = f"{profile_key}-{category}-{int(tier * 100):02d}-{sample_index:04d}"
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


def build_cases_for_tier(profile_key: str, tier: float, config: dict[str, Any]) -> list[TaskCase]:
    cases: list[TaskCase] = []
    base_seed = int(config["seed"])
    samples = int(config["samples_per_tier"])
    for sample_index in range(samples):
        category = TASK_ORDER[sample_index % len(TASK_ORDER)]
        rng = random.Random(f"{profile_key}-{base_seed}-{tier:.2f}-{sample_index}")
        cases.append(build_health_prompt(profile_key, category, tier, sample_index, config, rng))
    return cases


def write_cases(output_dir: Path, config: dict[str, Any], profile_key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(output_dir / "cases.jsonl", "w", encoding="utf-8") as handle:
        for tier in config["tiers"]:
            for case in build_cases_for_tier(profile_key, float(tier), config):
                row = task_case_to_record(case)
                row["health_profile"] = profile_key
                row["health_profile_title"] = PACK_PROFILES[profile_key]["title"]
                row["health_focus"] = PACK_PROFILES[profile_key]["focus"]
                rows.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def write_answer_key(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "case_id",
        "health_profile",
        "tier",
        "category",
        "sample_index",
        "needle_position",
        "expected_answer",
        "expected_json",
        "distractor_answers",
        "target_prompt_tokens",
        "estimated_prompt_tokens",
        "prompt_hash",
    ]
    with open(output_dir / "answer_key.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "health_profile": row["health_profile"],
                    "tier": row["tier"],
                    "category": row["category"],
                    "sample_index": row["sample_index"],
                    "needle_position": row["needle_position"],
                    "expected_answer": row["expected_answer"],
                    "expected_json": json.dumps(row["expected_json"], ensure_ascii=False),
                    "distractor_answers": json.dumps(row["distractor_answers"], ensure_ascii=False),
                    "target_prompt_tokens": row["target_prompt_tokens"],
                    "estimated_prompt_tokens": row["estimated_prompt_tokens"],
                    "prompt_hash": row["prompt_hash"],
                }
            )


def write_manifest(
    output_dir: Path,
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    profile_key: str,
    model_label: str,
) -> None:
    category_counts = Counter(row["category"] for row in rows)
    tier_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        tier_counts[f"{float(row['tier']):.2f}"] += 1
    manifest = {
        "case_pack": output_dir.name,
        "model_label": model_label,
        "health_profile": profile_key,
        "health_profile_title": PACK_PROFILES[profile_key]["title"],
        "health_profile_description": PACK_PROFILES[profile_key]["description"],
        "context_window_tokens": config["context_window_tokens"],
        "reserved_output_tokens": config["reserved_output_tokens"],
        "fixed_system_overhead_tokens": config["fixed_system_overhead_tokens"],
        "usable_input_budget": usable_input_budget(config),
        "tiers": config["tiers"],
        "samples_per_tier": config["samples_per_tier"],
        "repeats": config["repeats"],
        "seed": config["seed"],
        "total_cases": len(rows),
        "total_trials": len(rows) * int(config["repeats"]),
        "category_counts": dict(sorted(category_counts.items())),
        "tier_counts": dict(sorted(tier_counts.items())),
        "files": {
            "cases": "cases.jsonl",
            "answer_key": "answer_key.csv",
            "config": "run_config.json",
            "acceptance": "acceptance.md",
            "workbuddy_instructions": "WORKBUDDY_INSTRUCTIONS.md",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_acceptance(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], profile_key: str, model_label: str) -> None:
    profile = PACK_PROFILES[profile_key]
    content = f"""# 运动健康长上下文衰减实验验收标准

## 固定测试包

- 被测模型：{model_label}
- 题包方向：{profile["title"]}
- 题包说明：{profile["description"]}
- context window 假设：{config["context_window_tokens"]} tokens
- 预留输出：{config["reserved_output_tokens"]} tokens
- 固定系统开销：{config["fixed_system_overhead_tokens"]} tokens
- 可灌入输入预算：{usable_input_budget(config)} tokens
- 档位：{", ".join(f"{tier:.0%}" for tier in config["tiers"])}
- 样本数：每档 {config["samples_per_tier"]} 个固定 case，总计 {len(rows)} cases
- 重复次数：{config["repeats"]}

## 实验约束

WorkBuddy 只能读取 `run_config.json` 和 `cases.jsonl`，逐条调用固定模型并写回结果。不得新增、改写、筛选或替换测试样本；不得让模型自行生成测试上下文；不得启用摘要、压缩、历史裁剪、RAG 重排或 Auto 模型路由。

每一次模型调用都必须是一次性输入完整 prompt，不能通过多轮对话累计上下文。

## 运动健康场景

上下文模拟的是杂乱用户日常记录：运动记录、睡眠日志、心率/HRV、步数、饮食、日程、聊天、出差、装备、恢复、身体反馈和工作生活噪声混在一起。模型要从这些噪声里找到指定的用户习惯、当前规则或恢复偏好。

本实验只测试长上下文检索、推理和指令遵守能力，不评估真实医疗建议质量。

## 测试能力

- `fact_recall`：在杂乱日常 context 中召回用户当前稳定习惯代码。
- `needle_position`：关键信息分别放在 5%、25%、50%、75%、95% 位置，观察 Lost in the Middle。
- `multi_hop`：把用户、计划、时段、恢复 routine 的映射分散到上下文里，要求串联得到最终代码。
- `instruction_following`：长期健康响应规则放在上下文不同位置，检查 JSON 格式和 `safety_phrase` 是否漂移。
- `distractor_resistance`：加入过期习惯、相似用户或相邻训练块，检查模型是否被无关记录带偏。

## 通过/失败判定

每个 case 要求模型返回 JSON，至少包含 `answer` 字段；`instruction_following` 还必须包含正确的 `safety_phrase`。

- `fact_recall`：`answer` 必须包含答案键中的精确习惯代码。
- `needle_position`：`answer` 必须包含答案键中的精确 routine anchor。
- `multi_hop`：`answer` 必须是多跳链路得到的最终 routine code。
- `instruction_following`：`answer` 和 `safety_phrase` 都必须精确匹配。
- `distractor_resistance`：`answer` 必须是当前权威记录，且不得命中过期或相似 distractor。

## 明显下滑点定义

以 50% 档作为基线：

- 综合分下降 >= 10%，视为明显下滑候选；
- 任一关键能力下降 >= 15%，视为分项能力下滑；
- 如果 95% 置信区间不重叠，视为强证据；
- 如果 80%、90%、95% 连续下降，即使 CI 有重叠，也作为 context cliff 风险信号记录。

如果高档位失败原因是请求超限、接口截断、输出截断或 WorkBuddy 自动压缩，必须标记为“容量/接口失败”，不得误判为模型推理质量下降。

## 验收输出

WorkBuddy 完成后必须生成：

- `trials.jsonl`
- `summary_by_tier.csv`
- `category_by_tier.csv`
- `needle_by_position.csv`
- `report.md`
- `analysis_results.md`
- `overall_score_by_tier.svg`
- `category_scores_by_tier.svg`
- `needle_position_accuracy.svg`

报告必须说明实际使用模型、实际 context window、每个档位的综合分、下滑点、能力归因、失败样例、容量/接口风险，以及 70%、80%、90%、95% 是否出现明显下滑。
"""
    (output_dir / "acceptance.md").write_text(content, encoding="utf-8")


def write_workbuddy_instructions(output_dir: Path, config: dict[str, Any], profile_key: str, model_label: str) -> None:
    profile = PACK_PROFILES[profile_key]
    total_cases = len(list(open(output_dir / "cases.jsonl", "r", encoding="utf-8")))
    pilot_line = (
        "quick pilot 规模：每档最多 5 个 case，总计 30 次模型调用。"
        if int(config["samples_per_tier"]) > 5
        else "这个题包本身就是 pilot 规模：每档 5 个 case，总计 30 次模型调用。"
    )
    content = f"""# 发给 WorkBuddy 的执行指令

请严格按下面要求运行运动健康长上下文衰减实验。测试上下文、答案键和验收标准已经由外部预先准备好，WorkBuddy 只能执行，不允许自行生成或修改测试集。

## 模型

- 固定使用 `{model_label}`。
- 不要使用 `Auto`。
- 不要切换到 DeepSeek、GLM、Kimi、MiniMax 或其他模型。
- 本轮按 `{model_label} = 256K tokens context window` 设计。
- 如果 WorkBuddy API 内部模型 ID 不是 `{model_label}`，只允许把 `run_config.json` 里的 `provider.model` 改成 WorkBuddy 内部对应的 `{model_label}` 模型 ID，并在最终报告里记录实际模型 ID。不得改其他测试内容。

## 题包方向

- 方向：{profile["title"]}
- 说明：{profile["description"]}
- 背景：运动健康产品中的杂乱用户日常 context，包括运动、睡眠、饮食、心率、步数、日程、聊天、出差、装备、恢复和工作生活噪声。
- 目标：验证模型在 70%、80%、90%、95% 上下文占用率时，是否还能从一次性输入的长 context 中找出用户习惯、当前规则和恢复偏好。

## 固定测试包

使用这个目录：

```text
{output_dir}
```

必须使用：

```text
{output_dir}\\run_config.json
{output_dir}\\cases.jsonl
{output_dir}\\answer_key.csv
{output_dir}\\acceptance.md
```

`cases.jsonl` 已经包含每条完整 prompt、目标档位、答案键、distractor 和 prompt_hash。不要重新生成上下文，不要改写 prompt。

## 禁止项

- 不要让模型或 WorkBuddy 自行生成测试上下文。
- 不要启用 Auto 模型路由。
- 不要通过多轮对话累计上下文。
- 不要启用摘要、压缩、历史裁剪、RAG 重排或自动整理上下文。
- 不要打印、保存或展示 WorkBuddy token。
- 不要提交或改写 `runs/` 里的输出。

## 实验规模

- context window：{config["context_window_tokens"]} tokens
- 预留输出：{config["reserved_output_tokens"]} tokens
- 固定系统开销：{config["fixed_system_overhead_tokens"]} tokens
- 可灌入输入预算：{usable_input_budget(config)} tokens
- 档位：{", ".join(f"{tier:.0%}" for tier in config["tiers"])}
- 本题包固定 case 数：{total_cases}
- 每档覆盖：事实召回、Needle、Multi-hop、指令遵守、干扰抗性
- Needle 位置覆盖：5%、25%、50%、75%、95%

## 第一步：跑 smoke

在普通 Windows PowerShell 中运行，必须是已经登录 WorkBuddy 的同一个 Windows 用户：

```powershell
cd F:\\context
python experiments\\long_context_decay\\run_workbuddy_local_auth.py --config {output_dir}\\run_config.json --prepared-cases-path {output_dir}\\cases.jsonl --mode smoke
```

如果 smoke 失败，停止，不要继续消耗积分。报告错误原因。

## 第二步：跑 quick pilot

smoke 成功后，先跑 quick pilot。这个阶段只用于确认扣费、接口、输出格式和基础评分链路，不作为最终统计结论。

```powershell
cd F:\\context
python experiments\\long_context_decay\\run_workbuddy_local_auth.py --config {output_dir}\\run_config.json --prepared-cases-path {output_dir}\\cases.jsonl --mode pilot
```

{pilot_line}

如果 quick pilot 中出现请求超限、接口截断、输出截断、明显 token limit 错误或 WorkBuddy 自动压缩迹象，停止，不要继续跑主实验。

## 第三步：跑 full

quick pilot 成功后，运行 full：

```powershell
cd F:\\context
python experiments\\long_context_decay\\run_workbuddy_local_auth.py --config {output_dir}\\run_config.json --prepared-cases-path {output_dir}\\cases.jsonl --mode full
```

full 结果用于判断 70%、80%、90%、95% 是否出现明显下滑。

## 验收

按 `acceptance.md` 判定。最终必须输出：

- 实际使用模型名和模型 ID
- 是否确认为 {model_label}
- 是否确认 context window 为 256K tokens
- `report.md` 路径
- `analysis_results.md` 路径
- `summary_by_tier.csv` 路径
- `category_by_tier.csv` 路径
- `needle_by_position.csv` 路径
- 三张图路径：
  - `overall_score_by_tier.svg`
  - `category_scores_by_tier.svg`
  - `needle_position_accuracy.svg`
- 结论：70%、80%、90%、95% 是否出现明显下滑
- 分析：下滑主要来自哪类能力；是否有 Lost in the Middle；是否有容量/接口失败；给出失败 case 示例

如果高档位失败是因为请求超限、接口截断、输出截断或 WorkBuddy 自动压缩，要明确标记为“容量/接口失败”，不要误判为模型推理质量下降。
"""
    (output_dir / "WORKBUDDY_INSTRUCTIONS.md").write_text(content, encoding="utf-8")


def main() -> int:
    args = parser().parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(args, output_dir)
    rows = write_cases(output_dir, config, args.profile)
    write_answer_key(output_dir, rows)
    write_manifest(output_dir, rows, config, args.profile, args.model_label)
    write_acceptance(output_dir, rows, config, args.profile, args.model_label)
    (output_dir / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_workbuddy_instructions(output_dir, config, args.profile, args.model_label)
    print(f"Exported health case pack: {output_dir}")
    print(f"Profile: {args.profile}")
    print(f"Cases: {len(rows)}")
    print(f"Config: {output_dir / 'run_config.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
