# Open Questions

本文件收集研究过程中遇到的未解决问题、证据不足的判断、以及需要进一步验证的假设。

## 格式说明

- `[ ]` 待研究
- `[~]` 部分有线索但不充分
- `[x]` 已解决（记录解决方式和对应 Phase）

---

## Phase 00: 研究范围

- [ ] （初始化阶段，问题将在研究推进中逐步添加）

## Phase 01: 大模型 Context 管理

- [ ] "Lost in the Middle" 效应在超长上下文模型（>1M token）中是否依然显著？
- [ ] Attention Sink 现象在不同架构（Mamba, RWKV 等非 Transformer）中是否存在？
- [ ] Context compression 在实际产品中的部署效果有多少公开数据？

## Phase 02: 软件 Agent Prompt Assembly

- [ ] Claude Code 的 context window 具体分配比例是否有官方数据？
- [ ] Cursor 的 RAG 检索策略是否有公开的技术细节？

## Phase 03: 分层记忆框架

- [ ] Mem0 在生产环境中的效果是否有公开 benchmark？
- [ ] CoALA 框架在 2024-2026 年间是否有后续实现？

## Phase 04: 智能硬件输入

- [ ] 多模态事件切分的 SOTA 方法在低功耗设备上的可行性？
- [ ] 端侧 VLM 的 context 组装延迟是否能满足实时要求？

## Phase 05: 分层记忆架构

- [ ] 从 episodic memory 自动归纳 semantic memory 的可靠方法？
- [ ] 记忆遗忘策略在用户体验上的影响有无实验数据？

## Phase 06: Context Compiler

- [ ] Context Ranker 的权重应该是固定的还是可学习的？
- [ ] 主动服务场景中的"打扰代价"如何量化？

## Phase 07: 硬件案例

- [ ] Meta Ray-Ban AI 眼镜的 context 管理架构是否有公开信息？
- [ ] Humane AI Pin 失败的根本原因中，哪些与 context 管理相关？

## Phase 08: 综合架构

- [ ] 统一 Context Compiler 是否真的可以跨设备形态复用？
- [ ] 隐私保护与 context 质量之间的 trade-off 量化方法？
