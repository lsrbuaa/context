# 总研究地图设计

## 1. 总体隐喻

整个 GUI 是一座“Context Engineering 研究城市”。

城市不是装饰，而是内容结构：

- 城区代表研究主题群。
- 建筑代表核心研究对象。
- 道路代表研究主线和推导关系。
- 地铁线或能量线代表跨主题依赖。
- 天文台、档案馆、工厂、实验室等建筑隐喻对应不同的信息展示方式。

## 2. 城市总览

```text
                         [Evidence Observatory]
                                  |
                                  |
[Context Foundation] -> [Software Agent District] -> [Memory Archive]
                                  |                         |
                                  |                         |
                         [Hardware Sensor Port] -> [Memory Tower]
                                  |                         |
                                  |                         |
                           [Compiler Factory] -> [Hardware Lab]
                                  |
                                  |
                            [Roadmap Boulevard]
```

## 3. 城区列表

| 城区 ID | 城区名称 | 对应研究内容 | 视觉隐喻 | 用户第一眼应理解 |
|---|---|---|---|---|
| `foundation_district` | Context Foundation 区 | Context Window、RAG、Memory、Tool Context、12 个行为现象 | 观测站和知识图书馆 | 软件 Agent 的上下文管理底层逻辑 |
| `software_agent_district` | Software Agent 区 | Claude Code、Cursor、ChatGPT Memory、LangGraph、MCP | 工程工作室群 | 现有软件系统如何组装上下文 |
| `memory_archive_district` | Memory Framework 档案馆 | MemGPT、Generative Agents、CoALA、Mem0、Zep | 档案馆和展柜 | 不同记忆框架能迁移什么，缺什么 |
| `sensor_port_district` | Hardware Sensor 港口 | 摄像头、麦克风、IMU、GPS、设备状态、事件切分 | 多模态港口 | 硬件输入从连续流变成 Context Object |
| `memory_tower_district` | 七层记忆塔 | L1-L7 记忆架构 | 剖面高塔 | 智能硬件需要什么样的分层记忆 |
| `compiler_factory_district` | Context Compiler 工厂 | Trigger、Retrieval、Privacy、Ranking、Budget、Packing | 工厂生产线 | 模型调用前如何编译上下文 |
| `hardware_lab_district` | Hardware Lab | AI 眼镜、耳机、AI Pin、机器人 | 设备实验室 | 不同硬件形态的 context 策略差异 |
| `evidence_observatory_district` | Evidence Observatory | 证据矩阵、来源、开放问题 | 天文台和证据星图 | 每个结论的可信度和缺口 |
| `roadmap_district` | Roadmap Boulevard | AI 终端演进路线图 | 未来道路和阶段门 | 从被动问答到具身个人 Agent 的演进 |

## 4. 主道路

主道路承担第一次演示时的线性叙事。

```text
Context Foundation
  -> Software Agent District
  -> Memory Archive
  -> Sensor Port
  -> Memory Tower
  -> Compiler Factory
  -> Hardware Lab
  -> Roadmap Boulevard
```

叙事逻辑：

1. 先理解 LLM context window 里到底放什么。
2. 再看软件 Agent 如何在实际产品中做 Prompt Assembly。
3. 再比较现有记忆框架。
4. 然后迁移到智能硬件，处理连续多模态输入。
5. 设计七层记忆架构。
6. 通过 Context Compiler 选择、排序、压缩和拼接 context。
7. 用设备案例验证策略差异。
8. 最后得到路线图。

## 5. 跨区连接

跨区连接用于表达非线性的研究依赖。

