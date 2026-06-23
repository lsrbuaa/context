# 第一版可交互原型范围

## 1. 原型目标

第一版目标是验证 Generative Research GUI 的内容组织和交互体验是否成立。

不追求完整产品化，不追求所有文档全量覆盖。优先验证：

1. 总研究地图是否能让人一眼理解研究主线。
2. 点击建筑后进入全屏深挖界面是否自然。
3. 研究内容是否能通过空间、流程、层级、实验场景被理解。
4. 证据层和开放问题是否能增强可信度，而不是增加负担。
5. imagegen 底图和前端叠加是否能配合。
6. 用户看完后是否能把关键结论转化为产品、架构或研究行动。

第一版明确不追求：

- 展示全部研究内容。
- 覆盖每一个 Markdown 小节。
- 把所有表格、证据和案例同时显示。
- 让界面像资料库或知识库。

## 2. 第一版页面

| 页面 | 路由建议 | 类型 | 必做 |
|---|---|---|---|
| 世界地图 | `/` | Research World | 是 |
| Context Window 观测站 | `/building/context-window` | Concept Interior | 是 |
| 多模态传感器港口 | `/building/sensor-port` | Pipeline Interior | 是 |
| 七层记忆塔 | `/building/memory-tower` | Architecture Interior | 是 |
| Context Compiler 工厂 | `/building/compiler-factory` | Pipeline Interior | 是 |
| Hardware Lab | `/building/hardware-lab` | Device Simulator | 是 |
| Evidence Observatory | `/building/evidence` | Evidence View | 是 |
| Prompt Assembly 工作室 | `/building/prompt-assembly` | Mechanism Interior | 可选 |
| Roadmap Boulevard | `/building/roadmap` | Roadmap View | 可选 |

## 3. 第一版核心故事线

演示时建议走这条线：

```text
世界地图
  -> Context Window 观测站
  -> 多模态传感器港口
  -> 七层记忆塔
  -> Context Compiler 工厂
  -> Hardware Lab: AI 眼镜会议场景
  -> Evidence Observatory
```

这条线能回答：

> 为什么智能硬件时代的关键不是单次问答，而是 Context Assembly？

## 4. 必做交互

### 4.1 世界地图

- Hover 区域显示一句话介绍。
- 点击建筑进入全屏深挖界面。
- 主路径可高亮。
- 支持搜索节点。
- 支持打开证据图层。

### 4.2 Context Window 观测站

- 显示 context window 分层截面。
- 点击每层显示作用和风险。
- 展示 RAG、Memory、Tool Context 边界。
- 展示至少 3 个行为现象：
  - Lost in the Middle
  - Attention Sink
  - Recency Bias

### 4.3 多模态传感器港口

- 选择传感器输入。
- 显示原始输入到 Context Object 字段的映射。
- 播放“连续流 -> 事件切分 -> Context Object”。
- 可打开隐私过滤图层。

### 4.4 七层记忆塔

- 显示 L1-L7 七层。
- 点击每层进入该层说明。
- 展示写入流和召回流两种模式。
- L7 Governance 外壳可单独高亮。

### 4.5 Context Compiler 工厂

- 播放 9 步 pipeline。
- 点击 Context Ranking 进入权重控制台。
- 点击 Prompt Packing 进入首尾注意力布局。
- 展示超 token budget 时的降级策略。

### 4.6 Hardware Lab

- 选择至少一个设备：AI 眼镜。
- 播放一个场景：会议准备提醒。
- 显示完整链路：

```text
sensor input
  -> context object
  -> memory recall
  -> compiler decision
  -> output
  -> feedback update
```

### 4.7 Evidence Observatory

- 显示 Claim-to-source 网络。
- 支持按强、中、弱、待验证过滤。
- 从任意建筑跳到相关证据。
- 从证据跳回建筑。

## 5. 第一版数据范围

第一版只需要手工配置核心节点，不做自动全量解析。

核心节点：

| ID | 类型 | 来源 |
|---|---|---|
| `context_window` | concept | `01_llm_context_management.md` |
| `rag_memory_tool_boundary` | concept | `01_llm_context_management.md` |
| `context_behavior_lab` | mechanism | `01_llm_context_management.md` |
| `hardware_context_inputs` | pipeline | `04_hardware_context_inputs.md` |
| `context_object_schema` | schema | `schemas/context-object.json` |
| `seven_layer_memory` | architecture | `05_hierarchical_memory_architecture.md` |
| `context_compiler` | pipeline | `06_context_compiler.md` |
| `context_ranker` | mechanism | `06_context_compiler.md` |
| `ai_glasses_case` | device_case | `_archive/cases/ai-glasses.md` |
| `evidence_matrix` | evidence | `sources/evidence_matrix.md` |
| `open_questions` | open_question | `sources/open_questions.md` |

## 6. 建议技术实现

后续如果进入实现，可采用：

| 层 | 建议 |
|---|---|
| 前端框架 | React 或 Next.js |
| 地图和节点 | React Flow、SVG overlay 或 Canvas |
| 动效 | Framer Motion |
| 图表 | ECharts 或 D3 |
| 底图 | imagegen 输出 PNG/WebP |
| 内容数据 | 手工 JSON seed，后续再做 Markdown parser |
| 样式 | CSS variables + component system |

不建议第一版做完整 3D，因为内容理解优先级高于空间炫技。

## 7. 推荐文件结构

如果后续实现原型，可以使用：

```text
gui-prototype/
  src/
    data/
      nodes.json
      world-map.json
      evidence.json
      scenarios.json
    assets/
      world-map-base.webp
      memory-tower-base.webp
      compiler-factory-base.webp
      sensor-port-base.webp
    components/
      WorldMap.tsx
      BuildingInterior.tsx
      EvidenceLayer.tsx
      DetailPanel.tsx
      PipelineFactory.tsx
      MemoryTower.tsx
      ScenarioSimulator.tsx
    routes/
      index.tsx
      building/
  docs/
    interaction-spec.md
```

## 8. 验收标准

第一版原型完成后，应满足：

1. 一个不了解项目的人，在 2 分钟内能说出研究主线。
2. 点击建筑后确实进入新的深挖界面，而不是展开文本。
3. 七层记忆塔能让人理解每层职责和生命周期。
4. Context Compiler 工厂能让人理解模型调用前发生了什么。
5. AI 眼镜场景能串起输入、记忆、编译、输出、反馈。
6. 任一关键结论都能查看证据强度。
7. 页面中没有把关键文字烘焙在图片里。
8. 每个核心建筑都能输出 1 到 3 条实践指导。
9. 默认视图不拥挤，细节通过点击、图层或右侧面板下钻。
10. 看完演示的人能回答“如果我要设计智能硬件 context 系统，下一步应该重点做什么”。

## 9. 下一步建议

完成本蓝图后，建议按以下顺序继续：

1. 把 `01_content_architecture.md` 中的核心节点转成 `nodes.json`。
2. 用 `05_imagegen_asset_plan.md` 先生成 Batch 1 四张底图。
3. 为四张底图标注热点坐标。
4. 实现世界地图和 3 个核心建筑：Sensor Port、Memory Tower、Compiler Factory。
5. 接入 Evidence Layer。
6. 再补 Hardware Lab 的 AI 眼镜场景模拟。
