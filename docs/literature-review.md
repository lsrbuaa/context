# 论文综述：用户记忆与 Context Engineering

资料更新时间：2026-06-18。本文只保留对本仓库有工程决策价值的论文，不做泛泛的论文罗列。

## 1. 综述结论

当前学术界已经形成几个相对清晰的判断：

- 长上下文不是用户记忆系统的替代品。上下文变长后，信息位置、噪声和无关内容仍会显著影响模型使用关键信息的稳定性。
- 记忆不是向量库。生产级记忆至少要处理抽取、更新、遗忘、冲突、权限、证据和评估。
- 个性化大模型的工程入口主要在输入层，即 personalized context；模型微调和偏好对齐可以增强能力，但不适合作为跨设备记忆底座的第一步。
- RAG 和记忆检索在敏感数据场景下会带来泄露风险，隐私策略必须前置到检索和上下文组装阶段。
- 记忆系统需要专门评估。只评价模型回答自然度，无法发现过期记忆、错误记忆、隐私泄露和上下文浪费。

## 2. 关键论文矩阵

| 论文 | 研究方向 | 核心贡献 | 对本仓库的工程启发 |
|---|---|---|---|
| [A Survey of Context Engineering for Large Language Models](https://arxiv.org/abs/2507.13334) | Context Engineering | 将 context retrieval / generation、processing、management 和系统实现统一到一个分类框架 | 把本仓库从 prompt 讨论提升为“上下文载荷优化系统”，明确 Context Composer 是核心工程模块 |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) | 长上下文鲁棒性 | 证明模型使用长上下文时会受关键信息位置影响 | 不能依赖“更长窗口”解决记忆问题；需要少量、高密度、排序明确的 Context Package |
| [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) | RAG | 建立外部知识召回加生成的经典范式 | 用户记忆可以借鉴 RAG，但必须增加权限、生命周期和冲突处理 |
| [RAPTOR](https://arxiv.org/abs/2401.18059) | 分层检索与摘要 | 通过递归聚类和摘要构建多层级检索树 | Episode 到 Memory 可以采用分层摘要思想，但要保留证据和可删除性 |
| [Generative Agents](https://arxiv.org/abs/2304.03442) | Agent 记忆架构 | 使用 memory stream、reflection、planning 支持长期行为模拟 | 记忆应包含原始观察、反思摘要和任务规划之间的清晰边界 |
| [MemoryBank](https://arxiv.org/abs/2305.10250) | 长期对话记忆 | 通过更新和遗忘机制支持长期陪伴场景 | 记忆评分需要同时考虑重要性、时间衰减和用户画像演化 |
| [MemGPT](https://arxiv.org/abs/2310.08560) | 虚拟上下文管理 | 借鉴操作系统分层内存，在有限窗口内管理长期记忆 | 可把 Context Package 视为工作内存，把 Memory Store 视为外部长期记忆 |
| [A Survey on the Memory Mechanism of LLM-based Agents](https://arxiv.org/abs/2404.13501) | Agent Memory 综述 | 系统梳理记忆设计、更新、评估和应用 | 本仓库的 research agenda 应覆盖记忆表示、写入、检索、更新和评估全过程 |
| [A Survey of Personalized Large Language Models](https://arxiv.org/abs/2502.11528) | 个性化大模型 | 将个性化分为输入层、模型层和目标层 | 当前阶段应优先做 input-level personalization，而不是过早做模型微调 |
| [Privacy-Preserving RAG with Differential Privacy](https://arxiv.org/abs/2412.04697) | 隐私保护 RAG | 指出 RAG 输出可能泄露外部敏感数据，并探索 DP 保护 | 用户记忆的 privacy leakage 应成为一等评估指标 |
| [MemoryAgentBench](https://arxiv.org/abs/2507.05257) | 记忆评估 | 从多轮增量交互评估记忆检索、测试时学习、长程理解和选择性遗忘 | 本仓库 eval 不应只做静态 QA，要加入跨 session 的增量更新和遗忘任务 |
| [Mem0](https://arxiv.org/abs/2504.19413) | 生产级 Agent 记忆 | 动态抽取、合并和检索长期会话记忆，并用 LoCoMo 做多类问题评估 | 工程 PoC 应比较结构化记忆、普通 RAG、全上下文和第三方记忆平台的效果与成本 |
| [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/html/2501.13956v1) | 时间知识图谱记忆 | 用动态时间图谱表示会变化的实体、关系和事实 | 跨设备用户记忆需要时间有效性和关系失效机制，不能只存静态 profile |

## 3. 从论文转成工程规则

### 3.1 Context Package 要短而有证据

来自长上下文和 Context Engineering 研究的共同结论是：更多上下文并不天然带来更好结果。工程上应坚持：

- 每次模型调用只放入会改变决策的信息。
- 每条记忆都携带时间、置信度、来源和敏感等级。
- 重要约束放在稳定位置，避免被任务信息淹没。
- Context Composer 必须输出固定结构，而不是随意拼接文本。

### 3.2 记忆需要“写入治理”，不是只做检索

Generative Agents、MemoryBank、MemGPT、Agent Memory 综述都说明：记忆系统的关键不只是取回历史，还包括决定什么进入长期记忆、何时更新、何时遗忘。工程上应把写入拆成：

- candidate：从 Event / Episode 中抽取候选。
- score：按任务价值、频率、新近性、稳定性、显式反馈、敏感风险打分。
- confirm：对冲突、高敏或低置信记忆进入待确认状态。
- persist：写入 Memory Store，同时写入 Evidence 和 Policy。
- decay：长期未验证或被新信息覆盖时降权。

### 3.3 用户记忆比企业知识库更难

普通 RAG 面向相对静态的外部知识，而用户记忆有四个额外难点：

- 人会改变偏好。
- 同一设备可能被多人使用。
- 高价值信号经常也是高敏信号。
- 用户要求删除时，向量、摘要、缓存和审计都要联动处理。

因此，跨设备记忆底座必须把 Policy、Evidence、Audit Record 作为和 Memory 同级的对象。

### 3.4 个性化优先走输入层

Personalized LLM 综述把个性化分为输入层、模型层和目标层。对智能硬件厂商而言，第一阶段更适合做输入层个性化：

- 不依赖训练私有模型。
- 易于审计和删除。
- 可以按场景授权。
- 可以用 A/B 和离线 eval 快速验证。

模型微调、用户适配器和偏好对齐可以作为后续增强，但不应成为白皮书阶段的主路径。

### 3.5 评估必须覆盖风险

MemoryAgentBench、LoCoMo、Mem0 等研究说明，记忆评估需要覆盖多轮、跨会话、时间变化和遗忘。对本仓库而言，最小评估集至少要包含：

- 正确召回：应该想起的记忆是否被取出。
- 错误抑制：不相关记忆是否被排除。
- 过期处理：旧偏好是否被降权。
- 冲突处理：新近明确表达是否优先。
- 隐私保护：敏感记忆是否被阻止进入模型。
- 成本效率：相比全上下文是否降低 token、延迟和成本。

## 4. 研究空白

目前论文和工程案例对“跨设备智能硬件用户记忆”覆盖仍不充分，主要空白包括：

- 多设备身份归因：一个灯光调整、耳机状态或车机行为到底属于哪个用户。
- 家庭多人权限：家庭成员、访客、儿童和设备所有者之间的可见范围。
- 端云协同记忆：哪些摘要在端侧生成，哪些进入云端检索，哪些永不出端。
- 设备执行风险：记忆不只影响回答，还会影响开门、调温、支付、健康提醒等动作。
- 用户可控体验：记忆纠错、删除、授权和解释如何不打扰用户。

这些空白正是本仓库后续体现工程价值的重点。

## 5. 建议阅读顺序

1. 先读 [Lost in the Middle](https://arxiv.org/abs/2307.03172) 和 [A Survey of Context Engineering for Large Language Models](https://arxiv.org/abs/2507.13334)，建立“长上下文不等于好上下文”的基本判断。
2. 再读 [Generative Agents](https://arxiv.org/abs/2304.03442)、[MemoryBank](https://arxiv.org/abs/2305.10250)、[MemGPT](https://arxiv.org/abs/2310.08560)，理解记忆系统的基本结构。
3. 然后读 [A Survey on the Memory Mechanism of LLM-based Agents](https://arxiv.org/abs/2404.13501) 和 [Personalized LLM Survey](https://arxiv.org/abs/2502.11528)，建立更完整 taxonomy。
4. 最后读 [Privacy-Preserving RAG](https://arxiv.org/abs/2412.04697)、[MemoryAgentBench](https://arxiv.org/abs/2507.05257)、[Mem0](https://arxiv.org/abs/2504.19413)、[Zep](https://arxiv.org/html/2501.13956v1)，把隐私、评估和生产系统纳入设计。
