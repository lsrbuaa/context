# Imagegen 视觉资产计划

## 1. 使用原则

imagegen 适合生成高质量底图和空间隐喻，不适合生成真实文字、节点标签、可点击控件和证据徽标。

### 1.1 imagegen 负责

- 研究城市总地图底图。
- 建筑外观。
- 建筑内部空间的无文字底图。
- 复杂氛围和材质。
- 高质量组图的基础画面。

### 1.2 前端负责

- 所有中文和英文文字。
- 所有节点标签。
- 所有连线。
- 所有热点区域。
- 所有证据强度徽标。
- 所有搜索、筛选、面板和控件。
- 所有动态状态。

## 2. 统一视觉风格

建议风格：

```text
isometric technical editorial illustration,
futuristic research city,
clean architectural cutaway,
high detail,
professional product strategy visual,
soft neutral lighting,
clear spatial hierarchy,
glass, metal, light stone, subtle greenery,
no readable text,
no logos,
16:9
```

避免：

- 大面积紫蓝渐变。
- 纯营销海报风。
- 过暗、过模糊、过装饰。
- 把中文或英文文字画在图里。
- 让建筑过于拥挤，导致前端无法叠加标签。

## 3. 首批底图清单

| 资产 ID | 名称 | 用途 | 优先级 |
|---|---|---|---|
| `world_map_base` | Context Engineering 研究城市总图 | 首页总地图 | P0 |
| `context_observatory_base` | Context Window 观测站 | Foundation 深挖界面 | P1 |
| `prompt_workshop_base` | Prompt Assembly 工作室 | 软件 Agent 深挖界面 | P1 |
| `memory_archive_base` | Memory Framework 档案馆 | 框架对比界面 | P1 |
| `sensor_port_base` | 多模态传感器港口 | 硬件输入界面 | P0 |
| `memory_tower_cutaway_base` | 七层记忆塔剖面 | 分层记忆架构界面 | P0 |
| `compiler_factory_base` | Context Compiler 工厂 | Compiler Pipeline 界面 | P0 |
| `hardware_lab_base` | 智能硬件实验室 | 硬件案例界面 | P1 |
| `evidence_observatory_base` | 证据天文台 | 证据矩阵界面 | P1 |
| `roadmap_boulevard_base` | AI 终端路线图大道 | 演进路线图界面 | P1 |

P0 是第一版原型最需要的资产。

## 4. 资产规格

### 4.1 `world_map_base`

用途：首页总地图。

画面要求：

- 16:9 横向。
- 一座俯视或等距视角研究城市。
- 有 8 到 9 个清晰区域。
- 中央主路贯穿城市。
- 每个区域有不同建筑形态。
- 右侧和顶部留出 UI 面板空间。
- 不包含任何文字。

前端叠加：

- 区域名称。
- 建筑热点。
- 主研究路径。
- 证据图层。
- 搜索框。
- 面包屑。

Prompt:

```text
Create a high-detail isometric futuristic research city map for a generative user interface. The city has distinct architectural districts connected by a clear central boulevard: an observatory district, software engineering studios, a memory archive, a multimodal sensor port, a tall transparent memory tower, a context compiler factory, a hardware device laboratory, an evidence observatory, and a future roadmap boulevard. Clean professional product strategy visual, soft neutral lighting, glass and metal architecture with subtle greenery, clear open spaces for UI overlays, no readable text, no labels, no logos, no people close-up, 16:9.
```

Negative prompt:

```text
readable text, letters, logos, dark blurry background, heavy purple gradient, cluttered buildings, fantasy style, cartoon, poster typography
```

### 4.2 `context_observatory_base`

用途：Context Window 观测站深挖界面。

画面要求：

- 一个透明观测站内部。
- 中央有无文字的巨大分层容器或截面。
- 分层容器要能让前端叠加 System、User、RAG、Memory 等标签。
- 周围有观测仪器和数据光线。

前端叠加：

- Context Window 分层标签。
- 区块说明。
- 行为现象热点。

Prompt:

