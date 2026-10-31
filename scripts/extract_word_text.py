# -*- coding: utf-8 -*-
"""从 .docx 提取文字，便于按段落阅读教材，避免直接加载巨大的 Word 文件。

只用 Python 标准库（zipfile + xml.etree），不需要 python-docx。

用法：
  py -3 scripts/extract_word_text.py <docx> --outline
  py -3 scripts/extract_word_text.py <docx> --grep "集合" --context 2
  py -3 scripts/extract_word_text.py <docx> --start 100 --end 140
  py -3 scripts/extract_word_text.py <docx> --max-chars 20000
  py -3 scripts/extract_word_text.py <docx> --stats

说明：
- Word 用于日常阅读；页码、图片、排版、例题位置仍以 PDF 原页为准。
- 文字出现缺字、乱码、公式/表格不清时，回 PDF 对应页核对。
"""
import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {"w": W[1:-1]}


def text_of(el):
    parts = []
    for node in el.iter():
        if node.tag == W + "p" and node is not el:
            # 表格单元格可含多个段落，不能把相邻段落粘成一个词或数字。
            if parts and parts[-1] != "\n":
                parts.append("\n")
        elif node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
    return "".join(parts).strip()


def style_of(p):
    p_pr = p.find("w:pPr", NS)
    if p_pr is not None:
        st = p_pr.find("w:pStyle", NS)
        if st is not None:
            return st.get(W + "val", "") or ""
    return ""


def iter_blocks(docx):
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("w:body", NS)
    if body is None:
        return
    p_index = 0
    for child in body:
        tag = child.tag.split("}")[-1]
        if tag == "p":
            txt = text_of(child)
            if txt:
                p_index += 1
                yield {"kind": "p", "index": p_index, "style": style_of(child), "text": txt}
        elif tag == "tbl":
            rows = []
            for tr in child.findall("w:tr", NS):
                cells = [text_of(tc) for tc in tr.findall("w:tc", NS)]
                rows.append(" | ".join(cells))
            txt = "\n".join(r for r in rows if r.strip())
            if txt:
                yield {"kind": "table", "index": 0, "after_paragraph": p_index,
                       "style": "table", "text": txt}


def is_heading(style):
    s = (style or "").lower()
    return any(k in s for k in ("heading", "标题", "title", "subtitle")) or s in ("1", "2", "3")


HEADING_RE = re.compile(r"^(第[一二三四五六七八九十百0-9]+[章节]|\d+\.\d+\s*[\u4e00-\u9fff]|附录|Chapter\b)")
TOC_RE = re.compile(r"(?:\t|\s{2,})\d{1,3}\s*$")


def looks_like_heading(text):
    t = text.strip()
    return len(t) <= 100 and bool(HEADING_RE.match(t))


def heading_key(text):
    return re.sub(r"\s+", "", text.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--outline", action="store_true", help="只输出标题/非正文样式段落")
    ap.add_argument("--grep", help="只输出包含该关键词的段落（不区分大小写）")
    ap.add_argument("--context", type=int, default=1, help="grep 命中前后各输出几段（默认 1）")
    ap.add_argument("--start", type=int, help="起始段落序号（1 起，含段后表格）")
    ap.add_argument("--end", type=int, help="结束段落序号（含）")
    ap.add_argument("--max-chars", type=int, default=30000, help="输出字符上限（默认 30000）")
    ap.add_argument("--stats", action="store_true", help="只输出统计信息")
    a = ap.parse_args()
    if a.start is not None and a.start < 1:
        ap.error("--start 必须大于等于 1")
    if a.end is not None and a.end < 1:
        ap.error("--end 必须大于等于 1")
    if a.start is not None and a.end is not None and a.start > a.end:
        ap.error("--end 不能小于 --start")

    blocks = list(iter_blocks(a.docx))
    paras = [b for b in blocks if b["kind"] == "p"]
    tables = [b for b in blocks if b["kind"] == "table"]

    if a.stats:
        chars = sum(len(b["text"]) for b in blocks)
        print("paragraphs=%d tables=%d chars=%d" % (len(paras), len(tables), chars))
        print("first paragraph: %s" % (paras[0]["text"][:120] if paras else ""))
        print("last paragraph: %s" % (paras[-1]["text"][:120] if paras else ""))
        return

    if a.outline:
        selected = [b for b in paras if is_heading(b["style"]) or looks_like_heading(b["text"])]
        if not selected:
            selected = [b for b in paras if len(b["text"]) <= 40][:80]
        seen = set()
        for b in selected:
            if TOC_RE.search(b["text"]):
                continue
            key = heading_key(b["text"])
            if not key or key in seen:
                continue
            seen.add(key)
            print("[P%d] (%s) %s" % (b["index"], b["style"] or "-", b["text"]))
        return

    if a.grep:
        needle = a.grep.lower()
        hits = [i for i, b in enumerate(blocks) if needle in b["text"].lower()]
        if not hits:
            print("未找到：%s" % a.grep)
            return
        keep = set()
        for i in hits:
            for j in range(max(0, i - a.context), min(len(blocks), i + a.context + 1)):
                keep.add(j)
        selected = [blocks[i] for i in sorted(keep)]
    else:
        selected = blocks
        if a.start is not None or a.end is not None:
            lo = a.start if a.start is not None else 1
            hi = a.end if a.end is not None else max(1, len(paras))
            # 表格跟随其前一段；文首表格归入第 1 段的阅读范围。
            selected = [b for b in blocks if lo <= (
                b["index"] if b["kind"] == "p" else max(1, b["after_paragraph"])
            ) <= hi]

    out = []
    total = 0
    truncated = False
    for b in selected:
        if b["kind"] == "p":
            line = "[P%d] %s" % (b["index"], b["text"])
        else:
            line = "[表] %s" % b["text"]
        total += len(line)
        if total > a.max_chars:
            truncated = True
            break
        out.append(line)
    print("\n\n".join(out))
    if truncated:
        print("\n...（已截断，超过 --max-chars=%d；用 --start/--end 或 --grep 缩小范围）" % a.max_chars)


if __name__ == "__main__":
    main()
