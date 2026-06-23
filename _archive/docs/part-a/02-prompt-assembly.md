# 阶段 2：拆解 Prompt Assembly 机制

## 目标

深入研究"高质量 prompt 是如何被拼出来的"。

这一步非常重要，因为它是从软件应用过渡到智能硬件的桥梁。

## 研究问题

1. 一次模型调用前，系统如何决定把哪些内容放进 prompt？
2. Prompt 里的内容应该按什么顺序排列？
3. 当前任务、历史记忆、工具结果、用户偏好之间如何排序？
4. 怎么避免无关记忆污染 prompt？
5. 怎么在 token budget 受限时取舍 context？

## 通用 Prompt Assembly 模板

```
[System Policy]
[Device / Agent Identity]
[Stable User Preferences]
[Current Task]
[Current Scene / State]
[Relevant Retrieved Memories]
[Tool / Sensor Results]
[Constraints]
[Output Format]
```

### 软件 Agent 版本

```
[System Policy]
[Project Rules]
[User Request]
[Relevant Files]
[Recent Conversation]
[Tool Results]
[Coding Constraints]
[Output Format]
```

### 智能硬件版本

```
[System Policy]
[Device Role]
[User Long-term Preferences]
[Current Scene Summary]
[Recent Sensor Events]
[Relevant Episodic Memories]
[Device State]
[Available Actions]
[Safety / Privacy Constraints]
[Response / Action Format]
```

## Context Ranker 设计

### 排序维度

| 维度 | 定义 | 权重考量 |
|------|------|----------|
| Task Relevance | 与当前任务的相关性 | 最高权重 |
| Recency | 时间新鲜度 | 近期优先 |
| User Specificity | 与当前用户的匹配度 | 个性化加分 |
| Confidence | 信息可信度 | 低置信度降权 |
| Actionability | 能否直接指导行动 | 可执行内容加分 |
| Token Cost | 占用 token 数量 | 长内容降权 |

### Token Budget 分配原则

```
Total Budget: N tokens
├── System Policy:        ~5%   (固定)
├── Identity & Rules:     ~10%  (固定)
├── Current Task:         ~20%  (动态)
├── Retrieved Context:    ~35%  (动态, 按相关性截断)
├── Tool Results:         ~20%  (动态)
└── Output Reserve:       ~10%  (固定)
```

## Prompt 污染风险

| 风险类型 | 描述 | 缓解策略 |
|----------|------|----------|
| 记忆误召回 | 检索到与当前任务无关的记忆 | 提高 relevance threshold |
| 过时信息 | 旧信息覆盖新事实 | 加权 recency |
| 冲突信息 | 多条记忆互相矛盾 | 标注来源和时间戳 |
| 隐私泄漏 | 敏感信息进入不当场景 | privacy filter |
| Token 浪费 | 大量低价值内容占满窗口 | 压缩或摘要 |

## 预期产出

1. **Prompt Assembly 分层模板** — 软件版和硬件版
2. **Context Ranker 设计草案** — 评分维度和权重
3. **Token Budget 分配原则** — 不同组件的配额
4. **Prompt 污染与记忆误召回风险清单** — 问题与对策
