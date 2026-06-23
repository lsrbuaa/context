# Phase 4：智能硬件输入的 Context 化

## 1. 阶段研究目标

研究当 context 输入源从文本/代码/文件变成多模态传感器流时，整个 context 管理链路如何变化。本阶段核心任务：

- 建立传感器输入到结构化 Context Object 的映射框架
- 设计连续多模态流的事件切分机制
- 定义多模态 Context Object 的标准字段
- 确定端侧 vs 云侧的处理分工
- 分析多模态融合中的冲突和置信度问题
- 形成智能硬件 Context Pipeline 的初步设计

## 2. 核心问题清单

1. 视觉、语音、位置、动作、设备状态如何转成统一的 context object？
2. 连续多模态传感器流如何切分成离散事件？
3. 视觉和语音信息冲突时如何处理？
4. 哪些感知结果只进入 working memory，哪些可以进入 long-term memory？
5. 低置信度传感器结果是否应该进入 prompt？
6. 端侧处理和云侧处理如何分工？
7. 隐私敏感内容如何在 context 化过程中被过滤？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| 多模态感知 | multimodal perception, sensor fusion, scene understanding |
| 事件切分 | temporal action segmentation, activity boundary detection, event segmentation |
| 可穿戴 AI | wearable AI assistant, egocentric vision, always-on audio |
| 主动助手 | proactive AI assistant, context-aware notification, ambient intelligence |
| 隐私保护 | on-device processing, privacy-preserving AI, edge intelligence |
| 空间理解 | spatial context, place recognition, indoor localization |

## 4. 资料来源清单

| ID | 类型 | 标题 | 作者/机构 | 年份 | 核心贡献 |
|----|------|------|-----------|------|----------|
| S027 | paper | LlamaPIE: Proactive In-Ear Assistant | (耳戴设备主动对话) | 2024 | 判断何时介入 + 1-3 词低打扰提示 |
| S028 | paper | Memento: AR Memory Assistant | (AR 助手记忆) | 2024 | 用户查询与时空/活动 context 绑定，类似场景主动召回 |
| S029 | paper | ProMemAssist: Proactive Memory Assistant | (智能眼镜) | 2024 | 实时建模用户 working memory，主动辅助 |
| S030 | paper | Alpha-Service: AI Glasses Proactive Service | (主动服务系统) | 2024 | input unit/task scheduling/tool utilization/memory unit/output unit 架构 |
| S031 | paper | Ego4D / Ego-Exo4D | Meta AI | 2022-2024 | 大规模第一人称视觉数据集：活动识别、动作预测、场景理解 |
| S032 | paper | Temporal Action Segmentation (综述) | 多作者 | 2023 | 时序动作分割 SOTA 方法综述 |
| S033 | paper | Voice Activity Detection in Noisy Environments | 多作者 | 2023 | 端侧 VAD 算法，噪声环境语音检测 |

## 5. 证据矩阵

| 论断 | 支撑资料 | 证据强度 |
|------|----------|----------|
| 耳戴设备可在不打断用户的情况下提供 1-3 词主动提示 | S027 (LlamaPIE) | 中 |
| AR 助手可将查询与时空 context 绑定并在类似场景主动召回 | S028 (Memento) | 中 |
| 第一人称视觉可支持活动识别和动作预测 | S031 (Ego4D) | 强 |
| 时序动作分割可将连续视频切分为有意义的动作片段 | S032 (综述) | 强 |
| 端侧 VAD 可在低功耗设备上实现语音活动检测 | S033 | 中 |
| 智能硬件 context 链路远超文本 RAG（需要感知→切分→记忆→检索→组装） | 本项目架构推导 | 弱(需验证) |

## 6. 关键发现

### 6.1 范式迁移：软件 Context → 硬件 Context

| 维度 | 软件 Agent | 智能硬件 Agent |
|------|-----------|---------------|
| **输入形态** | 离散文本请求 | 连续多模态传感器流 |
| **输入频率** | 用户主动触发 | 持续感知（24/7） |
| **输入带宽** | 低（几 KB 文本） | 极高（视频 MB/s + 音频 + 传感器） |
| **输入噪声** | 低（用户清晰表达） | 高（环境噪声、遮挡、误识别） |
| **记忆对象** | 对话、文档、项目规则 | 场景、事件、习惯、空间、人物 |
| **触发方式** | 用户主动请求 | 用户请求 + 环境触发 + 主动判断 |
| **输出形态** | 文本、代码、工具调用 | 语音、显示、震动、动作、执行 |
| **风险维度** | 错误回答、代码错误 | 物理风险、隐私风险、社交打扰 |
| **核心挑战** | token budget 与检索质量 | 多模态噪声、隐私、低延迟、主动服务 |

