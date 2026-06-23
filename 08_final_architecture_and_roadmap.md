# Phase 8：综合架构、JSON Schema 与路线图

## 1. 阶段研究目标

综合 Phase 0-7 所有研究成果，形成最终的架构设计和战略路线图。

本阶段产出：
1. 智能硬件 Context Compiler 总体架构图
2. 分层记忆架构综合视图
3. Memory Object JSON Schema（正式版）
4. Prompt Assembly 标准模板
5. 技术演进路线图
6. 产品机会点分析
7. 风险与局限总结
8. 未来研究问题

## 2. 总体架构图

### 2.1 端到端系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   AI SMART HARDWARE CONTEXT SYSTEM                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ╔═══════════════════════════════════════════════════════════════════╗    │
│  ║  PERCEPTION LAYER (端侧, 持续运行)                                ║    │
│  ║  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        ║    │
│  ║  │Camera  │ │  Mic   │ │  IMU   │ │  GPS   │ │  ...   │        ║    │
│  ║  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘        ║    │
│  ║      └───────────┼──────────┼──────────┼──────────┘              ║    │
│  ║                  ↓                                                ║    │
│  ║      ┌──────────────────────────┐                                ║    │
│  ║      │  Signal Processing       │                                ║    │
│  ║      │  + Privacy Filter        │                                ║    │
│  ║      │  + Event Segmentation    │                                ║    │
│  ║      └──────────┬───────────────┘                                ║    │
│  ╚═════════════════╪═══════════════════════════════════════════════╝    │
│                    ↓                                                     │
│  ╔═══════════════════════════════════════════════════════════════════╗    │
│  ║  MEMORY LAYER (端侧+云侧, 七层架构)                              ║    │
│  ║                                                                    ║    │
│  ║  ┌─────────┐ ┌─────────┐ ┌─────────┐                            ║    │
│  ║  │L1 Raw   │→│L2 Percep│→│L3 Task  │  ← Working Memory          ║    │
│  ║  │Buffer   │ │WM       │ │WM       │                             ║    │
│  ║  └─────────┘ └─────────┘ └────┬────┘                             ║    │
│  ║                                ↓                                   ║    │
│  ║  ┌─────────┐ ┌─────────┐ ┌─────────┐                            ║    │
│  ║  │L4 Episo-│ │L5 Seman-│ │L6 Proce-│  ← Long-term Memory        ║    │
│  ║  │dic      │ │tic      │ │dural    │                             ║    │
│  ║  └─────────┘ └─────────┘ └─────────┘                             ║    │
│  ║                                                                    ║    │
│  ║  ┌─────────────────────────────────────────────────────────┐     ║    │
│  ║  │  L7 Governance (附属所有层: 来源/置信度/隐私/过期)       │     ║    │
│  ║  └─────────────────────────────────────────────────────────┘     ║    │
│  ╚═══════════════════════════════════════════════════════════════════╝    │
│                    ↓ ↑                                                    │
│  ╔═══════════════════════════════════════════════════════════════════╗    │
│  ║  CONTEXT COMPILER (云侧为主, 每次模型调用前执行)                  ║    │
│  ║                                                                    ║    │
│  ║  Trigger → Intent → Retrieve → Privacy → Rank → Budget → Pack    ║    │
│  ║                                                                    ║    │
│  ╚═══════════════════════════════════════════════════════════════════╝    │
│                    ↓                                                     │
│  ╔═══════════════════════════════════════════════════════════════════╗    │
│  ║  MODEL LAYER (云侧)                                              ║    │
│  ║  ┌─────────┐ ┌─────────┐ ┌─────────┐                            ║    │
│  ║  │  LLM    │ │  VLM    │ │  VLA    │                             ║    │
│  ║  └────┬────┘ └────┬────┘ └────┬────┘                             ║    │
│  ╚═══════╪═══════════╪═══════════╪═══════════════════════════════════╝    │
│          └───────────┼───────────┘                                       │
│                      ↓                                                    │
│  ╔═══════════════════════════════════════════════════════════════════╗    │
│  ║  OUTPUT LAYER (端侧, 执行)                                        ║    │
│  ║  语音 │ AR显示 │ 震动 │ 屏幕 │ 机器人动作                        ║    │
│  ╚═══════════════════════════════════════════════════════════════════╝    │
│                      ↓                                                    │
│              用户反馈 → Memory Update                                    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心数据流

