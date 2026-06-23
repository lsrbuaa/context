# Phase 1：大模型应用中的 Context 管理基础

## 1. 阶段研究目标

搞清楚当前大模型应用中 context 管理到底包含哪些模块、解决什么问题、存在什么约束。本阶段是整个研究的地基——后续所有阶段（从 Prompt Assembly 到 Context Compiler）都建立在这里定义的概念和机制之上。

核心任务：
- 定义 LLM context window 中各类信息的分类和关系
- 厘清 RAG、Memory、Tool Context 的边界
- 分析 context compression 的技术路线
- 系统化梳理 context window 的行为特性和工程约束（12 个关键现象）
- 评估"长上下文模型"能否替代外部记忆系统

## 2. 核心问题清单

1. LLM context window 里通常放了什么？各部分占比如何？
2. 哪些内容是稳定上下文（跨会话不变），哪些是动态上下文（每次调用变化）？
3. RAG、memory、tool calling、conversation history 的功能边界是什么？
4. "长上下文模型"（如 Gemini 1.5 的 1M token）是否可以替代结构化记忆系统？
5. 什么是"高质量 context"？如何衡量 context 对模型输出的贡献？
6. Context compression 有哪些技术方案？各自适用什么场景？
7. 模型对 context 中不同位置、不同类型信息的处理存在哪些非线性行为？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| 基础机制 | LLM context window, transformer attention, positional encoding |
| Context 管理 | context engineering, prompt assembly, context window management |
| RAG | retrieval augmented generation, dense retrieval, semantic search |
| 压缩 | context compression, prompt summarization, context distillation |
| 长上下文 | long context LLM, million token context, needle in haystack |
| 行为特性 | lost in the middle, attention sink, instruction following |

## 4. 资料来源清单

| ID | 类型 | 标题 | 作者/机构 | 年份 | 相关性 |
|----|------|------|-----------|------|--------|
| S001 | paper | Lost in the Middle: How Language Models Use Long Contexts | Liu et al. (Stanford) | 2023 | Context 位置偏差的核心证据 |
| S002 | paper | Efficient Streaming Language Models with Attention Sinks | Xiao et al. (MIT) | 2023 | Attention Sink 现象的发现和利用 |
| S003 | paper | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al. (Meta) | 2020 | RAG 原始论文，定义基础架构 |
| S004 | documentation | Claude Code Context Window Documentation | Anthropic | 2025 | 工业级 context 管理实践 |
| S005 | blog | Context Engineering for AI Agents | Anthropic | 2025 | Context Engineering 概念定义 |
| S006 | paper | MemGPT: Towards LLMs as Operating Systems | Packer et al. | 2023 | 分层记忆管理的类比框架 |
| S007 | paper | The Reversal Curse: LLMs trained on "A is B" fail to learn "B is A" | Berglund et al. | 2023 | Context 知识方向性限制 |
| S008 | paper | Can Long-Context Language Models Subsume Retrieval, RAG, SQL, and More? | Xu et al. | 2024 | 长上下文 vs RAG 的系统对比 |
| S009 | blog | What We Learned from a Year of Building with LLMs | Eugene Yan et al. | 2024 | 工程实践中的 context 管理经验 |
| S010 | documentation | LangChain Memory Documentation | LangChain | 2024 | Short-term vs long-term memory 工程区分 |

## 5. 证据矩阵

| 论断 | 支撑资料 | 证据强度 |
|------|----------|----------|
| 模型对 context 中间位置信息注意力低 20%+ | S001 (实验验证) | 强 |
| 序列开头 token 吸收异常注意力权重 | S002 (实验+理论解释) | 强 |
| RAG 可能降低模型性能（检索增强悖论） | S003 + 后续复现研究 | 中 |
| 长上下文模型不能完全替代结构化检索 | S008 (对比实验) | 中 |
| Context Engineering 是产品差异化关键 | S005 (行业观点) | 中(非实验证据) |
| 模型对知识方向性敏感（反转诅咒） | S007 (实验验证) | 强 |

