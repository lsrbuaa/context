# 智能硬件时代的 Context Engineering

**从大模型 Context 管理到智能硬件 Context 管理：面向下一代 AI 终端的分层记忆系统与 Context Compiler 架构研究**

## 核心结论

从软件 Agent 到智能硬件 Agent，Context 管理的核心从"把文档和历史对话塞进 prompt"，升级为"把现实世界的多模态事件、用户长期记忆、设备状态和行动约束**编译**成模型可用的任务上下文"。

## 研究主线

```
LLM Context Window (Phase 1)
        ↓
Prompt Assembly (Phase 2)
        ↓
Memory Frameworks (Phase 3)
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

## 文件结构

```
├── README.md
├── 00_research_scope.md              # Phase 0: 研究范围、术语、问题树
├── 01_llm_context_management.md      # Phase 1: LLM Context 管理 + 12个行为特性
├── 02_software_agent_prompt_assembly.md  # Phase 2: Claude/Cursor/ChatGPT/LangGraph
├── 03_memory_frameworks.md           # Phase 3: MemGPT/Generative Agents/CoALA/Mem0/Zep
├── 04_hardware_context_inputs.md     # Phase 4: 传感器→Context Object Pipeline
├── 05_hierarchical_memory_architecture.md  # Phase 5: 七层记忆架构设计
├── 06_context_compiler.md            # Phase 6: 9步Context Compiler Pipeline
├── 07_hardware_case_studies.md       # Phase 7: 眼镜/耳机/Pin/机器人案例
├── 08_final_architecture_and_roadmap.md   # Phase 8: 综合架构+路线图
├── schemas/
│   └── context-object.json           # Hardware Context Object JSON Schema
├── sources/
│   ├── source_registry.md            # 41条资料注册表
│   ├── evidence_matrix.md            # 论断→证据映射
│   └── open_questions.md             # 待研究问题清单
└── _archive/                         # 旧版研究内容(含 pitfalls 快速参考)
```

## 核心产出

1. **12 个 Context 行为特性** — Lost in the Middle 等现象及其硬件设计约束
2. **七层记忆架构** — Raw Buffer / Perception WM / Task WM / Episodic / Semantic / Procedural / Governance
3. **9 步 Context Compiler Pipeline** — Trigger → Intent → Retrieve → Privacy → Rank → Budget → Pack → Invoke → Feedback
4. **9 维度 Context Ranker** — TaskRelevance + Recency + Spatial + UserSpecific + Confidence + Actionability - Privacy - Interruption - TokenCost
5. **四类硬件案例验证** — AI 眼镜、AI 耳机、AI Pin、机器人
6. **技术演进路线图** — 被动问答 → 多模态助手 → 记忆型助手 → 主动服务终端 → 具身个人 Agent
