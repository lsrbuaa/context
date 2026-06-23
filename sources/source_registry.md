# Source Registry

本文件记录研究过程中引用的所有资料。每条资料包含完整元信息，便于追溯和验证。

## 格式说明

| 字段 | 说明 |
|------|------|
| ID | 唯一标识符 (S001, S002...) |
| 类型 | paper / documentation / blog / product / patent / report |
| 标题 | 资料原始标题 |
| 作者/机构 | 第一作者或发布机构 |
| 年份 | 发布年份 |
| URL/DOI | 可访问链接 |
| 核心观点 | 一句话概括该资料的核心贡献 |
| 引用阶段 | 在哪些 Phase 文档中被引用 |
| 可信度 | 高/中/低 |

---

## 学术论文

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| S001 | Lost in the Middle: How Language Models Use Long Contexts | Liu et al. (Stanford) | 2023 | arXiv:2307.03172 | 模型对 context 中间位置信息注意力低 20%+，呈 U 形曲线 | 01, 06 | 高 |
| S002 | Efficient Streaming Language Models with Attention Sinks | Xiao et al. (MIT) | 2023 | arXiv:2309.17453 | 序列开头 token 吸收异常注意力权重（Attention Sink 现象） | 01 | 高 |
| S003 | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al. (Meta) | 2020 | arXiv:2005.11401 | RAG 原始架构：检索+生成的组合范式 | 01 | 高 |
| S006 | MemGPT: Towards LLMs as Operating Systems | Packer et al. (UC Berkeley) | 2023 | arXiv:2310.08560 | 用 OS 虚拟内存类比管理 LLM context，fast/slow memory 分层 | 00, 01, 03 | 高 |
| S007 | The Reversal Curse: LLMs trained on "A is B" fail to learn "B is A" | Berglund et al. | 2023 | arXiv:2309.12288 | Context 中知识具有方向性，模型无法自动推出逆向关系 | 01, 05 | 高 |
| S008 | Can Long-Context Language Models Subsume Retrieval, RAG, SQL, and More? | Xu et al. | 2024 | arXiv:2406.13121 | 长上下文模型不能完全替代结构化检索和 RAG | 01 | 中 |
| S019 | MemGPT: Towards LLMs as Operating Systems | Packer et al. (UC Berkeley) | 2023 | arXiv:2310.08560 | 虚拟上下文管理：LLM 自主 push/pop memory | 03 | 高 |
| S020 | Generative Agents: Interactive Simulacra of Human Behavior | Park et al. (Stanford) | 2023 | arXiv:2304.03442 | 自然语言记忆流 + Recency/Importance/Relevance 三维度检索 + Reflection | 03 | 高 |
| S021 | Reflexion: Language Agents with Verbal Reinforcement Learning | Shinn et al. | 2023 | arXiv:2303.11366 | 语言反思存储为 episodic memory buffer，无需参数更新 | 03 | 高 |
| S022 | CoALA: Cognitive Architectures for Language Agents | Sumers et al. | 2023 | arXiv:2309.02427 | Agent 认知架构统一框架：Working/Episodic/Semantic/Procedural Memory + Structured Action Space | 03, 05 | 高 |
| S026 | A Survey on the Memory Mechanism of Large Language Model based Agents | Zhang et al. | 2024 | arXiv:2404.13501 | Agent 记忆机制综述，涵盖读/写/检索/反思操作分类 | 03 | 中 |
| S027 | LlamaPIE: A Proactive In-Ear Conversational AI Assistant | (耳戴设备研究) | 2024 | arXiv (待确认ID) | 耳戴设备主动对话助手，判断何时介入+低打扰1-3词提示 | 04, 07 | 中 |
| S028 | Memento: An AR-Enabled Memory Assistant | (AR 记忆研究) | 2024 | arXiv (待确认ID) | AR 助手将查询与时空/活动 context 绑定，类似场景主动召回 | 04, 07 | 中 |
| S029 | ProMemAssist: Proactive Memory Assistance with Smart Glasses | (智能眼镜) | 2024 | ACM | 实时建模用户 working memory，传感器驱动主动辅助 | 04, 07 | 中 |
| S030 | Alpha-Service: AI Glasses Proactive Service System | (主动服务) | 2024 | arXiv (待确认ID) | 五模块架构：input/task scheduling/tool/memory/output | 04, 07 | 中 |
| S031 | Ego4D: Around the World in 3,000 Hours of Egocentric Video | Meta AI / Ego-Exo4D | 2022-2024 | arXiv:2110.07058 | 大规模第一人称视觉数据集，支持活动识别、动作预测 | 04 | 高 |
| S032 | Temporal Action Segmentation: A Survey | 多作者 | 2023 | arXiv | 时序动作分割方法综述：SOTA 算法和 benchmark | 04 | 中 |
| S033 | Voice Activity Detection in Noisy Environments | 多作者 | 2023 | 多来源 | 端侧 VAD 算法：低功耗语音检测 | 04 | 中 |
| S034 | Memory Consolidation in Cognitive Architectures | 认知科学综述 | 多年 | 教科书 | 记忆巩固理论：编码→存储→巩固→检索 | 05 | 强(理论) |
| S035 | GDPR Article 17 - Right to Erasure (被遗忘权) | European Union | 2018 | gdpr.eu | 用户有权要求删除个人数据，记忆系统必须支持 | 05 | 强(法规) |
| S036 | Interruption Management in Smart/Ubiquitous Environments | HCI 研究综合 | 多年 | 多来源 | 打扰时机需考虑用户活动状态、认知负荷、社交情境 | 06 | 中 |
| S037 | OpenVLA: An Open-Source Vision-Language-Action Model | Kim et al. (Stanford) | 2024 | arXiv:2406.09246 | 开源 VLA：展示 action context 的输入格式和 tokenization 方式 | 06, 07 | 高 |
| S038 | MemoryVLA: Cognition-Memory-Action Framework | (具身智能研究) | 2025 | OpenReview | 机器人记忆系统：工作记忆+感知记忆库+动作决策结合 | 06, 07 | 中 |
| S039 | Meta Ray-Ban AI Glasses (产品分析) | Meta | 2023-2025 | meta.com | 第一人称视觉AI眼镜：支持拍照+问答，暂无主动服务/持续记忆 | 07 | 中(产品) |
| S040 | Humane AI Pin (产品分析与失败复盘) | Humane | 2024 | 多评测来源 | 无屏AI终端：延迟高、准确率不足、场景理解弱→context管理问题 | 07 | 中(推断) |
| S041 | Friend Pendant / Omi (产品分析) | Friend/Omi | 2024-2025 | friend.com/omi.me | 随身录音+记忆设备：聚焦记忆助手而非全能助手 | 07 | 中(产品) |

