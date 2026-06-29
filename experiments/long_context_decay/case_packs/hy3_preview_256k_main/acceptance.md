# Long Context Decay Acceptance Criteria

## 固定测试包

- 被测模型：Hy3 preview
- context window 假设：256000 tokens
- 预留输出：8192 tokens
- 固定系统开销：1500 tokens
- 可灌入输入预算：246308 tokens
- 档位：30%, 50%, 70%, 80%, 90%, 95%
- 样本数：每档 25 个固定 case，总计 150 cases
- 重复次数：1

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
