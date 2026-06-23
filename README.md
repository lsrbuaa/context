# 智能硬件时代的 Context Engineering

从 LLM 应用到多模态终端记忆系统的架构演进

## 研究主题

下一代 AI 终端的核心竞争力，不是单次问答能力，而是 **Context Assembly 能力**：它知道现在发生了什么，过去哪些事重要，用户通常怎么做，此刻是否该打扰，以及应该把哪些信息交给模型。

## 研究主线

```
LLM Context Window
        ↓
Prompt Assembly
        ↓
RAG / Tool Context / Session State
        ↓
Short-term Memory + Long-term Memory
        ↓
Context Ranker + Context Compressor
        ↓
Multimodal Context Object
        ↓
Hardware Context Compiler
        ↓
Embodied / Wearable / Robotic Memory System
        ↓
Proactive Personalized AI Terminal
```

## 研究框架

本研究分为两大部分：

### Part A：大模型应用中的 Context 管理

研究对象：Claude Code、Cursor、ChatGPT Memory、RAG Agent、MCP、LangGraph、MemGPT

核心问题：
1. Context window 怎么被填满
2. 哪些信息应该进入 prompt
3. 哪些信息应该存在外部记忆
4. 什么时候检索
5. 什么时候压缩
6. 如何避免 prompt 污染
7. 如何形成跨会话记忆

### Part B：智能硬件中的 Context 管理

研究对象：AI 眼镜、AI 耳机、AI Pin、桌面机器人、家庭机器人、AR 助手、VLA 机器人

核心链路：
```
持续感知 → 事件切分 → 记忆写入 → 记忆更新 → 检索排序 → Prompt 拼接 → 模型决策 → 设备执行 → 用户反馈 → 记忆修正
```

## 目录结构

```
├── README.md                     # 项目概览
├── docs/
│   ├── research-plan.md          # 10 周研究计划
│   ├── context-pitfalls-and-tricks.md  # 反直觉现象与实用技巧
│   ├── part-a/                   # Part A: 大模型 Context 管理
│   │   ├── 01-context-foundation.md      # 阶段1: 基础框架
│   │   ├── 02-prompt-assembly.md         # 阶段2: Prompt Assembly
│   │   └── 03-memory-architecture.md     # 阶段3: 多级记忆架构
│   └── part-b/                   # Part B: 智能硬件 Context 管理
│       ├── 04-multimodal-input.md        # 阶段4: 多模态输入
│       ├── 05-context-compiler.md        # 阶段5: Context Assembly
│       └── 06-hardware-scenarios.md      # 阶段6: 典型场景
├── cases/                        # 案例研究
│   ├── ai-glasses.md
│   ├── ai-earbuds.md
│   ├── ai-pin.md
│   └── ai-robot.md
├── schemas/                      # JSON Schema 设计
│   └── context-object.json
└── .gitignore
```

## 核心产出

1. **大模型 Context 管理范式图** — context window、prompt assembly、RAG、memory、tool calling 的关系
2. **智能硬件 Context Pipeline 图** — 传感器输入如何变成模型输入
3. **分层记忆架构图** — working/episodic/semantic/procedural/governance memory
4. **Context Compiler 机制** — 选择、排序、压缩、拼接上下文
5. **AI 智能终端演进路线图** — 被动问答 → 多模态助手 → 记忆型助手 → 主动服务终端 → 具身个人 Agent

## 核心结论

从软件 Agent 到智能硬件 Agent，Context 管理的核心从"把文档和历史对话塞进 prompt"，升级为"把现实世界的多模态事件、用户长期记忆、设备状态和行动约束编译成模型可用的任务上下文"。
