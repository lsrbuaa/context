# Phase 5：智能硬件分层记忆架构设计

## 1. 阶段研究目标

基于 Phase 3（记忆框架研究）和 Phase 4（硬件输入 Context 化）的成果，设计一个面向智能硬件的**七层记忆架构**。本阶段核心任务：

- 从 CoALA 的四层模型扩展为硬件适用的七层架构
- 为每层记忆设计具体的数据结构
- 定义每层的写入触发条件和遗忘规则
- 设计层间的升级/降级路径（Episode → Semantic 归纳等）
- 设计 Governance Memory 的隐私和元信息管理
- 定义记忆冲突的解决策略
- 确保用户对记忆系统拥有完整的可控性

## 2. 核心问题清单

1. 七层记忆各自存储什么？边界如何划定？
2. Perception Working Memory 和 Task Working Memory 为什么要区分？
3. 哪些信息只应停留在短期缓存？
4. 什么事件值得写入 episodic memory？阈值如何设定？
5. 多次 episode 如何归纳为 semantic memory 或 habit profile？
6. 哪些习惯应变成 procedural memory（行为规则）？
7. 每条记忆是否应包含来源、置信度、过期时间、隐私策略？
8. 记忆冲突时是覆盖、降权、并存还是询问用户？
9. 用户如何查看、修改、删除或冻结记忆？

## 3. 检索关键词

| 方向 | 关键词 |
|------|--------|
| 认知架构 | cognitive memory hierarchy, Atkinson-Shiffrin, Tulving memory |
| 工程实现 | memory lifecycle management, memory write policy, forgetting mechanism |
| 隐私治理 | data governance, right to be forgotten, memory provenance |
| 硬件约束 | on-device storage, edge memory, memory-constrained systems |
| 记忆巩固 | memory consolidation, episodic to semantic, habit formation |

## 4. 资料来源清单

| ID | 类型 | 标题 | 作者/机构 | 年份 | 核心贡献 |
|----|------|------|-----------|------|----------|
| S022 | paper | CoALA: Cognitive Architectures for Language Agents | Sumers et al. | 2023 | 四层记忆分类理论基础 |
| S020 | paper | Generative Agents | Park et al. | 2023 | Reflection 机制（episode→semantic 归纳） |
| S021 | paper | Reflexion | Shinn et al. | 2023 | 失败反思→procedural memory 路径 |
| S034 | paper | Memory Consolidation in Cognitive Architectures | (认知科学) | 多年 | 记忆巩固的认知科学基础 |
| S007 | paper | The Reversal Curse | Berglund et al. | 2023 | 双向索引设计的理论依据 |
| S035 | regulation | GDPR Article 17 - Right to Erasure | EU | 2018 | 用户删除记忆的法律基础 |

## 5. 证据矩阵

| 论断 | 支撑资料 | 证据强度 |
|------|----------|----------|
| Agent 记忆可分为 Working/Episodic/Semantic/Procedural 四层 | S022 (CoALA) | 强 |
| Reflection 可将多个 episode 归纳为高层洞察 | S020 (Generative Agents) | 强 |
| 失败经验反思可转化为 procedural memory | S021 (Reflexion) | 强 |
| 单向存储的知识无法反向检索（需双向索引） | S007 (Reversal Curse) | 强 |
| 用户有权要求删除其个人数据（被遗忘权） | S035 (GDPR Art.17) | 强(法规) |
| 需要区分 Perception WM 和 Task WM（认知科学双重 WM 模型） | 认知科学文献 | 中 |
| Governance Memory 是现有框架的共同缺失（Phase 3 结论） | Phase 3 否定性证据 | 强 |

## 6. 关键发现