```text
Create a clean isometric cutaway illustration of a futuristic observatory interior. In the center is a large transparent layered container representing an AI context window, with multiple empty horizontal bands and clear space for UI labels. Around it are subtle research instruments, screens without text, and soft data light beams. Professional technical editorial style, precise geometry, glass and brushed metal, neutral lighting, no readable text, no logos, 16:9.
```

### 4.3 `prompt_workshop_base`

用途：Prompt Assembly 工作室。

画面要求：

- 左侧多个输入仓。
- 中间装配台或机械臂。
- 右侧输出容器。
- 所有区域留白明确。

前端叠加：

- Input Bins 标签。
- Select、Rank、Compress、Pack 步骤。
- 最终 prompt 截面。

Prompt:

```text
Create a high-detail isometric technical workshop for AI prompt assembly. On the left are several empty input bins, in the center is a precise assembly bench with robotic arms and sorting rails, and on the right is a clean output container. The composition should clearly imply input, processing, and output, with open surfaces for UI overlays. Professional software engineering lab aesthetic, no readable text, no logos, soft neutral lighting, 16:9.
```

### 4.4 `memory_archive_base`

用途：Memory Framework 档案馆。

画面要求：

- 档案馆大厅。
- 多个无文字展柜。
- 中央有能力矩阵展示区，但屏幕无文字。
- 可以叠加 MemGPT、CoALA、Mem0 等标签。

Prompt:

```text
Create an isometric futuristic archive hall for AI memory frameworks. The hall contains multiple clean display cases arranged in a grid, a central comparison console with blank screens, and subtle shelves of abstract data artifacts. Clear spacing for UI overlays and labels. Elegant research museum atmosphere, glass cases, warm neutral light, no readable text, no logos, 16:9.
```

### 4.5 `sensor_port_base`

用途：多模态传感器港口。

画面要求：

- 港口或中转站隐喻。
- 不同数据流从左侧进入。
- 中间有过滤闸门和事件切分区域。
- 右侧输出标准化集装箱或对象容器。

前端叠加：

- Camera、Microphone、IMU、GPS 等输入标签。
- Privacy Filter。
- Event Segmentation。
- Context Object 字段。

Prompt:

```text
Create a detailed isometric multimodal sensor port for an AI hardware context system. Streams of abstract visual, audio, motion, location, calendar, and device-state data flow into a clean futuristic port. In the middle are filter gates and segmentation terminals, and on the right are standardized blank data containers representing context objects. Professional technical editorial illustration, clean spatial hierarchy, no readable text, no labels, no logos, 16:9.
```

### 4.6 `memory_tower_cutaway_base`

用途：七层记忆塔。

画面要求：

- 一栋可剖开的透明七层高塔。
- 七层清晰分开。
- 外侧有透明治理外壳。
- 每层空间有不同功能感，但不包含文字。

前端叠加：

- L1-L7 标签。
- 每层热点。
- 数据流和召回流。
- 证据和风险标记。

Prompt:

```text
Create a high-detail isometric cutaway of a transparent seven-level memory tower for an AI hardware system. The tower has seven clearly separated floors, with a subtle transparent outer shell wrapping all levels to represent governance. Lower levels look like fast sensor buffers, middle levels like active workspaces and event archives, upper levels like knowledge and rule libraries. Clean futuristic architecture, precise floor separation, open space for UI labels, no readable text, no logos, 16:9.
```

### 4.7 `compiler_factory_base`

用途：Context Compiler 工厂。

画面要求：

- 横向生产线。
- 左侧输入材料，中间 9 个连续机器位，右侧输出。
- 每台机器有清晰独立轮廓，方便叠加热点。
- 不能太拥挤。

前端叠加：

- 9 个 pipeline step。
- 输入输出流。
- 当前步骤高亮。
- Ranking 权重面板。

Prompt:

```text
Create a clean isometric cutaway illustration of a futuristic context compiler factory. A horizontal production line runs from left to right with nine distinct blank machine stations, input docks on the left, output docks on the right, and glowing abstract data flows moving through the line. The machine stations should have clear empty surfaces for UI overlays and clickable labels. Professional technical product architecture style, neutral lighting, glass and metal, no readable text, no logos, 16:9.
```