| 起点 | 终点 | 关系 |
|---|---|---|
| Context Window | Context Compiler | Compiler 的 Prompt Packing 依赖 context window 行为特性 |
| RAG / Memory / Tool Boundary | Memory Framework Archive | 框架对比需要先理解三者边界 |
| 12 Context Pitfalls | Prompt Assembly Studio | 软件 Agent 的装配策略是对这些现象的工程应对 |
| Memory Framework Archive | Memory Tower | 七层记忆架构吸收 CoALA、MemGPT、Generative Agents 等框架 |
| Sensor Port | Context Object Schema | 传感器输入被结构化为统一对象 |
| Context Object Schema | Context Compiler | Compiler 读取结构化对象进行 ranking 和 packing |
| Memory Tower | Context Compiler | Compiler 从不同记忆层检索候选内容 |
| Context Compiler | Hardware Lab | 设备案例验证 Compiler 策略 |
| Evidence Observatory | 所有建筑 | 每个关键结论都可反查证据 |
| Open Questions | 所有建筑 | 每个区域都暴露待研究问题 |

## 6. 建筑清单

### 6.1 Context Foundation 区

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `context_window_observatory` | Context Window 观测站 | 巨型 context window 截面 |
| `rag_memory_tool_boundary_hall` | RAG / Memory / Tool 边界大厅 | 三角边界对比图 |
| `context_behavior_lab` | Context 行为实验室 | 12 个现象的实验陈列 |

### 6.2 Software Agent 区

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `prompt_assembly_workshop` | Prompt Assembly 工作室 | Prompt 装配台 |
| `claude_code_studio` | Claude Code Studio | 项目规则、工具结果、compaction 机制剖面 |
| `ide_agent_studio` | IDE Agent Studio | 代码索引、当前编辑状态、检索上下文 |
| `memory_product_room` | ChatGPT Memory Room | 用户记忆写入、查看、删除和注入 |
| `mcp_gateway` | MCP Gateway | Tools、Resources、Prompts 接入门 |

### 6.3 Memory Archive

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `memory_framework_archive` | 记忆框架档案馆 | 框架展柜和能力矩阵 |
| `memgpt_exhibit` | MemGPT / Letta 展柜 | virtual context management 模型 |
| `generative_agents_exhibit` | Generative Agents 展柜 | observation、reflection、planning |
| `coala_exhibit` | CoALA 展柜 | working、episodic、semantic、procedural 分类 |
| `graph_memory_exhibit` | Zep / Graphiti 展柜 | 实体关系图谱记忆 |

### 6.4 Hardware Sensor 港口

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `sensor_port` | 多模态传感器港口 | 传感器流入港口并变成 context |
| `event_segmentation_terminal` | 事件切分码头 | 连续流到离散事件的切分线 |
| `privacy_filter_gate` | 隐私过滤闸门 | 端侧过滤、旁人数据、敏感级别 |
| `context_object_customs` | Context Object 海关 | Context JSON 字段检查器 |

### 6.5 七层记忆塔

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `seven_layer_memory_tower` | 七层记忆塔 | 可剖开的七层高塔 |
| `raw_buffer_floor` | L1 Raw Sensor Buffer | 环形缓存房间 |
| `perception_wm_floor` | L2 Perception Working Memory | 实时感知状态室 |
| `task_wm_floor` | L3 Task Working Memory | 当前任务工作台 |
| `episodic_memory_floor` | L4 Episodic Memory | 事件档案库 |
| `semantic_memory_floor` | L5 Semantic Memory | 用户画像和关系知识库 |
| `procedural_memory_floor` | L6 Procedural Memory | 行为规则引擎室 |
| `governance_memory_shell` | L7 Governance Memory | 覆盖全塔的治理外壳 |

### 6.6 Context Compiler 工厂

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `compiler_factory` | Context Compiler 工厂 | 9 步生产线 |
| `trigger_detection_machine` | Trigger Detection | 触发条件面板 |
| `retrieval_machine` | Context Retrieval | 从七层记忆拉取候选 |
| `ranking_machine` | Context Ranker | 多维评分控制台 |
| `budget_machine` | Token Budget Allocator | token 预算分配仪表盘 |
| `packing_machine` | Prompt Packing | 首尾注意力布局器 |
| `feedback_machine` | Feedback & Memory Update | 反馈写回回路 |

