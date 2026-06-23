# Phase 6：Context Compiler / Prompt Assembly 架构设计

## 1. 阶段研究目标

设计一个面向智能硬件的 **Context Compiler**——在每次模型调用前，从七层记忆系统中选择、排序、压缩、拼接最相关的信息，形成高质量模型输入。

本阶段核心任务：
- 设计 9 步 Context Assembly Pipeline 的完整规格
- 建立 Context Ranker 多维度评分模型
- 设计 Token Budget 分配和降级策略
- 区分 LLM / VLM / VLA 三种不同的 prompt 需求
- 设计主动服务场景的 Context Decision 机制
- 将 Phase 1 的 12 条行为特性转化为 Compiler 设计约束

## 2. 核心问题清单

1. 当前任务、当前场景、历史记忆、设备状态、用户偏好、可用动作如何进入 prompt？
2. Context Ranker 应该按照哪些维度排序？权重如何确定？
3. Token budget 如何在各组件之间分配？
4. 如何避免旧记忆污染 prompt（Phase 1 现象 4-6 的约束）？
5. 信息在 prompt 中的位置如何安排（Phase 1 现象 1-3, 9-10 的约束）？
6. 如何区分 LLM prompt、VLM prompt 和 VLA action context？
7. 主动服务场景下，如何判断是否应该调用模型/打扰用户？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| 架构设计 | context compiler, prompt packing, context assembly pipeline |
| 排序检索 | context ranking, relevance scoring, multi-criteria retrieval |
| Token 管理 | token budget allocation, context truncation, priority packing |
| 多模型 | VLM prompt, VLA action context, multimodal prompt design |
| 主动服务 | proactive AI, interruption management, notification decision |

## 4. 资料来源清单

| ID | 类型 | 标题 | 作者/机构 | 年份 | 核心贡献 |
|----|------|------|-----------|------|----------|
| S012 | blog | Effective Context Engineering for AI Agents | Anthropic | 2025 | "最小高信号 token 集"原则 |
| S001 | paper | Lost in the Middle | Liu et al. | 2023 | 位置效应约束 prompt 结构 |
| S020 | paper | Generative Agents | Park et al. | 2023 | Recency+Importance+Relevance 三维度检索 |
| S036 | paper | Interruption Management in Smart Environments | (HCI研究) | 多年 | 打扰时机判断模型 |
| S037 | paper | OpenVLA: An Open-Source Vision-Language-Action Model | Kim et al. | 2024 | VLA 的 context 输入格式 |
| S038 | paper | MemoryVLA: Cognition-Memory-Action Framework | (具身智能) | 2025 | 机器人记忆与动作决策结合 |

## 5. 证据矩阵

| 论断 | 支撑资料 | 证据强度 |
|------|----------|----------|
| Prompt 最佳结构：高注意力区(首尾)放关键信息 | S001 (Lost in the Middle) | 强 |
| 三维度检索(Recency+Importance+Relevance)有效 | S020 (实验验证) | 强 |
| Context 应追求"最小高信号 token 集" | S012 (工程原则) | 强 |
| 结构化标签(XML/Markdown)减少跨区域干扰 | S012 + Phase 1 现象12 | 中 |
| VLA 需要分离 high-level planning 和 low-level action context | S037, S038 | 中 |
| 打扰时机判断需考虑用户活动状态和社交情境 | S036 (HCI 研究) | 中 |
| 关键安全约束需在 prompt 末尾重申(Recency Bias) | Phase 1 现象10 | 中 |

## 6. 关键发现