### 4.8 `hardware_lab_base`

用途：智能硬件案例实验室。

画面要求：

- 中央设备选择台。
- 四个实验舱：眼镜、耳机、Pin、机器人。
- 每个实验舱有独特轮廓，但不使用真实品牌。

前端叠加：

- 设备名称。
- 场景列表。
- 输入源、输出通道、隐私风险。

Prompt:

```text
Create an isometric futuristic AI hardware laboratory with four distinct testing pods around a central selection platform. The pods represent smart glasses, AI earbuds, an AI pin or wearable recorder, and a home robot or VLA robot, but without any brand logos. Clean technical environment, clear spaces for UI overlays, subtle screens without text, professional product research style, no readable text, no logos, 16:9.
```

### 4.9 `evidence_observatory_base`

用途：证据天文台。

画面要求：

- 天文台内部。
- 中央有星图式网络，但无文字。
- 星点和连线不要过密。
- 右侧留出证据详情面板空间。

前端叠加：

- Claim 节点。
- Source 节点。
- 证据强度颜色。
- 开放问题。

Prompt:

```text
Create a clean isometric evidence observatory interior for a research GUI. The center contains a large blank star-map display with abstract nodes and light connections, sparse enough for UI overlays. Around it are research consoles with screens showing no text. Professional analytical atmosphere, soft neutral lighting, glass dome, no readable text, no logos, 16:9.
```

### 4.10 `roadmap_boulevard_base`

用途：路线图大道。

画面要求：

- 一条通向远方的未来道路。
- 六个阶段门或站点。
- 每个站点留出标签位置。
- 不含文字。

前端叠加：

- 阶段 1-6。
- 核心能力、技术、风险。
- 相关建筑跳转点。

Prompt:

```text
Create a wide isometric futuristic roadmap boulevard with six clear stage gates or stations along a path leading toward an advanced AI terminal city in the distance. Each station has open space for UI labels, with subtle architectural progression from simple devices to embodied intelligent agents. Clean professional strategy visualization, soft neutral lighting, no readable text, no logos, 16:9.
```

## 5. 组图拼装方式

推荐实现方式：

```text
Base Image
  + SVG hotspots
  + HTML labels
  + Canvas/SVG animated flows
  + React panels
  + Evidence/risk/open-question overlays
```

每张底图输出后，需要制作一个热点配置文件：

```json
{
  "asset_id": "compiler_factory_base",
  "hotspots": [
    {
      "id": "trigger_detection_machine",
      "shape": "rect",
      "x": 0.12,
      "y": 0.42,
      "width": 0.08,
      "height": 0.16
    }
  ]
}
```

坐标采用 0 到 1 的相对坐标，适配不同屏幕尺寸。

## 6. 生成顺序

不要一次性生成全部图片。建议按原型优先级分批：

### Batch 1

1. `world_map_base`
2. `memory_tower_cutaway_base`
3. `compiler_factory_base`
4. `sensor_port_base`

这四张支撑第一版核心叙事。

### Batch 2

1. `hardware_lab_base`
2. `context_observatory_base`
3. `prompt_workshop_base`
4. `evidence_observatory_base`

### Batch 3

1. `memory_archive_base`
2. `roadmap_boulevard_base`
3. 设备实验舱细分图
4. 单个楼层细分图

## 7. 质量检查

每张图生成后检查：

- 是否没有可读文字。
- 是否有足够留白叠加 UI。
- 主要区域是否清楚可分。
- 风格是否统一。
- 16:9 构图是否稳定。
- 亮度是否适合叠加深色或浅色文字。
- 是否过度偏紫、偏暗、偏营销海报。

## 8. 后续可选增强

如果第一版体验成立，可以继续生成：

- 七层记忆塔每一层的独立房间底图。
- Context Ranker 控制台底图。
- Prompt Packing 布局器底图。
- AI 眼镜会议场景模拟底图。
- 机器人 VLA 双层 Context 架构底图。
