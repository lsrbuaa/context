# 专业化升级计划

本文档回答一个问题：如何把当前仓库从“观点型白皮书”升级成“有证据链、有案例、有评估、有工程边界”的专业研究仓库。

## 1. 当前问题

仓库已有核心判断和基础框架，但仍有三个短板：

- 证据链不足：一些判断是合理的，但还没有和论文、框架、产品案例逐条绑定。
- 工程对象不够硬：Event、Memory、Policy、Context Package 已出现，但接口、状态机、索引关系和删除语义还不够具体。
- Eval 不够可执行：已有指标和样例，但还没有形成可复用 case schema、baseline、判分规则和最小数据集。

专业化的关键不是继续扩写宏观描述，而是把每个判断落到“来源、对象、接口、指标、验收标准”。

## 2. 升级原则

| 原则 | 具体要求 |
|---|---|
| 每个判断有来源 | 重要论断必须能指向论文、官方文档或工程案例 |
| 每个模块有输入输出 | 不能只写“记忆抽取”，要说明输入 Event、输出 MemoryCandidate、失败状态 |
| 每个对象有生命周期 | Memory、Policy、Evidence、Context Package 都要有状态机 |
| 每个能力可评估 | 抽取、检索、压缩、冲突、遗忘、隐私都要有指标 |
| 每个隐私动作可追溯 | 进入模型上下文的每条用户记忆都能解释来源和授权 |
| 每个工程建议有适用边界 | 说明适合什么场景、不适合什么场景、风险是什么 |

## 3. 文档结构升级

建议把仓库文档分成四层。

### 3.1 研究证据层

目标：让读者知道本仓库观点不是凭空提出。

应包含：

- `docs/literature-review.md`：论文综述和工程启发。
- `docs/engineering-cases.md`：工程案例矩阵和可复用模式。
- `docs/research-agenda.md`：从证据中抽出的研究问题。

验收标准：

- 至少覆盖 10 篇核心论文。
- 至少覆盖 8 个工程案例。
- 每个研究主线至少有 2 个外部锚点。

### 3.2 工程建模层

目标：让工程师能据此开始设计接口和数据表。

应强化：

- `docs/taxonomy.md`：补充对象之间的关系和状态机。
- `docs/memory-schema.md`：补充 Event、Episode、Memory、Policy、Evidence、Context Package 的 JSON Schema。
- `docs/architecture.md`：补充模块输入输出和关键失败模式。

验收标准：

- 每个核心对象都有 ID、owner、source、timestamp、status、policy、audit 字段。
- 每个模块都有输入、输出、依赖、失败模式。
- 明确结构化索引、向量索引、图谱索引之间如何保持一致。

### 3.3 评估验证层

目标：避免仓库停留在“感觉有道理”。

应强化：

- `docs/evaluation.md`：补充 baseline、case schema、自动判分和人工审查规则。
- 后续新增 `eval-cases/`：最小 20-50 条 JSONL 样例。
- 后续新增 `docs/experiment-design.md`：离线实验和线上灰度设计。

验收标准：

- 至少有五组 baseline：无记忆、最近 N 条对话、普通 RAG、结构化记忆、完整 Policy + Composer。
- 每条 case 都包含 expected_memory_ids、forbidden_memory_ids、expected_behavior、risk_checks。
- 隐私泄露、过期记忆、冲突处理不能只靠人工主观判断。

### 3.4 落地路线层

目标：让仓库能指导下一步 PoC。

应强化：

- `docs/roadmap.md`：从阶段计划改成 milestone + deliverables + exit criteria。
- 后续新增 `docs/poc-spec.md`：最小 PoC 的模块、API、数据样例和不做事项。

验收标准：

- 每个阶段都有明确退出条件。
- 不把“搭一个 demo”当作目标，而是把“验证一个工程假设”作为目标。
- PoC 只选一个低敏、高频、可验证场景，避免一开始覆盖所有智能硬件。

## 4. 近期最值得补的内容

### 4.1 数据资产地图

这是智能硬件厂商最有工程价值的部分。建议建立一张表：

