# 工程案例：生产系统如何做记忆与上下文

资料更新时间：2026-06-18。本文关注可借鉴的工程模式，不评价商业优劣。

## 1. 案例总览

| 案例 | 类型 | 可借鉴模式 | 对本仓库的启发 |
|---|---|---|---|
| [LangGraph Memory](https://docs.langchain.com/oss/python/concepts/memory) | Agent 框架 | 区分短期 thread memory 和长期 namespace memory，长期记忆分 semantic / episodic / procedural | Taxonomy 中应明确记忆类型和更新时机 |
| [LangMem SDK](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) | Agent 记忆 SDK | 将语义记忆、情节记忆、程序记忆拆成可优化对象 | Policy 和行为偏好可映射到 procedural memory，但必须可审计 |
| [LlamaIndex Memory](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/) | Agent 框架 | 短期 FIFO 消息和长期 Memory Block 组合，并用 token 预算和 priority 做截断 | Context Composer 需要显式 token 预算和优先级策略 |
| [Letta](https://docs.letta.com/guides/get-started/intro/) / [MemGPT](https://arxiv.org/abs/2310.08560) | Stateful Agent 平台 | Agent 拥有可编辑的状态和分层记忆，借鉴操作系统内存管理 | 跨设备记忆底座应把“当前工作上下文”和“外部长期记忆”分层 |
| [Mem0](https://docs.mem0.ai/core-concepts/memory-types) | 记忆基础设施 | Conversation / Session / User / Organization 多层记忆 | 本仓库可借鉴层级，但要补充设备、家庭和权限维度 |
| [Zep / Graphiti](https://help.getzep.com/graphiti/getting-started/overview) | 时间知识图谱记忆 | 用随时间演化的 Context Graph 表示实体、关系、事实和失效 | 跨设备记忆适合引入时间有效性、关系证据和冲突失效机制 |
| [Anthropic Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | RAG 工程实践 | 在 embedding 前为 chunk 补充局部上下文，并结合 rerank 降低失败召回 | Event / Episode 进入索引前也应补充场景、设备、时间和身份上下文 |
| [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Agent 工程方法 | 把 context 视为推理时的全部信息载荷，而不只是 prompt 文本 | 本仓库应围绕 Context Package 的质量定义工程目标 |
| [OpenAI ChatGPT Memory](https://openai.com/index/chatgpt-memory-dreaming/) | 用户级 AI 记忆产品 | saved memories 与后台自动整理的记忆并存，用于持续个性化 | 显式记忆和隐式整理应分开标注来源、置信度和可控性 |
| [Apple Intelligence / App Intents](https://developer.apple.com/wwdc26/guides/apple-intelligence/) | 端侧生态集成 | 通过 App Intents 和实体 schema 让 app 内容进入语义索引，并保留 attribution | 智能硬件生态需要标准实体和动作 schema，而不是每个 app 私有表达 |
| [Samsung Galaxy AI Personal Data Engine](https://www.samsungmobilepress.com/articles/samsung-introduces-future-ready-mobile-security-for-personalized-ai-experiences) | 端侧个性化与安全 | 将 routines、preferences 等个人洞察保留在设备侧，并用硬件安全能力保护 | 高敏记忆优先端侧处理，云端只接收最小化摘要或不接收 |
| [Gemini Enterprise Memory](https://docs.cloud.google.com/gemini/enterprise/docs/configure-personalization) | 企业个性化助手 | 从邮件、日历、文档等连接应用中抽取个人工作模式和项目上下文 | 跨设备记忆的数据资产地图要按来源、授权、用途和可撤销性建模 |

## 2. 可复用工程模式

### 2.1 分层记忆

多个系统都避免把“历史记录”作为唯一记忆形态。更常见的分层是：

- Conversation / Short-term：当前对话或任务内的上下文。
- Session / Working：当前任务的临时状态、工具输出和中间结论。
- User / Long-term：跨会话稳定的用户偏好、事实和习惯。
- Organization / Shared：团队、家庭或设备生态共享的上下文。
- Procedural / Policy：系统行为规则、权限约束和个性化风格。

本仓库应补充两个智能硬件特有层级：

- Device State Memory：设备状态、故障、能力和近期异常。
- Household / Multi-user Memory：家庭成员、访客、儿童、共享设备和可见范围。

### 2.2 热路径与后台路径分离

LangGraph、LlamaIndex、OpenAI 记忆实践都体现了一个关键权衡：记忆写入可以发生在用户请求的热路径，也可以在后台异步整理。

| 路径 | 适合做什么 | 风险 |
|---|---|---|
| 热路径 | 用户明确说“记住”“以后不要”、当前任务必须用到的状态 | 增加延迟，容易过度写入 |
| 后台路径 | 会话总结、长期偏好合并、过期记忆降权、跨设备证据聚合 | 用户不可见，必须加强解释和可撤销 |

工程建议：

- 显式反馈走热路径，立即生效。
- 行为规律走后台路径，先进入 candidate 或 pending_confirmation。
- 高敏记忆不得由后台静默写入 active 状态。

### 2.3 多索引不是多拷贝

生产系统常同时使用全文、向量、图谱、时间过滤和结构化字段。关键不是复制更多数据，而是保持同一 Memory 对象的一致身份：

```text
memory_id
  natural_language_summary
  structured_value
  vector_index_ref
  graph_node_ref
  evidence_refs
  policy_refs
  lifecycle_status
```

这样才能支持删除、审计、冲突处理和索引重建。否则，用户删除一条记忆后，摘要、向量或图谱边仍可能把它“复活”。

### 2.4 时间是一等属性

Zep / Graphiti 和 Agent memory 研究都强调状态变化。跨设备记忆尤其需要时间建模：

- valid_from / valid_until：记忆有效窗口。
- observed_at：证据发生时间。
- last_verified_at：最近一次被验证时间。
- stale_after：多久未验证后降权。
- superseded_by：被哪条新记忆覆盖。

没有时间字段，系统很难判断“长期偏好”和“最近临时变化”谁优先。

### 2.5 Context Composer 是产品边界

Anthropic 的 Context Engineering 和 LlamaIndex 的 token 预算设计都说明，最终进入模型的不是数据库，而是经过选择、排序、压缩和约束保留的上下文包。

一个工程化 Context Composer 至少要做：

- 权限过滤：未授权信息不能进入候选。
- 相关性重排：向量相似、关键词、场景、时间和设备状态综合打分。
- 冲突处理：新旧冲突时输出解释，而不是同时塞给模型。
- token 预算：不同信息类型有预算上限。
- 约束保留：隐私和安全约束不能被压缩掉。
- 可追溯输出：每条记忆对应 memory_id 和 evidence_id。

## 3. 案例带来的反面教训

### 3.1 只接向量库不够

向量库能解决相似召回，但不能单独解决：

- 用户删除。
- 权限授权。
- 多人身份归因。
- 新旧偏好冲突。
- 证据追溯。
- 端云边界。

因此，本仓库不能把 `memory-store` 写成单纯 vector store。

### 3.2 只做聊天记忆不够

很多记忆框架从对话历史出发，但智能硬件的关键数据来自设备和场景：

- 灯光、温度、噪声、睡眠、车机、耳机、门锁、家电。
- 这些数据不一定有自然语言表达。
- 这些数据通常伴随更强的隐私和执行风险。

因此，本仓库必须保留 Event Normalizer 和 Device State 层，而不是直接套聊天机器人记忆方案。

### 3.3 只强调个性化不够

ChatGPT Memory、Gemini Enterprise、Apple Intelligence、Samsung PDE 都说明个性化正在成为产品方向，但工程上必须同时回答：

- 用户如何知道系统记住了什么。
- 用户如何关闭、删除或临时不使用。
- 哪些记忆可以跨设备。
- 哪些记忆只能留在端侧。
- 记忆影响了哪次决策或设备动作。

本仓库要把用户可控和审计写成底座能力，不是产品后续优化项。

## 4. 对本仓库的架构修正

基于上述案例，后续架构文档应明确以下模块边界：

| 模块 | 必须回答的问题 |
|---|---|
| Device Signal Adapter | 设备事件如何标准化，如何处理多设备重复上报 |
| Identity Resolver | 当前信号属于哪个用户、家庭成员或访客 |
| Event Normalizer | 原始信号如何转成结构化 Event |
| Memory Candidate Builder | 哪些 Event / Episode 值得进入候选记忆 |
| Evidence Ledger | 记忆背后的证据如何追溯、删除和失效 |
| Policy Engine | 记忆在当前场景是否允许使用 |
| Memory Store | 结构化字段、全文、向量、图谱如何保持一致 |
| Context Composer | 如何输出短、准、可控的 Context Package |
| Memory Control Surface | 用户如何查看、纠错、删除和授权 |
| Eval Harness | 如何比较无记忆、最近对话、普通 RAG、结构化记忆和完整底座 |

## 5. 选型建议

本仓库当前不应绑定具体框架，但可以形成选型判断：

- 如果做通用 Agent 原型，LangGraph / LangMem 更适合快速验证 semantic、episodic、procedural memory。
- 如果做 RAG + agent 集成，LlamaIndex 的 Memory Block 和 token 预算机制值得借鉴。
- 如果研究“Agent 自管理记忆”，Letta / MemGPT 的分层上下文管理值得拆解。
- 如果研究生产级长期会话记忆，Mem0 的抽取、合并、检索和 benchmark 设计值得参考。
- 如果研究跨设备实体关系和状态变化，Zep / Graphiti 的 temporal KG 更接近问题本质。
- 如果研究智能硬件生态，Apple App Intents、Samsung PDE、Gemini Enterprise 的共同点是 schema、personal context、端侧安全和用户控制。

结论：跨设备用户记忆底座最可能是混合架构，而不是单一框架能完整覆盖。
