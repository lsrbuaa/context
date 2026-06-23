# Open Questions

本文件收集研究过程中遇到的未解决问题、证据不足的判断、以及需要进一步验证的假设。

## 状态标记

- `[ ]` 待研究
- `[~]` 部分有线索但证据不充分
- `[x]` 已解决（记录解决方式和对应 Phase）

---

## Phase 00: 研究范围

- [~] Context Engineering 是否已有公认的学术定义？— Anthropic 2025 年博客有明确定义，但尚无顶会论文专门定义此概念
- [ ] "分层记忆"模型在智能硬件中是否有已公开验证的完整实现？
- [~] Context Compiler 是否已有成熟开源实现？— LangGraph 最接近但不完整

## Phase 01: 大模型 Context 管理

- [ ] "Lost in the Middle" 效应在超长上下文模型（>1M token, 如 Gemini 1.5 Pro）中是否依然显著？
- [ ] Attention Sink 现象在非 Transformer 架构（Mamba, RWKV, SSM）中是否存在？
- [ ] Context compression 在实际产品中的部署效果：压缩后到底丢了多少对任务有用的信息？缺少标准度量。
- [ ] "高质量 context"的形式化定义——目前主要是经验判断("high-signal tokens")，缺乏统一可计算指标。
- [ ] 多模态 context（图像+文本混合）中，12 个位置/注意力现象是否同样适用？
- [~] Distractor Effect 的具体论文引用——已知多篇 RAG 研究发现此现象，需补充具体 paper ID
- [~] Knowledge Conflict 的机制论文——需补充 Chen et al. 2022 或 Xie et al. 2023 等论文

## Phase 02: 软件 Agent Prompt Assembly

- [ ] Claude Code 的 Compaction 具体保留什么？— 官方说"summarizes earlier parts"但未公开摘要算法细节
- [ ] Cursor 的语义索引：索引如何处理频繁修改的文件？重建索引频率？索引精度数据？
- [ ] ChatGPT Memory 的检索机制：从几百条记忆中如何选择相关条目？语义匹配？关键词？全部注入？
- [ ] LangGraph Memory Store 在上万条记忆规模下的检索延迟和准确性？
- [ ] MCP 在低带宽/离线环境下的适用性——智能硬件可能频繁断网，MCP 的容错机制？
- [~] Cursor 的 context 管理是否有公开技术细节？— 文档有限，社区有逆向分析但不权威

## Phase 03: 分层记忆框架

- [ ] MemGPT/Letta 在生产环境中的稳定性——自主 memory 管理在复杂长时间任务中是否可靠？
- [ ] Generative Agents 的检索可扩展性——当记忆条目超过 10 万条时的延迟和准确性表现？
- [ ] Mem0 的记忆提取准确率——自动提取的记忆中误提取率是多少？有无公开 benchmark？
- [ ] CoALA 框架在 2023-2026 年间是否有完整的工程化开源实现？
- [ ] 图谱式记忆（Zep/Graphiti）在隐私保护约束下如何可用——实体抽取不可避免涉及个人信息
- [~] 从 Episodic Memory 自动归纳 Semantic Memory 的可靠方法——Generative Agents 的 Reflection 是目前最接近方案，但归纳准确性未被系统评估
- [ ] 记忆主动遗忘的用户体验影响——遗忘策略是否会让用户感觉"系统忘了我"？需要用户研究支撑

## Phase 04: 智能硬件输入 (预填)

- [ ] 多模态事件切分的 SOTA 方法在低功耗设备（<1W）上的可行性？
- [ ] 端侧 VLM（如 MobileVLM）的 context 组装延迟能否满足实时要求（<500ms）？
- [ ] 视觉和语音信息冲突时的标准融合策略？
- [ ] 低置信度传感器结果进入 prompt 的收益/风险比？

## Phase 05: 分层记忆架构 (预填)

- [ ] 七层记忆架构中，Perception Working Memory 和 Task Working Memory 的精确分界？
- [ ] 从认知科学"记忆巩固"到工程实现的最佳时间窗口？（睡眠巩固对应设备空闲时处理？）
- [ ] 记忆冲突的最佳解决策略——覆盖/降权/并存/询问用户各有什么场景？

## Phase 06: Context Compiler (预填)

- [ ] Context Ranker 的权重应该是固定启发式还是可学习参数？
- [ ] 主动服务场景中"打扰代价 (InterruptionCost)"如何量化？需要用户研究。
- [ ] LLM prompt / VLM prompt / VLA action context 之间的结构差异是否需要三套不同 compiler？

## Phase 07: 硬件案例 (预填)

- [ ] Meta Ray-Ban AI 眼镜的 context 管理架构是否有公开技术信息？
- [ ] Humane AI Pin 失败因素中，哪些与 context 管理质量直接相关？
- [ ] Friend pendant / Omi 的记忆策略是否有公开文档？
- [ ] MemoryVLA 论文中的 cognition-memory-action 框架在真实机器人上的验证程度？

## Phase 08: 综合架构 (预填)

- [ ] 统一 Context Compiler 是否真的可以跨设备形态（眼镜/耳机/机器人）复用？还是需要设备特化？
- [ ] 隐私保护与 context 质量之间的 trade-off 如何量化——能否建立帕累托曲线？
- [ ] 端云协同记忆同步的一致性问题——离线期间端侧记忆与云端记忆如何合并？
