# GUI 内容架构

## 1. 设计目标

本 GUI 的目标不是把 Markdown 章节搬进网页，而是把研究内容转化为一个可探索、可深挖、可回溯证据的生成式研究界面。

更准确地说，它是一个面向外部理解和实践决策的展示系统：

- 让不了解完整文档的人快速理解研究主线。
- 让产品、架构、研究同事看到关键结论后知道该怎么用。
- 用图形、空间和交互解释复杂机制，而不是把所有资料完整塞进页面。
- 把详细证据和原文放在可下钻层，而不是默认占据主界面。

用户体验应当接近：

1. 先看到完整研究世界。
2. 选择一个研究区域。
3. 点击一个建筑或机制节点。
4. 进入该对象的内部空间。
5. 在内部空间中继续查看结构、数据流、案例、证据和开放问题。

## 2. 内容层级

整体内容分为 5 层。

| 层级 | 名称 | 用户看到的形式 | 内容职责 |
|---|---|---|---|
| L0 | Research World | 一张完整研究城市地图 | 建立全局认知，展示研究主线 |
| L1 | District | 城区或大区域 | 对应研究大主题 |
| L2 | Building | 建筑、实验室、工厂、塔 | 对应一个核心研究对象 |
| L3 | Interior | 建筑内部空间 | 展示机制、层级、流程、案例 |
| L4 | Evidence Layer | 证据、来源、开放问题 | 证明结论可信度，提示待研究问题 |

## 2.1 展示优先级

每个界面默认只展示四类信息，且顺序固定：

| 优先级 | 内容 | 目的 |
|---|---|---|
| P0 | 一句话关键结论 | 让用户立刻知道这一页想说明什么 |
| P1 | 机制图或空间隐喻 | 让抽象概念变成可理解结构 |
| P2 | 实践指导 | 告诉用户在产品、架构或研究中怎么用 |
| P3 | 证据和原文入口 | 支撑可信度，但不干扰第一眼理解 |

默认不展示：

- 长段原文。
- 完整章节列表。
- 大量并列表格。
- 过多学术来源细节。
- 与当前核心结论无关的支线内容。

## 3. 节点类型

GUI 中所有可点击对象都应归一为节点。节点类型决定点击后生成什么界面。

| 节点类型 | 代表内容 | 点击后生成的界面 |
|---|---|---|
| `concept` | Context Window、RAG、Memory、Tool Context | 概念剖面图、边界对比、相关证据 |
| `mechanism` | Prompt Assembly、Context Compression、Compaction | 装配台、机制分解、输入输出 |
| `pipeline` | Hardware Context Pipeline、Context Compiler | 动态流程线、每步输入输出、失败点 |
| `memory_layer` | Raw Buffer、Episodic Memory、Semantic Memory | 记忆层房间、数据结构、生命周期 |
| `framework` | MemGPT、LangGraph、Mem0、Zep | 档案馆展柜、能力矩阵、迁移价值 |
| `device_case` | AI 眼镜、耳机、AI Pin、机器人 | 场景模拟器、设备链路、风险分析 |
| `schema` | Context Object JSON Schema | 结构化对象检查器、字段解释 |
| `evidence` | 证据矩阵条目 | 证据链视图、来源、强度、缺口 |
| `open_question` | 待验证问题 | 假设空间、调研任务、验证路径 |
| `roadmap_stage` | AI 终端演进阶段 | 时间线、能力变化、架构变化 |

## 4. 内容对象模型

每个节点建议拥有统一的数据结构。前端可根据 `node_type` 生成不同的深挖界面。