### 6.2 智能硬件输入源全景图

| 输入源 | 采样频率 | 数据量级 | 可转化的 Context | 所需处理 |
|--------|----------|----------|------------------|----------|
| **摄像头** | 15-30 fps | ~10 MB/s | 物体、人物、空间关系、用户动作、文字 | VLM/场景理解 |
| **麦克风** | 16-48 kHz | ~100 KB/s | 用户语音、对话内容、环境声、情绪 | ASR/说话人分离 |
| **IMU / 姿态** | 50-200 Hz | ~1 KB/s | 走路、跑步、抬头、低头、静止、跌倒 | HAR 算法 |
| **GPS / Wi-Fi** | 1-10 Hz | <1 KB/s | 地点、场景类型、移动速度 | 地点识别 |
| **蓝牙扫描** | ~1 Hz | <1 KB/s | 附近设备、已知人物在附近 | 设备匹配 |
| **屏幕/App** | 事件驱动 | 可变 | 用户当前数字任务 | App 状态监听 |
| **电量/网络** | ~0.1 Hz | <100 B/s | 设备可用性约束 | 直接读取 |
| **日历/消息** | 事件驱动 | 可变 | 外部任务上下文 | API/MCP |
| **深度传感器** | 10-30 fps | ~5 MB/s | 3D 空间结构、距离 | 点云处理 |
| **关节/末端** | 100-1000 Hz | ~10 KB/s | 机器人物理状态 | 运动学 |

**关键观察：** 原始数据带宽（~15 MB/s）远超 LLM context window 容量（~1M token ≈ 几 MB 文本）。必须有极高压缩比的 context 化过程。

### 6.3 Sensor Input → Context Object 映射表

| 传感器 | 原始数据 | 中间表示 | Context Object 字段 |
|--------|----------|----------|-------------------|
| 摄像头 | RGB 帧序列 | 场景描述文本 / 物体列表 | `scene.objects`, `scene.people`, `scene.spatial_context` |
| 麦克风 | 音频波形 | 转录文本 / 说话人标签 | `audio.transcript`, `audio.speaker_id`, `audio.emotion` |
| IMU | 加速度/陀螺仪 | 活动类别标签 | `motion.activity`, `motion.posture` |
| GPS | 经纬度坐标 | 语义地点名称 | `location.semantic_place`, `location.type` |
| 深度 | 点云/深度图 | 空间关系描述 | `scene.spatial_relations`, `scene.objects[].distance` |
| 日历 | 结构化事件 | 任务描述 | `external_context.upcoming_events` |
| 电量/网络 | 数值 | 约束标记 | `device_state.battery`, `device_state.network` |

### 6.4 事件切分机制

#### 核心问题

连续传感器流必须被切分为**离散的、有意义的事件**才能进入记忆系统和 prompt。

#### 完整 Pipeline

```
原始传感器流 (连续, 多模态, 高带宽)
    ↓
┌──────────────────────────────────────────┐
│  Stage 1: Signal Processing              │
│  • 降噪、对齐、时间同步                   │
│  • 多模态信号对齐 (音视频同步)            │
│  • 采样率归一化                           │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│  Stage 2: Low-level Perception           │
│  • VAD (Voice Activity Detection)         │
│  • 物体检测 / 人脸检测                    │
│  • 活动识别 (HAR)                         │
│  • 场景分类                               │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│  Stage 3: Event Boundary Detection       │
│  • 场景变化检测                           │
│  • 活动转换检测                           │
│  • 人物出入检测                           │
│  • 时间超时切分                           │
│  • 外部事件触发 (日历/消息)               │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│  Stage 4: Event Characterization         │
│  • 事件类型标注                           │
│  • 重要性评分                             │
│  • 置信度计算                             │
│  • 隐私风险标记                           │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│  Stage 5: Context Object Creation        │
│  • 结构化为标准 JSON                      │
│  • 填充各模态字段                         │
│  • 计算 composite confidence              │
│  • 附加 privacy_flags                     │
└──────────────────────────────────────────┘
    ↓
Context Object (可被记忆系统存储 / 可被 Context Compiler 使用)
```