```
传感器流 ──→ Context Object ──→ Memory Write ──→ Memory Store
                                                       │
用户请求/环境触发 ──→ Context Compiler ──→ 从 Memory 检索
                         │                             │
                         ↓                             ↓
                    Ranked Context ──→ Packed Prompt ──→ Model ──→ Output
                                                                     │
                                                         Feedback ──→ Memory Update
```

---

## 3. Memory Object JSON Schema（正式版）

基于 Phase 5 设计，整合 Phase 7 案例验证后的正式版本。

完整 Schema 参见: [`schemas/context-object.json`](schemas/context-object.json)

### 3.1 Memory Object 核心结构

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Memory Object",
  "description": "智能硬件分层记忆系统的通用记忆对象",
  
  "type": "object",
  "required": ["memory_id", "type", "created_at", "content", "governance"],
  
  "properties": {
    "memory_id": {"type": "string", "pattern": "^mem_(ep|sem|proc)_[0-9]+$"},
    "type": {"enum": ["episodic", "semantic", "procedural"]},
    "created_at": {"type": "string", "format": "date-time"},
    "last_accessed": {"type": "string", "format": "date-time"},
    "access_count": {"type": "integer", "minimum": 0},
    
    "content": {
      "type": "object",
      "description": "记忆内容（结构因 type 不同而异）"
    },
    
    "context": {
      "type": "object",
      "properties": {
        "location": {"type": "string"},
        "activity": {"type": "string"},
        "people": {"type": "array", "items": {"type": "string"}},
        "time_of_day": {"type": "string"},
        "device_type": {"type": "string"}
      }
    },
    
    "embeddings": {
      "type": "object",
      "properties": {
        "text_vector": {"type": "array", "items": {"type": "number"}},
        "spatial_vector": {"type": "array", "items": {"type": "number"}},
        "temporal_vector": {"type": "array", "items": {"type": "number"}}
      }
    },
    
    "governance": {
      "type": "object",
      "required": ["source", "confidence", "privacy_level"],
      "properties": {
        "source": {"enum": ["user_explicit", "inferred", "sensor", "tool"]},
        "source_device": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "privacy_level": {"enum": ["public", "private", "sensitive"]},
        "contains_others_data": {"type": "boolean"},
        "expires_at": {"type": ["string", "null"], "format": "date-time"},
        "user_verified": {"type": "boolean"},
        "deletable": {"type": "boolean", "default": true}
      }
    }
  }
}
```

---

## 4. Prompt Assembly 标准模板

### 4.1 通用模板（所有设备形态）

```xml
<!-- Zone A: 固定区 (首部, 高注意力) ~15% budget -->
<system_policy>
  {设备角色定义}
  {核心行为约束}
  {输出通道和格式规范}
</system_policy>

<device_identity>
  {设备类型和能力}
  {当前传感器状态}
</device_identity>

<!-- Zone B: 半固定区 ~15% budget -->
<user_profile>
  {长期偏好 (从 L5 Semantic Memory 选择性注入)}
  {交互风格}
  {隐私设置}
</user_profile>

<active_rules>
  {当前生效的 Procedural Rules (从 L6 条件匹配)}
</active_rules>

<!-- Zone C: 动态区 (中部) ~55% budget -->
<current_scene>
  {当前感知状态 (L2 Perception WM 全量)}
  {时间、地点、活动、人物}
</current_scene>

<recent_events>
  {最近相关事件摘要 (L4 Episodic, Top-N by Ranker)}
</recent_events>

<retrieved_memories>
  {按 ContextScore 排序的相关记忆 (L4/L5, 截断至 budget)}
  <!-- 注意: 相关信息聚合放置，避免 Multi-hop Fragility -->
</retrieved_memories>

<device_state>
  {电量、网络、可用输出通道}
  {可执行动作列表}
</device_state>

<!-- Zone D: 任务区 (尾部, 高注意力) ~15% budget -->
<task>
  {触发条件 / 用户请求}
  {期望输出类型和约束}
</task>

<safety_reiteration>
  {关键安全红线重申 (利用 Recency Bias)}
  {不可执行动作}
  {打扰限制}
