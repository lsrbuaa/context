# 阶段 4：把输入源从软件扩展到智能硬件

## 目标

研究当 context 输入源从文本、代码、文件变成多模态传感器时，整个 context 管理链路如何变化。

## 范式迁移对比

| 维度 | 软件 Agent | 智能硬件 Agent |
|------|-----------|---------------|
| 输入 | prompt、文件、代码、工具 | 视觉、语音、动作、位置、设备状态 |
| 记忆对象 | 对话、文档、项目规则 | 场景、事件、习惯、空间、人物 |
| 触发方式 | 用户主动请求 | 用户请求 + 环境触发 + 主动判断 |
| 输出 | 文本、代码、工具调用 | 语音、显示、震动、动作、执行 |
| 风险 | 错误回答、代码错误 | 物理风险、隐私风险、社交打扰 |
| 核心挑战 | token budget 与检索质量 | 多模态噪声、隐私、低延迟、主动服务 |

## 智能硬件输入源分类

| 输入源 | 可能转化成的 Context |
|--------|---------------------|
| 麦克风 | 用户意图、对话内容、环境声音、情绪线索 |
| 摄像头 | 物体、人物、空间关系、用户动作 |
| IMU / 姿态 | 走路、跑步、抬头、低头、静止 |
| GPS / Wi-Fi / 蓝牙 | 地点、场景、附近设备 |
| 屏幕 / App 状态 | 用户当前数字任务 |
| 电量 / 网络 / 温度 | 设备可用性约束 |
| 日历 / 消息 / 待办 | 外部任务上下文 |
| 机器人关节 / 末端执行器状态 | 物理行动约束 |

## 研究问题

1. 多模态输入如何被转成统一的 context object？
2. 连续传感器流如何切分成事件？
3. 视觉和语音信息冲突时如何处理？
4. 哪些感知结果只进入 working memory，哪些可以进入 long-term memory？
5. 低置信度传感器结果是否可以进入 prompt？
6. 端侧处理和云侧处理如何分工？

## 事件切分机制

### 连续流 → 离散事件

```
原始传感器流
    ↓
┌──────────────────────────┐
│  Signal Processing       │  降噪、对齐、同步
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│  Activity Recognition    │  识别动作、场景、对话
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│  Event Segmentation      │  切分为离散事件
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│  Context Object Creation │  结构化为 context object
└──────────────────────────┘
```

### 切分触发条件

| 触发类型 | 示例 |
|----------|------|
| 场景变化 | 从办公室走到会议室 |
| 活动变化 | 从打字切换到对话 |
| 人物变化 | 新人加入 / 有人离开 |
| 时间跨度 | 超过 N 分钟无变化 |
| 显式事件 | 用户说"开始开会" |
| 设备事件 | 日历提醒触发 |

## 端侧 vs 云侧处理分工

| 处理阶段 | 端侧 | 云侧 |
|----------|------|------|
| 原始信号采集 | ✓ | |
| 降噪与预处理 | ✓ | |
| 简单模式识别 | ✓ | |
| 复杂场景理解 | | ✓ |
| 记忆检索 | 部分 | ✓ |
| LLM 推理 | | ✓ (或端侧小模型) |
| 隐私过滤 | ✓ | |
| 动作执行 | ✓ | |

## 多模态 Context Object 标准字段

```json
{
  "event_id": "string",
  "timestamp": "ISO 8601",
  "duration_ms": "integer",
  "modalities": {
    "visual": {
      "scene_description": "string",
      "objects": ["string"],
      "people": [{"id": "string", "confidence": "float"}],
      "spatial_relations": "string"
    },
    "audio": {
      "transcript": "string",
      "speaker_id": "string",
      "emotion": "string",
      "ambient_noise_level": "float"
    },
    "motion": {
      "activity": "string",
      "posture": "string",
      "velocity": "float"
    },
    "location": {
      "type": "string",
      "coordinates": "object | null",
      "semantic_place": "string"
    }
  },
  "confidence": "float",
  "processing_level": "raw | processed | verified",
  "privacy_flags": ["contains_face", "contains_voice", "public_space"]
}
```

## 预期产出

1. **智能硬件输入 → Context Object 映射表**
2. **事件切分机制设计**
3. **多模态 Context 标准字段**
4. **智能硬件 Context Pipeline 图**
