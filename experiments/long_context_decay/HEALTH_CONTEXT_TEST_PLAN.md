# 运动健康长上下文衰减实验方案

## 目标

验证 WorkBuddy 在运动健康产品场景下，当一次性输入的用户日常 context 占满 30%、50%、70%、80%、90%、95% 窗口时，是否会在“找习惯、找当前规则、抗噪声、遵守长期约束”这些能力上出现稳定下滑。

本实验不评估医疗建议质量，只评估长上下文中的信息检索、冲突消解、多跳推理、指令遵守和结构化输出能力。

## 被测模型

- 固定模型：`Hy3 preview`
- context window：256000 tokens
- 预留输出：8192 tokens
- 固定系统开销：1500 tokens
- 可灌入输入预算：246308 tokens
- 档位：30%、50%、70%、80%、90%、95%

所有 case 都是一次性输入完整 prompt，不能通过多轮对话累计上下文。实验必须关闭或绕开摘要、压缩、历史裁剪、RAG 重排、Auto 模型路由。

## 场景改造

旧题包偏抽象审计，不贴近产品。新版题包改为运动健康用户日常 context：

- 运动：跑步、骑行、游泳、力量、瑜伽、拉伸、鞋/装备轮换
- 恢复：酸痛、疲劳、低强度日、deload、拉伸、睡眠优先
- 生理数据：睡眠时长、静息心率、HRV、步数
- 生活噪声：日程、工作、出差、家庭聊天、购物、天气、餐食
- 冲突信息：旧计划、相似用户、相邻训练块、过期记录

答案仍然使用精确 ASCII code，例如 `HABITS-FACT_RECALL-30-0000-AMRUN`，这样可以稳定自动评分，不依赖主观判断。

## 题包设计

### 1. 主包：稳定习惯抽取

路径：

```text
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main
```

用途：正式统计主实验。

规模：

- 每档 25 个固定 case
- 6 个档位
- 总计 150 次模型调用

重点测试：从杂乱用户日常记录中找出稳定运动、睡眠、饮食或恢复习惯。

### 2. 探索包：习惯变更识别

路径：

```text
F:\context\experiments\long_context_decay\case_packs\health_change_events_256k_pilot
```

用途：低成本探索“旧习惯 vs 当前习惯”的失效模式。

规模：

- 每档 5 个固定 case
- 6 个档位
- 总计 30 次模型调用

重点测试：在旧计划、新计划、相似记录和日常噪声里识别当前有效习惯。

### 3. 探索包：健康约束与偏好记忆

路径：

```text
F:\context\experiments\long_context_decay\case_packs\health_safety_preferences_256k_pilot
```

用途：低成本探索“长期健康规则/恢复偏好”的失效模式。

规模：

- 每档 5 个固定 case
- 6 个档位
- 总计 30 次模型调用

重点测试：从身体反馈、恢复约束和长期偏好里找出应该遵守的规则，并避免生成医疗建议。

## 任务类型

所有题包共享 5 类任务，便于横向比较：

- `fact_recall`：在杂乱日常 context 中召回用户当前稳定习惯代码。
- `needle_position`：关键信息分别放在 5%、25%、50%、75%、95% 位置，观察 Lost in the Middle。
- `multi_hop`：用户、计划、时段、恢复 routine 的映射分散在上下文中，要求串联得到最终代码。
- `instruction_following`：长期健康响应规则放在上下文不同位置，检查 JSON 格式和 `safety_phrase` 是否漂移。
- `distractor_resistance`：加入过期习惯、相似用户或相邻训练块，检查模型是否被无关记录带偏。

## 评分

主指标：`pass@1`

辅指标：

- 结构化输出有效率
- 指令遵守率
- 引用错误率
- 幻觉率
- 平均延迟

综合分按配置中的 `score_weights` 加权后归一化：

- fact_recall: 0.40
- needle_position: 0.40
- instruction_following: 0.25
- multi_hop: 0.20
- distractor_resistance: 0.15

## 明显下滑点

以 50% 档作为基线：

- 综合分下降 >= 10%，视为明显下滑候选；
- 任一关键能力下降 >= 15%，视为分项能力下滑；
- 如果 95% 置信区间不重叠，视为强证据；
- 如果 80%、90%、95% 连续下降，即使 CI 有重叠，也记录为 context cliff 风险信号。

如果高档位失败是请求超限、接口截断、输出截断或 WorkBuddy 自动压缩，必须标记为“容量/接口失败”，不要误判为模型推理质量下降。

## 执行顺序

建议先跑主包的 smoke，再跑主包 quick pilot。确认接口、扣费和输出格式都正常后，再跑主包 full。

推荐顺序：

1. `health_habits_256k_main` smoke
2. `health_habits_256k_main` quick pilot
3. `health_habits_256k_main` full
4. `health_change_events_256k_pilot` full
5. `health_safety_preferences_256k_pilot` full

其中第 4、5 步是补充探索，不是主结论必须项。

## 验收产物

每个题包运行后都应生成：

- `trials.jsonl`
- `summary_by_tier.csv`
- `category_by_tier.csv`
- `needle_by_position.csv`
- `report.md`
- `analysis_results.md`
- `overall_score_by_tier.svg`
- `category_scores_by_tier.svg`
- `needle_position_accuracy.svg`

最终结论至少要回答：

- 70%、80%、90%、95% 是否相对 50% 基线出现明显下滑；
- 下滑主要来自哪类能力；
- 是否存在明显 Lost in the Middle；
- 是否有高档位容量/接口失败；
- 运动健康场景下最脆弱的是“习惯召回”“当前状态识别”“多跳推理”“长期规则遵守”还是“干扰抗性”；
- 失败 case 的具体例子，包括 case_id、档位、任务类型、期望答案、模型答案和失败原因；
- 对产品体验的解释：这些失败会如何影响运动健康助手识别用户习惯、遵守恢复约束、处理过期记录和避免噪声干扰。
