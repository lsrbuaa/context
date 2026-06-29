#!/usr/bin/env python3
"""Export a fixed long-context case pack before WorkBuddy runs the test."""

from __future__ import annotations

import argparse
import copy
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from run_experiment import (
    DEFAULT_CONFIG,
    build_cases_for_tier,
    load_config,
    task_case_to_record,
    usable_input_budget,
)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Pre-generate fixed prompts, answer key, and acceptance docs."
    )
    p.add_argument("--config", help="Base JSON config.")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--model-label", default="DeepSeek-V3.2")
    p.add_argument("--context-window-tokens", type=int, default=128000)
    p.add_argument("--reserved-output-tokens", type=int, default=4096)
    p.add_argument("--fixed-system-overhead-tokens", type=int, default=1200)
    p.add_argument("--samples-per-tier", type=int, default=5)
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
    config = load_config(args.config) if args.config else copy.deepcopy(DEFAULT_CONFIG)
    config["experiment_name"] = f"long_context_decay_{args.model_label.lower().replace('-', '_')}"
    config["context_window_tokens"] = args.context_window_tokens
    config["reserved_output_tokens"] = args.reserved_output_tokens
    config["fixed_system_overhead_tokens"] = args.fixed_system_overhead_tokens
    config["samples_per_tier"] = args.samples_per_tier
    config["repeats"] = args.repeats
    config["tiers"] = args.tiers
    config["seed"] = args.seed
    config["prepared_cases_path"] = str((output_dir / "cases.jsonl").resolve())
    config["provider"]["type"] = "workbuddy_api"
    config["provider"]["model"] = args.model_label
    config["provider"]["workbuddy_endpoint"] = "https://copilot.tencent.com"
    config["provider"]["workbuddy_api_key_env"] = "WORKBUDDY_API_TOKEN"
    config["provider"]["openai_base_url"] = "https://copilot.tencent.com/v1/chat/completions"
    return config


