#!/usr/bin/env python3
"""
从 arXiv 源码包解析论文完整内容：贡献、方法、实验结果、局限性
"""

import re
import sys
import os
import json
import urllib.request
import xml.etree.ElementTree as ET
import tarfile
import io

# ─── arXiv API ────────────────────────────────────────────────────────────────

def extract_arxiv_id(text):
    patterns = [
        r'arxiv\.org/abs/(\d+\.\d+)',
        r'arxiv\.org/pdf/(\d+\.\d+)',
        r'(\d+\.\d{4,})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None

def fetch_arxiv_metadata(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": str(e)}

    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return {"error": "未找到论文条目"}

    def get_text(tag):
        el = entry.find(f"atom:{tag}", ns)
        return el.text.strip() if el is not None and el.text else ""

    authors = [a.find("atom:name", ns).text
               for a in entry.findall("atom:author", ns)
               if a.find("atom:name", ns) is not None]

    return {
        "title": get_text("title").replace("\n", " "),
        "summary": get_text("summary"),
        "authors": authors,
        "published": get_text("published")[:10],
        "arxiv_id": arxiv_id,
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
    }

# ─── LaTeX 清洗 ──────────────────────────────────────────────────────────────

def clean_latex(text):
    """彻底清洗 LaTeX 命令，保留可读文本"""
    if not text:
        return ""
    # 先处理 \% 等带反斜杠的特殊字符（注意：不要用 \\\\ 匹配，因为 \\\\ 在原始 tex 中是转义）
    # \% 在 tex 源码中 = backslash + percent (一个反斜杠)
    # 我们先把 \% 替换成特殊占位符，最后再恢复
    _PCT = '\x00PCT\x00'
    text = text.replace('\\%', _PCT)
    text = text.replace('\\&', '&')
    text = text.replace('\\#', '#')
    text = text.replace('\\$', '$')
    text = text.replace('\\{', '{')
    text = text.replace('\\}', '}')
    # 移除 \\（双反斜杠=换行）
    text = text.replace('\\\\', ' ')
    text = text.replace('\\newline', ' ')
    # 然后清洗剩余的 LaTeX 命令
    text = re.sub(r'\\includegraphics\[[^\]]*\]', '', text)
    text = re.sub(r'\\caption\s*(\[[^\]]*\])?', '', text)
    text = re.sub(r'\\resizebox\[[^\]]*\]', '', text)
    text = re.sub(r'\\scalebox\[[^\]]*\]', '', text)
    text = re.sub(r'\\centering', '', text)
    text = re.sub(r'\\vspace\[[^\]]*\]', '', text)
    text = re.sub(r'\\hspace\[[^\]]*\]', '', text)
    text = re.sub(r'\\toprule|\\midrule|\\bottomrule', '', text)
    text = re.sub(r'\\cline\{[^}]+\}', '', text)
    text = re.sub(r'\\hline', '', text)
    text = re.sub(r'\\multirow\[[^\]]*\]', '', text)
    text = re.sub(r'\\ multicolumn\{[^}]+\}', '', text)
    text = re.sub(r'\\rowcolor\{[^}]+\}', '', text)
    text = re.sub(r'\\color\{[^}]+\}', '', text)
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\url\{[^}]+\}', '', text)
    text = re.sub(r'\\footnote\{[^}]*\}', '', text)
    text = re.sub(r'\\cite[pt]?\{[^}]+\}', '', text)
    text = re.sub(r'\\citep\{[^}]+\}', '', text)
    text = re.sub(r'\\citet\{[^}]+\}', '', text)
    text = re.sub(r'\\it\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\[[^\]]*\]', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # 恢复被保护的字符
    text = text.replace(_PCT, '%')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    return text

# ─── arXiv 源码包解析 ───────────────────────────────────────────────────────

def fetch_arxiv_source(arxiv_id):
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception as e:
        return {"error": f"源码下载失败: {e}"}

    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode='r:gz')
    except Exception as e:
        return {"error": f"tar 解压失败: {e}"}

    tex_files = {}
    for member in tar.getmembers():
        if member.name.endswith('.tex'):
            try:
                f = tar.extractfile(member)
                if f:
                    tex_files[member.name] = f.read().decode('utf-8', errors='replace')
            except Exception:
                pass

    if not tex_files:
        return {"error": "未找到 .tex 文件"}

    all_tex = '\n'.join(tex_files.values())

    return {
        "tex_files": tex_files,
        "all_tex": all_tex,
    }

# ─── 内容提取（无正则避免 Python 3.11 \p 转义问题）────────────────────────────

def extract_contributions(tex_text):
    """从 tex 提取贡献列表"""
    contributions = []

    begin = tex_text.find('\\begin{itemize}')
    end = tex_text.find('\\end{itemize}')
    if begin < 0 or end < 0:
        return contributions

    itemize = tex_text[begin:end]
    parts = re.split(r'\n\\item\s*\n?', itemize)

    for p in parts:
        p = p.strip()
        if not p or len(p) < 30 or p.startswith('\\setlength'):
            continue
        p = clean_latex(p)
        p = re.sub(r'\[[^\]]*\]', '', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if p and len(p) > 20:
            contributions.append(p[:400])

    return contributions

def _find_section(tex_text, keyword):
    """用字符串查找定位章节"""
    idx = tex_text.lower().find(keyword.lower())
    if idx < 0:
        return ""
    # 找到 \section{...keyword...} 的位置，往后找实际内容
    start = tex_text.find('{', idx)
    if start < 0:
        return ""
    # 数括号深度
    depth = 1
    i = start + 1
    while i < len(tex_text) and depth > 0:
        if tex_text[i] == '{':
            depth += 1
        elif tex_text[i] == '}':
            depth -= 1
        i += 1
    # 下一行开始是内容
    content_start = tex_text.find('\n', i)
    if content_start < 0:
        return ""
    # 截取到下一个 \section
    next_section = tex_text.find('\\section', content_start)
    if next_section < 0:
        return tex_text[content_start+1:]
    return tex_text[content_start+1:next_section]

def extract_limitations(tex_text):
    """从 tex 提取 Limitations 段落"""
    # 直接搜索 Limitations 文本
    idx = tex_text.lower().find('limitations')
    if idx < 0:
        return ""

    # 往前找到 \paragraph 命令开始处
    para_start = tex_text.rfind('\\paragraph', 0, idx)
    if para_start < 0:
        para_start = tex_text.rfind('\\paragraph*', 0, idx)
    if para_start < 0:
        para_start = max(0, idx - 50)

    # 往后找到下一个 \subsection 或 \section
    next_sub = tex_text.find('\\subsection', para_start)
    next_sec = tex_text.find('\\section', para_start)
    end = min(next_sub if next_sub > 0 else 999999,
              next_sec if next_sec > 0 else 999999)
    if end == 999999:
        end = len(tex_text)

    section_text = tex_text[para_start:end]
    text = clean_latex(section_text)
    return text[:400].strip()

def extract_key_results(tex_text):
    """提取含百分比的关键实验结果"""
    results = []
    pct_pat = re.compile(r'\d+(?:\.\d+)?\s*%')
    for line in tex_text.split('\n'):
        clean = clean_latex(line).strip()
        if pct_pat.search(clean):
            if clean and len(clean) > 15:
                m = re.search(r'[\d\.,]+\s*%.*', clean)
                if m:
                    snippet = m.group(0)[:150]
                    if snippet not in results:
                        results.append(snippet)
    return results[:6]

# ─── 主流程 ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        text = input("请输入包含链接的文本:\n")
    else:
        text = sys.argv[1]

    arxiv_id = extract_arxiv_id(text)
    if not arxiv_id:
        print("ERROR: 未找到 arXiv ID")
        sys.exit(1)

    print(f"找到 arXiv ID: {arxiv_id}")

    # 1. 获取元数据
    meta = fetch_arxiv_metadata(arxiv_id)
    if "error" in meta:
        print(f"ERROR: {meta['error']}")
        sys.exit(1)

    print(f"标题: {meta['title']}")

    # 2. 获取源码包
    print("正在下载 arXiv 源码包...")
    source = fetch_arxiv_source(arxiv_id)

    if "error" not in source:
        print("正在解析论文内容...")
        all_tex = source.get("all_tex", "")

        # 按文件分离
        intro_tex = ""
        experiment_tex = ""
        for name, content in source.get("tex_files", {}).items():
            name_base = os.path.splitext(os.path.basename(name))[0].lower()
            if 'intro' in name_base:
                intro_tex += content + "\n"
            elif 'experiment' in name_base:
                experiment_tex += content + "\n"

        # 如果没找到分文件，从整体 tex 分割
        if not intro_tex:
            intro_tex = _find_section(all_tex, 'introduction')
        if not experiment_tex:
            experiment_tex = _find_section(all_tex, 'experiment')

        contributions = extract_contributions(intro_tex)
        limitations = extract_limitations(experiment_tex)
        key_results = extract_key_results(experiment_tex)

        meta["contributions"] = contributions
        meta["limitations"] = limitations
        meta["key_results"] = key_results

        print(f"  贡献项: {len(contributions)}")
        print(f"  局限性: {'有' if limitations else '无'}")
        print(f"  关键结果: {len(key_results)}")
    else:
        print(f"  源码获取失败: {source['error']}，使用摘要")

    # 3. 保存
    with open("paper_meta.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已保存 paper_meta.json")

if __name__ == "__main__":
    main()
