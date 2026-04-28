# Embodied AI Papers — Wiki Schema

## 领域
具身智能（Embodied AI）论文知识库：机器人操作、视觉-语言-动作模型、模仿学习、强化学习、仿真环境等。

## 目录结构
```
embodied-ai-papers/
├── SCHEMA.md                    # 本文件，规范
├── index.md                     # 论文总索引
├── log.md                       # 操作日志
├── raw/
│   ├── papers/                  # 原始PDF/arXiv内容
│   └── links/                   # Issue解析后的原始链接
├── papers/                      # 结构化论文笔记
│   └── YYYY-MM/                 # 按月份归档
├── concepts/                    # 概念页（方法、任务类型）
└── index/                       # 主题索引
```

## 约定
- 文件名：小写+连字符，例 `rt-2-paper.md`
- 每篇论文一个 Markdown 文件，含 YAML frontmatter
- frontmatter 必须包含：`title`, `created`, `arxiv_id`, `source_issue`, `tags`
- 每篇笔记需包含：一句话总结、核心贡献、技术方案、实验结果、局限性
- 所有操作记录到 `log.md`

## Tag 体系
- `robot-manipulation` | `navigation` | `vrep` | `sim2real`
- `vla` | `rl` | `il` | `imitation-learning` | `reinforcement-learning`
- `vision-language` | `multimodal` | `foundation-model`
- `actuation` | `sensing` | `memory`
- `benchmark` | `dataset` | `simulation`

## GitHub Issue 提交格式
```markdown
## 论文链接
https://arxiv.org/abs/xxxx.xxxxx

## 类型（选填）
- [ ] 机器人操作
- [ ] 视觉导航
- [ ] VLA 模型
- [ ] 模仿/R强化学习
```

## 自动处理流程
1. 用户提交 GitHub Issue（含论文链接）
2. GitHub Actions 自动触发 `process-issue.yml`
3. 脚本抓取 arXiv 摘要 / PDF 文本
4. 生成结构化笔记（papers/YYYY-MM/）
5. 在 issue 下评论完成通知 + 笔记路径