## 官方文档

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| S004 | Claude Code Context Window Documentation | Anthropic | 2025 | platform.claude.com/docs | Claude Code 使用 system-reminder 标签在对话中间重新注入关键规则 | 01, 02 | 高 |
| S011 | Context Windows - Claude API Docs | Anthropic | 2025 | platform.claude.com/docs/en/docs/build-with-claude/context-windows | Context window 机制：compaction、context awareness (token budget 追踪)、thinking block stripping | 02 | 高 |
| S013 | Claude Code Documentation (System Prompt & Auto Memory) | Anthropic | 2025 | docs.anthropic.com | CLAUDE.md 多层级规则、auto memory 四类记忆、sub-agent delegation | 02 | 高 |
| S014 | MCP (Model Context Protocol) Introduction | Anthropic/MCP | 2024 | modelcontextprotocol.io/introduction | 连接 AI 应用与外部系统的标准化协议：Tools/Resources/Prompts 三原语 | 02 | 高 |
| S015 | LangGraph Memory Concepts | LangChain | 2024 | langchain-ai.github.io/langgraph/concepts/memory | Thread State (working memory) vs Memory Store (long-term) 双层区分 | 02, 03 | 高 |

## 技术博客与工程实践

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| S005 | Context Engineering for AI Agents (概念定义) | Anthropic | 2025 | anthropic.com/engineering | Context Engineering = 在 LLM 推理时策展最优 token 集 | 00, 01 | 高 |
| S009 | What We Learned from a Year of Building with LLMs | Eugene Yan et al. | 2024 | — | 工程实践中的 context 管理经验总结 | 01 | 中 |
| S012 | Effective Context Engineering for AI Agents | Anthropic | 2025 | anthropic.com/engineering/effective-context-engineering-for-ai-agents | 核心原则："最小高信号 token 集"；五大策略：结构化 prompt、tool 精简、few-shot、JIT 检索、长任务管理 | 02 | 高 |
| S016 | Building Effective Agents | Anthropic | 2024 | anthropic.com/research | Agent 架构模式：workflow vs agent、工具设计、context 管理最佳实践 | 02 | 高 |
| S018 | What We Learned from a Year of Building with LLMs (实践报告) | Eugene Yan et al. | 2024 | — | 多团队 LLM 工程经验：prompt 管理、RAG 策略、token 预算 | 02 | 中 |

## 开源项目文档

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| S023 | Mem0 Documentation | Mem0 | 2024 | docs.mem0.ai | AI 记忆层：自动提取、去重合并、语义检索、多用户隔离 | 03 | 中 |
| S024 | Zep / Graphiti Documentation | Zep AI | 2024 | docs.getzep.com | 知识图谱式长期记忆：实体抽取、关系建模、时序感知、图遍历检索 | 03 | 中 |
| S025 | LangGraph Memory Documentation (详细版) | LangChain | 2024 | langchain-ai.github.io/langgraph | Thread checkpointing + Namespace memory store 实现细节 | 03 | 高 |

## 产品文档

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| S017 | Cursor Documentation | Cursor/Anysphere | 2025 | cursor.com/docs | IDE Agent 的 context 管理：语义索引、.cursorrules、@引用、检索排序 | 02 | 中 |

## 行业报告

| ID | 标题 | 作者/机构 | 年份 | URL/DOI | 核心观点 | 引用阶段 | 可信度 |
|----|------|-----------|------|---------|----------|----------|--------|
| — | （暂无行业报告引用） | — | — | — | — | — | — |
