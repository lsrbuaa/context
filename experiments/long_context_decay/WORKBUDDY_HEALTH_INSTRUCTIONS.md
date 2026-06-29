# 发给 WorkBuddy 的运动健康长上下文实验指令

请严格按下面要求运行运动健康长上下文衰减实验。测试上下文、答案键和验收标准已经由外部预先准备好，WorkBuddy 只能执行，不允许自行生成或修改测试集。

## 模型

- 固定使用 `Hy3 preview`。
- 不要使用 `Auto`。
- 不要切换到 DeepSeek、GLM、Kimi、MiniMax 或其他模型。
- 本轮按 `Hy3 preview = 256K tokens context window` 设计。
- 如果 WorkBuddy API 内部模型 ID 不是 `Hy3 preview`，只允许把对应 `run_config.json` 里的 `provider.model` 改成 WorkBuddy 内部的 Hy3 preview 模型 ID，并在最终报告里记录实际模型 ID。不得改其他测试内容。

## 背景

这是运动健康产品场景的长上下文衰减实验。上下文是杂乱用户日常记录，包括运动、睡眠、饮食、心率、HRV、步数、日程、聊天、出差、装备、恢复和工作生活噪声。

目标是验证在 30%、50%、70%、80%、90%、95% 上下文占用率下，模型是否还能一次性从长 context 中找出用户习惯、当前规则、恢复偏好，并保持 JSON 输出和长期规则遵守。

## 禁止项

- 不要让模型或 WorkBuddy 自行生成测试上下文。
- 不要启用 Auto 模型路由。
- 不要通过多轮对话累计上下文。
- 不要启用摘要、压缩、历史裁剪、RAG 重排或自动整理上下文。
- 不要打印、保存或展示 WorkBuddy token。
- 不要提交或改写 `runs/` 里的输出。

## 主实验题包

优先运行这个题包：

```text
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main
```

必须使用这些文件：

```text
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main\run_config.json
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main\cases.jsonl
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main\answer_key.csv
F:\context\experiments\long_context_decay\case_packs\health_habits_256k_main\acceptance.md
```

主实验规模：

- context window：256000 tokens
- 预留输出：8192 tokens
- 可灌入输入预算：246308 tokens
- 档位：30%、50%、70%、80%、90%、95%
- 每档 25 个固定 case
- 总计 150 次模型调用
- 覆盖任务：事实召回、Needle、多跳推理、指令遵守、干扰抗性

## 第一步：跑主包 smoke

必须在已经登录 WorkBuddy 的同一个 Windows 用户下运行：

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\health_habits_256k_main\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\health_habits_256k_main\cases.jsonl --mode smoke
```

如果 smoke 失败，停止，不要继续消耗积分。报告错误原因。

## 第二步：跑主包 quick pilot

smoke 成功后运行：

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\health_habits_256k_main\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\health_habits_256k_main\cases.jsonl --mode pilot
```

quick pilot 规模：每档 5 个 case，总计 30 次模型调用。这个阶段只确认扣费、接口、输出格式和基础评分链路，不作为最终统计结论。

如果 quick pilot 中出现请求超限、接口截断、输出截断、明显 token limit 错误或 WorkBuddy 自动压缩迹象，停止，不要继续跑主实验。

## 第三步：跑主包 full

quick pilot 成功后运行：

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\health_habits_256k_main\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\health_habits_256k_main\cases.jsonl --mode full
```

full 规模：每档 25 个 case，总计 150 次模型调用。这个结果用于判断 70%、80%、90%、95% 是否出现明显下滑。

## 可选探索包

主包完成后，可以继续运行两个探索包。它们不是主结论必须项，但有助于定位失效模式。

### 习惯变更识别

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\health_change_events_256k_pilot\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\health_change_events_256k_pilot\cases.jsonl --mode full
```

用途：测试旧计划、新计划、相似记录和日常噪声中，模型是否能识别当前有效习惯。

### 健康约束与偏好记忆

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\health_safety_preferences_256k_pilot\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\health_safety_preferences_256k_pilot\cases.jsonl --mode full
```

用途：测试长期健康规则、身体反馈、恢复偏好和安全短语是否会在长 context 中漂移。

## 验收

按每个题包里的 `acceptance.md` 判定。最终必须输出：

- 实际使用模型名和模型 ID
- 是否确认为 Hy3 preview
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
- 下滑主要来自哪类能力：习惯召回、Needle、多跳推理、指令遵守或干扰抗性
- 详细分析：逐档综合分、分项能力归因、Needle 位置表现、失败 case 示例、疑似容量/接口失败、对运动健康产品体验的解释

如果高档位失败是因为请求超限、接口截断、输出截断或 WorkBuddy 自动压缩，要明确标记为“容量/接口失败”，不要误判为模型推理质量下降。
