# 建筑内部空间设计

## 1. 通用深挖界面框架

点击建筑后，进入全屏深挖界面。所有深挖界面共享以下布局，但不同建筑使用不同视觉隐喻。

```text
┌──────────────────────────────────────────────────────────────┐
│ 顶部：路径面包屑 / 搜索 / 证据图层 / 返回地图                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 中央：建筑内部空间、流程、剖面、实验场景                      │
│                                                              │
├───────────────────────┬──────────────────────────────────────┤
│ 左侧：子房间导航       │ 右侧：详情面板 / 证据 / 开放问题       │
└───────────────────────┴──────────────────────────────────────┘
```

固定功能：

- 返回总地图。
- 切换“结构层 / 证据层 / 风险层 / 开放问题层”。
- 点击内部模块继续进入二级深挖。
- 右侧详情面板展示来源、关键结论、证据强度和原文引用定位。

### 1.1 默认视图必须回答的问题

每个建筑的默认视图必须在 10 秒内回答：

1. 这个模块的关键结论是什么？
2. 它为什么对智能硬件 Context Engineering 重要？
3. 它给产品或架构实践带来什么直接指导？

默认视图不追求完整覆盖。完整资料放在详情、证据和原文入口中。

### 1.2 信息密度限制

每个建筑默认视图：

- 只显示 1 个主图。
- 只显示 1 条主结论。
- 只显示 3 条以内实践启发。
- 只展示 1 个默认案例或演示流。
- 不直接展示长表格和长段落。

## 2. Context Window 观测站

### 2.1 内容定位

解释 LLM 一次调用时 context window 里到底有哪些信息，以及为什么“给模型看什么”比“怎么措辞”更重要。

来源：

- `F:/context/01_llm_context_management.md`
- `F:/context/00_research_scope.md`
- 任务书 9.2、9.3、10.1、10.3

### 2.2 入口视图

视觉隐喻：一座巨大的观测站，中央是一块透明的 context window 截面，像一个被分层填充的能量容器。

中央结构：

```text
┌──────────────────────────────┐
│ System Policy                │
├──────────────────────────────┤
│ Developer / Project Rules    │
├──────────────────────────────┤
│ User Request                 │
├──────────────────────────────┤
│ Conversation History         │
├──────────────────────────────┤
│ RAG Results                  │
├──────────────────────────────┤
│ Tool Results                 │
├──────────────────────────────┤
│ Memory Objects               │
├──────────────────────────────┤
│ Constraints / Output Format  │
└──────────────────────────────┘
```

### 2.3 内部房间

| 房间 | 展示内容 | 交互 |
|---|---|---|
| `window_anatomy` | Context Window 构成 | 鼠标扫过每层，右侧显示来源、作用、风险 |
| `rag_memory_tool_boundary` | RAG、Memory、Tool Context 边界 | 三角图切换案例 |
| `long_context_vs_memory` | 长上下文模型和外部记忆的关系 | 滑块模拟 token 增加但噪声增加 |
| `context_compression_room` | 摘要、结构化抽取、事件化、滑动窗口 | 点击压缩策略看损失和收益 |
| `context_behavior_lab` | 12 个行为现象 | 每个现象有小实验动画 |

### 2.4 右侧详情面板

默认显示：

- 一句话：Context Window 是模型一次调用时可访问的信息总和。
- 核心问题：什么该进 prompt，什么该留在外部存储。
- 关键结论：长上下文不能替代结构化记忆和上下文选择机制。
- 实践指导：不要把 context window 当作无限容器；应先做选择、排序、压缩和隔离。
- 证据入口：Lost in the Middle、Attention Sink、Context Rot、RAG 边界。

### 2.5 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 RAG / Memory / Tool | 进入边界大厅 |
| 点击 Prompt Assembly | 进入 Prompt Assembly 工作室 |
| 点击 12 个行为现象 | 进入 Context 行为实验室 |
| 点击硬件启发 | 跳到 Sensor Port |

## 3. Prompt Assembly 工作室

### 3.1 内容定位

展示软件 Agent 如何从用户请求、项目规则、文件、历史、记忆和工具结果中组装 prompt。

来源：

- `F:/context/02_software_agent_prompt_assembly.md`
- 任务书 4.2、9.4、11.1

### 3.2 入口视图

视觉隐喻：一个工程装配台。左边是原料仓，中间是排序、过滤和压缩机械臂，右边输出最终 prompt。

```text
Input Bins
  user request
  project rules
  repo files
  recent conversation
  retrieved memories
  tool results
  constraints
        ↓
Assembly Bench
  select -> rank -> compress -> order -> pack
        ↓
Final Prompt
```

