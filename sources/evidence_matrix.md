# Evidence Matrix

本文件建立"核心论断 → 支撑证据"的映射关系。用于验证研究中每个重要判断是否有足够的证据支撑。

## 证据强度定义

| 等级 | 定义 | 示例 |
|------|------|------|
| **强** | 有原始论文实验数据或官方文档明确记录 | 论文中的 ablation study 结果 |
| **中** | 有可信来源支撑但非直接实验验证 | 官方博客的工程经验描述 |
| **弱** | 基于类比推理或间接证据 | 从软件系统经验推导硬件场景 |
| **待验证** | 有假设但无证据 | 标记 [NEEDS_CITATION] 的条目 |

---

## Phase 00: 研究范围

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.1 | Context Engineering 是模型能力之外的关键产品差异化因素 | S005, S012 | 中 |
| 6.3 | MemGPT 提出用 OS 内存层级类比管理 LLM context | S006/S019 | 强 |
| 6.4 | Context Engineering ≠ Prompt Engineering（关注信息架构而非措辞） | S005, S012 | 中 |

## Phase 01: 大模型 Context 管理

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.6-现象1 | 模型对 context 中间位置信息注意力低 20%+（Lost in the Middle） | S001 | 强 |
| 6.6-现象2 | 序列开头 token 吸收异常注意力权重（Attention Sink） | S002 | 强 |
| 6.6-现象3 | 对话变长后 system prompt 指令遵守率下降（Instruction Decay） | S004 (Claude system-reminder 机制间接证实) | 中 |
| 6.6-现象4 | 主题相关但任务无关内容比随机噪声伤害更大（Distractor Effect） | 多篇 RAG 研究 (具体论文待补) | 中 |
| 6.6-现象5 | RAG 检索有时反而降低模型性能（Retrieval Paradox） | S003 后续研究 | 中 |
| 6.6-现象6 | Context 信息与参数知识冲突时行为不可预测（Knowledge Conflict） | 多篇研究 (具体论文待补) | 中 |
| 6.6-现象7 | 推理所需事实分散在 context 中时正确率骤降（Multi-hop Fragility） | 推理 benchmark 研究 (待补具体论文) | 中 |
| 6.6-现象8 | 模型学会"A is B"无法推出"B is A"（Reversal Curse） | S007 | 强 |
| 6.6-现象9 | 前面信息强烈框定后续理解（Anchoring Effect） | 认知科学文献+LLM 行为观察 | 中 |
| 6.6-现象10 | prompt 末尾信息享有近因偏差优势（Recency Bias） | S001 (U 形曲线尾部) | 强 |
| 6.6-现象11 | 接近 token limit 时性能断崖式下降（Context Cliff） | S011 (context rot 概念) | 中 |
| 6.6-现象12 | XML/Markdown 标签分隔减少跨区域信息干扰（Role Separation） | S012 (结构化标签推荐) | 中 |
| 6.3 | RAG、Memory、Tool Context 功能边界不同 | S003, S010/S015, S014 | 强 |
| 6.4 | 长上下文模型不能完全替代结构化记忆系统 | S008, S011 (context rot) | 中 |

## Phase 02: 软件 Agent Prompt Assembly

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.1.2 | Claude 使用 Compaction 策略：服务端自动压缩早期对话 | S011 | 强 |
| 6.1.3 | Context Awareness：模型接收 token budget 信息并自主管理 | S011 | 强 |
| 6.1.2 | Thinking Block Stripping：前轮思考不计入后续 context | S011 | 强 |
| 6.1.2 | System Reminder 注入：对话中间重复关键规则 | S004, S013 | 强 |
| 6.1.2 | Sub-agent Delegation：子 agent 返回压缩摘要 | S012 | 强 |
| 6.1.4 | Auto Memory 分四类：user/feedback/project/reference | S013 | 强 |
| 6.5.1 | MCP 定位为 context 接入层而非记忆层 | S014 | 强 |
| 6.6 | Context Engineering 核心原则："最小高信号 token 集" | S012 | 强 |
| 6.6 | System prompt 应用 XML/Markdown 结构化分区 | S012 | 强 |
| 6.6 | Few-shot 示范优于详尽规则文档 | S012 | 中 |
| 6.6 | Just-in-time 检索优于全量预加载 | S012 | 中 |
| 6.4.1 | LangGraph 明确区分 Thread State (working) 和 Memory Store (long-term) | S015, S025 | 强 |

