# Phase 0：研究范围校准

## 1. 阶段研究目标

明确本研究的核心不是"智能硬件如何连接大模型"或"AIoT 数据传输"，而是从软件大模型 context management 到智能硬件 context management 的架构迁移研究。

本阶段需要回答：
- 研究到底在解决什么问题？
- 哪些是必须深入的主题，哪些是必须避免的跑偏方向？
- 核心术语如何定义？
- 最终交付物是什么？

## 2. 核心问题清单

1. 什么是 Context Engineering？它与 Prompt Engineering 的区别是什么？
2. 大模型应用中的 context 管理包含哪些子问题？
3. 当输入源从文本/代码扩展到多模态传感器时，context 管理面临什么新挑战？
4. "分层记忆系统"在软件 Agent 和智能硬件中分别意味着什么？
5. Context Compiler 的核心职责是什么？
6. 本研究的创新贡献在哪里？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| 基础概念 | context engineering, prompt assembly, context window management |
| 软件系统 | LLM memory system, agent memory, RAG architecture, tool augmented LLM |
| 分层记忆 | hierarchical memory, episodic memory AI, working memory LLM, cognitive architecture agent |
| 硬件 context | multimodal context, wearable AI memory, embodied agent memory, proactive AI assistant |
| 压缩与检索 | context compression, memory retrieval, context ranking, token budget |

## 4. 资料来源清单

本阶段主要依赖以下类型资料建立研究边界：

| 资料类型 | 用途 |
|----------|------|
| Anthropic 官方文档 | 定义 context engineering 概念框架 |
| 学术综述论文 | 确认 agent memory 研究现状 |
| 产品技术文档 | 确认工业界关注点 |
| 本项目已有内容 | 继承已建立的框架和结论 |

## 5. 证据矩阵

| 论断 | 证据来源 | 强度 |
|------|----------|------|
| Context Engineering 是模型能力之外的关键产品差异化因素 | Anthropic 官方博客 "Context Engineering" (2025) | 中 |
| MemGPT 提出分层记忆管理类比操作系统 | Packer et al. 2023, arXiv:2310.08560 | 强 |
| 智能硬件的 context 管理链路远超文本 RAG | 本项目推导（基于传感器特性分析） | 弱(待验证) |

## 6. 关键发现

### 6.1 研究问题树

```
根问题：智能硬件如何把现实世界连续流转化为可被大模型理解、调用、
        压缩、记忆和行动的高质量 Context？

├── 分支 A：大模型 Context 管理基础
│   ├── A1: Context Window 里放了什么？怎么填满的？
│   ├── A2: Prompt 是怎么被拼出来的？
│   ├── A3: RAG、Memory、Tool Context 各自的角色和边界？
│   ├── A4: 短期状态 vs 长期记忆如何协作？
│   └── A5: Context 如何被压缩、遗忘、更新？
│
├── 分支 B：从软件到硬件的范式迁移
│   ├── B1: 多模态传感器输入如何转化为结构化 Context？
│   ├── B2: 连续数据流如何切分为离散事件？
│   ├── B3: 智能硬件的分层记忆应该有几层？各层存什么？
│   ├── B4: 每次调模型前如何选择、排序、拼接 Context？
│   └── B5: 主动服务场景如何判断"该不该打扰用户"？
│
└── 分支 C：架构设计与验证
    ├── C1: Context Compiler 的 Pipeline 如何设计？
    ├── C2: 不同设备形态的 Context 策略有何差异？
    ├── C3: 隐私与 Context 质量如何平衡？
    └── C4: 演进路线图和产品机会点是什么？
```

### 6.2 范围边界表

