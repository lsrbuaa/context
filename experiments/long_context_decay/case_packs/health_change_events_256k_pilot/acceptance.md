# 运动健康长上下文衰减实验验收标准

## 固定测试包

- 被测模型：Hy3 preview
- 题包方向：运动健康习惯变更识别
- 题包说明：在旧计划、新计划和日常噪声中识别当前有效习惯。
- context window 假设：256000 tokens
- 预留输出：8192 tokens
- 固定系统开销：1500 tokens
- 可灌入输入预算：246308 tokens
- 档位：30%, 50%, 70%, 80%, 90%, 95%
- 样本数：每档 5 个固定 case，总计 30 cases
- 重复次数：1

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