### 6.1 Context Compiler 完整 Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CONTEXT COMPILER PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 1: TRIGGER DETECTION                                   │    │
│  │  判断是否需要调用模型：                                       │    │
│  │  • 用户显式请求                                              │    │
│  │  • 环境事件触发 (重要性 > 阈值)                              │    │
│  │  • 定时任务触发                                              │    │
│  │  • Procedural Rule 触发                                      │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 2: INTENT CLASSIFICATION                               │    │
│  │  确定本次调用的类型和需求：                                    │    │
│  │  • 响应类型: LLM(文本) / VLM(视觉理解) / VLA(动作执行)       │    │
│  │  • 任务类型: 问答 / 摘要 / 决策 / 动作规划                   │    │
│  │  • 输出通道: 语音 / 显示 / 震动 / 动作                       │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 3: CONTEXT RETRIEVAL                                   │    │
│  │  从七层记忆中检索候选内容：                                    │    │
│  │  • L2: 当前感知状态 (全量注入)                               │    │
│  │  • L3: 当前任务状态 (全量注入)                               │    │
│  │  • L4: 相关 episodic memories (Top-K 检索)                   │    │
│  │  • L5: 相关 semantic memories (按需检索)                     │    │
│  │  • L6: 适用的 procedural rules (条件匹配)                   │    │
│  │  • L7: 各记忆的 governance 信息 (过滤依据)                  │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 4: PRIVACY FILTER                                      │    │
│  │  基于 Governance Memory 过滤：                                │    │
│  │  • 隐私级别检查 (sensitive → 不发送到云端)                   │    │
│  │  • 旁人数据过滤                                              │    │
│  │  • 过期记忆排除                                              │    │
│  │  • 用户黑名单规则                                            │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 5: CONTEXT RANKING                                     │    │
│  │  对候选内容多维度评分排序 (详见 6.2)                          │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 6: TOKEN BUDGET ALLOCATION                             │    │
│  │  分配各区块 token 配额 (详见 6.3)                            │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 7: PROMPT PACKING                                      │    │
│  │  按模型注意力分布优化排列 (详见 6.4)：                        │    │
│  │  • 高注意力区(头): System + Identity + 锚定框架              │    │
│  │  • 中注意力区(中): 背景记忆 + 检索结果 (相关信息聚合)       │    │
│  │  • 高注意力区(尾): 当前场景 + 任务 + 安全约束               │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 8: MODEL INVOCATION                                    │    │
│  │  调用 LLM / VLM / VLA + 处理输出                            │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         ↓                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Step 9: FEEDBACK & MEMORY UPDATE                            │    │
│  │  • 执行输出 (语音/显示/动作)                                 │    │
│  │  • 收集用户反馈 (显式或隐式)                                 │    │
│  │  • 更新记忆 (成功→强化 / 失败→反思 / 否决→降权)            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 6.2 Context Ranker 评分模型

#### 评分公式

```
ContextScore(item) =
    w₁ × TaskRelevance(item, current_task)
  + w₂ × Recency(item)
  + w₃ × SpatialRelevance(item, current_location)
  + w₄ × UserSpecificity(item, user_profile)
  + w₅ × Confidence(item)
  + w₆ × Actionability(item, available_actions)
  - w₇ × PrivacyRisk(item)
  - w₈ × InterruptionCost(item, user_state)
  - w₉ × TokenCost(item)
```

#### 维度定义与权重

| 维度 | 定义 | 计算方式 | 默认权重 |
|------|------|----------|----------|
| **TaskRelevance** | 与当前任务/查询的语义相关性 | embedding 余弦相似度 | 0.30 |
| **Recency** | 时间新鲜度 | exp(-λ × hours_since) | 0.15 |
| **SpatialRelevance** | 与当前位置/场景的匹配度 | 场景类型匹配 + 距离衰减 | 0.15 |
| **UserSpecificity** | 是否针对当前用户个人信息 | 用户相关性标记 | 0.10 |
| **Confidence** | 信息来源的可信度 | L7 Governance 的 confidence 字段 | 0.10 |
| **Actionability** | 能否直接驱动当前可用动作 | 与 available_actions 的匹配度 | 0.10 |
| **PrivacyRisk** | 包含敏感信息的风险 | L7 privacy_level 评估 | -0.05 |
| **InterruptionCost** | 使用此信息可能导致的打扰代价 | 用户 interruptibility 评估 | -0.05 |
| **TokenCost** | 归一化的 token 占用量 | token_count / max_budget | -0.05 |

#### 权重自适应

权重不应是完全固定的。建议按设备类型和场景微调：

| 场景 | 提升的维度 | 降低的维度 |
|------|-----------|-----------|
| 安全紧急 | Actionability, Confidence | TokenCost, InterruptionCost |
| 社交场合 | InterruptionCost(绝对值) | Recency |
| 独处/空闲 | InterruptionCost→0 | Confidence(可容忍低置信) |
| 工作专注 | TaskRelevance | SpatialRelevance |
| 导航/移动 | SpatialRelevance | UserSpecificity |

---

### 6.3 Token Budget 分配

#### 硬件通用模板

