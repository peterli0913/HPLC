#!/usr/bin/env python3
"""English edition of UK_PDF_Portfolio_Briefing_2026-10-12-v3.1.

Text is replaced in place so figures and layout stay aligned with the Chinese
deck. The HTML is generated from the translated slides.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

from lxml import etree
from openpyxl import load_workbook
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.util import Pt

ROOT = Path("/workspace")
SRC = ROOT / "UK_PDF_Portfolio_Briefing_2026-10-12-v3.1.pptx"
OUT_PPT = ROOT / "UK_PDF_Portfolio_Briefing_2026-10-12-v3.1-EN.pptx"
OUT_HTML = ROOT / "UK_PDF_Portfolio_Briefing_2026-10-12-v3.1-EN.html"
MAP_PATH = Path(__file__).with_name("v31_en.json")

CJK = re.compile(r"[\u4e00-\u9fff]")
C_NS = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
T = json.loads(MAP_PATH.read_text(encoding="utf-8"))


def set_latin(run):
    run.font.name = "Calibri"
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", "Calibri")


def set_para(para, text):
    runs = list(para.runs)
    if not runs:
        return
    runs[0].text = text
    set_latin(runs[0])
    for run in runs[1:]:
        run.text = ""


def translate_tf(tf, missing):
    for para in tf.paragraphs:
        text = para.text
        if not text or not CJK.search(text):
            if text.strip():
                for run in para.runs:
                    set_latin(run)
            continue
        if text not in T:
            missing.add(text)
            continue
        set_para(para, T[text])


def translate_chart(chart, missing):
    for node in chart._element.iter(C_NS + "v"):
        if node.text and CJK.search(node.text):
            if node.text not in T:
                missing.add(node.text)
            else:
                node.text = T[node.text]
    for rel in chart.part.rels.values():
        if not str(rel.target_ref).endswith(".xlsx"):
            continue
        wb = load_workbook(io.BytesIO(rel.target_part.blob))
        ws = wb.active
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and CJK.search(cell.value):
                    if cell.value not in T:
                        missing.add(cell.value)
                    else:
                        cell.value = T[cell.value]
        buf = io.BytesIO()
        wb.save(buf)
        rel.target_part._blob = buf.getvalue()


def walk_shapes(shapes, missing):
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            walk_shapes(shape.shapes, missing)
            continue
        if shape.has_text_frame:
            translate_tf(shape.text_frame, missing)
            if shape.width.inches < 2.5 and shape.left.inches < 1.0:
                for para in shape.text_frame.paragraphs:
                    if para.runs and len(para.text) > 22:
                        para.runs[0].font.size = Pt(8)
        if getattr(shape, "has_table", False) and shape.has_table:
            long = any(len(c.text) > 70 for row in shape.table.rows for c in row.cells)
            for row in shape.table.rows:
                for cell in row.cells:
                    translate_tf(cell.text_frame, missing)
                    if not long:
                        continue
                    for para in cell.text_frame.paragraphs:
                        for run in para.runs:
                            if run.text:
                                run.font.size = Pt(9)
        if getattr(shape, "has_chart", False) and shape.has_chart:
            translate_chart(shape.chart, missing)


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_num(value):
    if isinstance(value, bool) or value is None or value == "":
        return ""
    if isinstance(value, (int, float)) and abs(value) >= 100:
        return f"?{int(round(value)):,}"
    return str(value)


def shape_bits(slide):
    bits = []
    for shape in slide.shapes:
        if shape.top.inches > 7.05:
            continue
        if shape.has_text_frame:
            lines = [p.text.strip() for p in shape.text_frame.paragraphs if p.text.strip()]
            if not lines:
                continue
            if len(lines) == 1 and re.fullmatch(r"\d+ / \d+", lines[0]):
                continue
            bits.append(("text", shape.top.inches, shape.left.inches, lines, shape.width.inches))
        elif getattr(shape, "has_table", False) and shape.has_table:
            rows = []
            for row in shape.table.rows:
                rows.append([c.text.strip().replace("\n", " ") for c in row.cells])
            bits.append(("table", shape.top.inches, shape.left.inches, rows, shape.width.inches))
        elif getattr(shape, "has_chart", False) and shape.has_chart:
            chart = shape.chart
            try:
                cats = [str(c) for c in chart.plots[0].categories]
            except Exception:
                cats = []
            series = [(str(ser.name), list(ser.values)) for ser in chart.series]
            bits.append(("chart", shape.top.inches, shape.left.inches, (cats, series), shape.width.inches))
    bits.sort(key=lambda b: (round(b[1], 1), b[2]))
    return bits


def slide_html(index, slide, total):
    bits = shape_bits(slide)
    title = ""
    subtitle = ""
    used = set()
    for n, bit in enumerate(bits):
        kind, top, _left, payload, width = bit
        if kind != "text" or top > 2.6 or width < 5:
            continue
        title = payload[0]
        if len(payload) > 1:
            subtitle = " ".join(payload[1:])
        used.add(n)
        break
    text_bits = [(n, b) for n, b in enumerate(bits) if b[0] == "text" and n not in used]
    clustered = {}
    for n, bit in text_bits:
        clustered.setdefault(round(bit[1] * 8) / 8, []).append((n, bit))
    gantt_rows = []
    gantt_ids = set()
    for key in sorted(clustered):
        group = sorted(clustered[key], key=lambda x: x[1][2])
        if len(group) >= 2 and group[0][1][2] < 1.2 and group[-1][1][2] > 8:
            gantt_rows.append((" ".join(group[0][1][3]), " ".join(group[-1][1][3])))
            gantt_ids.update(n for n, _ in group)
    body = []
    if gantt_rows:
        rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in gantt_rows)
        body.append(f'<table class="gantt"><tbody>{rows}</tbody></table>')
    for n, bit in enumerate(bits):
        if n in used or n in gantt_ids:
            continue
        kind, _top, _left, payload, _width = bit
        if kind == "text":
            paras = []
            for line in payload:
                if line.startswith("?"):
                    paras.append(f"<li>{esc(line.lstrip('?').strip())}</li>")
                else:
                    paras.append(f"<p>{esc(line)}</p>")
            if paras and all(x.startswith("<li>") for x in paras):
                body.append("<ul>" + "".join(paras) + "</ul>")
            else:
                body.append("".join(paras))
        elif kind == "table":
            html_rows = []
            for r, row in enumerate(payload):
                tag = "th" if r == 0 else "td"
                html_rows.append("<tr>" + "".join(f"<{tag}>{esc(c)}</{tag}>" for c in row) + "</tr>")
            body.append("<table>" + "".join(html_rows) + "</table>")
        elif kind == "chart":
            cats, series = payload
            if len(cats) <= 1:
                rows = "".join(
                    f"<tr><td>{esc(name)}</td><td>{esc(fmt_num(vals[0] if vals else ''))}</td></tr>"
                    for name, vals in series
                )
                cap = f"<p class='sub'>{esc(cats[0])}</p>" if cats else ""
                body.append(cap + "<table>" + rows + "</table>")
            else:
                head = "".join(f"<th>{esc(name)}</th>" for name, _ in series)
                rows = []
                for i_cat, cat in enumerate(cats):
                    cell = ""
                    for _name, vals in series:
                        value = vals[i_cat] if i_cat < len(vals) else ""
                        cell += f"<td>{esc(fmt_num(value))}</td>"
                    rows.append(f"<tr><td>{esc(cat)}</td>{cell}</tr>")
                body.append("<table><tr><th></th>" + head + "</tr>" + "".join(rows) + "</table>")
    sub = f'<p class="sub">{esc(subtitle)}</p>' if subtitle else ""
    return (
        f'<section class="slide" id="s{index}">'
        f'<p class="page">{index} / {total}</p>'
        f"<h2>{esc(title or 'Briefing')}</h2>{sub}"
        + "".join(f'<div class="block">{b}</div>' for b in body)
        + "</section>"
    )


HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Asymchem UK - Sandwich Pilot Plant - Capital Projects Briefing (12 October 2026)</title>
<style>
:root { --navy:#0f2b46; --text:#2c3e50; --muted:#5a6a7a; --line:#e2e8ee; --bg:#f4f6f8; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:16px/1.5 Calibri, "Segoe UI", sans-serif; }
header { background:var(--navy); color:#fff; padding:2.2rem 8vw 1.6rem; }
header h1 { margin:0 0 .3rem; font-size:1.8rem; font-weight:650; }
header p { margin:.2rem 0; color:#d5dee8; }
main { max-width:1100px; margin:0 auto; padding:1.5rem 1.2rem 3rem; }
nav { background:#fff; border:1px solid var(--line); border-radius:10px; padding:.8rem 1rem; margin-bottom:1rem; }
nav a { color:var(--navy); text-decoration:none; margin-right:.8rem; font-size:.92rem; }
.slide { background:#fff; border:1px solid var(--line); border-radius:12px; padding:1.1rem 1.25rem 1.3rem; margin:0 0 1rem; }
.page { margin:0; color:var(--muted); font-size:.8rem; }
h2 { margin:.15rem 0 .4rem; color:var(--navy); font-size:1.35rem; }
.sub { margin:.1rem 0 .7rem; color:var(--muted); }
.block { margin:.45rem 0; }
p { margin:.28rem 0; }
ul { margin:.2rem 0 .2rem 1.1rem; padding:0; }
li { margin:.18rem 0; }
table { width:100%; border-collapse:collapse; font-size:.92rem; margin:.3rem 0; }
th { background:var(--navy); color:#fff; text-align:left; font-weight:600; }
th, td { border-bottom:1px solid var(--line); padding:.32rem .45rem; vertical-align:top; }
tr:nth-child(even) td { background:#f7f9fb; }
table.gantt td:first-child { width:46%; font-weight:600; color:var(--navy); }
footer { color:var(--muted); font-size:.85rem; padding:0 0 2rem; text-align:center; }
@media print {
  .slide { break-inside:avoid; }
  body { background:#fff; }
}
</style>
</head>
<body>
<header>
  <h1>Asymchem UK - Sandwich Pilot Plant</h1>
  <p>Capital projects briefing, 12 October 2026</p>
  <p>English edition of the 12 October 2026 v3.1 briefing. Figures and wording follow that version.</p>
</header>
<main>
"""

