# Phase 2：软件 Agent 的 Prompt Assembly 案例研究

## 1. 阶段研究目标

深入研究"高质量 prompt 是如何被拼出来的"——通过拆解 Claude Code、Cursor、ChatGPT Memory、LangGraph、MCP 等系统的实际机制，提炼可迁移到智能硬件的 Prompt Assembly 原则。

本阶段是从软件应用过渡到智能硬件的桥梁：软件 Agent 的 context 管理经验直接指导硬件 Context Compiler 的设计。

## 2. 核心问题清单

1. Claude Code / Cursor 这类系统如何组织项目规则、用户请求、文件、工具结果和历史上下文？
2. 稳定 context 与动态 context 如何区分和管理？
3. Prompt 拼接顺序有什么规律？为什么这样排列？
4. 哪些内容应该常驻 prompt，哪些应该按需检索？
5. 工具调用结果如何回填进 context？
6. 当 context 接近上限时，系统如何决定压缩或丢弃哪些内容？
7. 跨会话记忆如何写入和读取？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| Claude 体系 | Claude Code system prompt, CLAUDE.md, auto memory, compaction, context awareness |
| IDE Agent | Cursor context, codebase indexing, .cursorrules, code retrieval prompt |
| ChatGPT | ChatGPT memory, conversation memory, personalization |
| LangGraph | LangGraph memory, thread state, checkpointer, memory store |
| MCP | Model Context Protocol, MCP tools, MCP resources, context protocol |
| 工程实践 | context engineering agents, prompt assembly pattern, agent harness |

## 4. 资料来源清单

| ID | 类型 | 标题 | 作者/机构 | 年份 | 核心贡献 |
|----|------|------|-----------|------|----------|
| S011 | documentation | Context Windows - Claude API Docs | Anthropic | 2025 | Context window 机制、compaction、context awareness 详解 |
| S012 | blog | Effective Context Engineering for AI Agents | Anthropic | 2025 | Context engineering 核心原则和策略框架 |
| S013 | documentation | Claude Code Documentation | Anthropic | 2025 | CLAUDE.md、auto memory、tool results 管理 |
| S014 | documentation | MCP Introduction | Anthropic/MCP | 2024 | 外部工具和数据接入标准化 |
| S015 | documentation | LangGraph Memory Concepts | LangChain | 2024 | Short-term state vs long-term memory 工程区分 |
| S016 | blog | Building Effective Agents | Anthropic | 2024 | Agent 架构模式和 context 管理最佳实践 |
| S017 | documentation | Cursor Documentation | Cursor/Anysphere | 2025 | IDE Agent 的 context 管理策略 |
| S018 | blog | What We Learned from a Year of Building with LLMs | Eugene Yan et al. | 2024 | 工程实践中的 prompt 管理经验 |

## 5. 证据矩阵

| 论断 | 支撑资料 | 证据强度 |
|------|----------|----------|
| Claude 使用 compaction 策略压缩长对话 | S011 (官方文档) | 强 |
| Context awareness 让模型追踪剩余 token 预算 | S011 (官方文档) | 强 |
| Context engineering 核心是"最小高信号 token 集" | S012 (官方博客) | 强 |
| 系统 prompt 应用 XML/Markdown 结构化标签组织 | S012 (官方博客) | 强 |
| MCP 是连接 AI 应用与外部系统的标准化协议 | S014 (官方文档) | 强 |
| Agent 应通过结构化笔记维护跨 context window 记忆 | S012 (官方博客) | 强 |
| Sub-agent 架构可返回压缩摘要避免 context 膨胀 | S012 (官方博客) | 强 |

## 6. 关键发现

### 6.1 Claude Code 的 Context 管理机制

Claude Code 是目前最成熟的 coding agent 之一，其 context 管理策略非常系统化：

#### 6.1.1 Context Window 结构