```
Total Available: T tokens (建议使用 ≤ 70% context window，避免 Context Cliff)

┌─────────────────────────────────────────────────────────────┐
│  [Zone A: 固定区] ~15% of T                                  │
│  ├── System Policy + Safety:    ~5%                          │
│  └── Device Identity + Rules:   ~10%                         │
├─────────────────────────────────────────────────────────────┤
│  [Zone B: 半固定区] ~15% of T                                │
│  ├── User Profile (L5 选择性):  ~10%                         │
│  └── Procedural Rules (L6):     ~5%                          │
├─────────────────────────────────────────────────────────────┤
│  [Zone C: 动态区] ~55% of T                                  │
│  ├── Current Scene (L2):        ~15%                         │
│  ├── Recent Events:             ~10%                         │
│  ├── Retrieved Memories (L4/5): ~20%  ← Ranker 排序截断     │
│  └── Device State + Actions:    ~10%                         │
├─────────────────────────────────────────────────────────────┤
│  [Zone D: 任务区] ~15% of T                                  │
│  ├── Task/Trigger Description:  ~10%                         │
│  └── Safety Reiteration:        ~5%   ← Recency Bias 利用   │
└─────────────────────────────────────────────────────────────┘
```

#### Budget 超出时的降级策略

| 级别 | 触发条件 | 操作 | 影响 |
|------|----------|------|------|
| 0 | < 70% | 正常工作 | 无 |
| 1 | 70-80% | 压缩历史事件摘要 | 细节丢失 |
| 2 | 80-85% | 截断低分检索结果 | recall 下降 |
| 3 | 85-90% | 清除旧的 device state 历史 | 状态感知降低 |
| 4 | 90-95% | 只保留 Top-3 记忆 | 严重依赖排序准确性 |
| 5 | > 95% | 紧急模式：System + Scene + Task + Safety only | 最小可用 |

---

### 6.4 Prompt Packing 策略（基于 Phase 1 行为特性）

将 12 个 context 行为特性转化为 Compiler 的设计约束：

| Phase 1 现象 | Compiler 设计约束 |
|-------------|------------------|
| Lost in the Middle | 关键信息放首尾，中间放补充性内容 |
| Attention Sink | 开头放 System Policy（利用 sink 做锚定） |
| Instruction Decay | 安全约束在末尾重申 |
| Distractor Effect | 设置 relevance 阈值，低于阈值不放入 |
| Retrieval Paradox | confidence < threshold 时宁可不检索 |
| Knowledge Conflict | 冲突记忆标注来源+时间，让模型自行判断 |
| Multi-hop Fragility | 需要关联推理的信息物理相邻放置 |
| Reversal Curse | 检索时使用双向索引 |
| Anchoring Effect | 开头的场景描述定调，注意不要过度悲观/乐观 |
| Recency Bias | 当前任务+安全约束放在最后 |
| Context Cliff | 永远不用满 budget，保留 30% |
| Role Separation | 不同来源的内容用 XML 标签隔离 |

#### 实际 Prompt 结构示例（AI 眼镜场景）

```xml
<system_policy>
你是一个智能眼镜助手。你只在用户需要时主动提供帮助。
你的输出通道是：低声语音(优先)、AR叠加文字(次选)、震动(提醒)。
你必须遵守：不在社交场合造成尴尬、不在公开场合大声输出。
</system_policy>

<device_state>
设备：智能眼镜 v2 | 电量 72% | 网络正常 | 显示可用 | 语音可用
</device_state>

<user_profile>
用户偏好：简洁回答、中文交互、会议中不打扰
用户关系：张工(技术部同事,日常联系)、李总(上级,正式)
</user_profile>

<retrieved_memories>
[EP-0035] 上周三张工提到 API 项目延期风险
[SEM-0103] 张工: 技术部同事, 负责后端, 注重细节
[PROC-0015] 规则: 会议中静默模式
</retrieved_memories>

<current_scene>
时间: 2026-06-23 14:30 | 地点: 3F会议室B
活动: 小组讨论 | 人物: 张工(确认), 1人未知
用户状态: 坐姿, 注视张工, 未说话
</current_scene>

<task>
触发原因: 张工提到"下周三截止日期"，系统检测到可提取的deadline信息
任务: 判断是否需要提醒用户记录此deadline
当前 interruptibility: low (会议中)
</task>

<safety>
约束: 当前为会议模式，不可语音输出。
如需提醒，仅可使用轻微震动。
如非紧急，应等会议结束后推送摘要。
</safety>
```

---

### 6.5 LLM / VLM / VLA Context 差异

