# Long Context Decay Acceptance Criteria

## 固定测试包

- 被测模型：DeepSeek-V3.2
- context window 假设：128000 tokens
- 预留输出：4096 tokens
- 固定系统开销：1200 tokens
- 可灌入输入预算：122704 tokens
- 档位：30%, 50%, 70%, 80%, 90%, 95%
- 样本数：每档 5，总计 30 cases
- 重复次数：1

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