## Phase 03: 分层记忆框架

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.1 | MemGPT 用 fast/slow memory 分层，LLM 自主 push/pop | S019 | 强 |
| 6.2 | Generative Agents 用 Recency+Importance+Relevance 三维度检索 | S020 | 强 |
| 6.2 | Generative Agents 通过 Reflection 将观察归纳为高层洞察 | S020 | 强 |
| 6.3 | Reflexion 将自我反思文本存储为 episodic memory buffer | S021 | 强 |
| 6.3 | Reflexion 在 HumanEval 上达到 91% pass@1 (超过 GPT-4 的 80%) | S021 | 强 |
| 6.4 | CoALA 提出 Working/Episodic/Semantic/Procedural 四层记忆分类 | S022 | 强 |
| 6.4 | CoALA 将 agent 动作分为 Internal (memory ops) 和 External (tool use) | S022 | 强 |
| 6.5 | Mem0 支持自动记忆提取、去重合并、语义检索 | S023 | 中 |
| 6.6 | Zep/Graphiti 用知识图谱结构存储实体和关系 | S024 | 中 |
| 6.10 | Agent 记忆分层对应认知科学 Atkinson-Shiffrin + Tulving 模型 | 教科书知识 + S022, S026 | 强(理论) |
| 6.8 | 现有框架均缺少 Governance Memory（隐私、权限、置信度） | S019-S025 全部无此层 | 强(否定性证据) |
| 6.8 | 现有框架均为纯文本设计，不支持多模态记忆 | S019-S025 架构分析 | 强(否定性证据) |
| 6.8 | 现有框架大多缺乏主动遗忘机制 | S019-S025 比较 | 强(否定性证据) |

## Phase 04: 智能硬件输入 Context 化

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.1 | 硬件 context 输入与软件存在根本范式差异（连续vs离散, 高带宽vs低带宽） | 架构分析 + S027-S030 | 中 |
| 6.2 | 原始传感器带宽（~15 MB/s）远超 LLM context window 容量，需 ~10000:1 压缩比 | 传感器规格计算 | 强 |
| 6.4 | 时序动作分割可将连续视频切分为有意义的动作片段 | S032 (综述) | 强 |
| 6.4 | 端侧 VAD 可在低功耗设备上实现语音活动检测 | S033 + 商业 VAD 芯片 | 强 |
| 6.2 | 第一人称视觉支持活动识别和动作预测 | S031 (Ego4D/Ego-Exo4D) | 强 |
| 6.5 | 置信度加权是多模态冲突的基本解决策略 | 多模态融合文献(通用知识) | 中 |
| 6.6 | 端侧处理负责低延迟感知和隐私过滤，云侧负责深度理解和推理 | 架构分析 + 算力约束 | 中 |
| 6.7 | 隐私过滤必须在端侧最早期执行 | GDPR/隐私法规 + 架构分析 | 强(法规) |
| 6.9 | 完整 context pipeline 需 7 步：信号→隐私→感知→切分→评分→理解→组装 | 本项目架构设计 | 弱(待验证) |

## Phase 05: 分层记忆架构设计

| Section | 论断 | 支撑资料 | 证据强度 |
|---------|------|----------|----------|
| 6.1 | 智能硬件需七层记忆（在 CoALA 四层基础上增加 Raw Buffer、Perception WM、Governance） | S022 + Phase 3/4 分析 | 中(设计推导) |
| 6.3 | Perception WM 和 Task WM 需分离（更新频率差异大） | 认知科学双重WM模型 | 中 |
| 6.4 | 记忆需要双向索引以避免 Reversal Curse | S007 | 强 |
| 6.5 | Episodic 写入需同时满足 importance≥0.6 AND confidence≥0.7 | 设计决策(基于 Phase 4 重要性模型) | 弱(待验证) |
| 6.6 | Episode→Semantic 归纳需 ≥3 次相关 episode + 时间跨度 ≥7 天 | S020 Reflection 机制启发 | 中 |
| 6.6 | Episodic 衰减半衰期 ~30 天合理 | 艾宾浩斯遗忘曲线类比 | 中(类比) |
| 6.7 | 冲突解决优先级：用户显式 > 高置信传感器 > 近期 > 推断 > 旧数据 | 设计原则(非实验验证) | 弱(设计) |
| 6.8 | 用户应拥有对记忆的完整控制权（查看/编辑/删除/冻结/导出） | S035 (GDPR) | 强(法规) |
| 6.10 | 端侧存储 ~100MB + 云端 ~50MB 可满足典型用户需求 | 规模估算(数万 episode) | 中(估算) |