| 维度 | LLM Context | VLM Context | VLA Context |
|------|-------------|-------------|-------------|
| **输入核心** | 文本（任务+记忆+规则） | 图像+文本（视觉场景+指令） | 观察+状态+指令 |
| **典型 token 量** | 2K-10K | 1K-5K文本 + 图像token | 500-2K文本 + 视觉 + 状态 |
| **延迟预算** | 1-5s | 1-3s | <100ms (实时控制) |
| **记忆检索重点** | 语义记忆、事件记忆 | 空间记忆、视觉记忆 | 动作记忆、物体记忆 |
| **输出类型** | 文本/决策/计划 | 场景描述/识别/推理 | 动作序列/轨迹 |
| **安全约束** | 内容安全 | 识别准确性 | 物理安全(碰撞/力矩) |
| **使用设备** | 所有设备 | 眼镜、机器人 | 机器人 |

#### VLA 的双层 Context 架构

```
┌────────────────────────────────────────────────────┐
│  High-Level Planning Context (LLM, 低频调用)        │
│  ├── 用户请求: "把杯子放到厨房"                      │
│  ├── 环境语义理解: 客厅茶几上有杯子，厨房在东侧     │
│  ├── 相关记忆: 用户偏好杯子放在水槽旁               │
│  ├── 任务分解: 导航→识别→抓取→导航→放置             │
│  └── 安全约束: 避开猫的区域、轻拿轻放               │
├────────────────────────────────────────────────────┤
│  Low-Level Action Context (VLA, 高频循环)           │
│  ├── 当前视觉观察: RGB-D 图像                       │
│  ├── 当前子任务: "approach_and_grasp"               │
│  ├── 关节状态: [0.1, -0.3, 0.8, ...]              │
│  ├── 目标物体位姿: {x, y, z, quat}                │
│  ├── 动作约束: max_force=5N, collision_objects=[..]│
│  └── Procedural Memory: "smooth_ceramic→top_grasp" │
└────────────────────────────────────────────────────┘
```

---

### 6.6 主动服务的 Context Decision

#### 核心问题：什么时候系统应该主动调用 LLM？

不是所有感知事件都需要调用模型。Context Compiler 需要一个"Pre-flight Check"：

```
ShouldInvoke = 
    EventImportance(event)
  × UserNeedProbability(event, user_state)
  × (1 - InterruptionCost(user_state))
  × SystemCapability(device_state)
  > InvocationThreshold
```

#### 决策矩阵

| 用户状态 | 事件重要性 高 | 事件重要性 中 | 事件重要性 低 |
|----------|-------------|-------------|-------------|
| **空闲/可打扰** | 立即调用 + 主动输出 | 调用 + 缓存结果 | 不调用 |
| **忙碌/低可打扰** | 调用 + 缓存等待窗口 | 不调用，记录事件 | 不调用 |
| **完全不可打扰** | 调用 + 紧急时震动 | 不调用 | 不调用 |
| **安全紧急** | 立即调用 + 无视打扰约束 | 立即调用 | 不调用 |

#### 主动服务时序图

```
时间 →

传感器: ━━━━━━[事件A]━━━━━━━━━━[事件B]━━━━━━━━━━[事件C]━━━
                 │                    │                    │
评估:      importance=0.4       importance=0.8       importance=0.3
           user=busy            user=idle            user=busy
                 │                    │                    │
决策:         不调用               ✓ 调用                不调用
                                      │
Compiler:                        检索→排序→拼接→调用LLM
                                      │
输出:                            语音提醒用户
                                      │
反馈:                            用户点头确认 → 更新记忆
```

---

### 6.7 不同硬件形态的 Compiler 策略差异

| 维度 | AI 眼镜 | AI 耳机 | AI Pin | 机器人 |
|------|---------|---------|--------|--------|
| **主要调用模型** | VLM + LLM | LLM | LLM | VLA + LLM |
| **主要输入** | 视觉+语音 | 语音 | 语音+位置 | 视觉+触觉+状态 |
| **Context 刷新频率** | 高 (视觉流) | 中 (对话流) | 低 (事件驱动) | 极高 (动作循环) |
| **Token Budget 压力** | 高 (视觉描述开销大) | 低 (语音简洁) | 低 | 极高 (多模态) |
| **隐私过滤强度** | 极高 (拍摄他人) | 高 (录音) | 中 | 中 (家庭场景) |
| **主动触发频率** | 中 (场景变化触发) | 高 (对话间隙触发) | 低 (事后触发) | 高 (持续规划) |
| **延迟要求** | <500ms | <300ms | <2s | <100ms |
| **Ranker 权重侧重** | SpatialRelevance↑ | Recency↑ | Recency↑ | Actionability↑ |
| **输出约束** | 社交得体性 | 极简(1-3词) | 事后推送 | 物理安全 |

