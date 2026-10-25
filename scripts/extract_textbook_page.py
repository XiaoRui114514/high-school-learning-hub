# -*- coding: utf-8 -*-
"""按页码读取教材：提取文字或渲染页面图片，替代整本扫描（Token 优化）。

用法：
  py -3 scripts/extract_textbook_page.py <PDF路径> --pages 9-12
  py -3 scripts/extract_textbook_page.py <PDF路径> --教材页 2 --offset 7
  py -3 scripts/extract_textbook_page.py <PDF路径> --教材页 2 --offset 7 --image --out 输出目录
"""
import argparse, os, re, sys

# 统一输出编码：管道 / 重定向读取时避免中文乱码（真实控制台输出不受影响）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_pages(spec):
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if m:
            pages.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            pages.append(int(part))
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages", help="PDF 页码，如 9-12 或 9,11,13")
    ap.add_argument("--教材页", dest="book_page", type=int, help="教材页码")
    ap.add_argument("--offset", type=int, default=0, help="PDF页码 = 教材页码 + offset")
    ap.add_argument("--image", action="store_true", help="渲染为 PNG 图片")
    ap.add_argument("--out", default="教材页输出")
    ap.add_argument("--scale", type=float, default=2.0)
    a = ap.parse_args()

    if not os.path.isfile(a.pdf):
        sys.exit("找不到文件：%s" % a.pdf)
    pages = parse_pages(a.pages) if a.pages else []
    if a.book_page:
        pages.append(a.book_page + a.offset)
    if not pages:
        sys.exit("请用 --pages 或 --教材页 指定页码")

    if a.image:
        try:
            import pypdfium2 as pdfium
        except ImportError:
            sys.exit("缺少 pypdfium2：py -3 -m pip install pypdfium2 pillow")
        os.makedirs(a.out, exist_ok=True)
        doc = pdfium.PdfDocument(a.pdf)
        for p in pages:
            if p < 1 or p > len(doc):
                print("跳过越界页码：%d" % p)
                continue
            img = doc[p - 1].render(scale=a.scale).to_pil()
            dst = os.path.join(a.out, "PDF页%03d.png" % p)
            img.save(dst)
            print("已输出：%s" % dst)
        return

    try:
        import pypdf
    except ImportError:
        sys.exit("缺少 pypdf：py -3 -m pip install pypdf")
    reader = pypdf.PdfReader(a.pdf)
    for p in pages:
        if p < 1 or p > len(reader.pages):
            print("跳过越界页码：%d" % p)
            continue
        text = reader.pages[p - 1].extract_text() or ""
        print("\n===== PDF 第 %d 页 =====\n%s" % (p, text.strip()))


if __name__ == "__main__":
    main()