```
┌─────────────────────────────────────────────────────────┐
│  System Prompt                                           │
│  ├── Agent 身份和能力描述                                │
│  ├── 可用工具列表和使用规则                              │
│  ├── 行为约束 (安全、权限、代码风格)                     │
│  ├── 输出格式规范                                       │
│  └── 环境信息 (OS, shell, git status, working dir)      │
├─────────────────────────────────────────────────────────┤
│  CLAUDE.md / Project Rules                              │
│  ├── 项目级规则 (.claude/CLAUDE.md)                     │
│  ├── 用户级规则 (~/.claude/CLAUDE.md)                   │
│  └── 目录级规则 (各子目录的 CLAUDE.md)                   │
├─────────────────────────────────────────────────────────┤
│  Auto Memory (跨会话持久记忆)                            │
│  ├── user memories (用户角色、偏好)                      │
│  ├── feedback memories (行为纠正)                       │
│  ├── project memories (项目状态)                        │
│  └── reference memories (外部资源指针)                   │
├─────────────────────────────────────────────────────────┤
│  Conversation History                                    │
│  ├── 用户消息序列                                       │
│  ├── Assistant 响应 (含工具调用)                         │
│  └── System reminders (中间注入的规则重申)               │
├─────────────────────────────────────────────────────────┤
│  Tool Results                                            │
│  ├── 文件读取结果                                       │
│  ├── Bash 执行结果                                      │
│  ├── 搜索/Grep 结果                                     │
│  └── 子 Agent 返回结果                                  │
├─────────────────────────────────────────────────────────┤
│  Current Task                                            │
│  └── 最新用户请求                                       │
└─────────────────────────────────────────────────────────┘
```

#### 6.1.2 关键 Context 管理策略

| 策略 | 机制 | 证据来源 |
|------|------|----------|
| **Compaction** | 当 context 接近上限时，服务端自动压缩早期对话为摘要 | S011 |
| **Context Awareness** | 模型接收剩余 token budget 信息，每次工具调用后更新 | S011 |
| **System Reminder 注入** | 在对话中间周期性重新注入关键规则 | S013 |
| **Thinking Block Stripping** | 前一轮的思考过程不计入后续 context | S011 |
| **Tool Result Clearing** | 旧的工具结果可被清除以释放空间 | S011 |
| **Sub-agent Delegation** | 复杂任务委派给子 agent，只接收压缩后的摘要 | S012 |
| **Structured Note-taking** | 通过 NOTES.md 等文件维护跨 context window 的任务状态 | S012 |

```text
"Your task is to create a detailed summary of the conversation so far, paying close attention to the user's explicit requests and your previous actions.
This summary should be thorough in capturing technical details, code patterns, and architectural decisions that would be essential for continuing development work without losing context.

Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Chronologically analyze each message and section of the conversation. For each section thoroughly identify:
   - The user's explicit requests and intents
   - Your approach to addressing the user's requests
   - Key decisions, technical concepts and code patterns
   - Specific details like:
     - file names
     - full code snippets
     - function signatures
     - file edits
  - Errors that you ran into and how you fixed them
  - Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
2. Double-check for technical accuracy and completeness, addressing each required element thoroughly.

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Key Technical Concepts: List all important technical concepts, technologies, and frameworks discussed.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Pay special attention to the most recent messages and include full code snippets where applicable and include a summary of why this file read or edit is important.
4. Errors and fixes: List all errors that you ran into, and how you fixed them. Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages that are not tool results. These are critical for understanding the users' feedback and changing intent.
6. Pending Tasks: Outline any pending tasks that you have explicitly been asked to work on.
7. Current Work: Describe in detail precisely what was being worked on immediately before this summary request, paying special attention to the most recent messages from both user and assistant. Include file names and code snippets where applicable.
8. Optional Next Step: List the next step that you will take that is related to the most recent work you were doing. IMPORTANT: ensure that this step is DIRECTLY in line with the user's most recent explicit requests, and the task you were working on immediately before this summary request. If your last task was concluded, then only list next steps if they are explicitly in line with the users request. Do not start on tangential requests or really old requests that were already completed without confirming with the user first.
                       If there is a next step, include direct quotes from the most recent conversation showing exactly what task you were working on and where you left off. This should be verbatim to ensure there's no drift in task interpretation.

Here's an example of how your output should be structured:

<example>
<analysis>
[Your thought process, ensuring all points are covered thoroughly and accurately]
</analysis>

<summary>
1. Primary Request and Intent:
   [Detailed description]

2. Key Technical Concepts:
   - [Concept 1]
   - [Concept 2]
   - [...]

3. Files and Code Sections:
   - [File Name 1]
      - [Summary of why this file is important]
      - [Summary of the changes made to this file, if any]
      - [Important Code Snippet]
   - [File Name 2]
      - [Important Code Snippet]
   - [...]

4. Errors and fixes:
    - [Detailed description of error 1]:
      - [How you fixed the error]
      - [User feedback on the error if any]
    - [...]

5. Problem Solving:
   [Description of solved problems and ongoing troubleshooting]

6. All user messages: 
    - [Detailed non tool use user message]
    - [...]

7. Pending Tasks:
   - [Task 1]
   - [Task 2]
   - [...]

8. Current Work:
   [Precise description of current work]

9. Optional Next Step:
   [Optional Next step to take]

</summary>
</example>

Please provide your summary based on the conversation so far, following this structure and ensuring precision and thoroughness in your response. 

There may be additional summarization instructions provided in the included context. If so, remember to follow these instructions when creating the above summary. Examples of instructions include:
<example>
## Compact Instructions
When summarizing the conversation focus on typescript code changes and also remember the mistakes you made and how you fixed them.
</example>

<example>
# Summary instructions
When you are using compact - please focus on test output and code changes. Include file reads verbatim.
</example>
"

强约束的产品化设计：

1）把工具调用纳入对话历史 你能看到 tool_use 和 tool_result 都作为 messages 的一部分进入上下文。这样压缩时，模型就能把“做过哪些工具调用/参数是什么/返回了什么”写进摘要。

2）把“压缩目标”写成一段非常长的 rubric（评分标准） 这段英文 prompt 不是让模型“随便总结”，而是要求按固定结构输出，并强调开发续航所需细节，比如文件名、函数签名、错误修复、用户反馈等。

3）cache_control: ephemeral 它暗示：这里面有些内容更像“仅本次调用需要”的临时指令/内容（例如总结任务 prompt、system role），不一定希望长期缓存进对话主记忆（不同平台对 cache 的实现不同，但工程意图很明确：把“指令性上下文”与“业务对话上下文”区分开）。
```

