# 05-Model Router (additional)

【技术博客】

## 摘要

本文用于展示 Model Router 的设计思路：根据任务类型、成本、延迟、质量要求、上下文长度和工具能力，在多个模型之间动态选择最合适的执行路径。

## 背景

实际 AI 应用通常不会只依赖单一模型。不同模型在推理能力、速度、成本、多模态能力、工具调用、长上下文和稳定性方面各有差异。

Model Router 的目标是在满足质量要求的前提下，降低成本、缩短延迟，并提升系统整体可靠性。

## 路由信号

- Task Type：问答、代码、摘要、检索、分类、规划、多模态理解。
- Quality Requirement：是否需要高推理能力、严格格式、事实核查。
- Cost Budget：单次请求预算、用户等级、业务优先级。
- Latency Target：实时交互、后台任务、批处理。
- Context Size：输入长度、是否需要长上下文模型。
- Tool Requirement：是否需要函数调用、浏览、代码执行或文件处理。
- Safety Level：是否涉及医疗、法律、金融等高风险领域。

## 路由策略

1. Rule-based Routing：通过规则直接匹配任务和模型。
2. Classifier Routing：先用轻量模型判断任务类别，再选择目标模型。
3. Cascade Routing：先用低成本模型处理，失败或不确定时升级。
4. Ensemble Routing：多个模型并行生成，再由评估器选择或融合。
5. Feedback Routing：根据历史效果、用户反馈和监控数据更新策略。

## Microsoft Foundry 的 Model Router 思路

Microsoft Foundry 的 Model Router 可以作为云厂商级路由产品的代表案例。它不是一个通用 LLM，而是一个轻量级机器学习模型，用于实时分析请求，并预测当前 prompt 最适合交给哪个底层模型处理。

它的路由过程可以概括为三步：

1. Understand the prompt：分析 system message、user message、tool definitions 和 conversation history，判断任务类型与难度。
2. Select the best model：结合模型池和路由模式选择最合适的模型。
3. Route and respond：把请求转发给目标模型，并在响应的 `model` 字段中暴露实际处理请求的模型。

Foundry 提供三类典型模式：

- Balanced：默认模式，在质量和成本之间折中。
- Cost：更积极地选择低成本模型，复杂任务再升级。
- Quality：优先选择高质量模型，即使成本更高。

对产品设计的启发是：路由器本身也需要可观测性。系统应记录每次请求的最终模型、路由模式、成本、延迟和失败率，否则很难判断路由策略是否真的降低了成本。

## 用 XML 标记提升路由与长文本召回效率

结构化 XML 标记不是路由器的唯一实现方式，但它能显著改善 prompt 可解析性，尤其适合路由判断和长文本召回。

在路由场景中，可以把输入拆成稳定字段：

```xml
<request>
  <task_type>code_review</task_type>
  <priority>quality</priority>
  <latency_target>interactive</latency_target>
  <context_budget>large</context_budget>
  <user_query>Review this pull request for correctness.</user_query>
</request>
```

这样做有三个好处：

- Router 可以直接读取任务类型、质量优先级和上下文预算，减少自然语言判断成本。
- 长文本召回可以把文档内容、来源、时间、权限和相关性分数分开，便于模型定位依据。
- 下游模型更容易区分指令、上下文、样例和用户输入，降低误解概率。

长上下文任务建议把大段文档放在前面，把最终问题和输出要求放在后面，并使用 `<document>`、`<source>`、`<document_content>` 等标签描述来源与正文。对多文档召回，可以让模型先提取相关证据，再生成答案，这能减少在长上下文中的噪声干扰。

## 工程案例：Weave Router

Weave Router 是一个面向 agentic systems 的模型路由代理。它以本地或托管 endpoint 的形式接入 Claude Code、Codex、Cursor 或自有应用，并在每次请求时选择合适模型。

其工程特点包括：

- Drop-in proxy：对上层应用暴露统一 endpoint，降低迁移成本。
- Multi-provider：支持 Anthropic、OpenAI、Gemini，以及通过 OpenRouter 接入的 OSS 模型。
- Per-request routing：每轮请求都可以独立选择模型。
- Local key control：BYOK 模式下，上游 provider key 保留在用户环境。
- Observability：通过 OTLP traces 和 dashboard 观察路由行为。

这个案例说明，Model Router 不只是算法问题，还涉及协议兼容、密钥管理、可观测性、安装体验和工具链集成。

## 论文案例：Avengers-Pro

2025 年论文 Beyond GPT-5: Making LLMs Cheaper and Better via Performance-Efficiency Optimized Routing 提出了 Avengers-Pro。它将查询 embedding 后聚类，再根据每个模型在不同 cluster 上的性能和成本计算 performance-efficiency score，推理时把新请求映射到相近 cluster，并选择得分最高的模型。

这个方法的关键点是：

- 不依赖手写 prompt 判断模型选择。
- 不需要额外训练神经网络路由器。
- 通过 trade-off parameter 调节性能与成本偏好。
- 对新增模型，只需要在数据集上增量评估其 cluster 表现。

论文报告称，在 6 个 benchmark 和 8 个模型上，Avengers-Pro 可以在不同成本约束下形成更优的 Pareto frontier：既可以在接近最强单模型准确率时降低成本，也可以在相近成本下获得更高准确率。

## 系统组成

- Request Analyzer：解析任务意图和约束。
- Policy Engine：执行路由规则和预算策略。
- Model Registry：维护模型能力、价格、延迟和可用性。
- Evaluator：评估输出质量、格式和安全性。
- Observability：记录路由决策、成本、失败率和用户反馈。

## 展示要点

- Model Router 是 AI 应用的基础设施层。
- 路由目标不是永远选择最强模型，而是选择最合适模型。
- 好的路由系统需要监控闭环，否则规则会快速过期。

## 后续补充

- 路由决策表。
- 质量评估指标。
- 成本与延迟优化案例。

## 参考资料

- Microsoft Foundry: [How model router works in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router-how-it-works)
- Anthropic Claude Docs: [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Weave Router: [workweave/router](https://github.com/workweave/router)
- Zhang et al., 2025: [Beyond GPT-5: Making LLMs Cheaper and Better via Performance-Efficiency Optimized Routing](https://arxiv.org/abs/2508.12631)