| 必须深入研究 | 必须避免跑偏 |
|-------------|-------------|
| LLM context window 管理机制 | 硬件通信协议（蓝牙/Wi-Fi/MQTT） |
| Prompt assembly / prompt packing | 泛泛的 AIoT 或智能家居讨论 |
| RAG 与 memory 的区别和协同 | 纯模型能力研究（训练/微调/对齐） |
| Short-term memory 与 long-term memory | 纯传感器数据采集技术 |
| 分层记忆系统设计 | 把 MCP/A2A 当主线而非工具 |
| Context compression / summarization / forgetting | 没有证据的行业空话 |
| Tool context 与 sensor context | 硬件产品商业分析 |
| 多模态 context object 设计 | 单纯的产品评测 |
| 智能硬件 context pipeline | 嵌入式系统底层开发 |
| 主动服务中的 context decision | 通用机器学习算法研究 |
| Context Compiler 架构设计 | |

### 6.3 核心术语定义

| 术语 | 定义 | 备注 |
|------|------|------|
| **Context** | 模型在一次推理调用中可以访问的所有信息的总和 | 包含 system prompt、历史、检索结果、工具结果等 |
| **Context Window** | 模型单次调用能接受的最大 token 数 | 物理限制，决定了 context 的容量上界 |
| **Context Engineering** | 系统性地设计、选择、组织和管理进入模型 context 的信息的工程实践 | 区别于 Prompt Engineering：后者关注措辞，前者关注信息架构 |
| **Prompt Assembly** | 在一次模型调用前，从多个来源选择并拼接内容形成最终 prompt 的过程 | 是 Context Engineering 的核心执行环节 |
| **Context Compiler** | 一个系统组件，负责将原始输入、记忆、状态编译为优化后的模型输入 | 类比编程语言的编译器：高级表达 → 优化执行 |
| **Working Memory** | 当前任务所需的活跃上下文，对应 context window 中的动态内容 | 短时、高频变化 |
| **Episodic Memory** | 具体事件、经历的记忆 | "上周二用户在办公室找文件" |
| **Semantic Memory** | 抽象事实、关系、用户画像 | "用户偏好安静环境""张三是同事" |
| **Procedural Memory** | 行为规则、流程、习惯模式 | "用户回家后先开灯""会议中只震动" |
| **Governance Memory** | 关于记忆本身的元信息：来源、置信度、权限、过期策略 | 记忆治理层 |
| **RAG** | Retrieval-Augmented Generation，检索增强生成 | 从外部知识库检索相关内容注入 context |
| **Context Ranker** | 对候选 context 内容按相关性、时效性等维度评分排序的组件 | 决定"放什么进 prompt" |
| **Token Budget** | 一次模型调用中可用于各类内容的 token 分配预算 | 是 Context Compiler 的核心约束 |
| **MCP** | Model Context Protocol，连接 AI 应用与外部工具/数据的开放协议 | 定位为"context 接入层"而非记忆层 |
| **VLA** | Vision-Language-Action model，视觉-语言-动作模型 | 机器人场景的核心模型类型 |
| **Proactive Service** | 设备主动判断用户需要并提供服务，无需用户显式请求 | 智能硬件的关键差异化能力 |

### 6.4 Context Engineering vs Prompt Engineering

| 维度 | Prompt Engineering | Context Engineering |
|------|-------------------|---------------------|
| 关注点 | 单次 prompt 的措辞和格式 | 整个信息管理系统的设计 |
| 范围 | 一次调用 | 跨会话、跨设备的信息生命周期 |
| 核心问题 | "怎么问" | "给模型看什么" |
| 包含组件 | 指令设计、few-shot 示例 | 检索、记忆、压缩、排序、预算分配 |
| 类比 | 写一封好邮件 | 设计整个邮件系统的信息流 |

## 7. 对智能硬件 Context 管理的启发

Phase 0 确立了一个关键框架判断：**智能硬件 Context 管理不是"把传感器数据塞进 prompt"，而是一个完整的信息编译管线**——从持续感知到事件切分，从记忆写入到检索排序，从预算分配到模型调用，从执行反馈到记忆更新。

