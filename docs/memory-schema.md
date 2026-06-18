# 记忆与事件 Schema

本文档定义事件、用户记忆、权限和生命周期的推荐数据结构。

## 设计原则

不建议只存自然语言，也不建议只存向量。每条记忆都应同时包含：

- 给模型看的自然语言摘要。
- 给系统使用的结构化字段。
- 可追溯证据。
- 时间范围。
- 置信度和重要度。
- 敏感等级与使用权限。
- 生命周期状态。

## Event Schema

结构化事件是从原始设备数据、App 行为、用户反馈或系统日志中清洗后的标准记录。

```json
{
  "event_id": "evt_101",
  "user_id": "user_123",
  "source": "smart_light",
  "event_type": "device.state_changed",
  "timestamp": "2026-06-10T22:45:00+08:00",
  "actor": {
    "type": "user",
    "id": "user_123"
  },
  "context": {
    "location": "home.bedroom",
    "scenario": "before_sleep",
    "device_id": "light_bedroom_01"
  },
  "payload": {
    "room": "bedroom",
    "brightness_before": 70,
    "brightness_after": 20,
    "color_temperature_after": "warm"
  },
  "sensitivity": "low",
  "consent_status": "granted",
  "reliability": 0.92,
  "created_at": "2026-06-10T22:45:03+08:00"
}
```

## Memory Schema

用户记忆是从事件或用户显式反馈中沉淀出的长期信息。

```json
{
  "memory_id": "mem_001",
  "user_id": "user_123",
  "type": "preference.environment.light",
  "summary": "用户睡前偏好卧室灯光低亮度、暖色温。",
  "structured_value": {
    "room": "bedroom",
    "brightness": "low",
    "color_temperature": "warm",
    "time_window": "before_sleep"
  },
  "evidence": [
    {
      "event_id": "evt_101",
      "source": "smart_light",
      "timestamp": "2026-06-10T22:45:00+08:00"
    }
  ],
  "confidence": 0.84,
  "importance": 0.72,
  "last_seen": "2026-06-15T22:38:00+08:00",
  "valid_from": "2026-05-01",
  "valid_until": null,
  "sensitivity": "low",
  "allowed_scenarios": ["smart_home", "sleep_assistant"],
  "denied_scenarios": ["public_voice_broadcast"],
  "status": "active",
  "conflicts_with": [],
  "created_at": "2026-06-01T10:00:00+08:00",
  "updated_at": "2026-06-15T22:40:00+08:00"
}
```

## 关键字段

| 字段 | 作用 |
|---|---|
| `type` | 记忆类型，支持分类检索和权限策略 |
| `summary` | 给模型看的简短自然语言 |
| `structured_value` | 给系统、工具和规则引擎使用的结构化值 |
| `evidence` | 记忆来源，支持解释和审计 |
| `confidence` | 当前可信度 |
| `importance` | 对未来任务的潜在价值 |
| `last_seen` | 最近一次被验证的时间 |
| `valid_until` | 过期时间 |
| `sensitivity` | 敏感等级 |
| `allowed_scenarios` | 允许使用场景 |
| `denied_scenarios` | 禁止使用场景 |
| `status` | 生命周期状态 |
| `conflicts_with` | 冲突记忆列表 |

## 敏感等级

| 等级 | 数据类型 | 默认策略 |
|---|---|---|
| `low` | 设备偏好、亮度、音量、常用模式 | 可用于个性化 |
| `medium` | 位置、作息、家庭场景、联系人关系 | 需场景授权和最小化使用 |
| `high` | 健康、财务、身份、儿童、私密对话 | 默认不进模型，需显式授权 |
| `forbidden` | 法律禁止或用户拒绝的数据 | 不采集、不推断、不使用 |

## 生命周期状态

| 状态 | 含义 |
|---|---|
| `active` | 当前可用 |
| `pending_confirmation` | 存在冲突或证据不足，需要确认 |
| `deprecated` | 已过期或长期未验证，不再主动使用 |
| `rejected` | 被用户或系统判定为错误，避免再次生成 |
| `deleted` | 用户删除，必须不可恢复或不可使用 |

## 记忆评分

候选记忆可使用综合分进入记忆库：

```text
memory_score =
  w1 * task_value
+ w2 * frequency
+ w3 * recency
+ w4 * stability
+ w5 * explicitness
+ w6 * user_feedback
- w7 * sensitivity_risk
- w8 * conflict_risk
```

初期建议采用保守进入规则：

- 用户明确表达的偏好优先进入记忆。
- 多次重复出现的行为可进入候选记忆。
- 单次偶发事件默认不进入长期记忆。
- 高敏数据必须显式授权。
- 与旧记忆冲突时进入待确认状态，而不是直接覆盖。

## 冲突处理示例

```json
{
  "old_memory": "用户早晨偏好喝咖啡",
  "new_signal": "用户最近不希望推荐咖啡",
  "resolution": "新信息优先，旧记忆降权",
  "status": "active_with_recent_override",
  "suggested_behavior": "近期不主动推荐咖啡，必要时询问是否为临时偏好变化"
}
```
