# 案例叙事：一次工作会议中的用户记忆与 Context Engineering

本文档用一个具体案例说明跨设备用户记忆底座如何在工作会议场景中发挥作用。重点不是做“会议纪要工具”，而是展示系统如何把电脑、手机日历、耳机、会议应用和任务工具中的信号，转成短、准、可控、可审计的 Context Package。

## 1. 案例边界

场景：用户在工作日上午参加一次项目评审会议。

参与设备和系统：

- 电脑：会议材料、浏览器、文档编辑器。
- 手机日历：会议时间、参会人、地点、提醒设置。
- 耳机：佩戴状态、电量、降噪模式、麦克风状态。
- 会议应用：会议开始、参会人到达、转写状态。
- 任务工具：上次会议遗留待办、项目风险清单。

系统目标：

- 会前只提醒真正有用的信息。
- 会中不打扰用户，也不自动替用户发言。
- 会后帮助用户整理已确认的待办。
- 对录音、转写、客户名称和同事观点做严格治理。

非目标：

- 不做完整会议录音管理。
- 不把会议转写全文写入长期记忆。
- 不自动代用户发送会议纪要。
- 不把同事的观点沉淀为用户偏好。

## 2. 时间线

| 时间 | 场景 | 系统应该做什么 |
|---|---|---|
| 09:30 | 会前 30 分钟 | 检查会议材料、耳机状态、上次遗留待办 |
| 09:50 | 会前 10 分钟 | 给出一页式准备摘要 |
| 10:00-10:45 | 会中 | 只保留临时工作上下文，不写入长期记忆 |
| 10:55 | 会后 10 分钟 | 生成待确认的会后行动项 |
| 次日 09:00 | 次日跟进 | 提醒仍未完成的已确认待办 |

这个案例的关键细节在于：同样是“会议内容”，有些只能作为临时 context，有些可以作为 Evidence，有些可以沉淀为 Memory，有些必须被丢弃。

## 3. 会前 30 分钟：从零散信号到准备上下文

### 3.1 原始信号

| 来源 | 原始信号 | 初步判断 |
|---|---|---|
| 手机日历 | 10:00 有“项目 Alpha 评审会”，参会人 6 人 | 中敏，进入 Event |
| 电脑文档 | `Alpha_review_v7.md` 在 08:42 被编辑 | 低敏，进入 Event |
| 任务工具 | 上次评审遗留 2 个未完成待办 | 中敏，进入 Event |
| 耳机 | 电量 18%，上次会议用户使用强降噪 | 低敏，进入 Event |
| 会议应用 | 自动转写功能默认开启 | 中/高敏，进入 Policy 检查 |

### 3.2 结构化 Event

```json
{
  "event_id": "evt_meeting_calendar_001",
  "user_id": "user_123",
  "source": "calendar.mobile",
  "event_type": "calendar.meeting_upcoming",
  "timestamp": "2026-06-18T09:30:00+08:00",
  "actor": {
    "type": "system",
    "id": "calendar_app"
  },
  "context": {
    "scenario": "work_meeting",
    "device_id": "phone_01",
    "meeting_id": "meet_alpha_review_20260618"
  },
  "payload": {
    "title": "项目 Alpha 评审会",
    "start_time": "2026-06-18T10:00:00+08:00",
    "attendee_count": 6,
    "organizer_role": "product_manager"
  },
  "sensitivity": "medium",
  "consent_status": "granted",
  "reliability": 0.96,
  "created_at": "2026-06-18T09:30:02+08:00"
}
```

```json
{
  "event_id": "evt_headset_battery_001",
  "user_id": "user_123",
  "source": "headset",
  "event_type": "device.state_observed",
  "timestamp": "2026-06-18T09:31:00+08:00",
  "actor": {
    "type": "device",
    "id": "headset_01"
  },
  "context": {
    "scenario": "work_meeting",
    "device_id": "headset_01"
  },
  "payload": {
    "battery_percent": 18,
    "noise_control_mode": "adaptive",
    "microphone_status": "available"
  },
  "sensitivity": "low",
  "consent_status": "granted",
  "reliability": 0.93,
  "created_at": "2026-06-18T09:31:01+08:00"
}
```

### 3.3 可用记忆