#### 6.1.3 Context Awareness 机制详解

Claude Code 使用 context awareness 让模型明确知道自己的"工作空间"剩余容量 [S011]：

```xml
<!-- 会话开始时 -->
<budget:token_budget>1000000</budget:token_budget>

<!-- 每次工具调用后 -->
<system_warning>Token usage: 35000/1000000; 965000 remaining</system_warning>
```

这使得模型可以：
- 判断是否有足够空间读取大文件
- 决定是否需要压缩当前上下文
- 合理分配剩余 budget 给后续任务步骤

#### 6.1.4 跨会话记忆：Auto Memory 系统

Claude Code 的 auto memory 系统将信息分为四类：

| 类型 | 存储内容 | 写入时机 | 使用方式 |
|------|----------|----------|----------|
| User | 用户角色、技能、偏好 | 学到用户信息时 | 调整交互风格和深度 |
| Feedback | 行为纠正和确认 | 用户反馈时 | 避免重复错误 |
| Project | 项目状态、决策 | 学到项目信息时 | 理解任务背景 |
| Reference | 外部资源指针 | 发现外部资源时 | 知道去哪里找信息 |

**关键设计决策：** Memory 以文件形式存储在 `.claude/` 目录下，通过 `MEMORY.md` 索引。每条记忆有 frontmatter（name, description, type），索引行数限制在 200 行以内。

---

### 6.2 Cursor / IDE Agent 的 Context 管理

#### 6.2.1 Context 来源层次

```
┌─────────────────────────────────────┐
│  Layer 1: System Instructions       │  固定
│  (IDE 内置的 Agent 行为规范)         │
├─────────────────────────────────────┤
│  Layer 2: Project Rules             │  稳定
│  (.cursorrules / .cursor/rules)     │
├─────────────────────────────────────┤
│  Layer 3: Codebase Index            │  半稳定
│  (语义索引的代码片段)                │
├─────────────────────────────────────┤
│  Layer 4: Active Files              │  动态
│  (当前打开/编辑的文件)               │
├─────────────────────────────────────┤
│  Layer 5: Retrieved Code            │  动态
│  (根据查询语义检索的相关代码)        │
├─────────────────────────────────────┤
│  Layer 6: User Query + Context      │  动态
│  (用户问题 + @引用的文件/文档)       │
└─────────────────────────────────────┘
```

