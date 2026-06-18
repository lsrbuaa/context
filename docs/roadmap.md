# 路线图

本文档把研究框架转成可执行的 MVP 阶段。

## 阶段 0：仓库整理

目标：

- 建立公开仓库。
- 梳理研究框架、架构、Schema、评估和路线图文档。
- 明确后续 PoC 的最小技术边界。

产出：

- `README.md`
- `docs/whitepaper.md`
- `docs/taxonomy.md`
- `docs/research-agenda.md`
- `docs/architecture.md`
- `docs/memory-schema.md`
- `docs/evaluation.md`
- `docs/roadmap.md`

## 阶段 1：数据资产地图，2-3 周

目标：

- 梳理现有设备和 App 可用数据。
- 标注数据可靠性、敏感度、授权状态。
- 选定 2-3 个高价值场景。

产出：

- 用户数据资产地图。
- 场景数据需求表。
- 隐私风险清单。

## 阶段 2：记忆 Schema 和事件标准，3-4 周

目标：

- 定义统一事件模型。
- 定义用户记忆 Schema。
- 建立记忆类型 taxonomy。

产出：

- Event Schema。
- Memory Schema。
- 记忆分类体系。
- 样例数据集。

## 阶段 3：记忆抽取与检索 PoC，4-6 周

目标：

- 从历史数据中抽取记忆候选。
- 建立记忆评分。
- 建立混合检索和 rerank。
- 初步接入一个 Agent 场景。

产出：

- 记忆抽取 pipeline。
- 用户记忆库。
- 检索服务。
- 场景 demo。

## 阶段 4：Context Composer 和评估集，4-6 周

目标：

- 实现上下文组装。
- 实现 token 预算控制。
- 构建个性化评测集。
- 对比不同记忆策略效果。

产出：

- Context Composer 服务。
- eval 数据集。
- 实验报告。
- MVP 产品建议。

## 阶段 5：用户可控与线上灰度，6-8 周

目标：

- 用户可查看、编辑、删除记忆。
- 增加权限控制和审计。
- 小流量灰度验证。

产出：

- 用户记忆管理界面。
- 权限和审计系统。
- 灰度实验数据。
- 产品化决策报告。

## 近期 Backlog

- 拆出记忆 taxonomy 初稿。
- 定义 `events/*.jsonl` 和 `memories/*.jsonl` 的样例数据格式。
- 实现一个最小 Context Composer CLI。
- 构建 20-50 条智能家居场景 eval case。
- 对比“最近对话”和“结构化记忆检索”的效果差异。
- 设计用户删除、纠错和冲突确认的最小交互流程。