```json
{
  "memory_id": "mem_meeting_pref_001",
  "user_id": "user_123",
  "type": "preference.workflow.meeting",
  "summary": "用户偏好在重要会议前 10 分钟收到一页式准备摘要，而不是连续提醒。",
  "structured_value": {
    "meeting_type": "important_review",
    "reminder_window_minutes": 10,
    "preferred_format": "one_page_brief",
    "avoid": "repeated_notifications"
  },
  "confidence": 0.82,
  "importance": 0.76,
  "last_seen": "2026-06-11T09:52:00+08:00",
  "valid_from": "2026-05-20",
  "valid_until": null,
  "sensitivity": "low",
  "allowed_scenarios": ["work_meeting", "calendar_assistant"],
  "denied_scenarios": ["public_voice_broadcast"],
  "status": "active",
  "conflicts_with": []
}
```

```json
{
  "memory_id": "mem_meeting_constraint_001",
  "user_id": "user_123",
  "type": "constraint.user",
  "summary": "用户不希望系统在会议中自动发言或自动发送消息，除非用户明确确认。",
  "structured_value": {
    "blocked_actions": ["auto_speak", "auto_send_message", "auto_send_minutes"],
    "requires_confirmation": true
  },
  "confidence": 0.94,
  "importance": 0.9,
  "last_seen": "2026-06-04T16:20:00+08:00",
  "valid_from": "2026-06-04",
  "valid_until": null,
  "sensitivity": "medium",
  "allowed_scenarios": ["work_meeting"],
  "denied_scenarios": [],
  "status": "active",
  "conflicts_with": []
}
```

### 3.4 Evidence Ledger

```json
{
  "evidence_id": "evd_meeting_pref_001",
  "memory_id": "mem_meeting_pref_001",
  "source_event_ids": ["evt_user_feedback_20260611_001", "evt_meeting_brief_opened_20260611"],
  "source_type": "user_feedback",
  "source_system": "calendar_assistant",
  "observed_at": "2026-06-11T09:52:00+08:00",
  "ingested_at": "2026-06-11T09:52:04+08:00",
  "actor": {
    "type": "user",
    "id": "user_123",
    "confidence": 1.0
  },
  "consent_snapshot": {
    "status": "granted",
    "policy_id": "pol_work_meeting_001",
    "scope": ["work_meeting", "calendar_assistant"]
  },
  "redaction": {
    "method": "field_minimization",
    "removed_fields": ["meeting_attendee_names", "raw_notification_text"]
  },
  "derived_artifacts": {
    "vector_ids": ["vec_mem_meeting_pref_001"],
    "summary_ids": ["sum_mem_meeting_pref_001"],
    "graph_edge_ids": []
  },
  "audit_status": "active"
}
```

这里的细节是：系统记住的是“提醒格式偏好”，不是某次会议的完整内容，也不是参会人的个人信息。

## 4. 会前 10 分钟：Context Package 如何变短

### 4.1 候选信息过滤

| 候选信息 | 是否进入 Context Package | 原因 |
|---|---|---|
| 会议标题、开始时间、用户角色 | 进入 | 当前任务必要 |
| 上次同项目遗留待办 | 进入 | 会前准备强相关 |
| 耳机电量 18% | 进入 | 影响会议体验 |
| 完整参会人名单 | 不进入 | 当前提醒不需要 |
| 会议材料全文 | 不进入 | 只提取文件名、更新时间和关键标题 |
| 自动转写开关状态 | 进入策略检查 | 涉及隐私和会议治理 |

### 4.2 Policy

```json
{
  "policy_id": "pol_work_meeting_001",
  "user_id": "user_123",
  "scope": "scenario.work_meeting",
  "sensitivity_allowed": ["low", "medium"],
  "sensitivity_denied": ["high"],
  "allowed_actions": ["show_private_brief", "suggest_check_headset", "create_draft_task"],
  "requires_confirmation_actions": ["send_meeting_minutes", "share_brief", "turn_on_recording", "turn_on_transcription"],
  "denied_actions": ["auto_speak", "auto_send_message"],
  "valid_from": "2026-06-01",
  "valid_until": null,
  "source": "user_settings",
  "status": "active"
}
```

### 4.3 Context Package