## 6. 关键发现

### 6.1 Context Window 构成模型

LLM 的 context window 可以看作一个有限容量的"工作台"，所有影响模型输出的信息都必须摆在这个台面上。

```
┌─────────────────────────────────────────────────┐
│              Context Window (Token Budget)        │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  System Prompt                           │    │  ← 稳定上下文
│  │  (身份、政策、约束、输出格式)             │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Rules / Project Configuration           │    │  ← 稳定上下文
│  │  (CLAUDE.md, .cursorrules, 项目规则)     │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  User Preferences / Memory               │    │  ← 半稳定上下文
│  │  (用户画像、偏好、跨会话记忆)            │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Conversation History                    │    │  ← 动态上下文
│  │  (对话轮次、逐步累积)                    │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Retrieved Documents (RAG)               │    │  ← 动态上下文
│  │  (语义检索结果、文件片段)                │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Tool Call Results                       │    │  ← 动态上下文
│  │  (代码执行结果、API 响应、搜索结果)      │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Current Task                            │    │  ← 动态上下文
│  │  (当前用户请求、任务描述)                │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 6.2 Context 类型三分法

| 类型 | 定义 | 变化频率 | 示例 |
|------|------|----------|------|
| **稳定上下文** | 跨会话不变或极少变化 | 周/月级 | System prompt, 项目规则, 用户长期偏好 |
| **半稳定上下文** | 会话内稳定，跨会话可能变化 | 会话级 | 当前任务描述, 活跃文件列表, 会话目标 |
| **动态上下文** | 每次模型调用都可能变化 | 调用级 | 工具结果, 最新对话, 检索结果, 传感器数据 |

### 6.3 RAG vs Memory vs Tool Context 对比

| 维度 | RAG | Memory | Tool Context |
|------|-----|--------|-------------|
| **定义** | 从外部知识库检索相关文档 | 系统主动维护的用户/项目状态信息 | 工具调用返回的结果 |
| **数据来源** | 预建索引的文档/代码库 | 对话历史中提取、用户显式声明 | 运行时工具执行 |
| **触发方式** | 每次查询时自动检索 | 系统主动注入或按需检索 | 模型决定调用工具后获得 |
| **生命周期** | 索引更新时变化 | 跨会话持久 | 单次调用后失效 |
| **准确性** | 取决于检索质量 | 取决于提取和更新机制 | 取决于工具可靠性 |
| **token 开销** | 中-高（文档片段） | 低-中（结构化摘要） | 变化大（从几行到几千行） |
| **典型系统** | Perplexity, Cursor 代码检索 | ChatGPT Memory, Claude auto memory | Claude Code tool results |
| **硬件对应** | 情景记忆检索 | 用户画像、习惯模型 | 传感器实时数据 |

### 6.4 长上下文模型 vs 记忆系统

**核心问题：如果模型能处理 1M+ token，是否还需要外部记忆？**

| 维度 | 长上下文模型 | 结构化记忆系统 |
|------|-------------|---------------|
| 容量 | 有物理上限（即使 1M 也有限） | 理论无限（外部存储） |
| 检索精度 | 依赖注意力机制（Lost in the Middle） | 可设计专用检索算法 |
| 成本 | token 数量线性增长 → 成本线性增长 | 只检索需要的，成本更可控 |
| 延迟 | 长 context → 高延迟 | 检索后注入，context 短延迟低 |
| 组织性 | 扁平序列，无结构 | 可分层、分类、带元数据 |
| 遗忘 | 不会主动遗忘 | 可设计遗忘策略 |
| 更新 | 每次都要重新放入 | 可增量更新 |

**结论**: 长上下文模型减轻了记忆系统的压力，但不能替代它。原因：
1. 即使 context 够长，Lost in the Middle 效应仍存在
2. 成本和延迟随 context 线性增长
3. 缺乏结构化组织和主动遗忘能力
4. 智能硬件场景的连续数据流远超任何 context window

### 6.5 Context Compression 技术路线

| 方法 | 原理 | 适用场景 | 局限 |
|------|------|----------|------|
| **对话摘要** | 将长对话压缩为摘要 | 多轮对话管理 | 可能丢失细节 |
| **滑动窗口** | 只保留最近 N 轮对话 | 实时对话系统 | 丢失早期上下文 |
| **选择性保留** | 按重要性评分保留关键信息 | token budget 紧张时 | 需要可靠的重要性判断 |
| **层级压缩** | 近期详细、远期摘要 | 长期运行的 agent | 实现复杂度高 |
| **嵌入压缩** | 将文本压缩为固定长度向量表示 | 大规模知识库 | 信息损失不可逆 |
| **Context Distillation** | 用小模型提取关键信息 | 高吞吐场景 | 引入额外延迟 |

Claude Code 的做法：当 context 接近上限时，自动压缩历史对话，保留最近内容和关键决策点。

---

## 6.6 Context Window 行为特性与工程约束（12 个关键现象）

模型对 context 的处理存在大量非线性、反直觉的行为模式。理解这些现象对设计 Context Assembly 系统至关重要——尤其在智能硬件场景中，token budget 更紧张、延迟要求更高、错误代价更大。

### 一、位置与注意力相关

#### 现象 1: Lost in the Middle

**现象**: 模型对上下文开头和结尾的信息注意力显著高于中间部分。当关键信息被埋在中间位置时，检索和推理准确率明显下降。

**原因假说**: Transformer 的注意力分布呈 U 形曲线（primacy + recency bias），可能与训练数据中信息分布模式以及位置编码的特性有关。

**实验证据**: Liu et al. (2023) "Lost in the Middle" 论文表明，当相关文档放在 10 篇检索结果的中间位置时，QA 准确率比放在首尾低 20%+。[S001]

**对智能硬件的启示**:
- Context Compiler 在拼接 prompt 时，应把最关键的当前场景和最相关记忆放在开头或结尾
- 中间区域放补充性、参考性内容
- 如果硬件 context 超过一定长度，中间的传感器数据很可能被"忽略"

---

#### 现象 2: Attention Sink

**现象**: 无论内容是什么，序列最开头的几个 token 总会吸收大量注意力权重。即使是无意义的 BOS token 也会获得远超比例的注意力。

**原因假说**: Transformer 在训练过程中学会把初始 token 当作"注意力垃圾桶"——当没有特别需要关注的内容时，注意力会默认分配给开头 token，避免分散到其他位置。[S002]

**实用技巧**: 一些系统故意在开头放置 filler token 或 system preamble，让真正重要的内容从"注意力稳定区"开始。

**对智能硬件的启示**:
- 设备 prompt 的前几个 token 不要放关键传感器数据
- System policy / device identity 放开头是合理的——它们本身就是"锚定框架"
- 真正需要模型精确处理的内容（如当前场景描述）应避开最前面几个 token 的"attention sink"区域

---

#### 现象 3: Instruction Following Decay

**现象**: 随着对话轮次增加或 context 变长，模型对 system prompt 中指令的遵守率逐步下降。到后期可能完全"忘记"初始约束。

**原因假说**: 长 context 中后续内容的注意力权重逐渐稀释了对早期 system prompt 的关注；同时后续对话中的隐含模式可能覆盖初始指令。

**实用技巧**:
- 在对话中定期重复关键指令（"system reminder"注入）
- 把核心约束放在最近的 user/system message 中而非仅依赖开头
- Claude Code 使用 `<system-reminder>` 标签在对话中间重新注入关键规则 [S004]

**对智能硬件的启示**:
- 长时间运行的硬件 agent 必须周期性刷新安全约束
- 不能假设"开机时设置一次规则就够了"
- 每次 LLM 调用都应在 prompt 末尾重申关键安全红线（物理安全、隐私边界）

---

### 二、检索与噪声相关

#### 现象 4: Distractor Effect（干扰项效应）

**现象**: 放入主题相关但任务无关的内容，比放入完全随机的噪声对模型性能伤害更大。模型会被"看起来有关但实际无用"的信息迷惑。

**原因假说**: 随机噪声容易被模型忽略（分布差异大），但主题相关的干扰项会激活相似的语义表示，导致模型难以区分真正有用的信息和干扰信息。

**实验证据**: 多篇 RAG 研究发现，检索到的"语义相近但答案无关"的文档比完全不相关的文档更能误导模型。

**对智能硬件的启示**:
- Context Ranker 的 relevance 阈值不能太宽松
- "宁可少放，不要多放"——宁可让 prompt 短一点，也不要塞入"看起来可能有关"的记忆
- 智能眼镜识别到的"类似场景"如果与当前任务无关，塞入 prompt 反而有害
- 记忆检索时的 precision 比 recall 更重要

---

#### 现象 5: Retrieval Augmentation Paradox（检索增强悖论）

**现象**: 有时 RAG 检索到的内容反而让模型表现比完全不检索更差。加了外部知识，回答质量下降了。

**触发条件**:
- 检索到的内容与问题表面相关但实质答案不同
- 检索到过时/错误信息，覆盖了模型本身的正确参数知识
- 检索到多条互相矛盾的结果

**对智能硬件的启示**:
- 记忆检索系统需要"不检索"的能力——当置信度不够时，宁可不召回
- 智能硬件的 episodic memory 如果记录了错误事件（误识别），召回后会污染决策
- 需要 confidence threshold：低于阈值的检索结果不进入 prompt

---

#### 现象 6: Knowledge Conflict（知识冲突）

**现象**: 当 context 中的信息与模型参数化知识矛盾时，模型行为变得不可预测——有时信上下文，有时信自己的"记忆"，有时生成含糊的折中答案。

**影响因素**:
- 冲突信息的位置（越靠后越容易被采信）
- 冲突信息的表述方式（越权威越容易被采信）
- 模型对自身参数知识的"确信度"

**对智能硬件的启示**:
- 当传感器数据与用户已知偏好冲突时（如"用户通常 7 点起床"vs"今天 5 点就起了"），需要明确的冲突解决策略
- 硬件 context 中应标注信息来源和时效性，帮助模型判断可信度
- Governance Memory 的 confidence 字段在此场景下至关重要

---

### 三、推理结构相关

#### 现象 7: Multi-hop Fragility（多跳推理脆弱性）

**现象**: 当完成推理所需的多个事实分散在 context 不同位置时，模型的推理正确率急剧下降。即使所有必要信息都在 context 中，分散放置也会导致失败。

**示例**: 
- 事实 A 在 prompt 开头："张三是产品经理"
- 事实 B 在 prompt 中间："产品经理负责周三的评审会"
- 问题："张三周三要做什么？"
- 模型可能无法正确串联 A→B

**对智能硬件的启示**:
- Context Compiler 应该尝试把相关信息聚合在一起，而非按时间/来源分散排列
- 如果机器人需要推理"用户偏好 + 当前环境 + 物体属性"才能决策，这些信息应紧邻放置
- 预处理阶段可以做"推理链预组装"——把可能需要关联推理的事实预先拼接

---

#### 现象 8: Reversal Curse（反转诅咒）

**现象**: 模型学会了"A is B"后，无法自动推出"B is A"。context 中提供的知识具有方向性。[S007]

**示例**: 
- Context 写了"Tom Cruise 的母亲是 Mary Lee Pfeiffer"
- 问"Mary Lee Pfeiffer 的儿子是谁？"模型可能答不出

**对智能硬件的启示**:
- 记忆存储时应考虑双向索引
- "张三是李四的同事" 应同时支持从张三查李四和从李四查张三
- 空间记忆也是如此："钥匙在抽屉里" 和 "抽屉里有什么" 是两个方向的查询
- 记忆写入时可以主动生成反向描述

---

#### 现象 9: Anchoring Effect（锚定效应）

**现象**: context 中前面出现的信息会强烈框定模型对后续内容的理解。即使后面给出了矫正信息，模型的判断仍会偏向最初的"锚"。

**示例**: 如果 prompt 开头描述"这是一个危险的环境"，后面即使给出安全数据，模型的输出仍倾向于保守/警惕。

**对智能硬件的启示**:
- Prompt 开头放置的场景描述会强烈影响后续推理的基调
- 如果想让设备做出果断行动，不要在 context 开头堆积风险/约束
- 反之，如果安全优先，在开头强调安全约束是有效的锚定策略
- Context 的排列顺序本身就是一种"隐式指令"

---

### 四、实用技巧

#### 现象 10: Recency Bias Exploitation（利用近因偏差）

**技巧**: 把最重要的指令或最关键的信息放在 prompt 最末尾（紧接模型输出位置），利用模型对近期内容的天然偏好提升遵从率和使用率。

**应用方式**:
- 关键安全约束在 prompt 末尾重申
- 最相关的检索结果放在其他结果之后
- 当前任务描述放在所有背景信息之后

**对智能硬件的启示**:
- 硬件 prompt 模板的最后几行应该是：当前任务 + 安全红线 + 输出格式
- 而非把当前任务放在中间被历史记忆包围

---

#### 现象 11: Context Stuffing Cliff（上下文填充断崖）

**现象**: 模型性能不是随 context 长度线性下降的。在接近 token limit 时，会出现断崖式性能崩溃——之前还能正常工作，突然各方面能力同时退化。

**原因假说**: 接近上限时注意力分配被极度稀释，同时位置编码可能在边界附近出现退化。

**实用技巧**: 永远不要用满 context window。建议预留 20-30% 的 buffer。

**对智能硬件的启示**:
- Token budget 规划必须保守
- 硬件场景的多模态 context 很容易膨胀（一张图的描述就可能上千 token）
- Context Compiler 必须有硬性截断机制，而非"能放多少放多少"
- 应设置 soft limit（开始压缩）和 hard limit（强制截断），soft limit 建议设在 70% 容量

---

#### 现象 12: Role Separation Trick（角色分隔技巧）

**技巧**: 用明确的格式分隔符（XML tag、markdown header、特殊分隔线）划分 context 的不同区块，可显著减少跨区域的信息干扰。

**原理**: 结构化标记帮助模型理解"这段内容属于什么角色/什么用途"，减少模型把一个区块的内容错误关联到另一个区块。

**应用方式**:
```
<system_rules>...</system_rules>
<user_profile>...</user_profile>
<current_scene>...</current_scene>
<retrieved_memories>...</retrieved_memories>
<device_state>...</device_state>
<task>...</task>
```

**对智能硬件的启示**:
- 硬件 Context Compiler 输出的 prompt 必须有清晰的区块结构
- 不同来源的信息（传感器 vs 记忆 vs 设备状态）用标签明确隔开
- 防止模型把"过去的记忆"误认为"当前的感知"
- 防止模型把"设备约束"误认为"用户偏好"

---

### 五、综合设计原则

基于以上 12 个现象，提炼出 Context Assembly 的"注意力预算"思维：

```
Prompt 结构（按模型注意力分布优化）:

┌─────────────────────────────────────────────┐
│  [高注意力区] System Identity + 锚定框架     │  ← Attention Sink 利用
├─────────────────────────────────────────────┤
│  [中注意力区] 背景记忆 + 补充 context        │  ← 放次要信息
│  (注意：相关信息要聚合，不要分散)            │  ← Multi-hop 对策
├─────────────────────────────────────────────┤
│  [高注意力区] 当前场景 + 任务 + 安全约束     │  ← Recency Bias 利用
└─────────────────────────────────────────────┘
     ↓
   模型输出
```

**硬件场景的特殊风险**:

| 现象 | 软件场景后果 | 硬件场景后果 |
|------|-------------|-------------|
| Lost in the Middle | 回答质量下降 | 遗漏关键安全信息 |
| Distractor Effect | 检索结果不精准 | 错误触发主动服务 |
| Instruction Decay | 格式不规范 | 忘记安全约束，物理风险 |
| Knowledge Conflict | 回答矛盾 | 执行错误动作 |
| Context Cliff | 输出退化 | 设备行为不可预测 |

**7 条设计原则**:

1. **位置即权重** — 信息放在哪里，决定了模型给它多少注意力
2. **少即是多** — 精选高质量 context 优于塞满 token window
3. **结构即指令** — 格式和分隔本身就在指导模型行为
4. **重复即强化** — 关键约束需要周期性重申
5. **聚合即推理** — 需要关联的信息要物理相邻
6. **方向即限制** — 知识的存储方向影响检索可达性
7. **安全要兜底** — 安全约束必须在高注意力区域出现

---

## 7. 对智能硬件 Context 管理的启发

本阶段研究对智能硬件设计的核心启发：

| 发现 | 硬件设计启示 |
|------|-------------|
| Context 有三种稳定性层次 | 硬件 prompt 也需区分设备规则(稳定)、用户状态(半稳定)、传感器数据(动态) |
| RAG ≠ Memory ≠ Tool Context | 硬件记忆系统不能把所有内容混为一谈，需要分层管理 |
| 长上下文不能替代记忆系统 | 即使模型支持长 context，硬件仍需外部分层记忆 |
| Lost in the Middle 效应 | 硬件 prompt 中关键安全信息必须在首尾，不能被传感器数据淹没 |
| Context Compression 技术多样 | 硬件需要混合使用多种压缩策略（近期详细+远期摘要+关键保留） |
| 12 个行为特性是工程约束 | Context Compiler 的每个设计决策都应考虑这些约束 |

## 8. 与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| Phase 0 | 承接术语定义，本阶段深入各概念的机制和证据 |
| → Phase 2 | 本阶段定义的分类框架，在 Phase 2 通过具体软件系统验证 |
| → Phase 3 | RAG vs Memory 的区分，在 Phase 3 通过开源框架进一步细化 |
| → Phase 5 | 12 个行为特性直接约束 Phase 5 的记忆架构设计 |
| → Phase 6 | 7 条设计原则是 Context Compiler 的核心设计指导 |

## 9. 尚不确定或证据不足的问题

1. **Lost in the Middle 在 >1M token context 中的表现** — 原论文测试范围有限，超长上下文模型是否改善？ [NEEDS_CITATION]
2. **Attention Sink 在非 Transformer 架构中是否存在** — Mamba、RWKV 等状态空间模型的行为？ [NEEDS_CITATION]
3. **Context Compression 的信息损失量化** — 压缩后到底丢了多少对任务有用的信息？目前缺少标准度量。
4. **"高质量 context"的形式化定义** — 目前主要是经验判断，缺乏统一指标。
5. **多模态 context（图像+文本）的位置效应** — 12 个现象主要在纯文本上验证，多模态场景是否一致？ [NEEDS_CITATION]

## 10. 下一阶段建议

Phase 2 应该：

1. **以 Claude Code 为主要案例** — 深度拆解其 context window 管理：system prompt 结构、CLAUDE.md 注入时机、auto memory 机制、tool result 回填、context compression 触发条件
2. **对比 Cursor 的检索策略** — 代码仓库如何被索引、什么时候检索、检索结果如何排序进入 prompt
3. **分析 ChatGPT Memory 的写入/读取机制** — 什么触发记忆写入、记忆如何在后续会话中被注入
4. **研究 LangGraph 的 state management** — thread state vs store 的区分如何映射到 working memory vs long-term memory
5. **明确 MCP 在 context pipeline 中的角色** — 它是 context 的接入层（获取外部数据），而非记忆层
