# 端到端 Worked Examples：从原始传感器到 Prompt 片段

## 概述

本文档为三类可穿戴设备各提供一个完整的数据追踪示例（Worked Example），展示从原始传感器字节到最终进入 LLM prompt 的具体文本的全过程。每一步标注数据量、延迟、处理位置。

---

## Example 1: AI 眼镜 — "识别同事并主动提供上下文"

### 场景描述
用户戴着 AI 眼镜走进办公室，遇到同事张工。系统识别人物并主动提示上次对话要点。

### Step-by-Step Trace

#### Step 1: 原始传感器采集 (端侧, 持续)

```
时间: 2026-06-23 09:15:32.000

摄像头输出:
  格式: YUV420, 1920×1080, 30fps
  当前帧大小: ~3.1 MB (未压缩) → H.264 编码后 ~170 KB/帧
  
麦克风输出:
  格式: PCM 16bit, 16kHz, 双通道
  1秒数据量: 64 KB
  当前内容: 办公室背景噪声 + 远处有人说话

IMU 输出:
  格式: int16[6] (acc_xyz + gyro_xyz), 100Hz
  1秒数据量: 1.2 KB
  当前读数: acc=[0.1, 0.2, 9.8] (静止/站立)
```

**数据量: ~5.2 MB/s (视频编码后主导)**

---

#### Step 2: 端侧预处理 (端侧, <50ms)

```
处理 1: 关键帧判断 (变化检测)
  输入: 当前帧 vs 上一关键帧
  方法: 帧差法 + 阈值
  结果: 检测到显著变化 (新人物进入视野) → 触发新关键帧
  延迟: 5ms

处理 2: 人脸检测 (MobileFaceNet)
  输入: 当前关键帧 (缩放至 320×320)
  输出: [{bbox: [412,180,580,380], confidence: 0.94}]
  延迟: 15ms

处理 3: 人脸特征提取 + 匹配
  输入: 人脸裁剪区域 (128×128)
  方法: ArcFace embedding (512-d) → 与本地联系人库比对
  输出: {person_id: "contact_zhang", similarity: 0.87}
  延迟: 20ms

处理 4: VAD
  输入: 最近 320ms PCM 音频
  输出: speech_detected = false (仅背景噪声)
  延迟: 10ms

处理 5: HAR (活动识别)
  输入: IMU 窗口 (最近 2 秒, 200 samples)
  输出: activity = "standing", confidence = 0.92
  延迟: 8ms
```

**输出数据量: ~200 bytes (结构化元数据)**
**总延迟: ~50ms (并行处理)**

---

#### Step 3: Perception Working Memory 更新 (端侧, 即时)

```json
// L2 Perception WM 更新
{
  "perception_id": "pwm_20260623_091532",
  "timestamp": "2026-06-23T09:15:32+08:00",
  "scene": {
    "location": "office_3F_hallway",
    "people_detected": [
      {"person_id": "contact_zhang", "confidence": 0.87, "distance_est": "2m"}
    ],
    "activity": "standing_encounter"
  },
  "user_state": {
    "posture": "standing",
    "head_direction": "facing_person",
    "gaze_duration_on_target": "1.2s"
  },
  "change_event": "new_person_recognized"
}
```

**数据量: ~400 bytes JSON**
**延迟: <1ms (内存写入)**

---

#### Step 4: 触发判断 (端侧, <10ms)

```
触发条件检查:
  ✓ 已知人物识别 (contact_zhang, confidence > 0.8)
  ✓ 用户注视时长 > 1s (表示可能在回忆此人信息)
  ✓ Procedural Rule: "识别到联系人时可提供上下文辅助"
  
结论: 触发 Context Compiler → 请求云端 LLM 辅助

Importance Score: 0.72
User Interruptibility: medium (站立/非对话中)
```

**延迟: 5ms**

---

#### Step 5: 记忆检索 (云侧, ~80ms)

