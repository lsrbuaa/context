# 阶段 5：研究智能硬件的 Context Assembly

## 目标

设计一个"硬件版 Context Compiler"。

它要解决的问题是：每次设备准备调用 LLM / VLM / VLA 前，如何从当前场景、近期事件、长期记忆、设备状态、用户习惯中选择最有用的内容，拼成高质量输入。

## Context Assembly Pipeline

```
1. Capture        采集视觉、语音、位置、设备状态
       ↓
2. Normalize      转成统一结构化对象
       ↓
3. Segment        切分为事件、任务、场景状态
       ↓
4. Write          决定是否写入短期 / 长期记忆
       ↓
5. Retrieve       根据当前任务召回相关记忆
       ↓
6. Rank           按相关性、时效性、空间性、置信度、隐私风险排序
       ↓
7. Pack           在 token budget 内拼接 prompt
       ↓
8. Act            调用 LLM / VLM / VLA / 工具 / 设备动作
       ↓
9. Feedback       根据用户反馈更新记忆
```

## Context Ranker 评分模型

```
ContextScore =
    TaskRelevance
  + Recency
  + SpatialRelevance
  + UserSpecificity
  + Confidence
  + Actionability
  - PrivacyRisk
  - InterruptionCost
  - TokenCost
```

### 各维度详细定义

| 维度 | 定义 | 取值范围 | 权重建议 |
|------|------|----------|----------|
| TaskRelevance | 与当前推理任务的语义相关性 | 0-1 | 0.30 |
| Recency | 时间衰减函数，越新越高 | 0-1 | 0.15 |
| SpatialRelevance | 与当前位置/场景的空间匹配 | 0-1 | 0.15 |
| UserSpecificity | 针对当前用户的个性化程度 | 0-1 | 0.10 |
| Confidence | 信息来源的可信度 | 0-1 | 0.10 |
| Actionability | 能否直接驱动输出动作 | 0-1 | 0.10 |
| PrivacyRisk | 包含隐私信息的风险 | 0-1 | -0.05 |
| InterruptionCost | 打扰用户的代价 | 0-1 | -0.05 |
| TokenCost | 归一化的 token 消耗 | 0-1 | -0.05 |

## 硬件 Prompt 拼接模板

```
[System Policy]
  - 设备角色定义
  - 安全约束
  - 输出格式要求

[Device Identity]
  - 设备类型 (眼镜/耳机/机器人)
  - 可用输出通道 (语音/显示/震动/动作)
  - 当前能力约束

[User Profile]
  - 长期偏好
  - 交互风格
  - 隐私设置

[Current Scene]
  - 时间、地点、活动
  - 在场人物
  - 环境状态

[Recent Events]
  - 最近 N 个相关事件摘要
  - 按时间倒序

[Retrieved Memories]
  - 按 ContextScore 排序的相关记忆
  - 截断至 budget 允许范围

[Device State]
  - 电量、网络、传感器状态
  - 可执行动作列表

[Task / Trigger]
  - 用户请求 或 系统触发条件
  - 期望输出类型

[Safety Constraints]
  - 不可执行动作
  - 隐私红线
  - 打扰限制
```

## 不同硬件形态的 Context 策略对比

| 维度 | AI 眼镜 | AI 耳机 | AI Pin | 机器人 |
|------|---------|---------|--------|--------|
| 主要输入 | 视觉 + 语音 | 语音 | 语音 + 位置 | 视觉 + 触觉 |
| Context 刷新频率 | 高 (视觉流) | 中 (对话流) | 低 (事件驱动) | 高 (动作循环) |
| Token Budget 压力 | 高 | 低 | 低 | 极高 |
| 隐私敏感度 | 极高 | 高 | 中 | 中 |
| 主动触发频率 | 中 | 高 | 低 | 高 |
| 延迟要求 | <500ms | <300ms | <2s | <100ms |
| 记忆检索重点 | 空间+视觉 | 对话+人物 | 事件+时间 | 动作+物体 |

## 预期产出

1. **Context Assembly Pipeline** — 9 步完整流程
2. **Context Ranker 评分模型** — 维度、权重、计算方式
3. **硬件 Prompt 拼接模板** — 通用模板
4. **不同硬件形态的 Context 策略对比** — 差异化设计
