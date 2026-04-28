#!/usr/bin/env python3
"""
从 Issue 内容中提取论文信息（arXiv ID 或 PDF 链接）
"""

import re
import sys
import os
import json
import urllib.request
import xml.etree.ElementTree as ET

def extract_arxiv_id(text):
    """从文本中提取 arXiv ID"""
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
    """通过 arXiv API 获取论文元数据"""
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


def main():
    if len(sys.argv) < 2:
        # 交互模式
        text = input("请输入包含链接的文本:\n")
    else:
        text = sys.argv[1]
    
    arxiv_id = extract_arxiv_id(text)
    
    if not arxiv_id:
        print("ERROR: 未找到 arXiv ID")
        sys.exit(1)
    
    print(f"找到 arXiv ID: {arxiv_id}")
    
    meta = fetch_arxiv_metadata(arxiv_id)
    
    if "error" in meta:
        print(f"ERROR: {meta['error']}")
        sys.exit(1)
    
    # 输出到 GITHUB_OUTPUT (GHA newer syntax)
    with open(os.environ.get("GITHUB_OUTPUT", ""), "a") as f:
        f.write(f"title={meta['title']}\n")
        f.write(f"arxiv_id={meta['arxiv_id']}\n")
        f.write(f"authors={', '.join(meta['authors'][:5])}\n")
        f.write(f"published={meta['published']}\n")

    # 也输出 JSON 供后续脚本使用
    with open("paper_meta.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 元数据已保存到 paper_meta.json")


if __name__ == "__main__":
    main()