```
检索请求:
  query: "contact_zhang 最近交互"
  filters: {person: "contact_zhang", recency: "30_days"}
  ranker_weights: {SpatialRelevance: 0.2, Recency: 0.25, TaskRelevance: 0.3}

检索结果 (Top-3 by ContextScore):
  
  1. mem_ep_0035 (score: 0.89)
     "上周三(6/18)张工在周会上提到 API 对接可能延期，需要额外一周"
     
  2. mem_ep_0029 (score: 0.74)
     "上周一(6/16)与张工在走廊聊天，他问了关于数据库迁移的进度"
     
  3. mem_sem_0103 (score: 0.71)
     "张工: 技术部后端开发, 负责API模块, 直接沟通风格"
```

**网络传输: ~2 KB (请求) + ~1 KB (结果)**
**延迟: 30ms网络 + 50ms检索 = 80ms**

---

#### Step 6: Context Compiler - Prompt Packing (云侧, ~20ms)

```
Token Budget: 2048 tokens (轻量辅助场景)
Budget 分配:
  System + Device: 200 tokens (固定)
  User Profile: 100 tokens
  Scene: 150 tokens
  Memories: 300 tokens
  Task: 200 tokens
  Safety: 100 tokens
  Reserve: 998 tokens (输出空间)
```

**生成的完整 Prompt:**

```xml
<system_policy>
你是智能眼镜助手。当用户遇到认识的人时，提供简短上下文辅助。
输出限制：1-2句话，仅通过AR文字显示3秒。不要大声朗读。
</system_policy>

<device>智能眼镜 | 可用输出: AR叠加文字, 轻微震动</device>

<user_profile>
用户偏好: 简洁提示, 中文, 工作场合不语音输出
</user_profile>

<current_scene>
时间: 2026-06-23 09:15
地点: 3F走廊
检测到: 张工 (技术部同事, confidence: 0.87)
用户状态: 站立, 面向张工, 注视1.2秒
</current_scene>

<retrieved_memories>
[近期] 6/18 张工在周会提到 API 对接可能延期一周
[近期] 6/16 张工问过数据库迁移进度
[画像] 张工: 技术部后端, 负责API模块, 直接沟通风格
</retrieved_memories>

<task>
用户遇到了张工，可能需要快速回忆上次交流要点。
请生成1行AR文字提示(≤15字)，帮助用户快速回忆上下文。
如果判断不需要提示，输出"SKIP"。
</task>

<safety>
不要在他人面前显示敏感信息。
AR文字仅用户可见。
</safety>
```

**Prompt Token 数: ~380 tokens**
**延迟: ~20ms (模板填充+截断)**

---

#### Step 7: LLM 推理 (云侧, ~300ms)

```
模型: Claude Haiku (低延迟场景)
输入: 380 tokens
输出: "张工 - API对接延期，上周问过DB迁移"
输出 Token: 18 tokens

推理延迟: ~300ms (Haiku TTFT ~100ms + 生成 ~200ms)
```

---

#### Step 8: 设备输出 (端侧)

```
输出通道: AR 文字叠加
显示内容: "张工 - API对接延期，上周问过DB迁移"
显示位置: 视野右下角，半透明
显示时长: 3秒后自动消失
同时: 轻微震动 (30ms) 提示用户有新信息
```

---

#### Step 9: 反馈收集 → 记忆更新

```
用户行为观察:
  - 用户看到AR提示后 → 向张工打招呼并提到"API对接的事"
  - 判断: 提示被使用 → 正反馈

记忆更新:
  - mem_ep_0035 access_count += 1 (被检索使用)
  - 新写入 mem_ep_0043: "6/23 09:15 走廊遇到张工，用户主动提及API对接"
  - 提示策略确认: "人物识别+注视 → AR提示" 策略有效
```

---

#### 全链路延迟汇总