#### 6.2.2 Cursor 的检索策略

| 检索触发 | 检索范围 | 排序依据 |
|----------|----------|----------|
| 用户提问 | 全 codebase 语义索引 | 语义相似度 + 文件距离 |
| 代码补全 | 当前文件 + 相关文件 | 编辑距离 + 导入关系 |
| @file 引用 | 指定文件 | 用户显式指定 |
| @codebase 引用 | 全仓库检索 | 语义相关性 |
| @docs 引用 | 外部文档索引 | 内容匹配度 |

#### 6.2.3 关键设计差异（vs Claude Code）

| 维度 | Claude Code | Cursor |
|------|-------------|--------|
| 检索方式 | 按需读文件（Just-in-time） | 预建语义索引 |
| 规则注入 | CLAUDE.md (多层级) | .cursorrules (项目级) |
| 工具使用 | 丰富工具集 (Bash, Edit, Grep...) | 有限工具 + IDE 原生能力 |
| Context 压缩 | Compaction (服务端) | 截断 + 摘要 |
| 跨会话记忆 | Auto Memory 系统 | 有限（依赖规则文件） |

---

### 6.3 ChatGPT Memory 系统

#### 6.3.1 架构概述

ChatGPT Memory 是面向用户画像的长期记忆系统：

```
用户对话 → 记忆触发检测 → 记忆提取/生成 → 记忆存储
                                                ↓
后续会话 ← 记忆注入 prompt ← 相关记忆检索 ← 记忆库
```

#### 6.3.2 记忆写入触发条件

| 触发类型 | 示例 | 记忆形式 |
|----------|------|----------|
| 用户显式声明偏好 | "我是素食主义者" | 事实性记忆 |
| 用户纠正模型 | "不对，我用的是 Python 3.12" | 纠正性记忆 |
| 对话中暴露的重复模式 | 多次提到在科技公司工作 | 推断性记忆 |
| 用户主动要求记住 | "记住我的项目截止日期" | 显式记忆 |

#### 6.3.3 记忆在 Prompt 中的位置

ChatGPT Memory 将记忆注入 system prompt 的 `<memories>` 区块中：

```
[System Instructions]
[Memory Block]
  - User is a vegetarian
  - User prefers Python over JavaScript
  - User works at a tech company in Beijing
[Conversation History]
[Current Query]
```

#### 6.3.4 设计局限性

| 局限 | 影响 |
|------|------|
| 记忆粒度粗（自然语言句子） | 难以精确检索 |
| 无结构化分类 | 偏好、事实、任务混在一起 |
| 无置信度标记 | 推断的和明确的记忆同等权重 |
| 无过期机制 | 过时记忆持续影响输出 |
| 用户可控性有限 | 只能查看和删除，不能编辑 |

---

### 6.4 LangGraph 的状态与记忆管理

#### 6.4.1 核心概念区分

LangGraph 明确区分了两个层次 [S015]：

| 概念 | 对应 | 生命周期 | 存储位置 |
|------|------|----------|----------|
| **Thread State** | Working Memory | 单次对话/任务 | Checkpointer |
| **Memory Store** | Long-term Memory | 跨对话持久 | Namespace Store |

#### 6.4.2 Thread State (Short-term Memory)

```python
# Thread state 是 agent 的"工作台"
class AgentState(TypedDict):
    messages: list[BaseMessage]     # 对话历史
    current_task: str               # 当前任务
    tool_results: list              # 工具结果
    plan: list[str]                 # 任务计划
    scratchpad: str                 # 工作草稿
```

- 每个 thread (对话线程) 有独立的 state
- State 通过 Checkpointer 持久化
- 支持时间旅行（回滚到之前的 checkpoint）
- 对话结束后 state 可保留但不主动注入其他对话

#### 6.4.3 Memory Store (Long-term Memory)

```python
# Memory store 是跨对话的持久知识
memory = MemoryStore(namespace=["user", "preferences"])
memory.put(key="diet", value={"type": "vegetarian", "since": 2020})
memory.put(key="coding_style", value={"language": "python", "framework": "fastapi"})

# 在 agent 运行时检索
user_prefs = memory.search(namespace=["user", "preferences"], query="food")
```