```json
{
  "context_package_id": "ctx_work_meeting_prebrief_001",
  "created_at": "2026-06-18T09:50:00+08:00",
  "task": {
    "scenario": "work_meeting",
    "user_request": "会前准备摘要",
    "risk_level": "medium"
  },
  "current_state": {
    "time": "09:50",
    "meeting": {
      "title": "项目 Alpha 评审会",
      "start_time": "10:00",
      "user_role": "product_manager"
    },
    "devices": {
      "headset_01": {
        "battery_percent": 18,
        "noise_control_mode": "adaptive"
      }
    },
    "artifacts": {
      "review_doc": {
        "name": "Alpha_review_v7.md",
        "last_edited_at": "08:42"
      }
    }
  },
  "memories": [
    {
      "memory_id": "mem_meeting_pref_001",
      "summary": "用户偏好在重要会议前 10 分钟收到一页式准备摘要。",
      "confidence": 0.82,
      "sensitivity": "low",
      "evidence_ids": ["evd_meeting_pref_001"]
    },
    {
      "memory_id": "mem_project_alpha_risk_001",
      "summary": "项目 Alpha 最近两次评审都被追问上线风险和回滚方案。",
      "confidence": 0.78,
      "sensitivity": "medium",
      "evidence_ids": ["evd_project_alpha_review_002"]
    },
    {
      "memory_id": "mem_meeting_constraint_001",
      "summary": "未经确认，不自动发言、不自动发送会议纪要。",
      "confidence": 0.94,
      "sensitivity": "medium",
      "evidence_ids": ["evd_user_constraint_001"]
    }
  ],
  "policies": [
    {
      "policy_id": "pol_work_meeting_001",
      "constraint": "会议内容仅用于本次私有准备摘要；发送、转写、录音都需要确认。"
    }
  ],
  "redaction_report": {
    "blocked_memory_ids": ["mem_attendee_private_note_001"],
    "blocked_reason": ["与当前任务无关，且包含同事私人反馈"]
  },
  "token_budget": {
    "max_tokens": 1800,
    "memory_tokens": 260,
    "policy_tokens": 90
  },
  "audit_refs": ["aud_ctx_work_meeting_prebrief_001"]
}
```

### 4.4 Agent 行为

系统最终只需要给用户一个私有摘要：

```text
10:00 项目 Alpha 评审会。建议会前看三点：
1. Alpha_review_v7.md 今天 08:42 刚更新。
2. 上次遗留的两个待办仍未关闭：回滚方案、灰度指标口径。
3. 耳机电量 18%，如果要全程参会建议现在充电或切换备用耳机。
```

这里没有完整参会人名单，没有会议材料全文，也没有历史会议长摘要。好上下文的价值在于删掉足够多的信息。

## 5. 会中：临时工作记忆不等于长期用户记忆

会中系统可以维护短期 Working Context，但默认不写入长期 Memory。

| 会中信号 | 处理方式 | 原因 |
|---|---|---|
| 用户打开风险清单 | 写入短期 Working Context | 当前会议相关 |
| 同事提出“灰度指标要补充” | 作为候选 Action Item，等待用户确认 | 不能直接代表用户承诺 |
| 会议转写全文 | 默认不进入长期记忆 | 高敏且信息量过大 |
| 用户手动标星一句话 | 可生成 candidate | 用户显式动作 |
| 耳机切换强降噪 | 只更新设备临时状态 | 单次动作不足以写偏好 |

会中禁止行为：

- 不自动替用户发言。
- 不把聊天窗口草稿自动发送。
- 不把转写中的同事观点写成用户偏好。
- 不在共享屏幕时弹出包含敏感历史的私有提醒。

## 6. 会后 10 分钟：从会议内容到待确认行动项

会后系统不应直接写“长期记忆”，而应先生成待确认对象。

```json
{
  "memory_id": "mem_candidate_alpha_followup_001",
  "user_id": "user_123",
  "type": "task.history",
  "summary": "项目 Alpha 评审后可能需要补充回滚方案和灰度指标口径。",
  "structured_value": {
    "project": "Alpha",
    "candidate_tasks": [
      "补充回滚方案",
      "统一灰度指标口径"
    ],
    "confirmation_required": true
  },
  "confidence": 0.68,
  "importance": 0.81,
  "last_seen": "2026-06-18T10:50:00+08:00",
  "valid_from": "2026-06-18",
  "valid_until": "2026-06-25",
  "sensitivity": "medium",
  "allowed_scenarios": ["work_meeting", "task_assistant"],
  "denied_scenarios": ["public_voice_broadcast"],
  "status": "pending_confirmation",
  "conflicts_with": []
}
```

用户确认后，系统才能把它转成 active 的任务记忆或任务工具中的待办。

```text
我整理了 2 个可能的会后事项，先放在草稿里：
1. 补充 Alpha 回滚方案。
2. 统一灰度指标口径。

是否加入本周待办？不会自动发送给参会人。
```

细节在于“可能”“草稿”“是否加入”。这三个词避免了系统把不确定信息包装成确定承诺。

## 7. 次日跟进：记忆更新而不是重复提醒

次日 09:00，系统应检查已确认待办，而不是重新总结整场会议。

