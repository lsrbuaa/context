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

前置目标：

- 基于 [literature-review.md](literature-review.md) 和 [engineering-cases.md](engineering-cases.md) 完成研究证据链。
- 明确仓库专业化升级项：证据、工程对象、评估、路线图。

目标：

- 梳理现有设备和 App 可用数据。
- 标注数据可靠性、敏感度、授权状态。
- 选定 2-3 个高价值场景。

产出：

- 用户数据资产地图。
- 场景数据需求表。
- 隐私风险清单。
- 关键判断与论文/案例的映射表。

退出条件：

- 每类数据源都有可靠性、敏感度、授权方式和默认处理策略。
- 至少选出一个低敏、高频、可验证的 PoC 场景。
- 明确哪些数据只能端侧处理，哪些可以进入云端记忆系统。

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
- Evidence Ledger Schema。
- Context Package Contract。

退出条件：

- Event、Memory、Policy、Evidence、Context Package 都有最小 JSON 结构。
- Memory 有 candidate、active、pending_confirmation、deprecated、deleted 等生命周期状态。
- 删除语义覆盖结构化记录、向量索引、摘要缓存和图谱关系。

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

退出条件：

- 能从样例 Event 中生成候选 Memory。
- 能解释每条 Memory 的 evidence。
- 能比较最近对话、普通 RAG、结构化记忆三组结果。
- 高敏或未授权记忆不会进入 Context Package。

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

退出条件：

- 至少完成 30 条 eval case。
- 五组 baseline 至少能离线对比。
- Context Package 长度稳定，不随历史数据线性增长。
- 输出包含 memory_id、policy_id 和 evidence 摘要，便于审计。

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

- 建立数据资产地图：设备、App、云端、客服、显式反馈。
- 补充 Evidence Ledger 和 Context Package Contract。
- 定义 `events/*.jsonl`、`memories/*.jsonl`、`policies/*.jsonl`、`eval-cases/*.jsonl` 的样例格式。
- 构建 30 条最小 eval case，覆盖智能家居、售后、日程、健康边界、多人家庭和删除纠错。
- 对比“无记忆”“最近对话”“普通 RAG”“结构化记忆”“完整 Policy + Composer”五组 baseline。
- 设计用户删除、纠错、权限撤回和冲突确认的最小交互流程。
- 在完成 eval case 之后，再实现最小 Context Composer CLI。
