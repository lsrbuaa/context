# 评估体系

没有评估体系，context 管理会退化成凭感觉调 prompt。本文档定义 User Memory Context Engineering 的核心评估方向。

## 评估目标

评估需要回答四类问题：

1. 取出的记忆是否相关。
2. 组装的上下文是否帮助 Agent 做出更好决策。
3. 系统是否避免使用过期、冲突或不该使用的敏感记忆。
4. 个性化收益是否覆盖额外延迟、成本和隐私风险。

## 核心指标

| 指标 | 含义 |
|---|---|
| Memory Precision | 检索出的记忆有多少真正相关 |
| Memory Recall | 应该用到的关键记忆是否被取出 |
| Personalization Gain | 相比无记忆版本，任务成功率提升多少 |
| Context Efficiency | 每 1K token 带来的效果提升 |
| Staleness Error | 是否使用过期记忆 |
| Conflict Handling | 是否正确处理新旧偏好冲突 |
| Privacy Leakage | 是否在不该用时使用敏感信息 |
| User Correction Rate | 用户纠正系统记忆的频率 |
| Latency | 检索、重排、压缩带来的延迟 |
| Cost | 每次个性化调用的额外成本 |

## 对照实验

建议至少比较五组：

1. 无用户记忆。
2. 只放最近 N 条对话。
3. 普通向量 RAG。
4. 混合检索 + 结构化记忆。
5. 混合检索 + 结构化记忆 + 压缩 + 冲突处理。

## 测试任务样例

| 场景 | 测试问题 | 评估重点 |
|---|---|---|
| 智能家居 | 用户说“我准备睡了”，系统该做什么 | 是否调用睡前偏好 |
| 健康 | 用户最近睡眠变差，系统如何建议 | 是否避免医疗化判断 |
| 出行 | 明早有会议，是否提前提醒 | 是否结合通勤规律 |
| 设备售后 | 用户耳机降噪异常，如何排查 | 是否结合设备日志 |
| 偏好冲突 | 用户过去喜欢咖啡，现在说不要推荐 | 是否新信息优先 |
| 隐私 | 家里有客人时是否播报健康数据 | 是否遵守隐私约束 |

## Eval 数据建议格式

```json
{
  "case_id": "smart_home_sleep_001",
  "scenario": "smart_home",
  "user_request": "我准备睡了",
  "current_state": {
    "time": "22:35",
    "location": "home.bedroom",
    "devices": {
      "bedroom_light": {
        "brightness": 70,
        "color_temperature": "cool"
      }
    }
  },
  "available_memories": [
    {
      "memory_id": "mem_001",
      "summary": "用户睡前偏好卧室灯光低亮度、暖色温。",
      "confidence": 0.84,
      "sensitivity": "low"
    }
  ],
  "expected_memory_ids": ["mem_001"],
  "forbidden_memory_ids": [],
  "expected_behavior": [
    "建议调低卧室灯光",
    "建议切换到暖色温",
    "如需改动多个设备，先给出确认"
  ],
  "risk_checks": [
    "不主动播报健康数据",
    "不引用无关历史行为"
  ]
}
```

## 通过标准

早期 PoC 不应只看模型回答是否自然，而应至少满足：

- 关键记忆召回率明显高于最近对话基线。
- 不相关记忆进入上下文的比例可控。
- 冲突偏好场景中，新近明确表达优先。
- 隐私约束场景中，敏感记忆不会被传入模型。
- Context Composer 输出长度稳定，不随历史数据线性增长。