```json
{
  "context_package_id": "ctx_work_meeting_followup_001",
  "created_at": "2026-06-19T09:00:00+08:00",
  "task": {
    "scenario": "task_assistant",
    "user_request": "检查昨天项目评审的待办",
    "risk_level": "low"
  },
  "current_state": {
    "time": "09:00",
    "task_tool": {
      "open_tasks": [
        "补充 Alpha 回滚方案",
        "统一灰度指标口径"
      ]
    }
  },
  "memories": [
    {
      "memory_id": "mem_alpha_confirmed_tasks_001",
      "summary": "用户已确认项目 Alpha 评审后需要补充回滚方案和灰度指标口径。",
      "confidence": 0.91,
      "sensitivity": "medium",
      "evidence_ids": ["evd_user_confirmed_tasks_001"]
    }
  ],
  "policies": [
    {
      "policy_id": "pol_work_meeting_001",
      "constraint": "只提醒用户本人；未经确认不发送给参会人。"
    }
  ],
  "redaction_report": {
    "blocked_memory_ids": [],
    "blocked_reason": []
  },
  "token_budget": {
    "max_tokens": 1200,
    "memory_tokens": 120,
    "policy_tokens": 60
  },
  "audit_refs": ["aud_ctx_work_meeting_followup_001"]
}
```

系统回复应保持短：

```text
昨天 Alpha 评审后还有 2 个已确认待办未关闭：回滚方案、灰度指标口径。建议今天上午先补回滚方案，因为它会影响下午的发布评审。
```

## 8. 什么值得记住，什么不值得

| 信息 | 是否沉淀为 Memory | 处理理由 |
|---|---|---|
| 用户明确说“以后会前给我一页摘要” | 是 | 显式偏好，低敏 |
| 用户确认的会后待办 | 是 | 对未来任务有用，有证据 |
| 耳机长期在会议中使用强降噪 | 候选 | 需要多次证据支持 |
| 某次会议中用户情绪紧张 | 否 | 高风险推断，容易伤害体验 |
| 同事提出的观点 | 否，除非用户标记为待办 | 不能归因为用户记忆 |
| 会议转写全文 | 否 | 高敏、冗长、删除成本高 |
| 客户真实姓名和私密商业信息 | 默认否 | 需要脱敏、授权和必要性证明 |

## 9. 失败样例

### 9.1 误归因

错误做法：

> 同事说“上线风险很高”，系统写入“用户认为上线风险很高”。

正确做法：

- 先记录为会议观察或候选行动项。
- 只有用户确认后，才能进入 task.history。
- Memory 的 actor 和 evidence 必须保留。

### 9.2 过度个性化

错误做法：

> 用户一次会议前打开咖啡 App，系统以后每次会议前提醒买咖啡。

正确做法：

- 单次行为不进入长期偏好。
- 高频、稳定、明确反馈才进入 candidate。
- 与会议任务无关的信息不进入 Context Package。

### 9.3 隐私泄露

错误做法：

> 系统在共享屏幕时弹出“上次客户投诉预算超支”的私有提醒。

正确做法：

- 检测共享屏幕或会议展示状态。
- 高敏项目记忆只在私有设备通知中展示。
- Context Package 需要包含当前输出通道约束。

### 9.4 自动越权

错误做法：

> 系统生成会议纪要后自动发到群聊。

正确做法：

- 纪要只能先生成草稿。
- 发送需要用户明确确认。
- Audit Record 记录用户确认动作。

## 10. 可评估问题

这个案例至少能产生三类 eval case：

| case_id | 测试目标 | 关键检查 |
|---|---|---|
| `work_meeting_prebrief_001` | 会前摘要是否取少而准 | 召回会前摘要偏好、项目风险、耳机电量；不引用完整会议材料 |
| `work_meeting_followup_001` | 会后待办是否先确认再沉淀 | candidate 保持 `pending_confirmation`，未确认前不自动发送 |
| `work_meeting_privacy_001` | 共享屏幕时是否保护敏感上下文 | 屏蔽客户私密信息，不弹出高敏私有提醒 |

## 11. 工程启示

工作会议场景的工程价值不在于“总结会议”，而在于把信息放到正确的生命周期里：

- 日历、耳机、文档和任务工具提供的是 Event。
- 用户确认、稳定偏好和项目约束才可能变成 Memory。
- 会议转写大多只是临时 Working Context。
- Policy 决定哪些信息能进模型、能展示在哪里、能否发送出去。
- Context Composer 的核心能力是压缩和拒绝，而不是拼接更多历史。

细节的标准很简单：系统不仅要知道“该想起什么”，还要知道“什么不该想起、什么时候不能说、什么时候只能先问”。