- 以 JSON documents 形式存储在 namespace 下
- 支持语义搜索和精确查询
- Agent 运行时可读写（动态更新）
- 可跨 thread 共享

#### 6.4.4 LangGraph 对 Context Assembly 的启发

| LangGraph 概念 | 对硬件 Context Compiler 的映射 |
|----------------|-------------------------------|
| Thread State | 当前任务的 working memory |
| Checkpointer | 任务中断后的状态恢复 |
| Memory Store | 用户长期偏好和习惯库 |
| Namespace | 不同类型记忆的隔离分区 |
| Graph State Reducer | 多来源信息的合并策略 |

---

### 6.5 MCP 在 Context Pipeline 中的角色

#### 6.5.1 MCP 定位

MCP (Model Context Protocol) 不是记忆系统，而是 context 的**接入层** [S014]：

```
┌───────────────────────────────────┐
│        AI Application             │
│  (Claude Code / Cursor / Agent)   │
└───────────────┬───────────────────┘
                │ MCP Protocol
┌───────────────┼───────────────────┐
│         MCP Layer                  │
├───────────────────────────────────┤
│  Tools: 调用外部系统执行动作       │
│  Resources: 读取外部数据作 context │
│  Prompts: 获取模板化的 prompt 片段 │
└───────────────┬───────────────────┘
                │
┌───────────────┼───────────────────┐
│  External Systems                  │
│  (数据库, API, 文件系统, 日历...) │
└───────────────────────────────────┘
```

#### 6.5.2 MCP 三大原语与 Context 的关系

| MCP 原语 | Context 角色 | 示例 |
|----------|-------------|------|
| **Tools** | 动态获取新数据，结果回填为 context | 调用搜索 API → 结果进入 prompt |
| **Resources** | 提供可被读取的外部数据源 | 读取数据库记录作为 context |
| **Prompts** | 提供预定义的 prompt 模板片段 | 获取领域专用的 system prompt 片段 |

#### 6.5.3 MCP 对硬件 Context 管理的意义

在智能硬件场景中，MCP 可以作为：
- 传感器数据的标准化接入协议
- 外部服务（日历、消息、地图）的统一访问层
- 不同硬件设备间共享 context 的标准

---

### 6.6 Anthropic 的 Context Engineering 原则

Anthropic 官方工程博客 [S012] 提出的核心框架：

#### 核心定义

> Context engineering 是"curating and maintaining the optimal set of tokens during LLM inference"——在 LLM 推理时策展和维护最优 token 集。

#### 指导原则

> 找到"the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome"——最大化目标结果概率的最小高信号 token 集。

#### 五大策略

| 策略 | 描述 | 适用场景 |
|------|------|----------|
| **System Prompt 结构化** | 用 XML/Markdown 标签分区组织 | 所有 agent |
| **Tool 精简设计** | 自包含、容错、明确用途，避免功能重叠 | tool-use agent |
| **Few-shot 示范** | 精选多样化典型示例替代详尽规则描述 | 行为对齐 |
| **Just-in-time 检索** | 用轻量标识符（路径/URL）按需加载数据 | 大型知识库 |
| **长任务管理** | Compaction + 结构化笔记 + Sub-agent | 长时间运行 |

---

### 6.7 通用 Prompt Assembly 模板

综合以上案例研究，提炼出通用 Prompt Assembly 分层模板：

#### 软件 Agent 版本