```json
{
  "id": "context_compiler",
  "node_type": "pipeline",
  "title": "Context Compiler",
  "subtitle": "把原始输入、记忆、状态和约束编译成模型可用上下文",
  "district": "compiler_district",
  "visual_metaphor": "factory",
  "source_files": [
    "F:/context/06_context_compiler.md",
    "C:/Users/lsr_buaa/Downloads/deep_research_context_hardware_plan.md"
  ],
  "core_question": "一次模型调用前，系统如何决定哪些 context 应该进入 prompt？",
  "key_claims": [
    "Context Compiler 不是简单检索，而是触发、分类、检索、过滤、排序、预算、拼接、调用和反馈更新的完整 pipeline。",
    "智能硬件场景下，Context Ranker 需要同时考虑任务相关性、空间相关性、隐私风险和打扰成本。",
    "Prompt Packing 应利用模型首尾注意力优势，把稳定约束和当前任务放在高注意力区域。"
  ],
  "practice_takeaways": [
    "不要把所有记忆都塞进 prompt，应先经过检索、隐私过滤、排序和预算分配。",
    "硬件场景的 ranker 必须考虑 spatial relevance、privacy risk 和 interruption cost。",
    "Prompt Packing 要把当前任务和安全约束放到高注意力区域。"
  ],
  "default_story": "从一次模型调用前的决策过程，解释为什么智能硬件需要 Context Compiler。",
  "children": [
    "trigger_detection",
    "intent_classification",
    "context_retrieval",
    "privacy_filter",
    "context_ranking",
    "token_budget_allocation",
    "prompt_packing",
    "model_invocation",
    "feedback_memory_update"
  ],
  "incoming_links": [
    "hardware_context_pipeline",
    "seven_layer_memory_architecture",
    "context_object_schema"
  ],
  "outgoing_links": [
    "prompt_packing_template",
    "hardware_case_simulator",
    "roadmap_proactive_terminal"
  ],
  "evidence_links": [
    "evidence_phase06_pipeline",
    "evidence_prompt_attention_pattern",
    "evidence_context_ranker_dimensions"
  ],
  "open_questions": [
    "ranker_weights_fixed_or_learned",
    "interruption_cost_quantification",
    "separate_compilers_for_llm_vlm_vla"
  ],
  "default_view": "factory_pipeline"
}
```

## 5. 主研究对象清单

第一版 GUI 不应覆盖所有细枝末节，应该先覆盖研究中最能建立认知的核心对象。

| ID | 标题 | 类型 | 来源 |
|---|---|---|---|
| `research_world` | Context Engineering 研究城市 | world | README、任务书 |
| `context_window` | LLM Context Window | concept | `01_llm_context_management.md` |
| `rag_memory_tool_boundary` | RAG / Memory / Tool Context 边界 | concept | `01_llm_context_management.md` |
| `context_pitfalls` | 12 个 Context 行为现象 | mechanism | `01_llm_context_management.md` |
| `software_prompt_assembly` | 软件 Agent Prompt Assembly | mechanism | `02_software_agent_prompt_assembly.md` |
| `agent_case_gallery` | 软件 Agent 案例馆 | framework | `02_software_agent_prompt_assembly.md` |
| `memory_framework_archive` | 记忆框架档案馆 | framework | `03_memory_frameworks.md` |
| `hardware_context_inputs` | 智能硬件输入 Context 化 | pipeline | `04_hardware_context_inputs.md` |
| `context_object_schema` | Multimodal Context Object | schema | `04_hardware_context_inputs.md`、`schemas/context-object.json` |
| `seven_layer_memory_architecture` | 七层记忆架构 | memory_layer | `05_hierarchical_memory_architecture.md` |
| `context_compiler` | Context Compiler | pipeline | `06_context_compiler.md` |
| `context_ranker` | Context Ranker | mechanism | `06_context_compiler.md` |
| `hardware_case_lab` | 智能硬件案例实验室 | device_case | `_archive/cases/*.md` |
| `evidence_observatory` | 证据天文台 | evidence | `sources/evidence_matrix.md` |
| `open_questions_board` | 开放问题控制台 | open_question | `sources/open_questions.md` |
| `terminal_roadmap` | 下一代 AI 终端路线图 | roadmap_stage | 任务书、README |

## 6. 主要叙事路径

GUI 应支持多条路径，而不是固定线性阅读。

### 6.1 主线学习路径

```text
Context Window
  -> Prompt Assembly
  -> RAG / Memory / Tool Context
  -> Memory Frameworks
  -> Hardware Context Inputs
  -> Seven-layer Memory
  -> Context Compiler
  -> Hardware Cases
  -> Roadmap
```

适合第一次看研究的人。

### 6.2 架构设计路径