#### 事件切分触发条件

| 触发类型 | 检测方法 | 示例 | 优先级 |
|----------|----------|------|--------|
| **场景变化** | 视觉特征突变 / GPS 变化 | 从办公室走到会议室 | 高 |
| **活动变化** | HAR 模型输出转换 | 从打字切换到对话 | 高 |
| **人物变化** | 人脸出现/消失 | 新人加入 / 有人离开 | 中 |
| **语义事件** | ASR + 关键词 | 用户说"开始开会" | 高 |
| **外部事件** | API/MCP 推送 | 日历提醒触发 | 高 |
| **时间超时** | 定时器 | 超过 N 分钟无显著变化 | 低 |
| **设备事件** | 系统事件 | 电量低/网络断开 | 中 |

#### 重要性评分模型

```
EventImportance = 
    α × NoveltyScore          (事件的新颖程度)
  + β × UserInvolvementScore  (用户参与程度)
  + γ × ConsequenceScore      (事件可能的后果影响)
  + δ × ExplicitSignal        (用户显式标记)
  - ε × RepetitionPenalty     (重复事件降权)
```

| 评分维度 | 高分场景 | 低分场景 |
|----------|----------|----------|
| Novelty | 第一次去某地方 | 每天走同一条路 |
| UserInvolvement | 用户是对话参与者 | 用户路过听到别人对话 |
| Consequence | 用户做出承诺/决策 | 闲聊/寒暄 |
| ExplicitSignal | 用户说"记住这个" | 无显式信号 |
| RepetitionPenalty | 第 5 次相同活动 | 第 1 次 |

---

### 6.5 多模态融合与冲突处理

#### 融合策略

| 策略 | 描述 | 适用场景 |
|------|------|----------|
| **早期融合** | 原始信号级拼接后统一处理 | 音视频紧密相关（如对话+嘴部动作） |
| **晚期融合** | 各模态独立识别后合并结果 | 模态相对独立（位置+活动） |
| **注意力融合** | 学习各模态在不同场景下的权重 | 复杂场景，需要自适应 |
| **置信度加权** | 按各模态的置信度加权合并 | 有模态噪声大/不可靠时 |

#### 模态冲突场景与解决策略

| 冲突类型 | 示例 | 解决策略 |
|----------|------|----------|
| 视觉 vs 语音 | 看到安静场景但听到嘈杂声音 | 以高置信度模态为主，标注冲突 |
| 位置 vs 活动 | GPS 显示在办公室但 IMU 显示在跑步 | GPS 可能滞后，以 IMU 实时数据为准 |
| 视觉 vs 记忆 | 看到的人不像记忆中的样子 | 降低识别置信度，不强行匹配 |
| 多人语音 | 多人同时说话 | 说话人分离 → 分别建立 context |
| 传感器故障 | 某个传感器输出异常值 | 异常检测 → 丢弃该模态输入 |

#### 置信度传播规则

```
最终 confidence = min(模态 confidence) × 融合一致性系数

规则：
- 单模态高置信度 (>0.9): 可直接使用
- 多模态一致 + 各自中置信度 (>0.7): 提升总置信度
- 模态冲突: 降低总置信度，标注 conflict_flag
- 单模态低置信度 (<0.5): 不写入长期记忆，只进 working memory
```

---

### 6.6 端侧 vs 云侧处理分工

| 处理阶段 | 端侧 | 云侧 | 分工原因 |
|----------|------|------|----------|
| 原始信号采集 | ✓ | | 物理必须在端侧 |
| 降噪与预处理 | ✓ | | 低延迟需求 |
| VAD / 唤醒词检测 | ✓ | | 隐私 + 功耗 |
| 简单活动识别 (HAR) | ✓ | | 低延迟 + 隐私 |
| 人脸检测 (是否有人) | ✓ | | 隐私 (不上传人脸) |
| 事件边界检测 | ✓ | | 实时性要求 |
| 隐私过滤/脱敏 | ✓ | | 敏感数据不出端 |
| ASR (语音转文字) | 部分 | ✓ | 端侧小模型+云端精确模型 |
| 复杂场景理解 (VLM) | | ✓ | 算力需求高 |
| 记忆检索 | 部分(近期) | ✓(全量) | 端侧缓存热数据 |
| LLM 推理 / 决策 | | ✓ | 算力+模型规模 |
| 动作执行 | ✓ | | 物理控制在端侧 |

