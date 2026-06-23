# 智能硬件时代的 Context Engineering

**从大模型 Context 管理到智能硬件 Context 管理：面向下一代 AI 终端的分层记忆系统与 Context Compiler 架构研究**

---

## 研究背景

当大模型的单次推理能力趋于同质化，产品体验的差异化正在转向一个新战场：**谁能给模型提供更好的上下文**。

在 Claude Code、Cursor、ChatGPT Memory 等软件系统中，我们已经看到了 Context Engineering 的雏形——系统在每次模型调用前，从项目规则、对话历史、代码检索、工具结果中选择最相关的内容拼装为 prompt。但这些系统的输入仍然是文本、代码和结构化数据。

当 AI 从软件走向智能硬件——AI 眼镜、AI 耳机、录音挂坠——输入变成了摄像头每秒 30 帧的视频流、麦克风持续采集的环境音频、IMU 捕捉的身体运动、GPS 记录的空间轨迹。这些连续、多模态、高带宽、带隐私风险的数据流，远非简单的"把文档塞进 prompt"所能应对。

本研究回答一个核心问题：

> **智能硬件如何把现实世界的多模态事件、用户长期记忆、设备状态和行动约束，编译成 LLM / VLM 可用的高质量任务上下文？**

## 研究方法

我们没有试图一次性写出一篇综述，而是按**分阶段、可验证、有证据链**的方式推进：

1. 先吃透软件世界的 Context 管理（Phase 1-3）——LLM context window 的行为特性、主流 Agent 的 prompt 拼接机制、开源记忆框架的能力与局限
2. 再将这些认知迁移到硬件场景（Phase 4-6）——传感器数据如何 context 化、七层记忆如何分工、Context Compiler 如何做选择
3. 最后通过真实设备案例验证架构（Phase 7-8）——AI 眼镜 535ms 链路追踪、AI 耳机 330ms 实时辅助、录音挂坠的全天数据流

每个阶段都有明确的证据矩阵（`sources/evidence_matrix.md`），每条核心论断都标注了来源和可信度等级。未解决的问题统一收录在 `sources/open_questions.md`。

## 核心发现

### 发现 1：模型对 Context 的处理存在 12 个反直觉的行为特性

Lost in the Middle（中间信息被忽略）、Attention Sink（开头 token 吸收注意力）、Instruction Decay（长对话忘记规则）、Distractor Effect（相关噪声比随机噪声更有害）……这些现象不是学术趣闻，而是 **Context Compiler 设计的硬约束**——决定了 prompt 中什么放开头、什么放结尾、什么不该放进去。

### 发现 2：没有一个现有框架能直接用于可穿戴硬件

我们系统评估了 MemGPT、Generative Agents、Mem0、Zep/Graphiti、LangGraph 五个框架，在 15 个维度上进行加权评分。**最高分仅 38/100**。所有框架都是纯文本设计、假设云端运行、缺乏隐私治理、不支持传感器流——可穿戴硬件需要自建核心架构，选择性复用各框架的最佳组件。

### 发现 3：从原始传感器到 prompt 是一个 10,000:1 的信息压缩过程

AI 眼镜的传感器原始带宽约 5 MB/s，而一个典型的 Context Object 仅 100-300 tokens（~0.5 KB）。这个万倍压缩不是简单的丢弃，而是一个端到端的智能管线：信号处理 → 隐私过滤 → 感知识别 → 事件切分 → 重要性评估 → 深度理解 → 结构化组装。

### 发现 4：七层记忆架构是可穿戴硬件的最小完备设计

在认知科学（Atkinson-Shiffrin, Tulving）和 AI 系统（CoALA）的基础上，我们提出了面向硬件的七层模型：

```
L1 Raw Buffer      → 30秒环形缓存，永不落盘
L2 Perception WM   → 当前"我看到/听到什么"，实时刷新
L3 Task WM         → 当前"我在做什么任务"，构成 prompt 核心
L4 Episodic        → "昨天张工说了什么"，数万条带向量索引
L5 Semantic        → "张工是技术部同事"，实体+关系图谱
L6 Procedural      → "会议中只震动提醒"，if-then 规则引擎
L7 Governance      → 每条记忆的来源、置信度、隐私级别、过期策略
```

### 发现 5：Context Compiler 是连接记忆与模型的关键枢纽

我们设计了 9 步 Pipeline：Trigger Detection → Intent Classification → Context Retrieval → Privacy Filter → Context Ranking → Token Budget → Prompt Packing → Model Invocation → Feedback & Update。其中 Context Ranker 使用 9 个维度评分（TaskRelevance, Recency, SpatialRelevance, Confidence, Actionability, UserSpecificity, -PrivacyRisk, -InterruptionCost, -TokenCost），权重按设备形态自适应。

## 研究主线