```text
Hardware Inputs
  -> Context Object
  -> Seven-layer Memory
  -> Context Ranker
  -> Prompt Packing
  -> Model Decision
  -> Feedback Memory Update
```

适合产品架构、系统架构讨论。

### 6.3 证据审查路径

```text
Claim
  -> Evidence Matrix
  -> Source Registry
  -> Evidence Strength
  -> Open Question
  -> Next Research Task
```

适合向他人展示“哪些结论已经可靠，哪些仍是假设”。

### 6.4 设备场景路径

```text
Select Device
  -> Select Scenario
  -> Sensor Inputs
  -> Context Object
  -> Memory Recall
  -> Compiler Decision
  -> Output Channel
  -> Privacy Risk
```

适合展示智能硬件为什么比软件 Agent 更复杂。

## 7. 每个深挖界面的内容结构

所有深挖界面都要有 7 个固定信息槽位，但默认只露出前 4 个。证据和细节必须通过下钻显示，避免主界面拥挤。

| 槽位 | 内容 | 表现形式 |
|---|---|---|
| `what` | 它是什么 | 一句话定义、视觉标题 |
| `why` | 为什么重要 | 核心问题、痛点、研究动机 |
| `how` | 如何工作 | 流程、层级、输入输出 |
| `so_what` | 对实践意味着什么 | 设计原则、架构决策、产品启发 |
| `example` | 一个具体例子 | 场景模拟、样例 JSON、Prompt |
| `evidence` | 证据强度 | 强/中/弱/待验证徽标，来源链接 |
| `next` | 继续深挖 | 子节点、相关节点、开放问题 |

## 7.1 每屏内容密度规则

每个默认视图遵守：

- 只表达 1 个主结论。
- 最多展示 3 个关键点。
- 最多展示 1 个主图。
- 最多展示 1 个默认案例。
- 证据只显示强度徽标和入口，不默认展开。
- 原文内容只作为右侧详情或二级页面。

如果一个研究对象有很多内容，必须拆成多个“故事视图”，而不是塞进同一屏。

## 8. 内容粒度规则

为了让 GUI 可用，内容不能太粗，也不能太碎。

| 粒度 | 是否适合成为可点击节点 | 示例 |
|---|---|---|
| 研究阶段 | 适合做区域，不适合做唯一节点 | Phase 04 |
| 核心机制 | 适合做建筑 | Context Compiler |
| 子步骤 | 适合做建筑内部模块 | Privacy Filter |
| 具体字段 | 适合做检查器或详情项 | `prompt_priority.task_relevance` |
| 单条证据 | 适合做证据层节点 | Lost in the Middle 论文证据 |
| 句子级结论 | 不适合单独做节点 | “需要压缩” |

## 8.1 内容筛选规则

一个内容只有满足以下任一条件，才进入主界面：

1. 能解释研究主线。
2. 能支撑关键结论。
3. 能帮助他人做产品或架构决策。
4. 能澄清容易误解的概念边界。
5. 能展示软件 Agent 到智能硬件 Agent 的关键差异。

否则放入：

- 证据层。
- 详情面板。
- 原文链接。
- 后续研究资料库。

## 9. 内容到 GUI 的转译原则

| 原始文档内容 | GUI 转译方式 |
|---|---|
| Markdown 一级标题 | 城区或建筑 |
| Markdown 二级标题 | 建筑内部房间 |
| Markdown 三级标题 | 房间内模块 |
| 表格 | 对比矩阵、控制台、检查器 |
| 代码块 Pipeline | 动态流程线 |
| JSON Schema | 可折叠字段树、样例对象 |
| 证据矩阵 | 证据天文台、claim-to-source 链 |
| 开放问题 | 问题雷达、假设板、调研任务 |

## 10. 设计边界

第一版先不做：

- 自动从 Markdown 全量解析生成所有节点。
- 把所有章节和所有表格完整搬进界面。
- 复杂三维城市漫游。
- 真实论文全文检索。
- 多用户协作批注。
- 完整后端数据库。

第一版必须做：

- 一张总地图。
- 至少 6 个可进入的建筑。
- 每个建筑有明确内部空间。
- 每个内部空间能看到研究结论、机制、证据和下一步。
- imagegen 底图和前端叠加层的职责分离。