#### 端云协作时序

```
端侧 (持续运行, 低功耗)          云侧 (按需调用, 高算力)
│                                  │
├── 持续感知 + 预处理              │
├── 事件边界检测                   │
├── 重要性评估                     │
│                                  │
├── [重要事件] ──── 发送 ─────────→├── VLM 场景理解
│                                  ├── 记忆检索
│                                  ├── LLM 推理
│   ←──────── 返回决策 ────────────├── Context Compiler
│                                  │
├── 执行动作/输出                   │
├── 收集用户反馈                   │
├── [反馈] ──── 发送 ─────────────→├── 记忆更新
│                                  │
```

---

### 6.7 隐私过滤层

隐私过滤必须在 Context 化的**最早期**进行，作为端侧的必经环节：

| 过滤规则 | 操作 | 时机 |
|----------|------|------|
| **旁人面部** | 模糊/不存储原始图像，仅保留"有人在场" | Stage 1 |
| **旁人语音** | 不存储原始音频，仅保留"有对话发生" | Stage 1 |
| **敏感位置** | 医院/宗教场所等地点降级为"敏感场所" | Stage 4 |
| **用户设置的禁区** | 特定时间/地点完全停止记录 | Stage 1 |
| **儿童相关** | 检测到儿童时提高过滤等级 | Stage 2 |
| **商业秘密** | 检测到工作场景的保密标记 | Stage 4 |

隐私标记直接写入 Context Object 的 `privacy_flags` 字段，影响后续记忆写入策略。

---

### 6.8 Multimodal Context Object 标准定义

```json
{
  "event_id": "evt_2026_06_23_0042",
  "timestamp": "2026-06-23T14:30:00+08:00",
  "duration_ms": 45000,
  "event_type": "conversation",
  "importance_score": 0.78,
  
  "modalities": {
    "visual": {
      "available": true,
      "scene_description": "办公室会议室，白板上有流程图",
      "objects": ["laptop", "whiteboard", "coffee_cup", "notebook"],
      "people": [
        {"person_id": "contact_zhang", "role": "colleague", "confidence": 0.85},
        {"person_id": null, "role": "unknown", "confidence": 0.0}
      ],
      "spatial_relations": "用户坐在桌子左侧，张工在对面",
      "confidence": 0.82
    },
    "audio": {
      "available": true,
      "transcript": "张工：下周三前我们需要完成 API 对接",
      "speakers": ["contact_zhang"],
      "user_speaking": false,
      "emotion": "neutral",
      "ambient_noise_level": 0.2,
      "confidence": 0.91
    },
    "motion": {
      "available": true,
      "activity": "sitting",
      "posture": "upright",
      "head_orientation": "facing_forward",
      "confidence": 0.95
    },
    "location": {
      "available": true,
      "type": "office",
      "semantic_place": "3F会议室B",
      "coordinates": null,
      "confidence": 0.98
    }
  },
  
  "derived_context": {
    "user_state": {
      "inferred_intent": "listening_to_colleague",
      "attention_state": "focused",
      "interruptibility": "low"
    },
    "event_summary": "张工在会议室讨论 API 对接截止日期（下周三）",
    "actionable_items": [
      {"type": "deadline", "content": "API 对接", "due": "2026-06-30", "person": "team"}
    ]
  },
  
  "confidence": 0.87,
  "processing_level": "processed",
  
  "privacy": {
    "contains_bystander": true,
    "bystander_handling": "face_blurred_voice_not_stored",
    "storage_policy": "short_term_only",
    "sensitivity_level": "private"
  },
  
  "memory_routing": {
    "write_to_working": true,
    "candidate_for_episodic": true,
    "candidate_for_semantic": false,
    "extraction_targets": ["deadline", "person_context"]
  }
}
```

---

### 6.9 智能硬件 Context Pipeline 完整图

