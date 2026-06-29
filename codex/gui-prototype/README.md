# Context Engineering Living City

这是一个 2.5D semantic zoom GenUI 原型。界面不再只是“点击建筑后换详情页”，而是用结构化 `UIPlan` 驱动一条连续缩放路径：

```text
研究城市 -> 建筑外观 -> 建筑剖面/房间 -> 房间物件 -> 证据/风险/开放问题
```

## 打开方式

直接用浏览器打开：

```text
F:\context\codex\gui-prototype\index.html
```

也可以用 hash 直达：

```text
index.html#context-window
index.html#sensor-port
index.html#memory-tower
index.html#compiler-factory
index.html#hardware-lab
index.html#genui-studio
index.html#evidence
```

房间和物件也支持 hash：

```text
index.html#genui-studio/schema-room/plan-validator
```

## 当前实现

- `ResearchWorld -> Building -> Room -> Object -> Evidence` 四级结构。
- 每个建筑包含空间坐标、缩放层级、组件类型、证据强度、风险、开放问题和关联来源。
- 每个建筑至少 3 个房间、6 个可点击物件。
- 世界层建筑已对象化：建筑体块、地面环、路线编号、状态点和绑定式铭牌属于同一个可交互 group。
- 世界层不再用漂浮文本卡片承载建筑说明；长文本进入 hover 短提示、建筑内部和右侧详情面板。
- `generateUIPlan(intent, focusNode)` 生成结构化计划。
- `validateUIPlan(plan)` 做确定性校验，失败时退回 fallback 模板。
- 城市里点击建筑会触发连续 zoom-in 动画。
- 建筑内使用 semantic zoom：建筑层显示房间，房间层展开物件，物件层显示 trace、机制、证据、风险和问题。
- 输入不同研究目标会自动映射到理解、设计、验证、演示四类意图，并改变路线、默认房间和证据显露。
- 证据、风险、问题图层可手动开关；验证意图会自动加强证据/风险/问题显露。

## 视觉资产

项目资产在：

```text
assets/generated/
```

原有地图/建筑外观：

- `world-map-base.png`
- `sensor-port-base.png`
- `memory-tower-base.png`
- `compiler-factory-base.png`
- `hardware-lab-base.png`
- `evidence-observatory-base.png`
- `genui-studio-base.png`

本轮用内置 imagegen 新增的无文字建筑剖面底图：

- `context-window-interior.png`
- `sensor-port-interior.png`
- `memory-tower-interior.png`
- `compiler-factory-interior.png`
- `hardware-lab-interior.png`
- `evidence-observatory-interior.png`
- `genui-studio-interior.png`

所有文字、热点、证据标记、风险标记和连线均由 HTML/SVG 叠加，不烘焙进图片。

## 设计约束

- LLM/GenUI 层只生成结构化 `UIPlan`，不直接生成 DOM。
- UI 组件由确定性前端模板渲染。
- 视觉资产只承担空间背景，不承担可解释内容。
- 每个自动生成的细节都保留证据、风险或开放问题入口。
- 默认使用 2.5D DOM/SVG/CSS transform，避免过早进入重型 3D 工程。