</safety_reiteration>
```

---

## 5. 技术演进路线图

### 5.1 五阶段演进

```
Stage 1              Stage 2              Stage 3              Stage 4              Stage 5
被动问答设备    →    多模态助手      →    记忆型助手      →    主动服务终端    →    具身个人Agent
(2023-2024)         (2024-2025)         (2025-2026)         (2026-2027)         (2027+)
│                    │                    │                    │                    │
│ 用户触发           │ 多模态输入         │ 跨会话记忆         │ 主动判断+服务      │ 持续学习+
│ 单次问答           │ 视觉+语音          │ 分层记忆           │ Context Compiler   │ 自主行动
│ 无记忆             │ 简单记忆           │ 记忆检索           │ 主动提醒           │ 物理执行
│                    │                    │                    │                    │
│ 代表:              │ 代表:              │ 代表:              │ 代表:              │ 代表:
│ 语音助手           │ Meta Ray-Ban       │ ChatGPT Memory     │ 本研究目标架构     │ VLA机器人+
│ (Siri/Alexa)      │ (拍照+问答)        │ + 硬件传感器       │ + 硬件形态         │ 全场景Agent
```

### 5.2 技术路线表

| 时间 | 技术里程碑 | 所需突破 |
|------|-----------|----------|
| **2024-2025** | 端侧感知 + 云端 LLM 基础链路 | 低功耗感知芯片、端云协作延迟 |
| **2025-2026** | 分层记忆系统 + 基础 Context Compiler | 记忆写入/检索效率、Privacy Filter |
| **2026-2027** | 完整主动服务 + 多设备记忆共享 | 主动触发准确率、跨设备一致性 |
| **2027-2028** | 个性化 Context Ranker + 自适应遗忘 | 用户反馈闭环、长期记忆治理 |
| **2028+** | 具身 Agent + 物理世界持续学习 | VLA 可靠性、安全保障、社会接受度 |

---

## 6. 产品机会点

### 6.1 现有产品能力差距

| 能力 | 现有产品水平 | 本架构支持 | 差距 |
|------|-------------|-----------|------|
| 持续感知+主动服务 | 无(仅用户触发) | 完整支持 | 大 |
| 跨会话结构化记忆 | ChatGPT Memory(粗粒度) | 七层分层记忆 | 大 |
| 空间+时间记忆检索 | 无 | Ranker 多维度 | 大 |
| 从失败中学习 | 无 | Reflexion→Procedural | 中 |
| 隐私可控的记忆管理 | 有限(删除) | 完整CRUD+冻结+导出 | 中 |
| 多设备记忆统一 | 无 | 统一 Memory Layer | 大 |
| 低打扰主动提示 | 无(全是推送通知) | InterruptionCost 评估 | 大 |

### 6.2 高价值场景优先级

| 场景 | 用户价值 | 技术可行性(近期) | 建议优先级 |
|------|----------|-----------------|-----------|
| 会议记录+待办提取 | 极高 | 高 | **P0** |
| 人物识别+关系辅助 | 高 | 中 | P1 |
| 空间记忆(物品/地点) | 高 | 中 | P1 |
| 日程+承诺追踪 | 极高 | 高 | **P0** |
| 对话实时辅助(耳机) | 高 | 中(延迟挑战) | P1 |
| 习惯学习+主动提醒 | 中 | 低(需长期数据) | P2 |
| 机器人家务执行 | 中 | 低(VLA不成熟) | P2 |

---

## 7. 风险与局限

### 7.1 技术风险

| 风险 | 影响 | 缓解策略 |
|------|------|----------|
| LLM 幻觉导致错误记忆 | 系统"记住"了没发生的事 | Governance confidence + 用户验证 |
| 端侧算力不足 | 事件切分/隐私过滤延迟高 | 专用 AI 芯片 + 模型量化 |
| 长期记忆积累后检索退化 | 记忆越多越慢/越不准 | 定期归纳+遗忘+索引优化 |
| 多模态融合误判 | 错误的 Context Object 污染记忆 | 置信度阈值 + 用户纠正通道 |
| VLA 动作安全性 | 物理伤害风险 | 硬编码安全约束 + 力矩限制 |

### 7.2 隐私与伦理风险

| 风险 | 影响 | 缓解策略 |
|------|------|----------|
| 持续录音/拍摄的社会接受度 | 用户被排斥/法律问题 | 明确指示灯 + 场所禁区 + 法规遵守 |
| 记忆系统被恶意利用 | 监控/跟踪 | 端到端加密 + 用户完全控制 |
| 推断性记忆的偏见 | 对用户形成错误画像 | 推断需标注置信度 + 用户可编辑 |
| 旁人的被遗忘权 | 他人出现在你的记忆中 | 旁人检测 + 默认不存储 |

### 7.3 产品与商业风险

| 风险 | 影响 | 缓解策略 |
|------|------|----------|
| 用户不信任记忆系统 | 功能被关闭 | 透明度设计 + 渐进式建立信任 |
| 记忆过度打扰 | 用户疲劳 | 保守的 InvocationThreshold |
| Humane AI Pin 式失败 | 延迟/不准导致产品口碑差 | 缩小 scope + 做好一个场景再扩展 |
| 竞争对手先发 | 市场窗口期 | 聚焦差异化(记忆系统)而非全能 |

---

## 8. 未来研究问题

### 近期可研究 (1-2 年)

1. Context Ranker 的最优权重如何通过用户反馈在线学习？
2. 端侧 7 层记忆的存储结构和索引设计最佳实践？
3. 从 Episodic 自动归纳 Semantic 的准确率和用户接受度？
4. 多设备间记忆同步和一致性保证？
5. 主动服务的 "打扰-价值" 平衡点的用户研究？

### 中期研究方向 (2-4 年)

6. 记忆系统的可解释性——用户如何理解"系统为什么知道这个"？
7. 社会记忆——多用户共享记忆的隐私和一致性？
8. 记忆迁移——更换设备后如何无缝转移个人记忆？
9. 记忆老化——长期使用后记忆系统的质量是否下降？
10. 文化差异——不同文化背景下的记忆偏好和隐私期望？

### 远期开放问题 (4+ 年)

11. 具身 Agent 的自主学习能否达到可信赖水平？
12. 个人 AI 终端的记忆是否会变成"第二个大脑"？伦理边界在哪？
13. 当 AI 记忆比人类记忆更准确时，法律和社会关系如何调整？

---

## 9. 核心结论

> 从软件 Agent 到智能硬件 Agent，Context 管理的核心从"把文档和历史对话塞进 prompt"，升级为"把现实世界的多模态事件、用户长期记忆、设备状态和行动约束**编译**成模型可用的任务上下文"。

本研究的核心贡献：

1. **建立了从 LLM Context 管理到硬件 Context 管理的完整迁移框架** — 证明了软件 context engineering 的原则和行为特性同样适用于硬件，但需要扩展
2. **提出了七层记忆架构** — 在 CoALA 四层基础上，为硬件场景增加了 Raw Buffer、Perception WM 和 Governance Memory
3. **设计了 Context Compiler 的完整 9 步 Pipeline** — 从触发检测到反馈更新的端到端架构
4. **建立了 9 维度 Context Ranker 模型** — 超越简单语义相似度，整合时间、空间、隐私、打扰代价
5. **将 12 个 context 行为特性转化为工程约束** — 从学术发现到 Prompt Packing 的具体设计规则
6. **通过四类设备案例验证了架构的通用性和差异化需求** — 统一框架 + 设备特化参数

---

## 10. 研究成果索引

| # | 成果 | 所在文件 |
|---|------|----------|
| 1 | 研究范围与术语定义 | `00_research_scope.md` |
| 2 | LLM Context 管理范式 + 12 个行为特性 | `01_llm_context_management.md` |
| 3 | 软件 Agent Prompt Assembly 案例 | `02_software_agent_prompt_assembly.md` |
| 4 | 分层记忆框架对比 (7 个系统) | `03_memory_frameworks.md` |
| 5 | 多模态输入 Context 化 Pipeline | `04_hardware_context_inputs.md` |
| 6 | 七层记忆架构设计 | `05_hierarchical_memory_architecture.md` |
| 7 | Context Compiler 完整架构 | `06_context_compiler.md` |
| 8 | 四类硬件案例验证 | `07_hardware_case_studies.md` |
| 9 | 综合架构 + 路线图 | `08_final_architecture_and_roadmap.md` |
| 10 | Context Object JSON Schema | `schemas/context-object.json` |
| 11 | 资料注册表 (41 条) | `sources/source_registry.md` |
| 12 | 证据矩阵 | `sources/evidence_matrix.md` |
| 13 | 开放问题清单 | `sources/open_questions.md` |
| 14 | Context 行为特性快速参考 | `_archive/docs/context-pitfalls-and-tricks.md` |
