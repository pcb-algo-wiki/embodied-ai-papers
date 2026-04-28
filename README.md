# Embodied AI Papers

具身智能论文知识库 — 自动解析 + 结构化笔记

## 🎯 是什么

一个 GitHub 驱动的具身智能论文学习系统：

1. **提交论文** → 在 Issues 里发一个包含 arXiv 链接的 issue
2. **自动解析** → GitHub Actions 抓取论文信息，生成结构化笔记
3. **通知回填** → Bot 在你的 issue 下评论，告诉你笔记路径

## 📋 提交流程

在 [Issues](https://github.com/pcb-algo-wiki/embodied-ai-papers/issues) 里新建，粘贴论文链接即可：

```markdown
## 论文链接
https://arxiv.org/abs/2303.XXXXX

## 备注（选填）
关注其中的 RT-2 扩散模型部分
```

Bot 会自动识别 arXiv 链接并处理。

## 📁 仓库结构

```
embodied-ai-papers/
├── SCHEMA.md              # 规范定义
├── index.md               # 论文总索引
├── log.md                 # 操作日志
├── papers/                # 结构化论文笔记（按月归档）
│   └── 2026-04/
│       └── rt-2-paper.md
└── .github/workflows/     # 自动处理流程
```

## 🔧 工作原理

- **触发**: Issue 包含 `arxiv.org` 链接
- **Actions**: 抓取 arXiv API 元数据 → 生成笔记模板 → 更新 index.md
- **通知**: 评论回填笔记路径

## 🏗 架构

基于 llm-wiki 模式构建，参考 [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