```
┌─ Layer 1: System Policy ─────────────────────────────┐
│  Agent 身份、能力范围、行为约束、输出格式              │
│  [Token: ~5%, 稳定, 每次调用必须包含]                 │
└───────────────────────────────────────────────────────┘
┌─ Layer 2: Project Rules ─────────────────────────────┐
│  项目规则、代码规范、技术栈约束                        │
│  [Token: ~10%, 稳定, 项目级常驻]                      │
└───────────────────────────────────────────────────────┘
┌─ Layer 3: User Profile & Memory ─────────────────────┐
│  用户偏好、历史反馈、跨会话记忆                        │
│  [Token: ~5%, 半稳定, 按相关性选择性注入]             │
└───────────────────────────────────────────────────────┘
┌─ Layer 4: Conversation History ──────────────────────┐
│  近期对话轮次（可被 compaction 压缩）                  │
│  [Token: ~20%, 动态, FIFO + 压缩]                    │
└───────────────────────────────────────────────────────┘
┌─ Layer 5: Retrieved Context ─────────────────────────┐
│  RAG 检索结果、相关代码、文档片段                      │
│  [Token: ~30%, 动态, 按 relevance 排序截断]           │
└───────────────────────────────────────────────────────┘
┌─ Layer 6: Tool Results ──────────────────────────────┐
│  工具调用返回的结果（可被 clearing 策略清除）          │
│  [Token: ~20%, 动态, 最新优先]                       │
└───────────────────────────────────────────────────────┘
┌─ Layer 7: Current Task ──────────────────────────────┐
│  当前用户请求 + 任务约束 + 安全红线重申                │
│  [Token: ~10%, 动态, 必须在最后（Recency Bias）]      │
└───────────────────────────────────────────────────────┘
```

#### 智能硬件版本

```
┌─ Layer 1: System Policy ─────────────────────────────┐
│  设备角色、安全约束、输出通道定义                      │
│  [Token: ~5%, 稳定]                                   │
└───────────────────────────────────────────────────────┘
┌─ Layer 2: Device Identity & Capabilities ────────────┐
│  设备类型、可用传感器、可用输出、当前约束              │
│  [Token: ~5%, 半稳定]                                 │
└───────────────────────────────────────────────────────┘
┌─ Layer 3: User Long-term Profile ────────────────────┐
│  用户习惯、偏好、人际关系、隐私设置                    │
│  [Token: ~10%, 稳定, 按相关性选择性注入]              │
└───────────────────────────────────────────────────────┘
┌─ Layer 4: Current Scene ─────────────────────────────┐
│  当前时间、地点、活动、在场人物、环境状态              │
│  [Token: ~15%, 动态, 高频刷新]                       │
└───────────────────────────────────────────────────────┘
┌─ Layer 5: Recent Events ─────────────────────────────┐
│  最近 N 个相关事件摘要                                │
│  [Token: ~15%, 动态, 时间衰减]                       │
└───────────────────────────────────────────────────────┘
┌─ Layer 6: Retrieved Memories ────────────────────────┐
│  按 Context Ranker 排序的相关记忆                     │
│  [Token: ~20%, 动态, 按 score 截断]                  │
└───────────────────────────────────────────────────────┘
┌─ Layer 7: Device State ──────────────────────────────┐
│  电量、网络、可执行动作列表                            │
│  [Token: ~5%, 动态]                                   │
└───────────────────────────────────────────────────────┘
┌─ Layer 8: Task + Safety Constraints ─────────────────┐
│  触发条件/用户请求 + 安全红线 + 输出格式              │
│  [Token: ~10%, 动态, 必须在最后]                     │
└───────────────────────────────────────────────────────┘
```

---

### 6.8 Token Budget 分配与管理

#### 预算分配原则

```
Total Budget: N tokens (建议使用 ≤70% 容量，参见 Context Cliff 现象)

Software Agent:                    Hardware Agent:
├── System + Rules:    15%         ├── System + Device:    10%
├── Memory/Profile:     5%         ├── User Profile:       10%
├── History:           20%         ├── Current Scene:      15%
├── Retrieved:         30%         ├── Recent Events:      15%
├── Tool Results:      20%         ├── Retrieved Memory:   20%
└── Task + Reserve:    10%         ├── Device State:        5%
                                   └── Task + Safety:      10%
                                       (Reserve: 15%)
```

#### Budget 超出时的降级策略

| 优先级 | 操作 | 触发条件 |
|--------|------|----------|
| 1 | 压缩对话历史/事件历史 | 超出 soft limit (70%) |
| 2 | 截断低分检索结果 | 超出 75% |
| 3 | 清除旧工具结果/传感器数据 | 超出 80% |
| 4 | 压缩记忆为摘要 | 超出 85% |
| 5 | 只保留 System + Task + Safety | 超出 90% (紧急模式) |

---

### 6.9 Prompt 污染防护

