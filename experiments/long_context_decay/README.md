# 长上下文衰减实验 Harness

这个目录把“强制不压缩 + 分档灌入上下文”的实验方案落成了一个可跑工具。它会生成 30%、50%、70%、80%、90%、95% 六个上下文占用率档位的混合任务集，调用模型或 WorkBuddy，再输出 JSONL、CSV、Markdown 报告和三张 SVG 图。

## 快速自检

```powershell
python experiments\long_context_decay\run_experiment.py --provider oracle --samples-per-tier 2 --repeats 1 --context-window-tokens 4000
```

`oracle` 是只用于烟测的正确答案提供器，应该全部通过。想验证报告里的“下滑点”检测是否工作，可以跑：

```powershell
python experiments\long_context_decay\run_experiment.py --provider degraded_mock --samples-per-tier 10 --repeats 2 --context-window-tokens 8000
```

## 预先固定测试包

为了避免 WorkBuddy 临场生成上下文，可以先导出固定 case pack：

```powershell
python experiments\long_context_decay\export_case_pack.py --output-dir experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k --model-label DeepSeek-V3.2 --context-window-tokens 128000 --samples-per-tier 5 --repeats 1
```

导出文件：

- `cases.jsonl`：完整 prompt、答案键和元数据
- `answer_key.csv`：验收答案表
- `acceptance.md`：评分和验收标准
- `run_config.json`：运行配置，已指向固定 `cases.jsonl`

WorkBuddy 运行时必须使用 `run_config.json`，不要让它自行生成测试样本。

输出在 `experiments/long_context_decay/runs/<run-id>/`：

- `trials.jsonl`：每次调用的原始评分记录
- `summary_by_tier.csv`：各上下文档位的综合分、pass@1、幻觉率、引用错误率、延迟
- `category_by_tier.csv`：事实召回、Needle、多跳、指令遵守、干扰抗性分项
- `needle_by_position.csv`：Needle 在 5%、25%、50%、75%、95% 位置的正确率
- `report.md`：自动汇总和下滑点判断
- `overall_score_by_tier.svg`
- `category_scores_by_tier.svg`
- `needle_position_accuracy.svg`

## 接入 WorkBuddy

本机已发现 WorkBuddy 桌面版入口和内置 `genie` 扩展。最轻量的接入方式有三种，优先级从高到低如下。

### 方式 A：WorkBuddy API provider

先从本机 WorkBuddy 安装包生成本地配置：

```powershell
python experiments\long_context_decay\workbuddy_probe.py
```

然后把 WorkBuddy API token 放到环境变量里，不写入配置文件：

```powershell
$env:WORKBUDDY_API_TOKEN='...'
python experiments\long_context_decay\run_experiment.py --config experiments\long_context_decay\config.workbuddy.local.json
```

默认会调用：

- endpoint: `https://copilot.tencent.com/v1/chat/completions`
- token env: `WORKBUDDY_API_TOKEN`
- model: 自动选择 `product.json` 里输入窗口最大的文本模型

如果 WorkBuddy 后端要求不同路径，可以直接改 `config.workbuddy.local.json` 里的 `provider.openai_base_url`。

如果想直接使用本机 WorkBuddy 登录态和积分，运行：

```powershell
python experiments\long_context_decay\run_workbuddy_local_auth.py --mode smoke
```

模式说明：

- `--mode smoke`：只跑 1 次，确认登录态、接口和扣费链路
- `--mode pilot`：每个档位 5 个样本，适合先看是否有明显 cliff
- `--mode full`：使用配置里的正式 30×6×3 实验

注意：这个脚本必须由登录 WorkBuddy 的同一个 Windows 用户运行；它只在内存里解密 token，不打印、不写文件。

如果已经导出了固定 case pack，则改用：

```powershell
python experiments\long_context_decay\run_workbuddy_local_auth.py --config experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\run_config.json --prepared-cases-path experiments\long_context_decay\case_packs\deepseek_v32_pilot_128k\cases.jsonl --mode pilot
```

### 方式 B：WorkBuddy HTTP endpoint

如果你能在 WorkBuddy 里开一个本地或远端 eval endpoint：

```powershell
$env:WORKBUDDY_EVAL_URL='http://127.0.0.1:8000/eval/no-compress'
python experiments\long_context_decay\run_experiment.py --provider http --model workbuddy-http
```

HTTP provider 会 POST：

```json
{
  "system": "...",
  "prompt": "...",
  "metadata": {
    "case_id": "...",
    "tier": 0.9,
    "category": "needle_position",
    "repeat_index": 0,
    "disable_compression": true
  }
}
```

### 方式 C：WorkBuddy CLI wrapper

如果 WorkBuddy 有命令行或脚本入口，推荐用 command provider，并在命令里显式关闭压缩、摘要、裁剪、RAG 重排等机制。

```powershell
$env:WORKBUDDY_EVAL_COMMAND='workbuddy eval --no-compress --no-rag-rerank --prompt-file "{prompt_file}"'
python experiments\long_context_decay\run_experiment.py --provider command --model workbuddy-local
```

命令需要把最终模型输出打印到 stdout。可用占位符：

- `{prompt_file}`：包含 system 和 user prompt 的临时文件
- `{case_id}`：实验样本 ID
- `{tier}`：上下文占用率
- `{repeat}`：重复次数索引

## 接入 OpenAI-compatible API

```powershell
$env:OPENAI_API_KEY='...'
python experiments\long_context_decay\run_experiment.py --provider openai_compatible --model gpt-4.1 --config experiments\long_context_decay\config.example.json
```

如需换 base URL，改 `config.example.json` 里的 `provider.openai_base_url`。

## 真实 WorkBuddy 样本

可以把少量真实任务放到 JSONL 文件里，然后通过 `real_tasks_path` 加入混合任务集。每行格式：

```json
{"context":"长会话或项目上下文","question":"最终问题","expected_answer":"精确答案","expected_json":{"answer":"精确答案"}}
```

运行：

```powershell
python experiments\long_context_decay\run_experiment.py --provider command --real-tasks-path path\to\workbuddy_real_cases.jsonl
```

## 判定规则

默认 50% 档位是基线。工具会标记两类信号：

- 综合分相对 50% 基线下降至少 10%
- 任一关键能力相对 50% 基线下降至少 15%

如果 95% 置信区间不重叠，报告会把信号标成更强；如果区间重叠，会提示需要更多样本。

## 重要注意

- token 计数默认是估算值；如果 provider 返回真实 usage，`trials.jsonl` 会保留真实输入/输出 token。
- 正式实验建议保持 `samples_per_tier=30-50`、`repeats=3`。
- 预留输出 token 不要设太低，否则测到的可能是输出截断，而不是长上下文质量下降。
- 如果真实 WorkBuddy 默认会压缩历史，请优先接入一个绕过压缩的 eval endpoint；否则实验归因会不干净。
