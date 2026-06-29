# 01-Prompt Engineering -> Context Engineering

【技术博客】

## 摘要

本文用于展示从 Prompt Engineering 到 Context Engineering 的范式迁移：从“写好一句提示词”扩展为“设计、组织、检索、压缩和验证模型所需上下文”的系统工程。

## 背景

Prompt Engineering 关注单次交互中的指令表达、角色设定和输出约束。随着模型进入复杂任务、长链路应用和多工具协作场景，仅靠提示词已经不足以稳定获得高质量结果。

Context Engineering 将关注点前移到上下文系统本身，包括任务目标、历史状态、用户偏好、业务数据、工具反馈、外部知识和运行约束的组合方式。

## 核心观点

- Prompt 是入口，Context 是工作台。
- 上下文质量决定模型可推理的边界。
- 好的上下文系统需要可检索、可压缩、可审计、可更新。
- 对复杂应用而言，Context Engineering 比单点提示词技巧更接近生产工程问题。

## 技术框架

1. Context Sources：用户输入、文档库、数据库、日志、代码仓库、工具结果。
2. Context Selection：根据任务目标选择相关片段，减少噪声。
3. Context Compression：对长历史和大文档进行摘要、分块和优先级排序。
4. Context Assembly：将任务、约束、证据和可执行指令组织为模型输入。
5. Context Verification：检查引用、事实一致性、工具结果和输出可复现性。

## 展示要点

- 对比“单条 prompt”与“上下文管线”的差异。
- 展示一个从用户请求到上下文组装的流程图。
- 强调上下文不是越多越好，而是越相关、越结构化越好。

## 后续补充

- 典型上下文模板。
- RAG 与 Context Engineering 的关系。
- 长上下文模型下的上下文治理策略。