### 6.7 Hardware Lab

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `hardware_case_lab` | 智能硬件实验室 | 设备选择大厅 |
| `ai_glasses_lab` | AI 眼镜实验舱 | 会议、人物识别、安全提醒模拟 |
| `ai_earbuds_lab` | AI 耳机实验舱 | 会议辅助、人名提醒、语言辅助 |
| `ai_pin_lab` | AI Pin 实验舱 | 会议摘要、承诺追踪、生活日志 |
| `robot_lab` | 机器人实验舱 | 物品整理、失败学习、主动陪伴 |

### 6.8 Evidence Observatory

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `evidence_observatory` | 证据天文台 | Claim-to-source 星图 |
| `source_registry_library` | 来源图书馆 | 来源清单和类型 |
| `open_questions_control_room` | 开放问题控制室 | 待研究问题雷达 |

### 6.9 Roadmap Boulevard

| 建筑 ID | 名称 | 点击后界面 |
|---|---|---|
| `terminal_roadmap` | AI 终端演进大道 | 六阶段路线图 |
| `passive_qa_gate` | 阶段 1 被动问答 | 基础设备能力 |
| `conversation_memory_gate` | 阶段 2 会话记忆 | 跨会话记忆 |
| `multimodal_assistant_gate` | 阶段 3 多模态感知 | 感知输入 |
| `personal_memory_gate` | 阶段 4 长期个性化记忆 | 画像和习惯 |
| `proactive_terminal_gate` | 阶段 5 主动服务终端 | 打扰判断和主动输出 |
| `embodied_agent_gate` | 阶段 6 具身个人 Agent | 动作、空间、多设备协同 |

## 7. 首页默认视角

首页应是 16:9 横向世界地图。

首屏信息优先级：

1. 先让用户看懂一句话结论：下一代 AI 终端的关键能力是 Context Assembly。
2. 中央主路清晰，表达从软件 Context 到硬件 Context 的迁移。
3. 七大区域可辨认，但不显示完整章节细节。
4. 每个区域只露出一个视觉锚点和一句话。
5. 不要在底图中嵌入大量文字。
6. 前端叠加区域名称、主路径、少量关键建筑、搜索框和证据图层开关。

首页不应像资料库首页，而应像一张研究结论地图。用户第一眼要能回答：

```text
这项研究在讲什么？
为什么智能硬件让 Context 管理变复杂？
我们最终提出了什么架构答案？
```

## 8. 首页交互

| 操作 | 结果 |
|---|---|
| Hover 城区 | 区域亮起，显示一句话说明 |
| 点击城区 | 镜头推进到该城区，显示建筑 |
| 点击建筑 | 进入全屏深挖界面 |
| 长按或右键建筑 | 打开证据和来源快速卡 |
| 搜索概念 | 地图高亮相关建筑和连接 |
| 打开证据图层 | 所有建筑显示证据强度颜色 |
| 打开开放问题图层 | 所有待验证节点显示标记 |

## 9. 颜色和视觉编码

| 信息 | 编码方式 |
|---|---|
| Part A 软件基础 | 冷色科技感，但避免单一蓝紫 |
| Part B 硬件迁移 | 金属、玻璃、绿色传感器光线 |
| 记忆架构 | 分层暖光和半透明剖面 |
| Compiler | 工业生产线、明亮能量流 |
| 证据强度强 | 绿色或实心标记 |
| 证据强度中 | 黄色或半实心标记 |
| 证据强度弱 | 橙色或虚线标记 |
| 待验证 | 红色或问号标记 |
| 隐私风险 | 深红边框或锁标记 |

## 10. 地图底图生成原则

地图底图可以用 imagegen 生成，但必须遵守：

- 不生成可读文字。
- 不把节点标签画死在图片里。
- 建筑形态要清楚，便于前端叠加热点。
- 留出顶部搜索栏、右侧图层面板、底部路径面包屑空间。
- 保持 16:9，适合演示屏。
