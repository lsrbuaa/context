# 研究议程：让跨设备用户记忆底座具备工程价值

本文档把“值得研究的问题”拆成可跟踪的工程研究主线。每条主线都包含研究问题、学术锚点、工程难点和可评估指标。

## 1. 记忆抽取：什么值得记住

核心问题：

- 哪些事件能沉淀为长期记忆？
- 用户显式反馈和隐式行为如何合并？
- 单次事件、重复行为和稳定偏好如何区分？

学术锚点：

- Agent memory 研究把记忆视为支持长期复杂交互的关键模块。
- Personalized LLM 研究强调用户画像、历史对话、内容和交互可用于个性化上下文。

工程难点：

- 行为规律不等于偏好。
- 多设备重复上报会造成伪频率。
- 家庭多人场景中，设备动作不一定来自同一用户。
- 高敏信号不能因为“有用”就直接进入模型。

可评估指标：

- Memory Candidate Precision。
- Explicit Preference Capture Rate。
- False Memory Rate。
- Sensitive Candidate Suppression Rate。

## 2. 记忆评分：如何决定权重和生命周期

核心问题：

- 记忆价值如何综合任务价值、频率、新近性和稳定性？
- 多久未出现的偏好应该降权？
- 用户纠错后旧记忆如何处理？

工程难点：

- 新近性和稳定性经常冲突。
- 长期习惯可能被临时偏好覆盖。
- 置信度、重要度和敏感度不能混成一个分数。

建议评分维度：

```text
memory_score =
  task_value
+ frequency
+ recency
+ stability
+ explicitness
+ user_feedback
- sensitivity_risk
- conflict_risk
```

可评估指标：

- Staleness Error。
- Conflict Resolution Accuracy。
- User Correction Rate。
- Deprecated Memory Recall Rate。

## 3. 检索重排：如何取少而准的记忆

核心问题：

- 任务相关性如何定义？
- 语义检索、关键词检索、时间过滤和场景过滤如何组合？
- 权限过滤应该发生在检索前、检索中还是检索后？

工程立场：

> 权限过滤必须早于模型输入；重排不能把未授权记忆重新带回上下文。

工程难点：

- 向量相似不等于任务相关。
- 高重要度记忆不一定适合当前场景。
- 低敏但无关的记忆会稀释模型注意力。
- 高敏但相关的记忆也可能不能使用。

可评估指标：

- Memory Precision。
- Memory Recall。
- Unauthorized Recall Rate。
- Context Token Waste。

## 4. Context Composer：如何把记忆变成模型能用的上下文

核心问题：

- 记忆以什么顺序放入上下文？
- 证据、置信度和约束如何表达？
- 如何在 token 预算内保留最能改变决策的信息？

学术锚点：

- Context Engineering 研究把上下文构造从 prompt 编写提升为系统化的信息载荷优化，包含 retrieval、processing、management 和 memory systems。

工程难点：

- 压缩不能丢失权限约束。
- 低置信信息不能被写成确定事实。
- 冲突记忆不能同时无解释地进入模型。
- 上下文长度不能随历史数据线性增长。

可评估指标：

- Context Efficiency。
- Constraint Retention Rate。
- Token Budget Stability。
- Model Decision Delta。

## 5. 冲突、遗忘与用户控制

核心问题：

- 新旧偏好冲突时如何决策？
- 用户删除一条记忆后，向量、摘要、缓存如何同步处理？
- 用户如何低成本纠正错误记忆？

工程难点：

- 删除不是改状态字段那么简单。
- 家庭多人共享设备会造成身份冲突。
- 用户不希望被频繁追问确认。
- 过度个性化会造成被监控感。

可评估指标：

- Deletion Success Rate。
- Correction Latency。
- Rejected Memory Regeneration Rate。
- User Trust Recovery。

## 6. 隐私保护个性化

核心问题：

- 如何在不暴露原始用户数据的前提下实现个性化？
- 哪些摘要可以在端侧完成？
- RAG 或记忆检索输出是否会泄露外部敏感数据？

学术锚点：

- Privacy-preserving RAG 研究指出，缺少额外隐私保护时，RAG 输出可能泄露外部数据源中的敏感信息。
- 个性化大模型研究把 personalized context 作为输入层个性化的重要路径，但这也放大了用户数据治理的重要性。

工程难点：

- 差分隐私、加密检索和端侧摘要都会影响召回质量。
- 敏感数据最小化和个性化效果存在张力。
- 审计日志本身也可能包含隐私信息。

可评估指标：

- Privacy Leakage。
- Sensitive Context Inclusion Rate。
- Consent Coverage。
- Edge Summary Utility。

## 7. 推荐研究顺序

如果后续进入工程 PoC，推荐顺序不是先做模型，而是：

1. 定义 Event / Memory / Policy / Context Package。
2. 构造 20-50 个 eval case。
3. 做无记忆、最近对话、普通 RAG、结构化记忆四组对照。
4. 再决定是否需要更复杂的记忆抽取和重排模型。

原因很简单：没有 eval，记忆系统会退化成凭感觉调 prompt。

## 8. 参考研究

- [A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501)
- [A Survey of Context Engineering for Large Language Models](https://arxiv.org/abs/2507.13334)
- [A Survey of Personalized Large Language Models: Progress and Future Directions](https://arxiv.org/abs/2502.11528)
- [Privacy-Preserving Retrieval-Augmented Generation with Differential Privacy](https://arxiv.org/abs/2412.04697)
