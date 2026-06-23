# 阶段 1：建立大模型 Context 管理基础框架

## 目标

搞清楚现在大模型应用里的 context 管理到底包含哪些模块。

## 研究问题

1. LLM context window 里通常放了什么？
2. 哪些内容是稳定上下文，哪些是动态上下文？
3. Prompt assembly 的输入源有哪些？
4. RAG、memory、tool calling、session state 的边界是什么？
5. "长上下文模型"是否能替代记忆系统？

## 重点研究对象

| 对象 | 研究价值 |
|------|----------|
| Claude Code | 研究 context window、项目记忆、规则文件、工具结果如何进入上下文 |
| Cursor / Windsurf 类 IDE Agent | 研究代码仓库、规则、检索结果、编辑历史如何拼接 |
| ChatGPT Memory | 研究用户画像类长期记忆 |
| LangGraph | 研究 short-term state 与 long-term memory 的工程区分 |
| MemGPT / Letta | 研究虚拟上下文管理和多级记忆 |
| MCP | 研究工具和外部资源如何接入 context |

## 关键概念

### Context Window 构成

```
┌─────────────────────────────────────┐
│          Context Window             │
├─────────────────────────────────────┤
│  System Prompt (政策、身份、约束)     │
│  Rules / Project Config             │
│  Conversation History               │
│  Retrieved Documents (RAG)          │
│  Tool Call Results                  │
│  User Preferences / Memory          │
│  Current Task Description           │
└─────────────────────────────────────┘
```

### 稳定上下文 vs 动态上下文

| 类型 | 定义 | 示例 |
|------|------|------|
| 稳定上下文 | 跨会话不变或极少变化 | System prompt, 项目规则, 用户偏好 |
| 半稳定上下文 | 会话内稳定，跨会话可能变化 | 当前任务描述, 活跃文件列表 |
| 动态上下文 | 每次模型调用都可能变化 | 工具结果, 最新对话, 检索结果 |

### Claude Code 的 Context 管理机制

Claude Code 是一个优秀的研究对象：
- 每个 session 都有新的 context window
- 通过 `CLAUDE.md` 文件在会话之间携带项目知识
- 通过 auto memory 系统持久化用户偏好和项目状态
- 文件读取、规则、工具结果明确占用上下文窗口
- 有 context compression 机制应对长会话

### MCP 的定位

MCP 不应该被当成"记忆系统"，而应该被放在"外部工具与外部数据接入协议"这一层：
- **Tools**: 让模型调用外部系统
- **Resources**: 让外部数据被读取并用作 context
- 它是连接 AI 应用与外部系统、数据源、工具和工作流的开放标准

## 预期产出

1. **LLM Context 管理模块图** — 各组件之间的关系
2. **Context 类型分类表** — 稳定/半稳定/动态
3. **Prompt Assembly 流程图** — 从输入源到最终 prompt
4. **大模型应用 Context 管理案例对比表** — 各系统的策略对比