def write_cases(output_dir: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(output_dir / "cases.jsonl", "w", encoding="utf-8") as handle:
        for tier in config["tiers"]:
            for case in build_cases_for_tier(float(tier), config):
                row = task_case_to_record(case)
                rows.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def write_answer_key(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "case_id",
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


def write_manifest(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], model_label: str) -> None:
    category_counts = Counter(row["category"] for row in rows)
    tier_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        tier_counts[f"{float(row['tier']):.2f}"] += 1
    manifest = {
        "case_pack": output_dir.name,
        "model_label": model_label,
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
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_acceptance(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], model_label: str) -> None:
    content = f"""# Long Context Decay Acceptance Criteria

## 固定测试包

- 被测模型：{model_label}
- context window 假设：{config["context_window_tokens"]} tokens
- 预留输出：{config["reserved_output_tokens"]} tokens
- 固定系统开销：{config["fixed_system_overhead_tokens"]} tokens
- 可灌入输入预算：{usable_input_budget(config)} tokens
- 档位：{", ".join(f"{tier:.0%}" for tier in config["tiers"])}
- 样本数：每档 {config["samples_per_tier"]}，总计 {len(rows)} cases
- 重复次数：{config["repeats"]}

## WorkBuddy 只允许做什么

WorkBuddy 只能读取 `run_config.json` 和 `cases.jsonl`，逐条调用模型并写回结果。不得新增、改写、筛选或替换测试样本；不得让模型自行生成测试上下文；不得启用摘要、压缩、历史裁剪、RAG 重排或 Auto 模型路由。

## 通过/失败判定

每个 case 要求模型返回 JSON。至少包含 `answer` 字段；`instruction_following` 还必须包含正确的 `safety_phrase`。

- `fact_recall`：`answer` 必须包含答案键中的精确值。
- `needle_position`：`answer` 必须包含答案键中的精确值，用于按 5%、25%、50%、75%、95% 位置统计。
- `multi_hop`：`answer` 必须是链式推理最终 reviewer。
- `instruction_following`：`answer` 和 `safety_phrase` 都必须精确匹配。
- `distractor_resistance`：`answer` 必须是当前权威 owner，且不得命中 retired/related distractor。

## 指标

- 主指标：`pass@1`
- 辅指标：结构化输出有效率、指令遵守率、引用错误率、幻觉率、平均延迟
- 综合分：
  `Score = 0.4 * fact_recall + 0.4 * needle_position + 0.25 * instruction_following + 0.2 * multi_hop + 0.15 * distractor_resistance`

## 下滑点定义

以 50% 档作为基线：

- 综合分下降 >= 10%，视为明显下滑候选；
- 任一关键能力下降 >= 15%，视为分项能力下滑；
- 如果 95% 置信区间不重叠，视为强证据；
- 如果 80%、90%、95% 连续下降，即使 CI 有重叠，也作为 context cliff 风险信号记录。

## 验收输出

WorkBuddy 完成后必须生成：

- `trials.jsonl`
- `summary_by_tier.csv`
- `category_by_tier.csv`
- `needle_by_position.csv`
- `report.md`
- `overall_score_by_tier.svg`
- `category_scores_by_tier.svg`
- `needle_position_accuracy.svg`

报告必须说明实际使用模型、实际 context window、每个档位的综合分和是否出现 70/80/90/95 下滑点。
"""
    (output_dir / "acceptance.md").write_text(content, encoding="utf-8")


def write_acceptance(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], model_label: str) -> None:
    content = f"""# Long Context Decay Acceptance Criteria

## 固定测试包

- 被测模型：{model_label}
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

## 测试能力

- `fact_recall`：在长上下文不同位置埋入精确 key-value，要求模型准确召回。
- `needle_position`：关键信息覆盖 5%、25%、50%、75%、95% 五个位置，用于观察 Lost in the Middle。
- `multi_hop`：A->B、B->C、C->D 分散在长上下文中，要求推理出最终 reviewer。
- `instruction_following`：长期规则放在上下文前部/中部/后部，检查格式和安全短语是否漂移。
- `distractor_resistance`：加入过期 owner 和相关但无关的 incident，检查模型是否被相似噪声带偏。

## 通过/失败判定

每个 case 要求模型返回 JSON。至少包含 `answer` 字段；`instruction_following` 还必须包含正确的 `safety_phrase`。

- `fact_recall`：`answer` 必须包含答案键中的精确值。
- `needle_position`：`answer` 必须包含答案键中的精确值，并按 5%、25%、50%、75%、95% 位置统计。
- `multi_hop`：`answer` 必须是链式推理得到的最终 reviewer。
- `instruction_following`：`answer` 和 `safety_phrase` 都必须精确匹配。
- `distractor_resistance`：`answer` 必须是当前权威 owner，且不得命中过期或相关 distractor。

## 指标

- 主指标：`pass@1`
- 辅指标：结构化输出有效率、指令遵守率、引用错误率、幻觉率、平均延迟
- 综合分：按 `score_weights` 加权后归一化计算

当前权重：

- fact_recall: 0.40
- needle_position: 0.40
- instruction_following: 0.25
- multi_hop: 0.20
- distractor_resistance: 0.15

## 明显下滑点定义

以 50% 档作为基线：

- 综合分下降 >= 10%，视为明显下滑候选；
- 任一关键能力下降 >= 15%，视为分项能力下滑；
- 如果 95% 置信区间不重叠，视为强证据；
- 如果 80%、90%、95% 连续下降，即使 CI 有重叠，也作为 context cliff 风险信号记录。

如果高档位失败原因是请求超限、接口截断或输出截断，必须标记为“容量/接口失败”，不得误判为推理质量下降。

## 验收输出

WorkBuddy 完成后必须生成：

- `trials.jsonl`
- `summary_by_tier.csv`
- `category_by_tier.csv`
- `needle_by_position.csv`
- `report.md`
- `overall_score_by_tier.svg`
- `category_scores_by_tier.svg`
- `needle_position_accuracy.svg`

报告必须说明实际使用模型、实际 context window、每个档位的综合分，以及 70%、80%、90%、95% 是否出现明显下滑。
"""
    (output_dir / "acceptance.md").write_text(content, encoding="utf-8")


def main() -> int:
    args = parser().parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(args, output_dir)
    rows = write_cases(output_dir, config)
    write_answer_key(output_dir, rows)
    write_manifest(output_dir, rows, config, args.model_label)
    write_acceptance(output_dir, rows, config, args.model_label)
    (output_dir / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported case pack: {output_dir}")
    print(f"Cases: {len(rows)}")
    print(f"Config: {output_dir / 'run_config.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