| 数据源 | 信号 | 可靠性 | 敏感度 | 是否端侧处理 | 可沉淀记忆 | 可支持场景 |
|---|---|---|---|---|---|---|
| 手机 | 时间、位置、日程、App 使用 | 高 / 中 | 中 / 高 | 部分 | 通勤、提醒、任务状态 | 出行、日程 |
| 手表 | 睡眠、运动、心率趋势 | 中 / 高 | 高 | 优先端侧 | 健康趋势摘要 | 睡眠、健康 |
| 耳机 | 降噪状态、佩戴状态、通话环境 | 中 | 中 | 可端侧 | 使用偏好、异常 | 音频、售后 |
| 智能家居 | 灯光、温度、房间、门锁 | 高 | 中 / 高 | 部分 | 场景偏好 | 家居控制 |
| 车机 | 路线、驾驶偏好、车内环境 | 中 / 高 | 高 | 部分 | 通勤与车内偏好 | 出行 |
| 客服 | 故障记录、维修记录、投诉偏好 | 高 | 中 | 云端 | 设备服务历史 | 售后 |

这张表能把“智能硬件厂商有数据优势”变成可讨论的工程资产。

### 4.2 记忆状态机

建议把 Memory 生命周期写成状态机：

```text
candidate
 -> active
 -> active_with_override
 -> deprecated
 -> deleted

candidate
 -> pending_confirmation
 -> active / rejected

active
 -> rejected
 -> deleted
```

每个状态转换都要说明触发条件：

- 用户明确确认。
- 新证据支持。
- 新证据冲突。
- 长期未验证。
- 用户删除。
- 权限撤回。
- 系统发现归因错误。

### 4.3 Evidence Ledger

要让仓库更专业，必须补 Evidence Ledger。每条记忆都应能回答：

- 哪些 Event 支撑了它。
- 哪个设备或应用产生了证据。
- 当时是否有授权。
- 是否经过脱敏。
- 是否被用户确认过。
- 是否被用于某次模型调用。

如果没有证据账本，记忆系统无法解释、纠错、删除和审计。

### 4.4 Context Package Contract

Context Composer 的输出要从示例文本升级为 contract：

```json
{
  "context_package_id": "ctx_001",
  "task": {},
  "state": {},
  "memories": [],
  "policies": [],
  "evidence_summaries": [],
  "tool_constraints": [],
  "token_budget": {},
  "redaction_report": {},
  "audit_refs": []
}
```

这能把“组装上下文”变成明确的工程接口。

### 4.5 最小 Eval Suite

建议先做 30 条高质量 case，而不是追求大规模数据：

- 8 条智能家居偏好。
- 5 条设备售后。
- 5 条日程出行。
- 4 条健康/睡眠边界。
- 4 条多人家庭身份冲突。
- 4 条删除、纠错和权限撤回。

每条 case 至少包含：

- 当前任务。
- 当前状态。
- 可用记忆。
- 禁止使用记忆。
- 期望行为。
- 风险检查。
- 判分规则。

## 5. 下一步执行顺序

### 第一步：补证据

已补：

- `docs/literature-review.md`
- `docs/engineering-cases.md`

下一步应把现有 `whitepaper.md`、`architecture.md`、`research-agenda.md` 中的重要判断链接到这两份证据文档。

### 第二步：补工程对象

优先补：

- Evidence Ledger。
- Context Package Contract。
- Memory 状态机。
- Policy 决策表。
- Device Signal Adapter 的输入输出。

### 第三步：补评估集

优先补：

- `eval-cases/schema.json`
- `eval-cases/smart-home.jsonl`
- `eval-cases/privacy-conflict.jsonl`
- `docs/eval-protocol.md`

### 第四步：再考虑 PoC

不建议现在直接写完整 CLI 或服务。更专业的路线是先用 eval case 固定问题边界，再实现最小 Context Composer。否则 demo 很容易变成“能跑但无法证明有效”。

## 6. 专业化后的仓库定位

升级后，仓库不再只是“用户记忆很重要”的观点库，而应成为：

> 面向智能硬件生态的跨设备用户记忆底座研究与工程规范仓库。

它应该让读者能做三件事：

1. 通过论文和案例理解为什么需要这套系统。
2. 通过 schema、状态机和架构边界知道系统怎么设计。
3. 通过 eval case 和 baseline 知道系统是否真的有效。
