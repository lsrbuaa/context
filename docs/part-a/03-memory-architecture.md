# 阶段 3：研究多级记忆架构

## 目标

从"context window 里放什么"扩展到"context window 外应该如何组织记忆"。

## 研究问题

1. 哪些记忆应该进入 working memory？
2. 哪些事件应该被写入 episodic memory？
3. 多次 episode 如何归纳成 semantic profile？
4. 哪些习惯应该变成 procedural memory？
5. 每条记忆是否需要来源、置信度、过期时间？
6. 记忆冲突时是覆盖、降权、并存还是询问用户？

## 六层记忆模型

| 记忆层级 | 定义 | 软件应用例子 | 智能硬件例子 |
|----------|------|-------------|-------------|
| Raw Buffer | 原始输入缓存 | 原始对话、日志、文件片段 | 原始音频、图像帧、传感器数据 |
| Working Memory | 当前任务工作状态 | 当前对话、当前编辑任务 | 当前场景、当前用户动作、设备状态 |
| Episodic Memory | 具体事件记忆 | 某次会话、某次任务结果 | "昨晚用户在厨房找钥匙" |
| Semantic Memory | 抽象事实与画像 | 用户偏好、项目规则 | 用户习惯、人物关系、常去地点 |
| Procedural Memory | 流程和技能 | debug 流程、代码规范 | "会议中只震动提醒""用户回家后先开灯" |
| Governance Memory | 权限、来源、可信度 | 用户授权、来源记录 | 传感器来源、置信度、隐私权限、过期时间 |

## 记忆架构图

```
┌─────────────────────────────────────────────────────┐
│                  Context Window                      │
│  (Working Memory: 当前任务所需的活跃上下文)           │
└───────────────────────┬─────────────────────────────┘
                        │ retrieve / write
┌───────────────────────┼─────────────────────────────┐
│              External Memory Store                    │
├─────────────────────────────────────────────────────┤
│  Episodic Memory    │ 事件、对话、体验片段           │
│  Semantic Memory    │ 事实、画像、关系、偏好         │
│  Procedural Memory  │ 规则、流程、习惯模式           │
│  Governance Memory  │ 来源、置信度、权限、过期策略    │
└─────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────┐
│              Raw Buffer / Archive                     │
│  原始数据、日志、传感器流 (可检索但不常驻内存)        │
└─────────────────────────────────────────────────────┘
```

## 记忆写入策略

| 事件类型 | 写入层级 | 写入条件 |
|----------|----------|----------|
| 用户显式偏好声明 | Semantic | 立即写入 |
| 任务完成结果 | Episodic | 任务结束时 |
| 重复行为模式 | Procedural | 出现 N 次以上 |
| 工具调用结果 | Working → 可能 Episodic | 当前任务结束后评估 |
| 传感器原始数据 | Raw Buffer | 持续写入，定期清理 |
| 用户纠正 | Semantic + Governance | 立即更新 |

## 记忆更新机制

### 合并策略

| 场景 | 策略 |
|------|------|
| 新记忆与旧记忆一致 | 更新时间戳，增加置信度 |
| 新记忆与旧记忆冲突 | 标记冲突，优先新记忆，保留旧记忆备查 |
| 旧记忆长期未被召回 | 降权或归档 |
| 用户主动删除 | 立即删除，记录删除事件 |

### 遗忘机制

- **时间衰减**: 长期未访问的记忆逐步降权
- **空间衰减**: 与当前场景距离远的记忆降权
- **显式清理**: 用户或策略触发的记忆删除
- **压缩归纳**: 多条相似 episodic 记忆压缩为一条 semantic 记忆

## 记忆对象 JSON Schema 初稿

```json
{
  "memory_id": "string",
  "type": "episodic | semantic | procedural | governance",
  "content": "string",
  "created_at": "ISO 8601",
  "last_accessed": "ISO 8601",
  "access_count": "integer",
  "confidence": "0.0 - 1.0",
  "source": {
    "type": "user_explicit | inferred | sensor | tool",
    "device": "string",
    "session_id": "string"
  },
  "context": {
    "location": "string | null",
    "activity": "string | null",
    "people": ["string"],
    "time_of_day": "string | null"
  },
  "governance": {
    "privacy_level": "public | private | sensitive",
    "expires_at": "ISO 8601 | null",
    "deletable_by_user": true,
    "requires_confirmation": false
  },
  "embeddings": {
    "text": "vector",
    "spatial": "vector | null",
    "temporal": "vector | null"
  }
}
```

## 预期产出

1. **六层记忆架构图** — 各层关系和数据流
2. **记忆写入策略表** — 何时写入、写到哪层
3. **记忆更新 / 合并 / 遗忘机制** — 生命周期管理
4. **记忆对象 JSON Schema 初稿** — 统一数据结构