### 6.1 七层记忆架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Layer 7: Governance Memory (元记忆层)                           │
│  每条记忆的来源、置信度、权限、过期策略、审计轨迹                 │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ 覆盖所有其他层 ─ ─ ─ ─ ─ ─ ─ ─ ─         │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 1: Raw Sensor Buffer                              │    │
│  │  原始传感器数据的短期环形缓存 (端侧, <1min)              │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓ perception                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 2: Perception Working Memory                      │    │
│  │  当前感知状态：场景、人物、环境 (端侧, 实时)             │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓ task context                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 3: Task Working Memory                            │    │
│  │  当前任务状态：目标、计划、中间结果 (context window)      │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓ event complete                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 4: Episodic Memory                                │    │
│  │  具体事件记录：时间、地点、人物、内容 (外部存储)          │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         ↓ consolidation                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 5: Semantic Memory                                │    │
│  │  抽象知识：用户画像、人物关系、地点知识 (外部存储)        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Layer 6: Procedural Memory                              │    │
│  │  行为规则：if-then 策略、习惯模式、服务规则 (外部存储)    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 各层详细定义

| 层级 | 名称 | 定义 | 容量 | 生命周期 | 存储位置 |
|------|------|------|------|----------|----------|
| L1 | Raw Sensor Buffer | 原始传感器数据的环形缓存 | 有限 (~30s-1min) | 秒级 | 端侧 RAM |
| L2 | Perception Working Memory | 当前感知场景的结构化表示 | 有限 (~当前场景) | 分钟级 | 端侧 RAM |
| L3 | Task Working Memory | 当前任务的活跃上下文 | Context Window | 任务级 | Context Window |
| L4 | Episodic Memory | 具体事件的结构化记录 | 大 (数万条) | 天-月级 | 端侧存储+云端 |
| L5 | Semantic Memory | 抽象知识、画像、关系 | 中 (数千条) | 月-年级 | 端侧+云端 |
| L6 | Procedural Memory | 行为规则和策略 | 小 (数百条) | 长期稳定 | 端侧+云端 |
| L7 | Governance Memory | 元信息：来源、权限、审计 | 跟随所有记忆 | 与被治理记忆同步 | 附属于各层 |

### 6.3 为什么需要区分 Perception WM 和 Task WM？

| 维度 | Perception Working Memory (L2) | Task Working Memory (L3) |
|------|-------------------------------|--------------------------|
| 内容 | "我现在看到/听到什么" | "我现在在做什么任务" |
| 更新频率 | 实时（每秒） | 任务级（每分钟-小时） |
| 来源 | 传感器直接输入 | 任务规划 + 记忆检索 + 用户请求 |
| 持续时间 | 场景切换即清除 | 任务完成或切换时清除 |
| 对应认知概念 | 感觉记忆 + 知觉表征 | Baddeley 工作记忆模型 |
| 在 LLM prompt 中 | 不直接进入（太底层） | 构成 prompt 的核心动态内容 |
| 硬件示例 | "面前有一个人在说话" | "正在帮用户整理今天的会议记录" |

分离理由：传感器数据的更新频率（实时）远高于任务状态的更新频率（分钟级）。如果混在一起，每次传感器更新都要重构任务上下文，造成不必要的计算开销。

---

### 6.4 各层数据结构

#### Layer 1: Raw Sensor Buffer

```json
{
  "buffer_type": "ring_buffer",
  "capacity": "30_seconds",
  "segments": [
    {
      "timestamp": "2026-06-23T14:30:00.000+08:00",
      "modality": "audio",
      "format": "PCM_16bit_16kHz",
      "data_ref": "buffer://audio/current",
      "size_bytes": 960000
    }
  ],
  "retention_policy": "overwrite_oldest",
  "privacy": "never_persisted_to_disk"
}
```

#### Layer 2: Perception Working Memory

```json
{
  "perception_id": "pwm_current",
  "last_updated": "2026-06-23T14:30:45+08:00",
  "scene": {
    "location": "office_meeting_room_3F_B",
    "activity": "group_discussion",
    "people_present": ["contact_zhang", "unknown_1"],
    "objects_notable": ["whiteboard_with_diagram", "laptops"],
    "ambient": {"noise_level": 0.3, "lighting": "bright"}
  },
  "user_state": {
    "posture": "sitting",
    "attention": "focused_on_speaker",
    "speaking": false,
    "interruptibility": "low"
  },
  "change_flags": {
    "scene_changed": false,
    "new_person": false,
    "activity_changed": false,
    "last_significant_change": "2026-06-23T14:25:00+08:00"
  }
}
```

