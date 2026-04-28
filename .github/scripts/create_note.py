#!/usr/bin/env python3
"""
根据论文元数据生成结构化学习笔记
"""

import sys
import json
import os
import re
from datetime import datetime

PAPER_DIR = "papers"
os.makedirs(PAPER_DIR, exist_ok=True)


def slugify(title: str) -> str:
    """生成安全的文件名"""
    safe = re.sub(r'[<>:"/\\|?*]', "", title)
    safe = re.sub(r'\s+', "-", safe)
    safe = "".join(c if c.isalnum() or c in "-_" else "" for c in safe)
    return safe[:60].lower() or "untitled"


def generate_note(meta: dict, issue_number: int, issue_url: str) -> str:
    """生成结构化笔记 Markdown"""
    
    title = meta.get("title", "Unknown")
    authors = meta.get("authors", [])
    published = meta.get("published", "")
    arxiv_id = meta.get("arxiv_id", "")
    summary = meta.get("summary", "")
    pdf_url = meta.get("pdf_url", "")
    
    today = datetime.now().strftime("%Y-%m-%d")
    year_month = datetime.now().strftime("%Y-%m")
    
    # 计算作者字符串
    author_str = ", ".join(authors[:5])
    if len(authors) > 5:
        author_str += f" et al. (+{len(authors)-5})"
    
    note = f"""---
title: "{title}"
created: {today}
arxiv_id: {arxiv_id}
source_issue: "{issue_url}"
source_issue_number: {issue_number}
tags: [embodied-ai]
summary: ""
authors: "{author_str}"
published: "{published}"
pdf: {pdf_url}
---

# {title}

> **arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})
> **PDF**: [Open]({pdf_url})
> **作者**: {author_str}
> **发布**: {published}
> **提交Issue**: [#${issue_number}]({issue_url})
> **学习日期**: {today}

---

## 📌 一句话总结
TODO: 填写


## 🎯 核心贡献
1. 
2. 
3. 


## 🔧 关键技术方案
### 任务/场景


### 方法架构


## 📊 实验结果
| 任务 | 指标 | 结果 |
|------|------|------|
|      |      |      |


## 🔑 重要发现
- 


## ⚠️ 局限性
- 


## 💬 个人笔记
> **疑问**: 
> **想法**: 


## 📚 相关工作
- [related paper](link)

---

*由 Embodied AI Papers Bot 自动生成 | 具身智能论文知识库*
"""
    return note


def main():
    # 解析参数
    args = sys.argv[1:]
    
    title = ""
    arxiv_id = ""
    issue_number = 0
    issue_url = ""
    
    i = 0
    while i < len(args):
        if args[i] == "--title" and i+1 < len(args):
            title = args[i+1]; i += 2
        elif args[i] == "--arxiv-id" and i+1 < len(args):
            arxiv_id = args[i+1]; i += 2
        elif args[i] == "--issue-number" and i+1 < len(args):
            issue_number = int(args[i+1]); i += 2
        elif args[i] == "--issue-url" and i+1 < len(args):
            issue_url = args[i+1]; i += 2
        else:
            i += 1
    
    # 读取 meta 文件
    if os.path.exists("paper_meta.json"):
        with open("paper_meta.json") as f:
            meta = json.load(f)
    else:
        meta = {
            "title": title or "Unknown",
            "arxiv_id": arxiv_id,
            "authors": [],
            "published": "",
            "summary": "",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else "",
        }
    
    if issue_number:
        meta["issue_number"] = issue_number
    if issue_url:
        meta["issue_url"] = issue_url
    
    # 生成笔记
    note = generate_note(meta, issue_number, issue_url)
    
    # 保存
    year_month = datetime.now().strftime("%Y-%m")
    subdir = f"{PAPER_DIR}/{year_month}"
    os.makedirs(subdir, exist_ok=True)
    
    filename = slugify(meta["title"])
    note_path = f"{subdir}/{filename}.md"
    
    with open(note_path, "w") as f:
        f.write(note)
    
    print(f"✅ 笔记已生成: {note_path}")
    with open("note_path.txt", "w") as f:
        f.write(note_path)
    
    # 更新 index
    update_index(meta, note_path)


def update_index(meta: dict, note_path: str):
    """追加到 index.md"""
    index_file = "index.md"
    title = meta.get("title", "Unknown")[:60]
    arxiv_id = meta.get("arxiv_id", "")
    authors = ", ".join(meta.get("authors", [])[:3])
    
    entry = f"- [{title}]({note_path}) — `{arxiv_id}` | {authors}\n"
    
    if os.path.exists(index_file):
        with open(index_file) as f:
            content = f.read()
    else:
        content = "# Embodied AI Papers Index\n\n"
    
    # 在 `## Papers` 下追加
    marker = "## Papers\n"
    if marker in content:
        content = content.replace(marker, marker + entry)
    else:
        content += "\n## Papers\n" + entry
    
    with open(index_file, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