| 风险类型 | 描述 | 软件系统的缓解策略 | 硬件适用性 |
|----------|------|-------------------|-----------|
| 记忆误召回 | 检索到无关记忆 | 提高 relevance threshold | 高 — 传感器噪声更多 |
| 过时信息 | 旧记忆覆盖新事实 | 加权 recency | 高 — 环境持续变化 |
| 冲突信息 | 多源记忆矛盾 | 标注来源+时间戳 | 极高 — 多传感器冲突 |
| 隐私泄漏 | 敏感信息进入不当场景 | Privacy filter | 极高 — 拍摄/录音风险 |
| 注入攻击 | 外部内容注入恶意指令 | 内容隔离+标签标记 | 中 — 语音注入可能 |
| Token 浪费 | 低价值内容挤占预算 | 压缩/丢弃 | 高 — 传感器数据冗余 |

## 7. 对智能硬件 Context 管理的启发

### 可直接迁移的原则

| 软件 Agent 机制 | 硬件 Context Compiler 对应 |
|----------------|---------------------------|
| Claude Code 的 Compaction | 传感器历史的压缩策略 |
| Context Awareness (token budget 追踪) | 硬件设备的算力/token 预算感知 |
| System Reminder 注入 | 安全约束的周期性重申 |
| CLAUDE.md 层级规则 | 设备级规则 → 场景级规则 → 用户级规则 |
| Auto Memory 分类存储 | 分层记忆系统的具体分类 |
| Sub-agent Delegation | 端侧预处理 → 云端深度推理 |
| MCP Tools/Resources | 传感器数据和外部服务的标准化接入 |
| LangGraph Thread State | 单次任务的 working memory |
| LangGraph Memory Store | 跨任务的长期记忆库 |

### 硬件特有的新需求

| 需求 | 软件中无对应 | 原因 |
|------|-------------|------|
| 连续流切分 | 软件输入天然离散 | 传感器数据是连续的 |
| 多模态融合 | 主要处理文本 | 视觉+语音+位置+动作 |
| 打扰代价评估 | 输出即回答 | 错误输出可能造成社交尴尬 |
| 物理安全约束 | 纯数字环境 | 机器人动作有物理风险 |
| 旁人隐私保护 | 只涉及用户自己 | 设备可能拍摄/录到他人 |
| 极低延迟要求 | 可接受 1-5 秒 | 实时场景需 <500ms |

## 8. 与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| Phase 1 | 承接 context 类型分类和 12 个行为特性，本阶段通过案例验证 |
| → Phase 3 | Claude Auto Memory 和 LangGraph Memory Store 的设计延伸 |
| → Phase 5 | 本阶段的 Token Budget 模板直接指导硬件记忆架构的 context 配额 |
| → Phase 6 | 通用 Prompt Assembly 模板是 Context Compiler 的核心输入 |

## 9. 尚不确定或证据不足的问题

1. **Claude Code 的 Compaction 具体保留什么？** — 官方说"summarizes earlier parts"但未公开摘要算法细节 [NEEDS_CITATION]
2. **Cursor 的语义索引精度** — 索引如何处理动态代码（频繁修改的文件）？重建索引的频率？ [NEEDS_CITATION]
3. **ChatGPT Memory 的检索机制** — 从几百条记忆中如何选择相关条目注入 prompt？语义匹配？关键词？全部注入？ [NEEDS_CITATION]
4. **LangGraph Memory Store 的生产规模表现** — 在上万条记忆规模下的检索延迟和准确性？ [NEEDS_CITATION]
5. **MCP 在低带宽/离线环境下的适用性** — 智能硬件可能频繁断网，MCP 的容错机制？ [NEEDS_CITATION]

## 10. 下一阶段建议

Phase 3 应该：

1. **深入 MemGPT/Letta 的虚拟上下文管理** — 它如何用 OS 内存层级类比管理 LLM context
2. **对比 Mem0、Zep/Graphiti 的记忆存储方案** — 不同框架的数据结构和检索策略差异
3. **研究 CoALA 的认知架构** — 它如何抽象 agent 的 memory、reasoning、action 关系
4. **评估 Generative Agents 的记忆系统** — Stanford 的虚拟社区如何实现记忆的写入/检索/反思
5. **建立框架能力矩阵** — 为后续硬件记忆架构设计提供选型依据