```
Phase 0  研究范围校准（术语、边界、问题树）
    ↓
Phase 1  LLM Context 管理基础（含 12 个行为特性）
    ↓
Phase 2  软件 Agent Prompt Assembly（Claude Code / Cursor / ChatGPT / LangGraph / MCP）
    ↓
Phase 3  分层记忆框架对比（MemGPT / Generative Agents / CoALA / Mem0 / Zep）
    ↓
Phase 4  智能硬件输入的 Context 化（传感器 → Context Object Pipeline）
    ↓
Phase 5  七层记忆架构设计（数据结构 + 写入/遗忘规则 + 用户控制权）
    ↓
Phase 6  Context Compiler 架构（9步Pipeline + Ranker + 主动服务决策）
    ↓
Phase 7  硬件案例验证（眼镜 / 耳机 / Pin / 机器人）
    ↓
Phase 8  综合架构 + 技术路线图
```

## 文件结构

```
├── README.md                                   # 本文件
│
├── 00_research_scope.md                        # Phase 0: 研究范围、术语、问题树
├── 01_llm_context_management.md                # Phase 1: LLM Context 管理 + 12个行为特性
├── 02_software_agent_prompt_assembly.md        # Phase 2: Claude/Cursor/ChatGPT/LangGraph/MCP
├── 03_memory_frameworks.md                     # Phase 3: 7个框架系统对比
├── 04_hardware_context_inputs.md               # Phase 4: 传感器→Context Object Pipeline
├── 05_hierarchical_memory_architecture.md      # Phase 5: 七层记忆架构设计
├── 06_context_compiler.md                      # Phase 6: 9步Context Compiler Pipeline
├── 07_hardware_case_studies.md                 # Phase 7: 四类硬件案例
├── 08_final_architecture_and_roadmap.md        # Phase 8: 综合架构+路线图
│
├── supplements/                                # 深化补充文档
│   ├── sensor_data_specs.md                    # 传感器数据规格（格式/带宽/压缩比）
│   ├── worked_examples.md                      # 端到端 Trace（原始字节→prompt 文本）
│   ├── storage_tech_decisions.md               # 存储技术选型（SQLite/向量库/图DB）
│   └── framework_capability_matrix.md          # 15维度框架评估矩阵
│
├── schemas/
│   └── context-object.json                     # Hardware Context Object JSON Schema
│
├── sources/                                    # 证据管理
│   ├── source_registry.md                      # 41条资料注册表
│   ├── evidence_matrix.md                      # 核心论断→证据映射
│   └── open_questions.md                       # 待研究问题清单
│
└── _archive/                                   # 早期研究内容
    └── docs/context-pitfalls-and-tricks.md     # 12个现象的独立快速参考
```

## 核心产出清单

| # | 产出 | 文件 |
|---|------|------|
| 1 | 12 个 Context 行为特性及其工程约束 | `01_llm_context_management.md` §6.6 |
| 2 | 七层记忆架构（含完整 JSON Schema） | `05_hierarchical_memory_architecture.md` |
| 3 | 9 步 Context Compiler Pipeline | `06_context_compiler.md` §6.1 |
| 4 | 9 维度 Context Ranker 评分模型 | `06_context_compiler.md` §6.2 |
| 5 | 三类可穿戴设备端到端 Trace | `supplements/worked_examples.md` |
| 6 | 传感器数据规格与压缩比计算 | `supplements/sensor_data_specs.md` |
| 7 | 七层存储技术选型方案 | `supplements/storage_tech_decisions.md` |
| 8 | 15维度框架能力评估矩阵 | `supplements/framework_capability_matrix.md` |
| 9 | Hardware Context Object JSON Schema | `schemas/context-object.json` |
| 10 | 技术演进路线图（5阶段） | `08_final_architecture_and_roadmap.md` §5 |

## 技术演进路线图

```
Stage 1 (2023-24)     Stage 2 (2024-25)     Stage 3 (2025-26)     Stage 4 (2026-27)     Stage 5 (2027+)
被动问答设备      →   多模态助手       →   记忆型助手       →   主动服务终端     →   具身个人Agent
Siri/Alexa           Meta Ray-Ban          ChatGPT Memory       本研究目标架构      VLA + 全场景
用户触发/无记忆      拍照+问答/简单记忆     跨会话记忆/检索      Context Compiler     持续学习/自主行动
```

## 适合谁阅读

- **AI 硬件产品经理** — 理解"记忆系统"为什么是下一代设备的核心竞争力
- **AI 系统架构师** — 获取可落地的七层架构设计和存储选型方案
- **LLM 应用开发者** — 学习 Context Engineering 的系统化方法论
- **学术研究者** — 获取从认知科学到工程实现的完整映射和开放问题清单

## 引用与致谢

本研究引用了 41 篇/项资料（详见 `sources/source_registry.md`），核心参考包括：
- Liu et al. "Lost in the Middle" (2023) — Context 位置效应
- Packer et al. "MemGPT" (2023) — 虚拟上下文管理
- Park et al. "Generative Agents" (2023) — 记忆流与反思
- Sumers et al. "CoALA" (2023) — 认知架构分类
- Anthropic "Effective Context Engineering" (2025) — 工程原则

---

*本研究持续更新中。开放问题和待验证假设见 `sources/open_questions.md`。*