| 步骤 | 位置 | 延迟 | 累计 |
|------|------|------|------|
| 传感器采集 | 端侧 | ~33ms (1帧) | 33ms |
| 端侧预处理 | 端侧 | ~50ms | 83ms |
| L2 更新 + 触发判断 | 端侧 | ~6ms | 89ms |
| 网络传输(上行) | 网络 | ~30ms | 119ms |
| 记忆检索 | 云侧 | ~50ms | 169ms |
| Prompt Packing | 云侧 | ~20ms | 189ms |
| LLM 推理 | 云侧 | ~300ms | 489ms |
| 网络传输(下行) | 网络 | ~30ms | 519ms |
| AR 渲染显示 | 端侧 | ~16ms | **535ms** |

**总延迟: ~535ms (满足 <500ms 困难，但 <600ms 可接受)**

---

## Example 2: AI 耳机 — "会议中主动提供信息辅助"

### 场景描述
用户在会议中，对方提到一个项目名称，用户短暂停顿（可能在回忆），系统主动低声提示关键信息。

### Step-by-Step Trace

#### Step 1: 原始传感器采集

```
时间: 2026-06-23 14:32:15.000

外部麦克风:
  格式: PCM 24bit, 16kHz, mono
  内容: 对方正在说话 "...Alpha项目的最新进度怎么样了..."
  1秒数据: 48 KB

IMU:
  格式: int16[6], 50Hz
  内容: 用户头部轻微点头 → 突然停止 (可能在思考)
  1秒数据: 0.6 KB
```

---

#### Step 2: 端侧预处理 (<30ms)

```
处理 1: VAD
  结果: speech_active = true, speaker = "not_user" (外部麦克风为主)
  延迟: 10ms

处理 2: 流式 ASR (端侧 Whisper-tiny)
  输入: 最近 3 秒 PCM
  输出: "Alpha项目的最新进度怎么样了"
  confidence: 0.88
  延迟: 150ms (流式，每 1s 输出一次)

处理 3: 用户状态检测
  IMU 分析: 头部动作从"点头"变为"静止" → 可能在思考/回忆
  端侧语音: 用户麦克风未检测到语音 (用户未说话)
  判断: user_state = "thinking_pause"
  延迟: 30ms
```

---

#### Step 3: 触发判断 (端侧, <10ms)

```
触发信号组合:
  ✓ 对方提出问题 (ASR 检测到"怎么样"问句模式)
  ✓ 问题包含项目名称 "Alpha项目" (关键实体)
  ✓ 用户停顿 > 0.8s (可能需要回忆)
  ✓ Procedural Rule: "检测到用户可能需要信息辅助时，可主动提示"

ShouldIntervene 计算:
  NeedProb = 0.75 (停顿+被问问题)
  InfoValue = 0.8 (如果有Alpha项目记忆)
  SocialRisk = 0.3 (会议中，但对方在等回答)
  Score = 0.75 × 0.8 × (1-0.3) = 0.42 > threshold(0.35)

结论: 触发辅助
```

---

#### Step 4: 记忆检索 (云侧, ~60ms)

```
检索请求:
  query: "Alpha项目 进度"
  context: {current_speaker: "colleague", user_state: "thinking"}

检索结果 (Top-2):
  1. mem_ep_0038 (score: 0.92)
     "上周五(6/20) Alpha项目完成第一阶段里程碑，通过了QA验证"
     
  2. mem_sem_0088 (score: 0.78)
     "Alpha项目: 内部API重构项目, 负责人张工, 计划3个阶段, 6月底完成"
```

---

#### Step 5: Prompt Packing (云侧, ~10ms)

```xml
<system>
你是耳机助手。用户在会议中被问到问题，可能需要回忆。
输出限制：最多5个字的低声提示词。只输出关键信息片段。
如果不确定，输出"SKIP"。
</system>

<context>
对方问: "Alpha项目的最新进度怎么样了"
用户状态: 短暂停顿，似乎在回忆
</context>

<memories>
[6/20] Alpha项目完成第一阶段，通过QA
[背景] Alpha: API重构, 3阶段, 6月底截止
</memories>

<output_constraint>
只输出≤5字的提示词。例如: "上周五过了QA"
</output_constraint>
```

