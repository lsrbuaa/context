# 10 周研究计划

## 总览

| 周期 | 主题 | 关键问题 | 产出 |
|------|------|----------|------|
| 第 1 周 | Context Engineering 基础 | LLM context 由哪些部分组成？ | 概念图、术语表 |
| 第 2 周 | Prompt Assembly 案例 | Claude Code / Cursor 如何拼上下文？ | 软件 Agent Prompt 拼接图 |
| 第 3 周 | RAG 与 Memory | 检索、长期记忆、短期状态有什么区别？ | RAG vs Memory 对比表 |
| 第 4 周 | MemGPT / LangGraph / MCP | 分层记忆、状态机、工具协议如何协同？ | 框架评估表 |
| 第 5 周 | 多级记忆模型 | 工作记忆、情景记忆、语义记忆、程序性记忆如何分层？ | 六层记忆架构 |
| 第 6 周 | 多模态输入 Context 化 | 视觉、语音、位置、设备状态如何转成 context object？ | Context Object Schema |
| 第 7 周 | 智能硬件 Prompt Assembly | 设备调用模型前如何组装 context？ | 硬件版 Context Compiler |
| 第 8 周 | 主动服务链路 | 什么时候提醒、什么时候沉默、什么时候执行？ | 主动服务时序图 |
| 第 9 周 | 案例研究 | 眼镜、耳机、机器人、AI Pin 对比 | 4 类硬件案例拆解 |
| 第 10 周 | 架构综合与路线图 | 下一代 AI 终端记忆系统如何演进？ | 总报告、路线图、JSON Schema |

## 阶段划分

### Phase 1-3: Part A — 大模型 Context 管理 (第 1-4 周)

**阶段 1: 建立大模型 Context 管理基础框架**
- 文档: `docs/part-a/01-context-foundation.md`
- 目标: 搞清楚现在大模型应用里的 context 管理到底包含哪些模块

**阶段 2: 拆解 Prompt Assembly 机制**
- 文档: `docs/part-a/02-prompt-assembly.md`
- 目标: 深入研究"高质量 prompt 是如何被拼出来的"

**阶段 3: 研究多级记忆架构**
- 文档: `docs/part-a/03-memory-architecture.md`
- 目标: 从"context window 里放什么"扩展到"context window 外应该如何组织记忆"

### Phase 4-6: Part B — 智能硬件 Context 管理 (第 5-9 周)

**阶段 4: 把输入源从软件扩展到智能硬件**
- 文档: `docs/part-b/04-multimodal-input.md`
- 目标: 研究多模态传感器输入如何转化为 context

**阶段 5: 研究智能硬件的 Context Assembly**
- 文档: `docs/part-b/05-context-compiler.md`
- 目标: 设计一个"硬件版 Context Compiler"

**阶段 6: 研究典型智能硬件应用场景**
- 文档: `docs/part-b/06-hardware-scenarios.md`
- 目标: 选几个典型形态，拆完整链路

### Phase 7: 综合 (第 10 周)

- 最终报告
- 架构综合
- 演进路线图

## 关键参考文献

### Part A 参考
- Claude Code 文档 — context window、项目记忆、规则文件、工具结果
- MemGPT (arXiv) — virtual context management、分层记忆
- LangGraph / LangChain Memory — short-term state vs long-term memory
- MCP 协议 — 外部工具与数据接入

### Part B 参考
- LlamaPIE (arXiv) — 耳戴设备 proactive conversation assistant
- Memento (arXiv) — AR 助手永久记录与时空 context 主动召回
- ProMemAssist (ACM) — 智能眼镜实时建模 working memory
- Alpha-Service (arXiv) — AI glasses 主动服务系统架构
- OpenVLA (arXiv) — 开源 VLA 模型
- MemoryVLA (OpenReview) — cognition-memory-action 框架