这意味着：
- 不能只关注"RAG 用什么向量数据库"这种局部问题
- 必须设计端到端的 context pipeline
- 硬件形态不同，context 策略也不同（眼镜 vs 耳机 vs 机器人）
- 隐私和打扰风险是硬件独有的 context 治理维度

## 8. 与其他阶段的关系

| 阶段 | 与 Phase 0 的关系 |
|------|-------------------|
| Phase 1 | 承接术语定义，深入 LLM context window 机制 |
| Phase 2 | 承接 Prompt Assembly 概念，通过案例具体化 |
| Phase 3 | 承接分层记忆术语定义，通过开源系统研究验证 |
| Phase 4 | 承接"范式迁移"判断，具体化多模态输入处理 |
| Phase 5 | 承接六层记忆定义，扩展为完整架构设计 |
| Phase 6 | 承接 Context Compiler 概念，形成工程化方案 |
| Phase 7 | 用设备案例验证前面所有阶段的框架 |
| Phase 8 | 综合所有阶段成果，形成最终交付物 |

## 9. 尚不确定或证据不足的问题

1. **Context Engineering 是否已有公认的学术定义？** — 目前主要来自 Anthropic 和 LangChain 的工程实践文章，尚无权威学术论文专门定义此概念。
2. **"分层记忆"模型在智能硬件中是否有已验证的实现？** — 目前主要是学术论文提出概念（MemGPT、CoALA），尚无公开的智能硬件产品完整实现。
3. **Context Compiler 是否已有成熟的开源实现？** — 目前最接近的是 LangGraph 的 state management + retrieval，但离完整 compiler 还有距离。

## 10. 下一阶段建议

Phase 1 应该从以下方向切入：

1. **首先厘清 LLM context window 里到底放了什么** — 通过分析 Claude、GPT-4、Gemini 的文档和实践
2. **建立 RAG vs Memory vs Tool Context 的三角对比** — 这是后续所有设计的基础区分
3. **收集 context compression 的技术方案** — 为后续 Token Budget 分配提供技术支撑
4. **完整整合 12 个 context 行为特性** — 将 pitfalls-and-tricks 的内容系统化为工程约束

---

## 附录：最终交付物清单

| # | 交付物 | 对应文件 |
|---|--------|----------|
| 1 | 研究范围与术语定义 | `00_research_scope.md` |
| 2 | 大模型 Context 管理范式研究 | `01_llm_context_management.md` |
| 3 | 软件 Agent Prompt Assembly 案例研究 | `02_software_agent_prompt_assembly.md` |
| 4 | 分层记忆框架与开源系统研究 | `03_memory_frameworks.md` |
| 5 | 智能硬件输入的 Context 化研究 | `04_hardware_context_inputs.md` |
| 6 | 智能硬件分层记忆架构设计 | `05_hierarchical_memory_architecture.md` |
| 7 | Context Compiler 架构设计 | `06_context_compiler.md` |
| 8 | 典型智能硬件案例研究 | `07_hardware_case_studies.md` |
| 9 | 综合架构、Schema 与路线图 | `08_final_architecture_and_roadmap.md` |
| 10 | 资料注册表 | `sources/source_registry.md` |
| 11 | 证据矩阵 | `sources/evidence_matrix.md` |
| 12 | 开放问题清单 | `sources/open_questions.md` |
| 13 | Context Object JSON Schema | `schemas/context-object.json` |
| 14 | Context 行为特性快速参考 | `_archive/docs/context-pitfalls-and-tricks.md` |

## 附录：研究主线图

```
LLM Context Window (Phase 1)
        ↓
Prompt Assembly (Phase 2)
        ↓
Memory Frameworks: RAG / Agent Memory (Phase 3)
        ↓
Multimodal Context Object (Phase 4)
        ↓
Hierarchical Memory Architecture (Phase 5)
        ↓
Context Compiler (Phase 6)
        ↓
Hardware Case Studies (Phase 7)
        ↓
Final Architecture & Roadmap (Phase 8)
```
