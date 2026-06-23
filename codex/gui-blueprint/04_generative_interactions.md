# 生成式交互规则

## 1. 交互目标

本 GUI 的核心交互不是“点击展开”，而是“点击进入一个根据内容对象生成的新空间”。

生成新空间的目的不是展示更多内容，而是用更形象的结构解释一个关键结论，并让用户知道如何把这个结论用于实践。

用户点击不同类型节点时，系统应生成不同界面：

- 点击概念，进入概念剖面。
- 点击机制，进入机制操作台。
- 点击管线，进入流程生产线。
- 点击记忆层，进入楼层房间。
- 点击设备案例，进入场景模拟器。
- 点击证据，进入证据链星图。

## 2. 导航状态模型

界面导航分为 5 种状态。

| 状态 | 名称 | 描述 |
|---|---|---|
| `world` | 世界地图 | 显示完整研究城市 |
| `district` | 城区视图 | 聚焦一个研究主题区域 |
| `building` | 建筑入口 | 显示建筑外观和内部入口 |
| `interior` | 内部空间 | 进入机制、楼层、工厂、实验室 |
| `detail` | 详情面板 | 在内部空间右侧展示证据和原文 |

状态转换：

```text
world
  -> district
  -> building
  -> interior
  -> detail
```

任意状态都应支持：

```text
返回上一层
返回世界地图
打开证据层
搜索节点
复制当前视图链接
```

## 3. 节点点击生成规则

| 节点类型 | 生成场景 | 中央视觉 | 右侧面板 | 下一步 |
|---|---|---|---|---|
| `concept` | 概念剖面 | 分层截面或边界图 | 关键定义、误区、实践启发 | 相关机制 |
| `mechanism` | 操作台 | 输入、处理、输出 | 关键策略、风险、实践启发 | 管线或案例 |
| `pipeline` | 生产线 | 动态流程 | 主结论、关键步骤、设计原则 | 子步骤 |
| `memory_layer` | 楼层房间 | 数据架、缓存、规则墙 | 存什么、何时用、怎么治理 | Compiler |
| `framework` | 档案展柜 | 展柜和能力徽标 | 可迁移价值、短板、采用建议 | Memory Tower |
| `device_case` | 场景模拟器 | 设备舱和时间线 | 输入、决策、输出、实践风险 | Pipeline |
| `schema` | 字段检查器 | JSON 字段树 | 必要字段、使用场景、风险 | Sensor Port |
| `evidence` | 证据星图 | Claim-source 网络 | 结论可信度、缺口、下一步 | 原建筑 |
| `open_question` | 假设工作台 | 问题卡、验证路径 | 为什么影响实践、如何验证 | Evidence |
| `roadmap_stage` | 阶段门 | 时间线站点 | 能力跃迁、技术门槛、风险 | 相关建筑 |

## 4. 深挖界面生成模板

### 4.1 概念剖面模板

适用：

- Context Window
- RAG / Memory / Tool Context
- Context Engineering vs Prompt Engineering

结构：

```text
Header: 概念名 + 一句话
Center: 概念边界或剖面图
Left: 子概念列表
Right: 定义、为什么重要、证据
Bottom: 相关机制和案例
```

生成逻辑：

1. 读取节点 `key_claims`。
2. 生成概念图层。
3. 将 `children` 渲染为可点击区域。
4. 将 `evidence_links` 渲染为证据徽标。

### 4.2 机制操作台模板

适用：

- Prompt Assembly
- Context Compression
- Context Ranking
- Prompt Packing

结构：

```text
Left: 输入材料
Center: 机制操作区
Right: 输出结果
Bottom: 参数、权重、风险提示
```

交互：

- 拖动输入材料。
- 调整权重。
- 查看输出变化。
- 打开证据层查看为什么这样设计。

### 4.3 管线生产线模板

适用：

- Hardware Context Pipeline
- Context Compiler

结构：

```text
Input Dock -> Step Machines -> Output Dock
```

每个步骤有：

```json
{
  "step_id": "privacy_filter",
  "title": "Privacy Filter",
  "input": ["candidate_context", "governance_metadata"],
  "output": ["allowed_context", "blocked_context"],
  "failure_modes": ["bystander leakage", "sensitive cloud upload"],
  "evidence_links": []
}
```

交互：

- 点击机器进入二级内部。
- 播放一次端到端 flow。
- 切换设备形态后，pipeline 权重和输出通道变化。

### 4.4 记忆楼层模板

适用：

- L1 Raw Sensor Buffer 到 L7 Governance Memory

结构：

```text
Top: 楼层名和生命周期
Center: 存储空间视觉化
Left: 写入入口
Right: 召回出口
Bottom: 数据结构和治理信息
```

交互：

- 查看一条样例记忆如何写入。
- 查看它是否进入 prompt。
- 查看过期、降权、删除。
- 切换设备场景。

### 4.5 设备场景模拟器模板

适用：

- AI 眼镜
- AI 耳机
- AI Pin
- 机器人

结构：

```text
Timeline:
  scene event
  sensor input
  context object
  memory recall
  compiler decision
  output action
  feedback update
```

交互：

- 选择设备。
- 选择场景。
- 播放 pipeline。
- 在每一步点击查看内部机制。
- 切换隐私严格程度。
- 切换用户可打扰程度。

## 5. 图层系统