#### Layer 3: Task Working Memory

```json
{
  "task_id": "twm_active",
  "current_task": {
    "type": "passive_listening",
    "description": "用户在会议中，系统待命",
    "trigger_conditions": ["user_addressed", "keyword_detected", "meeting_end"]
  },
  "context_for_llm": {
    "scene_summary": "3F会议室B，张工在讨论API对接进度",
    "relevant_memories": ["mem_ep_0041", "mem_sem_api_project"],
    "pending_actions": [],
    "constraints": ["do_not_interrupt", "meeting_mode"]
  },
  "session_history": [
    {"role": "system_event", "content": "Meeting started at 14:00", "ts": "14:00"}
  ]
}
```

#### Layer 4: Episodic Memory

```json
{
  "memory_id": "mem_ep_0042",
  "type": "episodic",
  "created_at": "2026-06-23T15:05:00+08:00",
  "last_accessed": "2026-06-23T15:05:00+08:00",
  "access_count": 0,
  
  "event": {
    "summary": "张工在周一会议上确认 API 对接截止日期为下周三",
    "timestamp_start": "2026-06-23T14:30:00+08:00",
    "timestamp_end": "2026-06-23T14:31:00+08:00",
    "location": "office_meeting_room_3F_B",
    "people": ["contact_zhang"],
    "activity_type": "work_meeting",
    "importance_score": 0.82
  },
  
  "content": {
    "transcript_snippet": "张工：下周三前我们需要完成 API 对接",
    "extracted_items": [
      {"type": "deadline", "content": "API 对接完成", "due": "2026-06-30"}
    ]
  },
  
  "embeddings": {
    "text_vector": "[...]",
    "temporal_vector": "[...]",
    "spatial_vector": "[...]"
  },
  
  "governance": {
    "source": "audio_transcription",
    "confidence": 0.88,
    "privacy_level": "private",
    "contains_others_data": true,
    "expires_at": null,
    "user_verified": false
  }
}
```

#### Layer 5: Semantic Memory

```json
{
  "memory_id": "mem_sem_0103",
  "type": "semantic",
  "created_at": "2026-06-15T00:00:00+08:00",
  "last_updated": "2026-06-23T15:10:00+08:00",
  "access_count": 12,
  
  "category": "person_profile",
  "subject": "contact_zhang",
  "content": {
    "name": "张工",
    "relationship": "colleague",
    "department": "技术部",
    "topics": ["API开发", "后端架构", "项目管理"],
    "interaction_frequency": "daily",
    "communication_style": "直接、注重细节"
  },
  
  "derived_from": ["mem_ep_0012", "mem_ep_0023", "mem_ep_0035", "mem_ep_0042"],
  "confidence": 0.92,
  
  "bidirectional_index": {
    "forward": "张工 → 技术部同事",
    "reverse": "技术部同事 → 张工"
  },
  
  "governance": {
    "source": "inferred_from_episodes",
    "last_verified": "2026-06-20",
    "privacy_level": "private",
    "user_editable": true
  }
}
```

#### Layer 6: Procedural Memory

```json
{
  "memory_id": "mem_proc_0015",
  "type": "procedural",
  "created_at": "2026-06-10T00:00:00+08:00",
  "last_triggered": "2026-06-23T14:00:00+08:00",
  "trigger_count": 18,
  
  "rule": {
    "name": "meeting_mode_activation",
    "description": "会议期间切换为静默模式",
    "condition": {
      "trigger": "calendar_event_start AND location_match(meeting_room)",
      "confidence_threshold": 0.8
    },
    "action": {
      "set_interruptibility": "none",
      "output_mode": "haptic_only",
      "record_mode": "meeting_summary",
      "suppress_notifications": true
    },
    "exceptions": [
      "urgent_call_from_family",
      "safety_alert"
    ]
  },
  
  "evidence": {
    "derived_from": "user_explicit_setting + 5_consistent_behaviors",
    "success_rate": 0.94,
    "last_user_override": null
  },
  
  "governance": {
    "source": "user_explicit + behavior_inferred",
    "user_modifiable": true,
    "priority": "high"
  }
}
```

