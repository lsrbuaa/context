# 案例研究：桌面机器人 / 家庭机器人 / VLA 机器人

## 产品定位

具身智能体，通过空间感知、动作执行和持续学习，在物理世界中执行任务并主动服务用户。

## Context 管理链路

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  视觉+深度+触觉  │────→│  环境状态感知     │────→│  任务规划        │
│  + 关节状态      │     │  物体/空间理解    │     │  (LLM Context)   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                        ┌──────────────────┐               │
                        │  程序性记忆       │←──────────────┤
                        │  (成功/失败经验)  │               │
                        └──────┬───────────┘               ↓
                               │               ┌─────────────────┐
                               └──────────────→│  动作生成        │
                                               │  (VLA Context)   │
                                               └────────┬────────┘
                                                        │
                                                        ↓
                                               ┌─────────────────┐
                                               │  执行 + 反馈     │
                                               │  → 记忆更新      │
                                               └─────────────────┘
```

## 双 Context 架构

机器人的核心特点是需要两层 context：

### High-level Planning Context (LLM)

```json
{
  "user_request": "帮我把桌上的杯子放到厨房",
  "environment_state": {
    "current_room": "客厅",
    "target_room": "厨房",
    "obstacles": ["地上有书包"],
    "object_location": "杯子在茶几右侧"
  },
  "user_preferences": {
    "cup_placement": "厨房水槽旁",
    "path_preference": "避开猫的区域"
  },
  "past_experience": {
    "similar_task_success_rate": 0.92,
    "known_failure_modes": ["茶几边缘容易碰倒其他物品"]
  },
  "task_decomposition": [
    "导航到茶几",
    "识别目标杯子",
    "规划抓取姿态",
    "抓取",
    "导航到厨房",
    "放置在水槽旁"
  ]
}
```

### Low-level Action Context (VLA)

```json
{
  "current_observation": "RGB-D image tensor",
  "joint_states": [0.1, -0.3, 0.8, 0.2, -0.1, 0.5, 0.0],
  "end_effector_pose": {"x": 0.4, "y": 0.1, "z": 0.3, "quat": [1,0,0,0]},
  "target_object": {
    "class": "cup",
    "estimated_pose": {"x": 0.6, "y": 0.2, "z": 0.1},
    "grasp_candidates": [...]
  },
  "action_constraints": {
    "max_force": 5.0,
    "collision_objects": ["other_cup", "book"],
    "workspace_bounds": {...}
  },
  "current_subtask": "approach_and_grasp"
}
```

## 典型场景

### 场景 A：日常物品整理

**触发条件**: 用户说"帮我收拾一下桌子" 或 检测到桌面混乱度超过阈值

**Context Assembly**:
- Visual: 桌面物品识别和位置
- Semantic Memory: 用户的物品归位偏好
- Procedural Memory: 上次整理的成功策略
- Constraints: 哪些东西不能动（用户正在使用的物品）

### 场景 B：从失败中学习

**触发条件**: 抓取杯子失败（滑落）

**Feedback Loop**:
1. 记录失败：物体类型（光滑陶瓷杯）+ 抓取策略（侧面抓取）+ 结果（滑落）
2. 更新 procedural memory：光滑陶瓷杯 → 改用顶部包围抓取
3. 下次遇到类似物体时，检索并应用新策略

### 场景 C：主动陪伴服务

**触发条件**: 检测到用户长时间久坐（> 2 小时）

**Context Assembly**:
- Activity Memory: 用户已坐 2.5 小时
- User Preferences: 用户设置了久坐提醒
- Procedural: 提醒方式 = 走到用户身边 + 语音提醒

**输出**: 机器人走近用户 + "你已经坐了两个半小时了，要不要起来活动一下？"

## 程序性记忆设计

```json
{
  "memory_id": "proc_grasp_ceramic",
  "type": "procedural",
  "trigger": {
    "task": "grasp",
    "object_property": "smooth_ceramic",
    "size_range": "medium"
  },
  "strategy": {
    "approach": "top_enveloping",
    "force_profile": "gentle_increasing",
    "pre_grasp_check": "surface_moisture"
  },
  "evidence": {
    "success_count": 12,
    "failure_count": 2,
    "last_updated": "2026-06-20",
    "failure_modes": ["side_grasp_slip"]
  }
}
```

## 关键设计决策

| 决策点 | 选项 | 推荐 |
|--------|------|------|
| 规划频率 | 每步重新规划 / 只在失败时 | 混合：简单任务一次规划，复杂任务每步检查 |
| 记忆更新时机 | 实时 / 任务结束后 | 任务结束后批量更新 |
| 安全约束优先级 | 硬编码 / 可学习 | 安全约束硬编码，策略可学习 |
| 用户偏好来源 | 显式设置 / 行为推断 | 混合：初始显式设置，逐步行为推断调整 |

## 参考论文

- **OpenVLA** (arXiv) — 开源 VLA 模型，基于大规模机器人示范数据训练
- **MemoryVLA** (OpenReview) — cognition-memory-action 框架，工作记忆 + 感知认知记忆库 + 动作决策