每个界面支持四个图层。

| 图层 | 作用 | 默认状态 |
|---|---|---|
| `structure_layer` | 结构、流程、建筑内部 | 开 |
| `evidence_layer` | 证据强度、来源连接 | 可切换 |
| `risk_layer` | 隐私、打扰、错误、物理风险 | 可切换 |
| `open_question_layer` | 待验证问题和研究缺口 | 可切换 |

图层叠加规则：

- `structure_layer` 是主图层。
- `evidence_layer` 用徽标、亮度或连线表达，不遮挡主结构。
- `risk_layer` 用边框、警示点、锁标记表达。
- `open_question_layer` 用问号、虚线或待验证标签表达。
- 默认只开启 `structure_layer`，避免第一眼信息过载。
- 证据、风险、开放问题是增强理解的图层，不是默认内容堆叠。

## 6. 证据交互

所有关键结论都必须可回溯证据。

### 6.1 证据徽标

| 证据强度 | 视觉 |
|---|---|
| 强 | 实心绿色徽标 |
| 中 | 黄色半实心徽标 |
| 弱 | 橙色虚线徽标 |
| 待验证 | 红色问号徽标 |

### 6.2 证据详情

点击证据徽标后，右侧面板显示：

```text
Claim:
  该结论是什么

Evidence:
  支撑资料 ID 和名称

Strength:
  强 / 中 / 弱 / 待验证

Source Type:
  论文 / 官方文档 / 技术博客 / 产品文档 / 本项目推导

Related Open Questions:
  相关待研究问题

Jump:
  跳到证据天文台
```

## 7. 搜索和生成

搜索不只是跳到文档，而是生成一张局部关系图。

示例：

用户搜索：

```text
privacy
```

生成结果：

```text
Privacy Filter
  -> Governance Memory
  -> Context Object privacy fields
  -> AI Pin privacy risks
  -> Evidence: GDPR / privacy regulation
  -> Open Questions: privacy-quality trade-off
```

点击任意结果，直接进入对应深挖界面。

## 8. 场景播放规则

场景播放用于设备实验室和 Compiler 工厂。

播放状态：

| 状态 | 描述 |
|---|---|
| `setup` | 选择设备和场景 |
| `sensing` | 展示输入源 |
| `contextualizing` | 生成 Context Object |
| `remembering` | 写入或召回记忆 |
| `compiling` | 排序、预算、打包 |
| `deciding` | 模型调用和主动服务判断 |
| `acting` | 输出或行动 |
| `updating` | 反馈写回记忆 |

每个状态都能暂停并查看内部。

## 9. 生成式页面配置示例

```json
{
  "route": "/building/context_compiler",
  "template": "pipeline_factory",
  "background_asset": "compiler_factory_base",
  "overlays": [
    "pipeline_nodes",
    "evidence_badges",
    "risk_markers",
    "breadcrumb",
    "right_detail_panel"
  ],
  "default_layers": ["structure_layer"],
  "available_layers": [
    "evidence_layer",
    "risk_layer",
    "open_question_layer"
  ],
  "entry_animation": "zoom_from_world_map",
  "child_routes": [
    "/building/context_compiler/context_ranking",
    "/building/context_compiler/prompt_packing",
    "/building/context_compiler/privacy_filter"
  ]
}
```

## 10. 动效原则

动效应服务理解，不做纯装饰。

| 动效 | 用途 |
|---|---|
| 镜头推进 | 从总地图进入建筑 |
| 建筑剖开 | 显示内部层级 |
| 流光移动 | 表示数据流 |
| 节点脉冲 | 表示当前处理步骤 |
| 颜色衰减 | 表示遗忘或置信度下降 |
| 权重条变化 | 表示 ranking 权重调整 |
| 路径高亮 | 表示跨主题推导关系 |

## 11. 前端叠加和底图职责

底图负责：

- 空间隐喻。
- 建筑轮廓。
- 氛围和材质。
- 没有文字的结构空间。

前端负责：

- 所有真实文字。
- 所有节点标签。
- 所有可点击热点。
- 所有连线和图层。
- 所有证据徽标。
- 所有状态变化。
- 所有筛选和搜索。

原因：

- imagegen 生成的文字不可控。
- 研究内容会更新。
- 证据强度和开放问题需要动态维护。
- 交互热点必须精确。

## 12. 第一版必须支持的生成式交互

第一版至少实现：

1. 从世界地图进入 6 个建筑。
2. 每个建筑有独立全屏内部空间。
3. Context Compiler 可以播放 9 步 pipeline。
4. 七层记忆塔可以点击每一层。
5. Hardware Lab 可以播放一个 AI 眼镜场景。
6. Evidence Layer 可以在任一建筑中打开。
7. 搜索一个概念后能高亮相关节点。

暂不实现：

- 全 3D 漫游。
- 自由拖拽城市布局。
- 自动从任意 Markdown 生成新建筑。
- 多用户实时协作。

## 13. 清晰度约束

任何生成式界面都必须通过以下检查：

1. 用户是否能在 10 秒内说出这一屏的主结论？
2. 是否有明确的实践启发，而不只是知识展示？
3. 是否避免同时展示超过 3 个并列重点？
4. 证据和细节是否被放在可下钻层，而不是默认挤在主屏？
5. 当前视觉隐喻是否真的帮助理解机制？