---

### 6.8 Compiler 性能与质量指标

| 指标 | 定义 | 目标值 | 测量方式 |
|------|------|--------|----------|
| **Compilation Latency** | 从触发到 prompt 生成完成的时间 | <200ms | 端到端计时 |
| **Retrieval Precision** | 检索到的记忆中相关的比例 | >0.8 | 人工标注 |
| **Budget Utilization** | 实际使用 token / 分配 budget | 0.6-0.8 | 自动统计 |
| **Safety Compliance** | 安全约束在输出中的遵守率 | >0.99 | 规则检查 |
| **User Satisfaction** | 主动服务的用户满意度 | >0.7 | 反馈统计 |
| **False Trigger Rate** | 不应触发但触发的比例 | <0.1 | 日志分析 |
| **Missed Trigger Rate** | 应触发但未触发的比例 | <0.2 | 回溯评估 |

## 7. 对智能硬件 Context 管理的启发

| 设计决策 | 理由 | 依据 |
|----------|------|------|
| 9步 Pipeline 而非简单检索→拼接 | 硬件需要触发判断、隐私过滤、主动决策等额外步骤 | Phase 4-5 分析 |
| Ranker 使用 9 维度而非简单语义相似度 | 硬件场景需要空间、时间、隐私、打扰代价等维度 | Phase 1 行为特性 |
| 根据设备形态自适应 Ranker 权重 | 眼镜重空间、耳机重时间、机器人重可执行性 | 各设备特性分析 |
| Prompt 结构遵循"首尾高注意力"模式 | Lost in the Middle + Recency Bias | Phase 1 现象 1,10 |
| 安全约束必须在 prompt 末尾重申 | Instruction Decay + Recency Bias 组合 | Phase 1 现象 3,10 |
| VLA 使用双层 Context 架构 | 规划(低频/高级)与动作(高频/底层)需求截然不同 | S037, S038 |
| 主动服务需要"Pre-flight Check" | 错误触发的代价(打扰)远高于延迟响应 | S036 + 产品原则 |

## 8. 与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| Phase 1 | 12 条行为特性 → 本阶段 Prompt Packing 的核心约束 |
| Phase 2 | 软件 Prompt Assembly 模板 → 本阶段硬件版扩展 |
| Phase 3 | Generative Agents 三维度检索 → Ranker 设计基础 |
| Phase 4 | Context Object → Compiler 的输入数据结构 |
| Phase 5 | 七层记忆 → Compiler 从各层检索的策略 |
| → Phase 7 | 各硬件案例是本架构的具体实例化和验证 |
| → Phase 8 | Compiler Pipeline 是最终架构图的核心组件 |

## 9. 尚不确定或证据不足的问题

1. **Ranker 权重应该是固定的还是可学习的？** — 可学习权重需要用户反馈数据，冷启动如何处理？
2. **主动服务的 InvocationThreshold 最优值** — 太低则打扰频繁，太高则错过重要事件。需要 A/B 测试。
3. **Compilation Latency <200ms 在端侧是否可行** — 检索+排序+拼接的计算开销在低功耗芯片上的表现？
4. **多模态 prompt 的 token 计数** — VLM 中图像 token 的计算方式不同厂商不一致。
5. **Context Ranker 的可解释性** — 用户询问"为什么推荐这个"时能否解释排序逻辑？
6. **长期运行的 Compiler 状态漂移** — 是否需要定期重置/校准 Ranker 参数？

## 10. 下一阶段建议

Phase 7 应该：

1. **用四类硬件设备验证 Compiler Pipeline** — 眼镜/耳机/Pin/机器人各跑一遍完整链路
2. **为每类设备实例化 Ranker 权重和 Budget 分配** — 不同设备侧重不同
3. **设计每类设备的主动服务场景** — 具体的触发条件和输出方式
4. **对比实际产品** — Meta Ray-Ban、Humane AI Pin、Friend pendant、各类机器人
5. **识别每类设备独有的 Context 管理挑战** — 隐私、延迟、打扰、安全