#### Layer 7: Governance Memory (附属于其他层)

```json
{
  "governed_memory_id": "mem_ep_0042",
  "governance_record": {
    "provenance": {
      "source_device": "smart_glasses_v2",
      "source_sensors": ["microphone"],
      "processing_pipeline": "端侧VAD → 云端ASR → 实体抽取",
      "model_versions": {"asr": "whisper-v3", "extraction": "claude-haiku"}
    },
    "confidence": {
      "overall": 0.88,
      "breakdown": {"asr_accuracy": 0.92, "extraction_accuracy": 0.85}
    },
    "privacy": {
      "classification": "private",
      "contains_pii": true,
      "contains_others_data": true,
      "consent_status": "implicit_user_only",
      "storage_location": "encrypted_cloud",
      "encryption_method": "AES-256"
    },
    "lifecycle": {
      "created_at": "2026-06-23T15:05:00+08:00",
      "expires_at": null,
      "retention_policy": "until_user_deletes",
      "last_accessed": "2026-06-23T15:05:00+08:00",
      "access_log": [{"by": "context_compiler", "at": "2026-06-23T15:05:00"}]
    },
    "user_controls": {
      "viewable": true,
      "editable": true,
      "deletable": true,
      "shareable": false,
      "freezable": true
    }
  }
}
```

---

### 6.5 记忆写入策略

#### 写入触发条件

| 目标层 | 触发条件 | 来源 | 写入决策者 |
|--------|----------|------|-----------|
| L1 Raw Buffer | 持续（传感器开启即写入） | 传感器 | 系统自动 |
| L2 Perception WM | 感知结果更新（场景/人物/活动变化） | L1 处理后 | 端侧模型 |
| L3 Task WM | 用户请求/系统触发/任务状态变更 | 多来源 | Context Compiler |
| L4 Episodic | 事件结束 + importance_score > 阈值 | L2/L3 事件 | 重要性评估模型 |
| L5 Semantic | 多个 episode 呈现一致模式 (≥N次) | L4 归纳 | 归纳模型(定期运行) |
| L6 Procedural | 用户显式设置 OR 行为重复≥5次且成功率>90% | 用户/L4 | 用户确认/系统推荐 |
| L7 Governance | 任何记忆被创建/修改/访问时 | 所有层操作 | 系统自动 |

#### 写入阈值设计

```
Episodic Memory 写入条件:
  importance_score ≥ 0.6
  AND confidence ≥ 0.7
  AND NOT duplicate_of_existing
  AND privacy_check_passed

Semantic Memory 归纳条件:
  related_episodes ≥ 3
  AND pattern_consistency ≥ 0.8
  AND time_span ≥ 7 days (避免短期偏差)

Procedural Memory 生成条件:
  (user_explicit_rule)
  OR (repeated_behavior ≥ 5 times AND success_rate ≥ 0.9)
```

---

### 6.6 记忆遗忘与衰减机制

#### 各层遗忘策略

| 层级 | 遗忘策略 | 触发条件 | 衰减速度 |
|------|----------|----------|----------|
| L1 | 环形覆盖 | 缓存满 (30s-1min) | 即时 |
| L2 | 场景切换清除 | 新场景检测 | 即时 |
| L3 | 任务结束归档 | 任务完成/切换 | 即时 |
| L4 | 时间衰减 + 访问衰减 | 长期未访问 | 半衰期 30 天 |
| L5 | 证据失效 | 相关 episode 被删/被否 | 手动或自动 |
| L6 | 成功率下降 | 规则多次触发但被用户否决 | 3 次否决即停用 |
| L7 | 跟随被治理记忆 | 主记忆删除时同步清理 | 同步 |

#### Episodic Memory 衰减公式

```
MemoryWeight(t) = BaseImportance × RecencyFactor(t) × AccessFactor

RecencyFactor(t) = exp(-λ × days_since_creation)
  λ = 0.023 (半衰期 ≈ 30 天)

AccessFactor = 1 + log(1 + access_count)
  每次被检索/使用，access_count += 1

阈值: MemoryWeight < 0.1 → 候选归档
      MemoryWeight < 0.01 → 候选删除
```

