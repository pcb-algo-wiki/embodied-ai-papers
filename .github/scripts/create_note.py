#!/usr/bin/env python3
"""
根据 paper_meta.json 生成结构化学习笔记（llm-wiki 格式）
"""

import sys
import json
import os
import re
from datetime import datetime

PAPER_DIR = "papers"
os.makedirs(PAPER_DIR, exist_ok=True)


def slugify(title: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', "", title)
    safe = re.sub(r'\s+', "-", safe)
    safe = "".join(c if c.isalnum() or c in "-_" else "" for c in safe)
    return safe[:60].lower() or "untitled"


def truncate(text: str, maxlen: int = 200) -> str:
    text = text.strip()
    if len(text) <= maxlen:
        return text
    return text[:maxlen] + "..."


def generate_note(meta: dict, issue_number: int, issue_url: str) -> str:
    title = meta.get("title", "Unknown")
    authors = meta.get("authors", [])
    published = meta.get("published", "")
    arxiv_id = meta.get("arxiv_id", "")
    summary = meta.get("summary", "")
    pdf_url = meta.get("pdf_url", "")
    contributions = meta.get("contributions", [])
    key_results = meta.get("key_results", [])
    limitations = meta.get("limitations", "")

    today = datetime.now().strftime("%Y-%m-%d")

    author_str = ", ".join(authors[:5])
    if len(authors) > 5:
        author_str += " et al. (+%d)" % (len(authors) - 5)

    # 截取摘要前 2 句
    summary_sentences = summary.split(".")
    summary_short = ". ".join(s.strip() for s in summary_sentences[:2] if s.strip())
    if not summary_short:
        summary_short = "TODO: 填写"

    # 贡献列表
    contrib_lines = []
    for i, c in enumerate(contributions[:5], 1):
        contrib_lines.append("%d. %s" % (i, truncate(c)))
    contrib_md = "\n".join(contrib_lines) if contrib_lines else "*(内容待补充)*"

    # 关键结果
    result_lines = []
    for r in key_results[:6]:
        result_lines.append("- %s" % truncate(r))
    results_md = "\n".join(result_lines) if result_lines else "*(内容待补充)*"

    # 局限性
    if limitations:
        limitations_md = "- %s" % truncate(limitations, 300)
    else:
        limitations_md = "- *(内容待补充)*"

    # 组装 Markdown
    lines = [
        "---",
        "title: \"%s\"" % title,
        "created: %s" % today,
        "arxiv_id: %s" % arxiv_id,
        "source_issue: \"%s\"" % issue_url,
        "source_issue_number: %d" % issue_number,
        "tags: [embodied-ai, vla]",
        "summary: \"%s\"" % truncate(summary, 200),
        "authors: \"%s\"" % author_str,
        "published: \"%s\"" % published,
        "pdf: %s" % pdf_url,
        "---",
        "",
        "# %s" % title,
        "",
        "> **arXiv**: [%s](https://arxiv.org/abs/%s)" % (arxiv_id, arxiv_id),
        "> **PDF**: [Open](%s)" % pdf_url,
        "> **作者**: %s" % author_str,
        "> **发布**: %s" % published,
        "> **提交Issue**: [#%d](%s)" % (issue_number, issue_url),
        "> **学习日期**: %s" % today,
        "",
        "---",
        "",
        "## 📌 一句话总结",
        truncate(summary_short),
        "",
        "## 🎯 核心贡献",
        contrib_md,
        "",
        "## 🔧 关键技术方案",
        "### 任务/场景",
        "TODO: 填写",
        "",
        "### 方法架构",
        "TODO: 填写",
        "",
        "## 📊 实验结果",
        results_md,
        "",
        "## 🔑 重要发现",
        "- *(内容待补充)*",
        "",
        "## ⚠️ 局限性",
        limitations_md,
        "",
        "## 💬 个人笔记",
        "> **疑问**:",
        "> **想法**:",
        "",
        "## 📚 相关工作",
        "- [related paper](link)",
        "",
        "---",
        "",
        "*由 Embodied AI Papers Bot 自动生成 | 具身智能论文知识库*",
        "",
    ]
    return "\n".join(lines)


def main():
    issue_number = 0
    issue_url = ""

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--issue-number" and i + 1 < len(sys.argv):
            issue_number = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--issue-url" and i + 1 < len(sys.argv):
            issue_url = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not os.path.exists("paper_meta.json"):
        print("ERROR: paper_meta.json not found")
        sys.exit(1)

    with open("paper_meta.json") as f:
        meta = json.load(f)

    meta["issue_number"] = issue_number
    meta["issue_url"] = issue_url

    note = generate_note(meta, issue_number, issue_url)

    year_month = datetime.now().strftime("%Y-%m")
    subdir = os.path.join(PAPER_DIR, year_month)
    os.makedirs(subdir, exist_ok=True)

    filename = slugify(meta["title"])
    note_path = os.path.join(subdir, filename + ".md")

    with open(note_path, "w") as f:
        f.write(note)

    print("note_path=%s" % note_path)
    with open("note_path.txt", "w") as f:
        f.write(note_path)

    update_index(meta, note_path)
    update_log(meta, note_path, issue_number)
    print("✅ 笔记已生成: %s" % note_path)


def update_index(meta: dict, note_path: str):
    index_file = "index.md"
    title = truncate(meta.get("title", "Unknown"), 60)
    arxiv_id = meta.get("arxiv_id", "")
    authors = ", ".join(meta.get("authors", [])[:3])

    entry = "- [%s](%s) — `%s` | %s\n" % (title, note_path, arxiv_id, authors)

    if os.path.exists(index_file):
        with open(index_file) as f:
            content = f.read()
    else:
        content = "# Embodied AI Papers Index\n\n"

    marker = "## Papers\n"
    if marker in content:
        content = content.replace(marker, marker + entry)
    else:
        content += "\n## Papers\n" + entry

    with open(index_file, "w") as f:
        f.write(content)


def update_log(meta: dict, note_path: str, issue_number: int):
    log_file = "log.md"
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = truncate(meta.get("title", "Unknown"), 60)
    arxiv_id = meta.get("arxiv_id", "")

    entry = "- %s | [%s](%s) | arXiv:`%s` | Issue:#%d\n" % (
        today, title, note_path, arxiv_id, issue_number
    )

    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
    else:
        content = "# 操作日志\n\n"

    content += entry

    with open(log_file, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
