# 发给 WorkBuddy 的执行指令

请严格按下面要求运行长上下文衰减实验。注意：测试上下文、答案键和验收标准已经由外部预先准备好，WorkBuddy 只能执行，不允许自行生成或修改测试集。

## 模型

- 固定使用 DeepSeek-V3.2。
- 不要使用 Auto。
- 不要切换到 DeepSeek-V4-Flash；V4-Flash 支持 1M 上下文，会过度消耗积分，不适合作为第一轮主实验。
- 如果 API 模型 ID 不是 `DeepSeek-V3.2`，请只把 `run_config.json` 里的 `provider.model` 改成 WorkBuddy 内部对应的 DeepSeek-V3.2 模型 ID，并在最终报告里记录实际模型 ID。不得改其他测试内容。

## 固定测试包

使用这个目录：

```text
F:\context\experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k
```

必须使用：

```text
F:\context\experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\run_config.json
F:\context\experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\cases.jsonl
F:\context\experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\answer_key.csv
F:\context\experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\acceptance.md
```

`cases.jsonl` 已经包含每条完整 prompt、目标档位、答案键、distractor 和 prompt_hash。不要重新生成上下文，不要改写 prompt。

## 禁止项

- 不要让模型或 WorkBuddy 自行生成测试上下文。
- 不要启用 Auto 模型路由。
- 不要通过多轮对话累计上下文。
- 不要启用摘要、压缩、历史裁剪、RAG 重排或自动整理上下文。
- 不要打印、保存或展示 WorkBuddy token。
- 不要提交或改写 `runs/` 里的输出。

## 先跑 smoke

在普通 Windows PowerShell 中运行，必须是已经登录 WorkBuddy 的同一个 Windows 用户：

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\cases.jsonl --mode smoke
```

如果 smoke 失败，停止，不要继续消耗积分。报告错误原因。

## smoke 成功后跑 pilot

```powershell
cd F:\context
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\cases.jsonl --mode pilot
```

pilot 包规模：

- context window 假设：128000 tokens
- 预留输出：4096 tokens
- 可灌入输入预算：122704 tokens
- 档位：30%、50%、70%、80%、90%、95%
- 每档 5 个固定 case，总计 30 次模型调用
- 每个档位覆盖：事实召回、Needle、Multi-hop、指令遵守、干扰抗性

## 验收

按 `acceptance.md` 判定。最终必须输出：

- 实际使用模型名和模型 ID
- 是否确认为 DeepSeek-V3.2
- `report.md` 路径
- `summary_by_tier.csv` 路径
- `category_by_tier.csv` 路径
- `needle_by_position.csv` 路径
- 三张图路径：
  - `overall_score_by_tier.svg`
  - `category_scores_by_tier.svg`
  - `needle_position_accuracy.svg`
- 结论：70%、80%、90%、95% 是否出现明显下滑

如果 95% 档失败是因为请求超限、接口截断或输出截断，要明确标记为“容量/接口失败”，不要误判为模型推理质量下降。