#### 压缩归纳（Episode → Semantic 的路径）

```
定期巩固任务 (每日/空闲时运行):

1. 扫描近期 episodic memories
2. 聚类相似 episode (按人物/地点/活动)
3. 检测重复模式:
   - 同一人物出现 ≥ 3 次 → 候选生成 person profile (L5)
   - 同一地点+活动 ≥ 3 次 → 候选生成 place habit (L5)
   - 同一时间+动作 ≥ 5 次 → 候选生成 procedural rule (L6)
4. 生成候选 semantic/procedural memory
5. 低风险的自动写入，高风险的询问用户确认
6. 归纳完成后，原始 episode 降权（不删除，但权重降低）
```

---

### 6.7 记忆冲突解决策略

| 冲突类型 | 示例 | 解决策略 |
|----------|------|----------|
| **新旧事实冲突** | 记忆说"用户不喝咖啡" vs 今天看到用户买咖啡 | 新证据优先，旧记忆标记 conflict |
| **多源不一致** | 视觉说"无人" vs 蓝牙说"张工手机在附近" | 保留两条，标注 confidence，不强行合并 |
| **推断 vs 显式** | 系统推断"用户喜欢安静" vs 用户说"我喜欢音乐" | 用户显式声明 > 系统推断 |
| **时效性冲突** | 去年的偏好 vs 今天的行为 | 近期行为权重更高 |
| **隐私冲突** | 记忆有价值但含旁人信息 | 保留脱敏版本，删除原始 |

冲突解决优先级：
```
用户显式声明 > 高置信度传感器 > 近期数据 > 多次验证的推断 > 单次推断 > 旧数据
```

---

### 6.8 用户记忆控制权

#### 用户可执行的操作

| 操作 | 描述 | 影响范围 |
|------|------|----------|
| **查看** | 浏览所有记忆，按类型/时间/人物筛选 | 只读 |
| **编辑** | 修改记忆内容（纠正错误） | 更新记忆+记录编辑历史 |
| **删除** | 永久删除单条记忆 | 删除记忆+Governance 记录标记 |
| **批量删除** | 删除某时段/某地点/某人相关的所有记忆 | 级联删除 |
| **冻结** | 记忆不再被自动更新或遗忘 | 停止衰减和覆盖 |
| **导出** | 导出个人记忆数据 (GDPR portability) | 生成数据包 |
| **暂停** | 临时停止记忆系统 | 不写入任何新记忆 |
| **设置规则** | 定义"永远不要记住X"的规则 | 写入 L6 作为负向规则 |

#### 记忆透明度设计

```
用户界面应提供:
├── "今日新记忆" 摘要 (每日推送)
├── "系统认为你..." 推断记忆确认
├── "即将遗忘" 通知 (重要记忆衰减前询问)
├── "记忆来源" 溯源 (点击任意记忆可查来源)
└── "记忆健康度" 仪表盘 (各层容量/质量/新鲜度)
```

---

### 6.9 层间数据流图

```
传感器 ──→ [L1: Raw Buffer] ──→ (处理后丢弃)
                │
                ↓ 感知处理
          [L2: Perception WM] ──→ (场景切换时清除)
                │
                ↓ 构建任务上下文
          [L3: Task WM] ──→ (任务结束时归档)
                │
                ↓ 事件完成 + importance > threshold
          [L4: Episodic Memory] ←──── (时间衰减)
                │
                ↓ 多次 episode 归纳 (定期巩固)
          [L5: Semantic Memory] ←──── (证据失效衰减)
                │
                ↓ 行为模式固化 (高重复+高成功率)
          [L6: Procedural Memory] ←──── (用户否决停用)

          [L7: Governance] ←──── 附属于所有层的每条记忆
```

**反向流:**
```
L5 Semantic → L3 Task WM   (检索用户偏好注入任务 context)
L4 Episodic → L3 Task WM   (检索相关事件注入任务 context)
L6 Procedural → L2/L3      (规则约束当前行为/任务)
L7 Governance → 检索过滤   (隐私级别限制记忆的可检索性)
```