HTML_FOOT = """
</main>
<footer>Asymchem UK - Sandwich PDF capital projects - 12 October 2026</footer>
</body>
</html>
"""


def _font_pt(tf, default=14):
    for para in tf.paragraphs:
        if para.runs and para.runs[0].font.size:
            return para.runs[0].font.size.pt
    return default


def _set_size(tf, pt):
    for para in tf.paragraphs:
        for run in para.runs:
            if run.text:
                run.font.size = Pt(pt)


def _needed_height(tf, width, pt):
    cpl = max(8, width * 72 / pt * 1.7)
    lines = 0
    for para in tf.paragraphs:
        text = para.text
        if not text.strip():
            continue
        lines += max(1, -(-len(text) // int(cpl)))
    return lines * pt * 1.25 / 72


def fit_text(shape, floor):
    if not shape.has_text_frame:
        return
    text = shape.text_frame.text.strip()
    if not text or shape.top.inches > 7.0 or shape.height.inches < 0.2:
        return
    if len(text) < 28:
        return
    tf = shape.text_frame
    pt = _font_pt(tf)
    while pt > floor and _needed_height(tf, shape.width.inches, pt) > shape.height.inches * 1.08:
        pt -= 1
    if pt != _font_pt(tf):
        _set_size(tf, pt)
    need = _needed_height(tf, shape.width.inches, pt)
    room = 7.12 - shape.top.inches
    if need > shape.height.inches * 1.08 and need <= room:
        shape.height = Pt(need * 72 + 2)


def polish(prs):
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                current = _font_pt(shape.text_frame)
                floor = 16 if current >= 24 else 10
                fit_text(shape, floor)
            if getattr(shape, "has_table", False) and shape.has_table:
                for row in shape.table.rows:
                    rh = row.height.inches if row.height else 0
                    if rh <= 0:
                        continue
                    for ci, cell in enumerate(row.cells):
                        if len(cell.text) < 50:
                            continue
                        width = shape.table.columns[ci].width.inches
                        pt = _font_pt(cell.text_frame, 11)
                        while pt > 8 and _needed_height(cell.text_frame, width, pt) > rh * 1.05:
                            pt -= 1
                        if pt != _font_pt(cell.text_frame, 11):
                            _set_size(cell.text_frame, pt)


def main():
    prs = Presentation(str(SRC))
    missing = set()
    for slide in prs.slides:
        walk_shapes(slide.shapes, missing)
    if missing:
        print("UNTRANSLATED", len(missing))
        for item in sorted(missing):
            print("---")
            print(item)
        raise SystemExit(1)
    leftover = []
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame and CJK.search(shape.text_frame.text):
                leftover.append((i, shape.text_frame.text[:120]))
            if getattr(shape, "has_table", False) and shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        if CJK.search(cell.text):
                            leftover.append((i, cell.text[:120]))
    if leftover:
        print("CJK LEFT", leftover[:30])
        raise SystemExit(1)
    polish(prs)
    prs.save(str(OUT_PPT))
    from build_en_v31_show import write_html
    write_html(OUT_PPT, OUT_HTML)
    print("wrote", OUT_PPT, OUT_PPT.stat().st_size)


if __name__ == "__main__":
    main()