### 3.3 内部房间

| 房间 | 展示内容 | 交互 |
|---|---|---|
| `software_prompt_template` | 软件 Agent Prompt Assembly 模板 | 拖拽调整 prompt 区块顺序 |
| `claude_code_room` | CLAUDE.md、工具结果、compaction、system reminder | 播放一个 coding task 的 context 生命周期 |
| `cursor_room` | IDE context、代码索引、当前文件、编辑历史 | 高亮“当前编辑状态”如何影响检索 |
| `chatgpt_memory_room` | 用户记忆写入、更新、删除、注入 | 记忆卡片进入 prompt 的过程 |
| `langgraph_room` | Thread State 与 Memory Store | 状态图和 namespace 检索 |
| `mcp_gateway_room` | MCP tools、resources、prompts | 外部资源如何接入 context assembly |
| `pollution_guard_room` | Prompt 污染防护 | 放入过期、低置信、敏感记忆，看系统如何过滤 |

### 3.4 关键互动

用户可以选择一个任务：

```text
“帮我修改一个项目中的登录 bug”
```

界面动态展示：

1. 用户请求进入装配台。
2. 项目规则被加载。
3. 相关文件被检索。
4. 工具结果被添加。
5. 历史对话被压缩。
6. 输出最终 prompt 截面。

### 3.5 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 Memory Store | 进入 Memory Framework 档案馆 |
| 点击 MCP Gateway | 进入 MCP 机制详情 |
| 点击 Hardware Prompt Template | 跳到 Context Compiler 工厂 |

## 4. Memory Framework 档案馆

### 4.1 内容定位

比较现有 agent memory 框架，提取可迁移到智能硬件的能力和缺口。

来源：

- `F:/context/03_memory_frameworks.md`
- 任务书 4.3、9.10

### 4.2 入口视图

视觉隐喻：一个研究档案馆。每个框架是一个展柜，展柜上方有能力徽标。

展柜：

```text
MemGPT / Letta
Generative Agents
Reflexion
CoALA
Mem0
Zep / Graphiti
LangGraph Memory
```

### 4.3 内部房间

| 房间 | 展示内容 | 交互 |
|---|---|---|
| `framework_gallery` | 所有框架展柜 | 点击展柜进入框架剖面 |
| `capability_matrix` | Memory Layer Coverage、Multimodal、Governance、Edge 等维度 | 按维度排序 |
| `migration_value_room` | 可迁移价值 | 显示“迁移到硬件后可用/需改造/不可用” |
| `limitation_wall` | 现有框架缺口 | 高亮多模态、治理、主动遗忘、低延迟缺口 |
| `cognitive_mapping_room` | 认知科学记忆分层映射 | 从 working/episodic/semantic/procedural 连接到七层塔 |

### 4.4 框架展柜模板

每个框架详情页固定展示：

| 字段 | 内容 |
|---|---|
| 核心理念 | 框架解决什么问题 |
| 记忆层级 | 支持哪些记忆类型 |
| 写入机制 | 如何创建记忆 |
| 检索机制 | 如何召回 |
| 更新/遗忘 | 是否支持合并、衰减、删除 |
| 硬件迁移价值 | 哪些能力可复用 |
| 主要短板 | 对智能硬件缺什么 |
| 证据强度 | 强/中/弱/待验证 |

### 4.5 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 CoALA 记忆分类 | 跳到七层记忆塔 |
| 点击 Governance 缺口 | 跳到 L7 Governance Memory |
| 点击 Multimodal 缺口 | 跳到 Sensor Port |

## 5. 多模态传感器港口

### 5.1 内容定位

解释智能硬件输入为什么不同于软件 Agent：它是连续、高带宽、多模态、有噪声、有隐私风险的现实世界输入。

来源：

- `F:/context/04_hardware_context_inputs.md`
- `F:/context/schemas/context-object.json`
- 任务书 4.5、9.6、9.7、9.9

### 5.2 入口视图

视觉隐喻：多模态港口。不同传感器流像货船、管线或光束进入港口，经过海关、过滤、切分，变成标准 Context Object 集装箱。

```text
Camera      -> objects / people / scene
Microphone  -> transcript / speaker / emotion
IMU         -> activity / posture
GPS         -> semantic place
Calendar    -> external task
Device      -> battery / network / outputs
                    ↓
        Privacy Filter + Event Segmentation
                    ↓
             Context Object
```

### 5.3 内部房间

