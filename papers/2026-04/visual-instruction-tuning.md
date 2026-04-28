---
title: "Visual Instruction Tuning"
created: 2026-04-28
arxiv_id: 2304.08485
source_issue: ""
source_issue_number: 0
tags: [embodied-ai, vla]
summary: "Instruction tuning large language models (LLMs) using machine-generated instruction-following data has improved zero-shot capabilities on new tasks, but the idea is less explored in the multimodal fie..."
authors: "Haotian Liu, Chunyuan Li, Qingyang Wu, Yong Jae Lee"
published: "2023-04-17"
pdf: https://arxiv.org/pdf/2304.08485.pdf
---

# Visual Instruction Tuning

> **arXiv**: [2304.08485](https://arxiv.org/abs/2304.08485)
> **PDF**: [Open](https://arxiv.org/pdf/2304.08485.pdf)
> **作者**: Haotian Liu, Chunyuan Li, Qingyang Wu, Yong Jae Lee
> **发布**: 2023-04-17
> **提交Issue**: [#0]()
> **学习日期**: 2026-04-28

---

## 📌 一句话总结
Instruction tuning large language models (LLMs) using machine-generated instruction-following data has improved zero-shot capabilities on new tasks, but the idea is less explored in the multimodal fie...

## 🎯 核心贡献
1. { Multimodal instruction-following data}. One key challenge is the lack of vision-language instruction-following data. We present a data reformation perspective and pipeline to convert image-text pair...
2. { Large multimodal models}. We develop a large multimodal model (LMM), by connecting the open-set visual encoder of CLIP~ with the language decoder Vicuna~, and fine-tuning end-to-end on our generated...
3. { Multimodal instruction-following benchmark}. We present LLaVA-Bench with two challenging benchmarks, with a diverse selection of paired images, instructions and detailed annotations.
4. { Open-source}. We release the following assets to the public: the generated multimodal instruction data, the codebase, the model checkpoints, and a visual chat demo.

## 🔧 关键技术方案
### 任务/场景
TODO: 填写

### 方法架构
TODO: 填写

## 📊 实验结果
- 5% Detail + 10% Complex & 81.0 { (-2.1)} & 68.4 { (-7.1)} & 91.5 { (-5.0)} & 80.5 { (-4.4)}
- 85.1%.
- 29%) and OpenFlamingo (+48%).
- 81.7% performance on complex reasoning questions, with an overall score of 67.3%.
- 90.92% accuracy, which is quite close to the SoTA 91.68%.
- 82.69% accuracy, which is a 7.52% absolute gain compared with 75.17% from GPT-3.5. For a substantial number of questions, we note that GPT-4 fails sim

## 🔑 重要发现
- *(内容待补充)*

## ⚠️ 局限性
- This is designed to be challenging and to reveal a model's weaknesses. We provide two examples with associated captions and questions in Table~.
% It takes around 10 minutes for the human annotator to finish the caption of this image, with the access to the Internet.
For the ramen example (left), to...

## 💬 个人笔记
> **疑问**:
> **想法**:

## 📚 相关工作
- [related paper](link)

---

*由 Embodied AI Papers Bot 自动生成 | 具身智能论文知识库*