```
┌─────────────────────────────────────────────────────────────────┐
│                     HARDWARE CONTEXT PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Camera  │  │   Mic   │  │   IMU   │  │   GPS   │  ...       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       │             │            │             │                  │
│       └─────────────┼────────────┼─────────────┘                │
│                     ↓                                            │
│         ┌──────────────────────┐                                │
│         │  1. Signal Processing │  (端侧, 实时)                 │
│         │  降噪/对齐/同步      │                                │
│         └──────────┬───────────┘                                │
│                    ↓                                             │
│         ┌──────────────────────┐                                │
│         │  2. Privacy Filter    │  (端侧, 实时)                 │
│         │  旁人脱敏/禁区检查   │                                │
│         └──────────┬───────────┘                                │
│                    ↓                                             │
│         ┌──────────────────────┐                                │
│         │  3. Perception       │  (端侧, 低延迟模型)            │
│         │  VAD/HAR/检测/分类   │                                │
│         └──────────┬───────────┘                                │
│                    ↓                                             │
│         ┌──────────────────────┐                                │
│         │  4. Event Boundary   │  (端侧)                        │
│         │  切分连续流为事件    │                                │
│         └──────────┬───────────┘                                │
│                    ↓                                             │
│         ┌──────────────────────┐                                │
│         │  5. Importance Score │  (端侧)                        │
│         │  评估是否值得处理    │                                │
│         └──────────┬───────────┘                                │
│                    ↓                                             │
│            [重要事件上传云端]                                     │
│                    ↓                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  6. Deep Understanding (云侧)                            │    │
│  │  VLM 场景理解 / ASR 精确转录 / 实体抽取                  │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  7. Context Object Assembly                              │    │
│  │  结构化为标准 JSON / 填充字段 / 计算置信度               │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓                                        │
│              ┌──────────────────┐                                │
│              │  Context Object  │ ← 输出                        │
│              └──────────────────┘                                │
│                    ↓          ↓                                   │
│        写入记忆系统     供 Context Compiler 使用                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 7. 对智能硬件 Context 管理的启发

| 发现 | 设计启示 |
|------|----------|
| 原始带宽远超 context window 容量 | Context 化 = 极高压缩比的信息提炼（~10000:1） |
| 连续流必须切分为离散事件 | 事件切分质量决定了记忆质量 |
| 多模态可能冲突 | 必须有置信度评估和冲突标记机制 |
| 隐私过滤必须在最早期 | 端侧第一步就是 privacy filter |
| 不同模态的延迟差异大 | 视觉处理（秒级）vs IMU（毫秒级）→ 异步融合 |
| 低置信度数据有风险 | threshold 策略：低于阈值不进入长期记忆 |
| 端侧必须轻量但不能太弱 | 端侧负责过滤和切分，云侧负责理解和推理 |

## 8. 与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| Phase 1 | 承接"动态 context"概念，传感器数据是最典型的动态 context |
| Phase 3 | 承接记忆框架研究——Context Object 是记忆系统的输入 |
| → Phase 5 | Context Object 的 memory_routing 字段直接指导记忆写入层级 |
| → Phase 6 | Context Object 是 Context Compiler 的核心输入数据结构 |
| → Phase 7 | 各硬件设备的 Context Pipeline 是本阶段框架的具体实例化 |

## 9. 尚不确定或证据不足的问题

1. **端侧事件切分模型的精度** — 在低功耗芯片 (<1W) 上能否达到可用的切分质量？ [NEEDS_CITATION]
2. **VLM 场景描述的 token 效率** — 一张复杂场景用 VLM 描述需要多少 token？是否需要专门的"context-efficient"描述格式？
3. **多模态融合的最优策略** — 早期/晚期/注意力融合在穿戴设备场景下哪种最优？无公开对比实验。
4. **隐私过滤的误杀率** — 过于激进的隐私过滤是否会导致重要 context 丢失？
5. **事件重要性评分的准确性** — 用户认为重要的事件和系统评估的重要性是否一致？需要用户研究。
6. **离线场景的 Context Object 堆积** — 无网络时端侧产生的 Context Object 如何高效同步？

## 10. 下一阶段建议

Phase 5 应该：

1. **基于 Context Object 的 memory_routing 字段设计写入策略** — 什么事件写入哪层记忆
2. **将 Phase 3 的 CoALA 四层模型扩展为硬件七层** — 增加 Raw Buffer、Perception Working Memory、Governance Memory
3. **为每层记忆设计具体的数据结构** — 参考本阶段的 Context Object 格式
4. **设计记忆间的升级路径** — Episodic → Semantic 的归纳机制
5. **设计 Governance Memory 的隐私策略** — 基于本阶段的 privacy_flags 字段