| 房间 | 展示内容 | 交互 |
|---|---|---|
| `input_panorama` | 摄像头、麦克风、IMU、GPS、蓝牙、屏幕、设备状态 | 选择传感器，看数据量、频率和可转化 context |
| `sensor_to_context_mapping` | Sensor Input -> Context Object 映射表 | 点击字段看来源和置信度 |
| `event_segmentation_line` | 连续流到离散事件 | 拖动时间轴，观察切分点 |
| `multimodal_fusion_room` | 多模态融合与冲突处理 | 制造语音/视觉冲突，看置信度传播 |
| `edge_cloud_split_room` | 端侧 vs 云侧处理分工 | 切换网络/电量，看处理位置变化 |
| `privacy_filter_gate` | 隐私过滤层 | 选择旁人、敏感场景、位置数据，查看过滤策略 |
| `context_object_inspector` | JSON Schema 字段树 | 结构化字段检查器 |

### 5.4 场景示例

默认场景：AI 眼镜在会议前看到会议室和同事。

链路：

```text
camera + microphone + calendar + location
  -> scene.people + audio.transcript + external_context
  -> event boundary: meeting starts
  -> Context Object
  -> Perception WM
  -> Task WM
  -> Context Compiler
```

### 5.5 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 Context Object | 进入 Schema 检查器 |
| 点击 Perception WM | 进入七层记忆塔 L2 |
| 点击 Event Complete | 进入 Episodic Memory |
| 点击 Compiler Input | 进入 Context Compiler 工厂 |

## 6. 七层记忆塔

### 6.1 内容定位

展示智能硬件分层记忆架构。它不是普通长期记忆，而是从原始传感器缓存到治理元信息的完整体系。

来源：

- `F:/context/05_hierarchical_memory_architecture.md`
- 任务书 4.3、9.5

### 6.2 入口视图

视觉隐喻：一座可剖开的七层记忆塔。L7 Governance Memory 像透明外壳覆盖全塔，其他层在塔内垂直排列。

```text
L7 Governance Memory  覆盖所有层
  L6 Procedural Memory
  L5 Semantic Memory
  L4 Episodic Memory
  L3 Task Working Memory
  L2 Perception Working Memory
  L1 Raw Sensor Buffer
```

### 6.3 每层房间模板

点击任一楼层，进入该层房间。

| 模块 | 内容 |
|---|---|
| 定义 | 这一层存什么 |
| 生命周期 | 秒、分钟、任务级、天月级、长期 |
| 存储位置 | 端侧 RAM、context window、端云存储 |
| 写入条件 | 什么时候写入 |
| 召回方式 | 如何检索进入 Compiler |
| 更新方式 | 合并、强化、降权、覆盖、询问用户 |
| 遗忘策略 | TTL、衰减、用户删除、隐私策略 |
| 数据结构 | JSON 示例或索引结构 |
| 典型硬件例子 | 眼镜、耳机、Pin、机器人 |
| 证据和假设 | 支撑来源和待验证点 |

### 6.4 楼层内容

| 楼层 | 核心内容 | 默认示例 |
|---|---|---|
| L1 Raw Sensor Buffer | 原始音频、视频、IMU 环形缓存 | 最近 30 秒音频片段 |
| L2 Perception WM | 当前看到/听到/感知到什么 | 面前有同事在说话 |
| L3 Task WM | 当前任务状态和目标 | 正在准备会议提醒 |
| L4 Episodic Memory | 具体事件记录 | 昨天会议中用户答应提交材料 |
| L5 Semantic Memory | 稳定事实、偏好、关系 | 用户经常上午 9 点前需要会议提醒 |
| L6 Procedural Memory | 行为规则和服务策略 | 会议中只震动提醒，不语音打断 |
| L7 Governance Memory | 来源、权限、置信度、过期、审计 | 该记忆来自日历，允许长期保存 |

### 6.5 核心互动

1. 切换“数据流模式”：显示 L1 -> L2 -> L3 -> L4 -> L5 的写入和归纳路径。
2. 切换“召回模式”：显示 L2/L3/L4/L5/L6 如何被 Compiler 检索。
3. 切换“治理模式”：L7 外壳高亮每条记忆的权限、置信度和过期策略。
4. 点击一条记忆：右侧显示完整治理元信息。

### 6.6 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 L2 | 跳到 Sensor Port 的 Perception 输出 |
| 点击 L3 | 跳到 Compiler 的当前任务输入 |
| 点击 L4/L5/L6 | 跳到 Context Retrieval |
| 点击 L7 | 跳到 Privacy Filter 和 Evidence |

## 7. Context Compiler 工厂

### 7.1 内容定位

展示模型调用前，系统如何把多源 context 编译成高质量 prompt 或 VLM/VLA 输入。