**Prompt Token: ~180 tokens**

---

#### Step 6: LLM 推理 (云侧, ~50ms)

```
模型: Claude Haiku (最小延迟)
输出: "上周五过了QA"
输出 Token: 6 tokens
延迟: ~50ms
```

---

#### Step 7: 输出

```
输出方式: 骨传导/低声耳语 (仅用户可听)
内容: "上周五过了QA" (5个字)
音量: -20dB (远低于环境音)
或: 不用TTS，直接以震动节奏编码 → 用户看手表/触摸耳机查看文字
```

---

#### 全链路延迟汇总

| 步骤 | 位置 | 延迟 | 累计 |
|------|------|------|------|
| ASR 流式输出 | 端侧 | 150ms | 150ms |
| 触发判断 | 端侧 | 10ms | 160ms |
| 网络上行 | 网络 | 20ms | 180ms |
| 记忆检索 | 云侧 | 60ms | 240ms |
| Prompt Pack | 云侧 | 10ms | 250ms |
| LLM 推理 | 云侧 | 50ms | 300ms |
| 网络下行 | 网络 | 20ms | 320ms |
| 音频输出 | 端侧 | 10ms | **330ms** |

**总延迟: ~330ms (满足 <300ms 有挑战，但在对话间隙中可接受)**

---

## Example 3: AI Pin — "全天录音后生成每日承诺摘要"

### 场景描述
用户佩戴录音挂坠一整天，系统在晚间自动生成"今日承诺/待办"摘要推送到手机。

### Step-by-Step Trace

#### Step 1: 全天持续采集 (端侧, 低功耗)

```
工作时间: 08:00 - 22:00 (14 小时)
麦克风: PCM 16bit, 16kHz, mono → 32 KB/s

全天原始数据:
  14h × 3600s × 32KB = ~1.6 GB

端侧 VAD 实时过滤:
  有效语音占比: ~35%
  过滤后: ~560 MB
```

---

#### Step 2: 端侧实时预处理 (全天持续)

```
每秒处理:
  VAD: speech/silence 标记 → 过滤静默段
  场景分类: 每30秒判断一次 (会议/对话/独处/通勤/用餐)
  重要性预评估: 简单规则 (多人对话=中, 独处=低, 检测到"记住"/"承诺"=高)

当天产出:
  有效语音段: 312 段 (平均 1-5 分钟/段)
  场景标签: {会议: 3次, 面对面对话: 15次, 电话: 5次, 独处: 多段}
  高重要性标记: 28 段 (importance > 0.6)
```

---

#### Step 3: 批量上传 + 云端处理 (Wi-Fi 可用时)

```
上传时机: 午休 + 晚间 Wi-Fi 连接时

上传内容: 28 段高重要性音频 (~45 分钟, ~86 MB 压缩后)
网络: Wi-Fi, ~5 分钟完成

云端处理管线:
  1. 高质量 ASR (Whisper-large-v3)
     → 28 段转录文本, 共约 12,000 字 (~8,000 tokens)
     
  2. 说话人分离 (Pyannote)
     → 标注用户 vs 对方
     
  3. 结构化抽取 (Claude Sonnet)
     输入: 各段转录 + "提取承诺、决策、待办、关键信息"
     输出: 结构化 JSON 列表
```

---

#### Step 4: 结构化抽取结果 (LLM 输出)

```json
[
  {
    "event_time": "09:30",
    "event_type": "commitment",
    "speaker": "user",
    "content": "周五前把设计文档发给王总",
    "deadline": "2026-06-27",
    "related_person": "王总",
    "context": "早会讨论Q3规划时"
  },
  {
    "event_time": "11:00",
    "event_type": "decision",
    "speaker": "team",
    "content": "API方案采用方案B (GraphQL)",
    "context": "技术评审会"
  },
  {
    "event_time": "14:30",
    "event_type": "commitment",
    "speaker": "user",
    "content": "下周一给张工review代码",
    "deadline": "2026-06-30",
    "related_person": "张工",
    "context": "午后1:1讨论"
  },
  {
    "event_time": "16:00",
    "event_type": "info",
    "speaker": "colleague",
    "content": "服务器迁移计划推迟到7月第二周",
    "context": "茶水间闲聊"
  }
]
```