---

### 6.10 存储规模估算

| 层级 | 典型条目数 | 单条大小 | 总存储 | 存储位置 |
|------|-----------|----------|--------|----------|
| L1 | N/A (流式) | N/A | ~50 MB RAM | 端侧 RAM |
| L2 | 1 (当前场景) | ~2 KB | ~2 KB | 端侧 RAM |
| L3 | 1 (当前任务) | ~10 KB | ~10 KB | 端侧 RAM / Context |
| L4 | 10,000-50,000 | ~1 KB | 10-50 MB | 端侧 Flash + 云端 |
| L5 | 1,000-5,000 | ~0.5 KB | 0.5-2.5 MB | 端侧 Flash + 云端 |
| L6 | 100-500 | ~0.3 KB | 30-150 KB | 端侧 Flash + 云端 |
| L7 | 随 L4-L6 | ~0.2 KB/条 | 2-10 MB | 随主记忆 |

**总计:** 端侧 ~100 MB（含 L4 热数据），云端 ~50 MB（全量备份）——完全在现代移动设备能力范围内。

## 7. 对智能硬件 Context 管理的启发

| 架构决策 | 设计理由 | 依据 |
|----------|----------|------|
| 七层而非四层 | 硬件需要区分原始缓存/感知状态/任务状态（软件不需要） | Phase 4 分析 |
| 独立 Governance 层 | 现有框架共同缺失，而硬件隐私要求远高于软件 | Phase 3 结论 |
| 端侧+云端混合存储 | 隐私敏感数据(L1-L2)必须端侧，大容量(L4-L5)需要云端 | Phase 4 端云分工 |
| 双向索引 | Reversal Curse 要求记忆支持正反向检索 | Phase 1 现象8 |
| 定期巩固 | 模拟人类睡眠巩固，设备空闲时归纳 episode→semantic | Phase 3 认知科学 |
| 用户完全可控 | GDPR 被遗忘权 + 用户信任需求 | 法规 + 产品原则 |

## 8. 与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| Phase 3 | 承接 CoALA 四层模型 + Generative Agents Reflection + Reflexion 机制 |
| Phase 4 | 承接 Context Object 定义 → L4 Episodic 的输入格式 |
| → Phase 6 | 直接输出：Context Compiler 从 L2-L6 检索记忆组装 prompt |
| → Phase 7 | 各硬件设备的 memory strategy 是本架构的实例化 |
| → Phase 8 | Memory Object JSON Schema 基于本阶段数据结构 |

## 9. 尚不确定或证据不足的问题

1. **Perception WM 和 Task WM 的精确分界** — 某些场景下两者重叠（如"看到什么"就是"任务需要知道的"），需要具体实现时验证
2. **Episode→Semantic 归纳的准确率** — 自动归纳可能产生错误的 semantic memory，需要什么程度的用户确认？
3. **衰减半衰期 30 天是否合适** — 不同类型的 episode 可能需要不同衰减速度（工作 vs 生活）
4. **端侧存储 100MB 是否足够** — 重度使用场景（全天记录设备）可能需要更多空间或更积极的压缩
5. **Governance Memory 的性能开销** — 每条记忆都附带 governance 记录是否会显著增加读写延迟？
6. **冲突解决的自动化程度** — 多少冲突可以自动解决，多少需要询问用户？过多询问会导致用户疲劳。

## 10. 下一阶段建议

Phase 6 应该：

1. **设计从七层记忆中检索和拼接 prompt 的完整 pipeline** — Context Compiler 的核心算法
2. **实现 Context Ranker** — 基于 Phase 3 Generative Agents 的三维度评分 + Phase 1 的 12 条约束
3. **设计 Token Budget 分配** — 基于 Phase 2 的分配模板适配硬件场景
4. **区分 LLM/VLM/VLA 三种不同的 prompt 需求** — 各自需要什么层的记忆
5. **设计主动服务的 context decision** — 什么时候系统应该主动调用 LLM