来源：

- `F:/context/06_context_compiler.md`
- 任务书 4.4、9.7、11.2、11.3

### 7.2 入口视图

视觉隐喻：一条完整工厂生产线。左边输入材料，中间九台机器，右边输出模型调用和记忆更新。

默认主结论：

> 智能硬件调用模型前，需要一个 Context Compiler 来决定“该不该调用、取哪些上下文、过滤哪些风险、按什么顺序打包”。

默认实践指导：

- 不要设计成 retrieve-then-prompt 的简单链路。
- 必须把 privacy filter 放在 ranking 和 packing 之前。
- 主动服务场景必须显式计算 interruption cost。

```text
Raw Inputs + Memory + State + Constraints
        ↓
1 Trigger Detection
        ↓
2 Intent Classification
        ↓
3 Context Retrieval
        ↓
4 Privacy Filter
        ↓
5 Context Ranking
        ↓
6 Token Budget Allocation
        ↓
7 Prompt Packing
        ↓
8 Model Invocation
        ↓
9 Feedback & Memory Update
```

### 7.3 内部机器

| 机器 | 输入 | 输出 | 交互 |
|---|---|---|---|
| Trigger Detection | 用户请求、环境事件、定时任务、规则 | 是否调用模型 | 调整阈值，看主动服务是否触发 |
| Intent Classification | 当前任务和场景 | LLM/VLM/VLA、任务类型、输出通道 | 切换设备形态 |
| Context Retrieval | 七层记忆 | 候选 context 列表 | 选择记忆层，看候选变化 |
| Privacy Filter | 候选 context + L7 | 可用候选 | 切换隐私策略，看过滤结果 |
| Context Ranking | 可用候选 | 排序列表 | 拖动 9 个权重 |
| Token Budget Allocation | 排序列表 + 模型限制 | 区块预算 | 模拟超预算降级 |
| Prompt Packing | 预算内内容 | 最终 prompt | 选择首尾注意力布局 |
| Model Invocation | prompt + model type | 决策或输出 | 切换 LLM/VLM/VLA |
| Feedback Update | 用户反馈、执行结果 | 记忆强化/降权/删除 | 选择成功、失败、否决 |

### 7.4 Context Ranker 控制台

点击 Context Ranking 机器后进入独立控制台。

评分维度：

```text
TaskRelevance
Recency
SpatialRelevance
UserSpecificity
Confidence
Actionability
PrivacyRisk
InterruptionCost
TokenCost
```

交互：

- 拖动每个维度权重。
- 切换场景：安全紧急、社交场合、独处空闲、会议中、机器人动作。
- 左侧候选 context 卡片实时重新排序。
- 右侧显示“最终进入 prompt / 仅工具可查 / 压缩摘要 / 排除”的分组结果。

### 7.5 Prompt Packing 布局器

显示模型注意力分布：

```text
High Attention Head:
  System + Identity + Stable Rules

Middle:
  Background Memories + Retrieved Results

High Attention Tail:
  Current Scene + Current Task + Safety Constraints + Output Contract
```

交互：

- 拖动区块改变位置。
- 显示 Lost in the Middle 风险提示。
- 超预算时显示压缩、删除、降级策略。

### 7.6 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击 Context Retrieval | 七层记忆塔 |
| 点击 Privacy Filter | Sensor Port 隐私闸门 |
| 点击 Ranking 权重 | Context Ranker 控制台 |
| 点击 Hardware Strategy | Hardware Lab 设备场景 |
| 点击 Feedback Update | 记忆塔 L4/L5/L6 |

## 8. Hardware Lab 设备实验室

### 8.1 内容定位

用典型智能硬件场景验证 Context Pipeline、Memory Architecture 和 Compiler 策略。

来源：

- `F:/context/_archive/cases/ai-glasses.md`
- `F:/context/_archive/cases/ai-earbuds.md`
- `F:/context/_archive/cases/ai-pin.md`
- `F:/context/_archive/cases/ai-robot.md`
- 任务书 4.5、9.8

### 8.2 入口视图

视觉隐喻：设备实验室。中间是设备选择台，四周是 AI 眼镜、耳机、AI Pin、机器人实验舱。

### 8.3 设备实验舱模板

每个设备房间固定展示：

| 模块 | 内容 |
|---|---|
| 设备定位 | 设备是什么、主要交互形态 |
| 输入源 | 摄像头、麦克风、IMU、日历、位置等 |
| 记忆层级 | 哪些记忆层最重要 |
| 场景列表 | 3 个典型场景 |
| Prompt Assembly | 当前场景下如何组装 prompt |
| 主动服务触发 | 什么时候提醒，什么时候沉默 |
| 输出通道 | 语音、视觉、震动、动作 |
| 隐私风险 | 旁人、位置、音频、行动风险 |
| 技术瓶颈 | 延迟、置信度、功耗、误触发 |