**抽取结果: 4 条结构化记忆 (实际一天可能 10-20 条)**

---

#### Step 5: 记忆写入 (云侧)

```
写入 L4 Episodic Memory: 4 条

每条写入格式:
{
  "memory_id": "mem_ep_0044",
  "type": "episodic",
  "event": {
    "summary": "用户承诺周五前把设计文档发给王总",
    "timestamp": "2026-06-23T09:30:00+08:00",
    "location": "office_meeting_room",
    "people": ["王总"],
    "importance": 0.85
  },
  "governance": {
    "source": "audio_transcription",
    "confidence": 0.88,
    "privacy_level": "private"
  },
  "embeddings": { "text_vector": [...512d...] }
}
```

---

#### Step 6: 每日摘要生成 (晚间自动触发)

**Prompt 组装:**

```xml
<system>
你是用户的个人记忆助手。请根据今天的记忆生成每日摘要。
输出格式：
1. 今日承诺/待办 (带截止日期)
2. 重要决策
3. 值得记住的信息
</system>

<today_memories>
1. [09:30] 承诺: 周五前把设计文档发给王总
2. [11:00] 决策: API方案采用方案B (GraphQL)
3. [14:30] 承诺: 下周一给张工review代码
4. [16:00] 信息: 服务器迁移推迟到7月第二周
</today_memories>

<existing_todos>
- [进行中] Q3规划文档初稿 (本周五截止)
- [进行中] API重构第二阶段
</existing_todos>

<output_format>
生成简洁的每日摘要，适合手机通知推送阅读(≤200字)。
</output_format>
```

**Prompt Token: ~350 tokens**

---

#### Step 7: LLM 输出 + 推送

```
LLM 输出 (Claude Sonnet):

📋 今日摘要 (6月23日)

待办:
• 周五前发设计文档给王总 ⏰
• 下周一review张工代码

决策:
• API方案确定用GraphQL (方案B)

备忘:
• 服务器迁移推迟到7月第二周

输出 Token: ~80 tokens
```

推送到手机 App，用户可查看/编辑/删除。

---

#### 全链路时间线

| 步骤 | 时间点 | 处理 |
|------|--------|------|
| 全天录音 | 08:00-22:00 | 端侧持续采集+VAD过滤 |
| 午休上传 | 12:30 | 上午段音频上传 |
| 晚间上传 | 21:00 | 下午段音频上传 |
| 云端处理 | 21:00-21:10 | ASR + 说话人分离 + 抽取 |
| 摘要生成 | 21:10-21:12 | Prompt 组装 + LLM 生成 |
| 推送 | 21:12 | 手机 App 通知 |

**非实时场景：全链路延迟无严格约束，重点是准确性和完整性。**

---

## 关键对比：三个 Example 的差异

| 维度 | AI 眼镜 | AI 耳机 | AI Pin |
|------|---------|---------|--------|
| **触发方式** | 人物识别 (视觉) | 对话停顿 (音频) | 定时批量 |
| **实时性** | ~535ms | ~330ms | 非实时(小时级) |
| **Prompt 大小** | 380 tokens | 180 tokens | 350 tokens |
| **输出长度** | 15字 AR文字 | 5字低声提示 | 200字摘要 |
| **端侧计算量** | 高 (人脸检测+匹配) | 中 (流式ASR) | 低 (仅VAD+分类) |
| **云侧计算量** | 中 (检索+LLM) | 低 (快速LLM) | 高 (大量ASR+LLM抽取) |
| **关键瓶颈** | VLM 延迟 | 总链路<300ms | ASR 准确率 |
| **记忆操作** | 检索 L4+L5 | 检索 L4+L5 | 写入 L4 (批量) |