### 8.4 AI 眼镜实验舱

场景：

1. 会议准备提醒。
2. 人物识别辅助。
3. 环境安全提醒。

默认模拟：

```text
用户走进会议室
  -> 摄像头识别会议室和同事
  -> 日历确认会议即将开始
  -> 召回上次会议承诺
  -> 判断可低打扰提醒
  -> 视觉 overlay 或轻声提示
```

### 8.5 AI 耳机实验舱

场景：

1. 会议中的信息辅助。
2. 社交场合人名提醒。
3. 语言辅助。

关键展示：

- 无视觉输入或弱视觉输入下，音频 context 权重更高。
- 输出通道极短，必须控制打扰成本。
- 会议中语音打断风险高，震动或短提示更合适。

### 8.6 AI Pin 实验舱

场景：

1. 会议摘要生成。
2. 承诺追踪。
3. 生活日志查询。

关键展示：

- 长时间记录带来高隐私风险。
- 什么值得记住、什么应丢弃非常关键。
- Episodic Memory 和 Governance Memory 是核心。

### 8.7 机器人实验舱

场景：

1. 日常物品整理。
2. 从失败中学习。
3. 主动陪伴服务。

关键展示：

- 机器人需要 high-level planning context 和 low-level action context 分离。
- Procedural Memory 和 Spatial Memory 权重高。
- 输出不是文本，而是物理动作，错误成本更高。

### 8.8 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击输入源 | Sensor Port |
| 点击记忆层级 | 七层记忆塔 |
| 点击 Prompt Assembly | Compiler Factory |
| 点击隐私风险 | Evidence / Governance |
| 点击路线图阶段 | Roadmap Boulevard |

## 9. Evidence Observatory 证据天文台

### 9.1 内容定位

把研究结论、证据来源、证据强度和开放问题可视化。

来源：

- `F:/context/sources/evidence_matrix.md`
- `F:/context/sources/source_registry.md`
- `F:/context/sources/open_questions.md`

### 9.2 入口视图

视觉隐喻：天文台。每个核心论断是一颗星，来源是星座连接，证据强度决定亮度。

### 9.3 内部房间

| 房间 | 展示内容 | 交互 |
|---|---|---|
| `claim_star_map` | 核心论断和来源连接 | 点击论断看来源、强度、相关建筑 |
| `evidence_strength_filter` | 强、中、弱、待验证 | 筛选地图节点 |
| `source_library` | 学术论文、官方文档、技术博客、产品文档 | 按类型过滤 |
| `open_questions_radar` | 待研究问题 | 按 Phase、风险、重要性分类 |
| `weak_claim_queue` | 弱证据和待验证判断 | 转成下一步调研任务 |

### 9.4 关键互动

从任何建筑打开证据图层时：

1. 当前建筑的关键论断变成星点。
2. 星点连接到来源。
3. 弱证据和待验证问题高亮。
4. 用户可以反向跳回对应建筑或研究阶段。

## 10. Roadmap Boulevard 路线图大道

### 10.1 内容定位

展示下一代 AI 智能终端可信记忆架构的演进路线。

来源：

- 任务书 9.11
- `F:/context/README.md`
- `F:/context/00_research_scope.md`

### 10.2 入口视图

视觉隐喻：一条通向未来的道路，六个阶段是六道门或六个站点。

```text
1 Passive QA Device
  -> 2 Conversation Memory Assistant
  -> 3 Multimodal Perception Assistant
  -> 4 Long-term Personalized Memory Terminal
  -> 5 Proactive Service Terminal
  -> 6 Embodied Personal Agent
```

### 10.3 每个阶段展示

| 模块 | 内容 |
|---|---|
| 核心能力 | 这一阶段能做什么 |
| 关键技术 | 需要哪些技术成熟 |
| 代表产品或研究 | 对应案例和来源 |
| 主要风险 | 隐私、打扰、错误、物理行动风险 |
| 架构变化 | context pipeline 和记忆架构如何变化 |
| 进入下一阶段条件 | 技术或产品门槛 |

### 10.4 跳转关系

| 动作 | 跳转 |
|---|---|
| 点击阶段 3 | Sensor Port |
| 点击阶段 4 | 七层记忆塔 |
| 点击阶段 5 | Compiler Factory 的主动服务 |
| 点击阶段 6 | Robot Lab |
