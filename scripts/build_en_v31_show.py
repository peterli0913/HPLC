#!/usr/bin/env python3
"""Presentation HTML for the English v3.1 deck.

Wording and figures are taken from the English PPTX. Nothing is added.
"""
from __future__ import annotations

import html
import math
import re
from datetime import datetime
from pathlib import Path

from pptx import Presentation

ROOT = Path("/workspace")
SRC = ROOT / "UK_PDF_Portfolio_Briefing_2026-10-12-v3.1-EN.pptx"
OUT = ROOT / "UK_PDF_Portfolio_Briefing_2026-10-12-v3.1-EN.html"

COLORS = ["#0f2b46", "#1a4a6e", "#009688", "#c9a227", "#5b6eae", "#2e6da4", "#8a9bae", "#1f7a6f"]
DATE_RE = re.compile(r"(\d{4})/(\d{2})\s*[\u2013-]\s*(\d{4})/(\d{2})")
PAGE_RE = re.compile(r"^\d+ / \d+$")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def paras(shape) -> list[str]:
    return [p.text.strip() for p in shape.text_frame.paragraphs if p.text.strip()]


def moneyish(text: str) -> bool:
    t = text.strip()
    return t.startswith("\u00a3") or t in {"\u2014", "-", "\u2013"} or bool(re.fullmatch(r"[\d,.]+", t))


class Box:
    def __init__(self, kind, top, left, width, height, text="", rows=None, chart=None):
        self.kind = kind
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.text = text
        self.lines = [ln for ln in text.split("\n") if ln.strip()] if text else []
        self.rows = rows or []
        self.chart = chart
        self.used = False


def collect(slide) -> tuple[list[Box], str, str]:
    boxes = []
    footer = "Asymchem UK · Sandwich PDF capital projects"
    page = ""
    for shape in slide.shapes:
        top = shape.top.inches
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if not text:
                continue
            if top > 7.05:
                if PAGE_RE.match(text):
                    page = text
                elif len(text) > 8:
                    footer = text
                continue
            boxes.append(Box("text", top, shape.left.inches, shape.width.inches, shape.height.inches, text))
        elif getattr(shape, "has_table", False) and shape.has_table:
            rows = []
            for row in shape.table.rows:
                rows.append([c.text.strip().replace("\n", "\n") for c in row.cells])
                # keep paragraph breaks inside a cell
            fixed = []
            for row in shape.table.rows:
                cells = []
                for cell in row.cells:
                    parts = [p.text.strip() for p in cell.text_frame.paragraphs if p.text.strip()]
                    cells.append("\n".join(parts))
                fixed.append(cells)
            boxes.append(Box("table", top, shape.left.inches, shape.width.inches, shape.height.inches, rows=fixed))
        elif getattr(shape, "has_chart", False) and shape.has_chart:
            chart = shape.chart
            try:
                cats = [str(c) for c in chart.plots[0].categories]
            except Exception:
                cats = []
            series = []
            for ser in chart.series:
                series.append((str(ser.name), [float(v or 0) for v in ser.values]))
            boxes.append(Box("chart", top, shape.left.inches, shape.width.inches, shape.height.inches, chart=(cats, series)))
    boxes.sort(key=lambda b: (b.top, b.left))
    return boxes, footer, page


def pair_gantt(boxes: list[Box]):
    rows = []
    dates = [b for b in boxes if b.kind == "text" and b.left > 10 and DATE_RE.search(b.text)]
    for date_box in dates:
        label = None
        best = 9
        for box in boxes:
            if box.kind != "text" or box.left > 3 or box.width > 2.6:
                continue
            gap = abs(box.top - date_box.top)
            if gap < best and gap < 0.12:
                best = gap
                label = box
        if label is None:
            continue
        m = DATE_RE.search(date_box.text)
        start = datetime(int(m.group(1)), int(m.group(2)), 1)
        end = datetime(int(m.group(3)), int(m.group(4)), 28)
        rows.append((label.text, date_box.text, start, end))
        label.used = True
        date_box.used = True
    rows.sort(key=lambda r: r[2])
    # restore visual order (top), not date order
    rows_by_top = []
    for date_box in sorted(dates, key=lambda b: b.top):
        if not date_box.used:
            continue
        for row in rows:
            if row[1] == date_box.text and row not in rows_by_top:
                rows_by_top.append(row)
                break
    return rows_by_top


def bar_tone(label: str) -> str:
    low = label.lower()
    if "indicative" in low:
        return "assume"
    if low.startswith("fs") or "baseline" in low:
        return "done"
    if "engineer mobil" in low:
        return "staff"
    if any(k in low for k in ("retrofit", "construction", "commissioning and", "installation and qual")):
        return "build"
    if any(k in low for k in ("fat", "ship", "validation", "manufacture", "spec /", "procurement", "fume", "furniture", "trade", "risk allowance", "order and")):
        return "warn"
    return "plan"


def gantt_html(rows, legend, show_today: bool) -> str:
    if not rows:
        return ""
    t0 = min(r[2] for r in rows)
    t1 = max(r[3] for r in rows)
    span = max((t1 - t0).days, 1)

    def pct(dt):
        return max(0, min(100, (dt - t0).days / span * 100))

    body = []
    for label, dates, start, end in rows:
        left = pct(start)
        width = max(1.2, pct(end) - left)
        body.append(
            f'<div class="grow"><div class="gl">{esc(label)}</div>'
            f'<div class="gtrack"><div class="gbar {bar_tone(label)}" style="left:{left:.2f}%;width:{width:.2f}%"></div></div>'
            f'<div class="gd">{esc(dates)}</div></div>'
        )
    today = ""
    if show_today:
        mark = pct(datetime(2026, 10, 12))
        today = f'<div class="gtoday" style="left:calc(9.2rem + (100% - 16.4rem) * {mark/100:.4f})"></div>'
    legs = "".join(f'<span><i class="{bar_tone(name) if name.lower() not in {"done","today"} else "done"}"></i>{esc(name)}</span>' for name in legend)
    # legend colors should follow the words, not bar_tone of the legend phrase itself
    legs = []
    for name in legend:
        tone = {
            "done": "done",
            "procurement / manufacture": "warn",
            "construction / qualification": "build",
            "critical path": "warn",
            "engineer mobilisation": "staff",
            "§4.3 indicative": "assume",
            "design / preparation": "plan",
            "order and manufacture": "warn",
            "installation / qualification": "build",
            "design / contracts": "plan",
            "procurement / manufacture / allowance": "warn",
            "construction / commissioning": "build",
        }.get(name.lower(), "plan")
        legs.append(f'<span><i class="{tone}"></i>{esc(name)}</span>')
    return '<div class="gantt">' + today + "".join(body) + '</div><div class="legend">' + "".join(legs) + "</div>"


def kpi_pairs(boxes: list[Box]) -> list[tuple[str, str]]:
    values = [
        b for b in boxes
        if not b.used and b.kind == "text" and 2.0 <= b.width <= 4.3 and 0.45 <= b.height <= 0.7 and b.top < 6.2
    ]
    pairs = []
    claimed = set()
    for val in sorted(values, key=lambda b: (b.top, b.left)):
        if id(val) in claimed:
            continue
        label = None
        best = 9
        for box in boxes:
            if box.used or box is val or box.kind != "text" or id(box) in claimed:
                continue
            if abs(box.left - val.left) > 0.25 or abs(box.width - val.width) > 1.0:
                continue
            gap = box.top - val.top
            if 0.15 < gap < 1.4 and gap < best:
                best = gap
                label = box
        if label is None:
            continue
        pairs.append((val, label))
        claimed.add(id(val))
        claimed.add(id(label))
    pairs.sort(key=lambda pl: (pl[0].top, pl[0].left))
    for val, label in pairs:
        val.used = True
        label.used = True
    return [(v.text.replace("\n", " "), l.text.replace("\n", " ")) for v, l in pairs]


def card_groups(boxes: list[Box]) -> list[tuple[str, list[str]]]:
    titles = [b for b in boxes if not b.used and b.kind == "text" and b.height <= 0.42 and 3.2 <= b.width <= 6.2 and "\u2022" not in b.text]
    groups = []
    for title in titles:
        body = None
        best = 9
        for box in boxes:
            if box.used or box.kind != "text" or box is title:
                continue
            if abs(box.left - title.left) > 0.35:
                continue
            gap = box.top - title.top
            if 0.15 < gap < 0.7 and gap < best and ("•" in box.text or box.height > 0.6):
                best = gap
                body = box
        if body is None:
            continue
        lines = [ln.lstrip("•").strip() for ln in body.text.split("\n") if ln.strip()]
        groups.append((title, body, lines))
    groups.sort(key=lambda g: (g[0].top, g[0].left))
    for title, body, _lines in groups:
        title.used = True
        body.used = True
    return [(t.top, t.text, lines) for t, _b, lines in groups]


def table_html(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = not moneyish(rows[0][-1]) and not rows[0][-1].startswith("£")
    # A cost sheet starts with a named total and a ? figure.
    if rows[0][-1].startswith("£"):
        header = False
    widths = {
        2: ["72%", "28%"],
        4: ["20%", "32%", "18%", "30%"],
        5: ["16%", "18%", "34%", "16%", "16%"],
        6: ["10%", "22%", "16%", "11%", "11%", "30%"],
        7: ["16%", "13%", "16%", "12%", "11%", "16%", "16%"],
    }.get(len(rows[0]), [])
    colgroup = ""
    if widths:
        colgroup = "<colgroup>" + "".join(f'<col style="width:{w}"/>' for w in widths) + "</colgroup>"
    body = [colgroup]
    for r, row in enumerate(rows):
        tag = "th" if header and r == 0 else "td"
        cells = []
        for c, val in enumerate(row):
            cls = []
            show = val
            if c == len(row) - 1 and (val.startswith("£") or val in {"—", "-"}):
                cls.append("num")
            if tag == "td" and val in {"Lost", "Live · second source", "Live · transfer to Sandwich", "Enquiry", "Requirement listed"}:
                kind = {
                    "Lost": "lost",
                    "Live · second source": "live",
                    "Live · transfer to Sandwich": "sw",
                    "Enquiry": "enq",
                    "Requirement listed": "listed",
                }[val]
                show = f'<span class="pill {kind}">{esc(val)}</span>'
                cells.append(f'<{tag} class="{" ".join(cls)}">{show}</{tag}>')
                continue
            if tag == "td" and val in {"Phase 1", "Phase 2", "Later", "New", "Existing", "New / existing"}:
                kind = {
                    "Phase 1": "p1",
                    "Phase 2": "p2",
                    "Later": "later",
                    "New": "p1",
                    "Existing": "later",
                    "New / existing": "p2",
                }[val]
                show = f'<span class="pill {kind}">{esc(val)}</span>'
                cells.append(f'<{tag}>{show}</{tag}>')
                continue
            label = row[0]
            if tag == "td" and c == 0 and (label.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.")) is False) and moneyish(row[-1]):
                cls.append("strong")
            if re.match(r"^\d+\.\d+", label) and c == 0:
                cls.append("leaf")
            if label.lower() in {"total", "subtotal"} or label.startswith("Phase 1 investment") or label.startswith("of which"):
                cls.append("total")
            cells.append(f'<{tag} class="{" ".join(cls)}">{esc(val).replace(chr(10), "<br>")}</{tag}>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + "".join(body) + "</table>"


def donut_svg(pairs: list[tuple[str, float]], caption: str = "") -> str:
    total = sum(v for _, v in pairs) or 1
    r = 38
    circ = 2 * math.pi * r
    offset = 0
    rings = []
    for i, (_name, val) in enumerate(pairs):
        dash = val / total * circ
        rings.append(
            f'<circle cx="60" cy="60" r="{r}" fill="none" stroke="{COLORS[i % len(COLORS)]}" '
            f'stroke-width="18" stroke-dasharray="{dash:.2f} {circ - dash:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 60 60)"/>'
        )
        offset += dash
    legend = []
    for i, (name, val) in enumerate(pairs):
        legend.append(
            f'<li><i style="background:{COLORS[i % len(COLORS)]}"></i>'
            f'<span>{esc(name)}</span><b>£{int(round(val)):,}</b></li>'
        )
    cap = f'<div class="chartcap">{esc(caption)}</div>' if caption else ""
    return (
        f'<div class="chart">{cap}'
        f'<svg viewBox="0 0 120 120" class="donut">{"".join(rings)}'
        f'<text x="60" y="64" text-anchor="middle">£{total/1e6:.2f}M</text></svg>'
        f'<ul class="cl">{"".join(legend)}</ul></div>'
    )


def stack_html(pairs: list[tuple[str, float]], caption: str) -> str:
    total = sum(v for _, v in pairs) or 1
    segs = []
    legend = []
    for i, (name, val) in enumerate(pairs):
        segs.append(f'<div style="width:{val / total * 100:.2f}%;background:{COLORS[i % len(COLORS)]}"></div>')
        legend.append(
            f'<li><i style="background:{COLORS[i % len(COLORS)]}"></i>'
            f'<span>{esc(name)}</span><b>£{int(round(val)):,}</b></li>'
        )
    cap = f'<div class="chartcap">{esc(caption)}</div>' if caption else ""
    return f'<div class="chart">{cap}<div class="stack">{"".join(segs)}</div><ul class="cl">{"".join(legend)}</ul></div>'


def chart_html(box: Box, caption: str) -> str:
    cats, series = box.chart
    if len(cats) <= 1 and len(series) > 1:
        return stack_html([(name, vals[0] if vals else 0) for name, vals in series], caption)
    if len(series) == 1 and len(cats) > 1:
        vals = series[0][1]
        return donut_svg([(cat, vals[i] if i < len(vals) else 0) for i, cat in enumerate(cats)], caption)
    return ""


def bullets_html(text: str) -> str:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if lines and all(ln.startswith("•") for ln in lines):
        items = "".join(f"<li>{esc(ln.lstrip('\u2022').strip())}</li>" for ln in lines)
        return f"<ul>{items}</ul>"
    return "".join(f"<p>{esc(ln)}</p>" for ln in lines)


def render(index: int, slide, total: int) -> str:
    boxes, footer, page = collect(slide)
    if not page:
        page = f"{index} / {total}"

    # Cover and closing slides are laid out from the same text, not as a form.
    texts = [b for b in boxes if b.kind == "text"]
    if index == 1:
        return cover_html(texts, footer, page)
    if index == total and any(b.text.strip() == "Thank you" for b in texts):
        date = next((b.text for b in texts if "2026" in b.text), "")
        return (
            f'<section class="slide thanks"><div class="thanks-inner">'
            f'<h2>Thank you</h2><p>{esc(date)}</p>'
            f'<p class="fine">{esc(footer)}</p></div>'
            f'<footer><span>{esc(footer)}</span><span>{esc(page)}</span></footer></section>'
        )

    gantt = pair_gantt(boxes)
    legend = []
    show_today = False
    if gantt:
        for box in boxes:
            if box.used or box.kind != "text":
                continue
            if box.text.strip() == "Today":
                box.used = True
                show_today = True
            elif re.fullmatch(r"\d{4} H[12]", box.text.strip()):
                box.used = True
            elif box.top > 6.4 and box.height <= 0.36 and box.left > 2:
                legend.append(box.text.strip())
                box.used = True

    kpis = kpi_pairs(boxes)
    cards = card_groups(boxes)

    title = ""
    subtitle = ""
    heads = [b for b in boxes if not b.used and b.kind == "text" and b.width > 8 and b.top < 2.3]
    heads.sort(key=lambda b: b.top)
    if heads:
        title = heads[0].text.strip()
        heads[0].used = True
        if len(heads) > 1 and heads[1].top - heads[0].top < 1.15:
            subtitle = heads[1].text.strip()
            heads[1].used = True
    badge = ""
    for box in boxes:
        if box.used or box.kind != "text" or box.top > 1.2 or box.width > 2.8:
            continue
        if len(box.text) < 20:
            badge = box.text.strip()
            box.used = True
            break

    # Headings that sit just above a chart.
    chart_caps = {}
    charts = [b for b in boxes if b.kind == "chart"]
    for chart in charts:
        cap = None
        best = 9
        for box in boxes:
            if box.used or box.kind != "text":
                continue
            if abs(box.left - chart.left) > 0.6:
                continue
            gap = chart.top - box.top
            if 0 < gap < 0.55 and gap < best:
                best = gap
                cap = box
        if cap is not None:
            chart_caps[id(chart)] = cap.text.strip()
            cap.used = True

    chunks = []
    if kpis:
        cells = "".join(f'<div class="kpi"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in kpis)
        chunks.append((1.15, f'<div class="kpis n{len(kpis)}">{cells}</div>'))

    banners = [
        b for b in boxes
        if not b.used and b.kind == "text" and b.width > 4.5 and b.height < 0.7 and "\u2022" not in b.text and b.top > 1.2
    ]
    banners.sort(key=lambda b: (b.top, b.left))
    if len(banners) >= 2 and abs(banners[0].top - banners[1].top) < 0.15:
        chunks.append((banners[0].top, '<div class="stats">' + "".join(f"<div>{esc(b.text)}</div>" for b in banners[:2]) + "</div>"))
        for b in banners[:2]:
            b.used = True

    tables = [b for b in boxes if b.kind == "table"]
    charts_sorted = sorted(charts, key=lambda b: b.left)
    if len(tables) == 2:
        chunks.append((min(t.top for t in tables), '<div class="cols">' + "".join(f'<div class="panel">{table_html(t.rows)}</div>' for t in tables) + "</div>"))
        for t in tables:
            t.used = True
    elif tables:
        for t in tables:
            chunks.append((t.top, f'<div class="panel">{table_html(t.rows)}</div>'))
            t.used = True

    if charts_sorted:
        blocks = []
        for chart in charts_sorted:
            blocks.append(f'<div class="panel">{chart_html(chart, chart_caps.get(id(chart), ""))}</div>')
            chart.used = True
        chunks.append((min(c.top for c in charts_sorted), '<div class="cols charts">' + "".join(blocks) + "</div>"))

    if cards:
        cells = []
        for _top, name, lines in cards:
            items = "".join(f"<li>{esc(ln)}</li>" for ln in lines)
            cells.append(f'<article class="card"><h3>{esc(name)}</h3><ul>{items}</ul></article>')
        chunks.append((min(c[0] for c in cards), f'<div class="cards n{len(cards)}">{"".join(cells)}</div>'))

    if gantt:
        chunks.append((2.2, gantt_html(gantt, legend, show_today)))

    for box in boxes:
        if box.used or box.kind != "text":
            continue
        chunks.append((box.top, f'<div class="note">{bullets_html(box.text)}</div>'))
        box.used = True
    chunks.sort(key=lambda c: c[0])
    parts = [html_bit for _top, html_bit in chunks]

    sub = f'<p class="sub">{esc(subtitle)}</p>' if subtitle else ""
    badge_html = f'<div class="badge">{esc(badge)}</div>' if badge else ""
    return (
        f'<section class="slide"><div class="rule"></div>'
        f'<header class="hd">{badge_html}<h2>{esc(title)}</h2>{sub}</header>'
        f'<div class="main">{"".join(parts)}</div>'
        f'<footer><span>{esc(footer)}</span><span>{esc(page)}</span></footer></section>'
    )


def cover_html(texts: list[Box], footer: str, page: str) -> str:
    badge = next((b.text for b in texts if b.top < 1.5 and b.width < 4), "")
    title = next((b.text for b in texts if b.width > 8 and b.top < 2.2), "")
    sub = next((b.text for b in texts if b.width > 8 and 2.2 <= b.top < 3.1), "")
    date = next((b.text for b in texts if "date" in b.text.lower() or b.top > 6), "")
    cards = []
    heads = [b for b in texts if 3.2 < b.top < 4.1 and b.width < 4]
    heads.sort(key=lambda b: b.left)
    for head in heads:
        value = next((b for b in texts if abs(b.left - head.left) < 0.3 and 4.0 < b.top < 4.9), None)
        detail = next((b for b in texts if abs(b.left - head.left) < 0.3 and b.top >= 4.9 and b.width < 5), None)
        detail_html = ""
        if detail:
            detail_html = "".join(f"<span>{esc(ln)}</span>" for ln in detail.lines)
        cards.append(
            f'<article class="cover-card"><h3>{esc(head.text)}</h3>'
            f'<b>{esc(value.text if value else "")}</b><p>{detail_html}</p></article>'
        )
    return (
        '<section class="slide cover"><div class="rule"></div><div class="cover-inner">'
        f'<div class="badge">{esc(badge)}</div><h1>{esc(title)}</h1><p class="lede">{esc(sub)}</p>'
        f'<div class="cover-cards">{"".join(cards)}</div><p class="date">{esc(date)}</p></div>'
        f'<footer><span>{esc(footer)}</span><span>{esc(page)}</span></footer></section>'
    )


CSS = r"""
:root {
  --navy:#0f2b46; --teal:#1f7a6f; --gold:#c9a227; --text:#243140; --muted:#5c6b7a;
  --line:#e3e8ee; --bg:#f3f5f8; --card:#fff; --warn:#b43a2a;
}
* { box-sizing: border-box; }
html, body { margin:0; height:100%; background:#101820; color:var(--text);
  font-family: Calibri, "Segoe UI", sans-serif; }
.stage { height:100vh; display:flex; align-items:center; justify-content:center; }
.slide { display:none; width:min(100vw, calc(100vh * 16 / 9)); height:min(100vh, calc(100vw * 9 / 16));
  background:var(--bg); position:relative; padding:1.6% 2.2% 4.6%; flex-direction:column; overflow:hidden; }
.slide.on { display:flex; }
.rule { position:absolute; left:0; right:0; top:0; height:7px;
  background:linear-gradient(90deg,#0f2b46 0 42%, #1f7a6f 42% 72%, #c9a227 72% 100%); }
.hd h2 { margin:0; color:var(--navy); font-size:1.7rem; line-height:1.15; font-weight:700; }
.sub { margin:.15rem 0 0; color:var(--muted); font-size:.92rem; }
.main { flex:1; min-height:0; display:flex; flex-direction:column; gap:.55rem; margin-top:.55rem; }
.kpis { display:grid; gap:.5rem; }
.kpis.n2 { grid-template-columns:repeat(2,1fr); }
.kpis.n3 { grid-template-columns:repeat(3,1fr); }
.kpis.n4 { grid-template-columns:repeat(4,1fr); }
.kpis.n5 { grid-template-columns:repeat(5,1fr); }
.kpi, .card, .panel, .note { background:var(--card); border:1px solid var(--line); border-radius:10px; }
.kpi { padding:.45rem .7rem .5rem .75rem; border-left:4px solid var(--teal); min-width:0; }
.kpi b { display:block; color:var(--navy); font-size:1.25rem; line-height:1.15; }
.kpi span { display:block; color:var(--muted); font-size:.78rem; line-height:1.25; margin-top:.12rem; }
.cols { display:grid; grid-template-columns:1fr 1fr; gap:.55rem; min-height:0; }
.cols.charts { flex:1; }
.cols.charts .panel { display:flex; }
.cols.charts .chart { width:100%; }
.panel { padding:.35rem .45rem; overflow:auto; min-height:0; }
.panel.grow, .gantt { flex:1; min-height:0; }
table { width:100%; border-collapse:collapse; font-size:.74rem; table-layout:fixed; }
th { background:var(--navy); color:#fff; text-align:left; font-weight:600; position:sticky; top:0; }
th, td { padding:.28rem .4rem; border-bottom:1px solid var(--line); vertical-align:top; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.strong, td.total { font-weight:700; color:var(--navy); }
td.leaf { color:#607080; }
tr:nth-child(even) td { background:#f7f9fb; }
.pill { display:inline-block; border-radius:99px; padding:.05rem .45rem; font-weight:700; font-size:.72rem; white-space:nowrap; }
.pill.lost { color:var(--warn); background:#fdecea; }
.pill.live { color:#1a4a6e; background:#e7eef5; }
.pill.sw { color:var(--teal); background:#e5f4f1; }
.pill.enq { color:#5c6b7a; background:#eef1f4; }
.pill.listed { color:#0f6b4c; background:#e5f6ef; }
.pill.p1 { color:var(--teal); background:#e5f4f1; }
.pill.p2 { color:#8a6a12; background:#fbf3dc; }
.pill.later { color:#5c6b7a; background:#eef1f4; }
.cards { display:grid; gap:.5rem; min-height:0; flex:1; }
.cards.n2 { grid-template-columns:1fr 1fr; }
.cards.n3 { grid-template-columns:repeat(3,1fr); }
.cards.n4 { grid-template-columns:1fr 1fr; }
.card { padding:.55rem .7rem .65rem; border-top:4px solid var(--navy); overflow:auto; }
.card h3 { margin:0 0 .3rem; color:var(--navy); font-size:.95rem; }
.card ul, .notes ul, .note ul { margin:.1rem 0 0; padding-left:1.05rem; }
.card li, .note li { margin:.16rem 0; font-size:.84rem; line-height:1.35; }
.stats { display:grid; grid-template-columns:1fr 1fr; gap:.5rem; }
.stats div { background:#fff; border:1px solid var(--line); border-radius:8px; padding:.35rem .7rem; font-weight:700; color:var(--navy); }
.notes { display:flex; flex-direction:column; gap:.4rem; }
.note { border-left:4px solid var(--gold); padding:.4rem .65rem; font-size:.86rem; line-height:1.35; }
.note p { margin:.12rem 0; }
.chart { display:flex; flex-direction:column; gap:.35rem; height:100%; }
.chartcap { text-align:center; font-weight:700; color:var(--navy); font-size:.85rem; }
.stack { display:flex; height:28px; border-radius:6px; overflow:hidden; background:#eef2f6; }
.donut { width:150px; height:150px; align-self:center; }
.donut text { font-size:11px; fill:var(--navy); font-weight:700; }
.cl { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.22rem; font-size:.75rem; }
.cl li { display:grid; grid-template-columns:12px 1fr auto; gap:.35rem; align-items:center; }
.cl i { width:10px; height:10px; border-radius:2px; display:block; }
.cl b { font-variant-numeric:tabular-nums; color:var(--navy); }
.gantt { position:relative; display:flex; flex-direction:column; justify-content:space-between; background:#fff; border:1px solid var(--line); border-radius:10px; padding:.35rem .5rem; overflow:hidden; }
.grow { display:grid; grid-template-columns:9.2rem 1fr 6.6rem; gap:.35rem; align-items:center; }
.gl { font-size:.68rem; font-weight:700; color:var(--navy); text-align:right; line-height:1.15; }
.gtrack { position:relative; height:14px; background:#eef2f6; border-radius:4px; }
.gbar { position:absolute; top:2px; height:10px; border-radius:3px; }
.gbar.done { background:#009688; }
.gbar.plan { background:#1a4a6e; }
.gbar.build { background:#2e6da4; }
.gbar.warn { background:#c9a227; }
.gbar.staff { background:#5b6eae; }
.gbar.assume { background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 4px,#8f7db8 4px,#8f7db8 8px); }
.gd { font-size:.62rem; color:var(--muted); text-align:right; white-space:nowrap; }
.gtoday { position:absolute; top:.3rem; bottom:1.5rem; width:2px; background:var(--warn); }
.legend { display:flex; flex-wrap:wrap; gap:.45rem .7rem; font-size:.68rem; color:var(--muted); margin-top:.15rem; }
.legend i { display:inline-block; width:9px; height:9px; border-radius:2px; margin-right:.2rem; vertical-align:middle; }
.legend i.done { background:#009688; } .legend i.plan { background:#1a4a6e; }
.legend i.build { background:#2e6da4; } .legend i.warn { background:#c9a227; }
.legend i.staff { background:#5b6eae; }
.legend i.assume { background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 3px,#8f7db8 3px,#8f7db8 6px); }
footer { position:absolute; left:0; right:0; bottom:0; height:4.2%; background:#fff; border-top:1px solid var(--line);
  display:flex; align-items:center; justify-content:space-between; padding:0 2.2%; color:var(--muted); font-size:.75rem; }
.cover { background:linear-gradient(180deg,#f7f8fa,#eef2f5); }
.cover-inner { padding:4% 2% 0; }
.badge { display:inline-block; background:var(--navy); color:#fff; border-radius:99px; padding:.28rem .7rem; font-size:.78rem; font-weight:700; }
.cover h1 { margin:.7rem 0 .15rem; color:var(--navy); font-size:2.3rem; line-height:1.05; }
.lede { margin:0; color:var(--muted); font-size:1.15rem; }
.cover-inner { flex:1; display:flex; flex-direction:column; }
.cover-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem; margin-top:auto; margin-bottom:auto; }
.cover-card { background:#fff; border-radius:14px; padding:.9rem 1rem 1rem; border:1px solid var(--line); box-shadow:0 8px 24px rgba(15,43,70,.06); }
.cover-card h3 { margin:0; color:var(--navy); font-size:1rem; min-height:2.4rem; }
.cover-card b { display:block; margin:.35rem 0; font-size:2.1rem; color:#1f7a6f; }
.cover-card:nth-child(1) b { color:#5b6eae; }
.cover-card:nth-child(3) b { color:#1a4a6e; }
.cover-card p { margin:0; display:flex; flex-direction:column; gap:.15rem; color:var(--muted); font-size:.88rem; }
.date { margin:1rem 0 0; color:var(--muted); }
.thanks { background:var(--navy); color:#fff; align-items:center; justify-content:center; }
.thanks-inner { text-align:center; }
.thanks h2 { font-size:3.2rem; margin:0 0 .4rem; }
.thanks p { color:#d5dee6; font-size:1.05rem; }
.thanks .fine { color:#8aa0b5; }
.navhint { position:fixed; right:14px; bottom:10px; color:#9aabbc; font-size:12px; z-index:5; }
@media print {
  .stage { display:block; height:auto; }
  .slide { display:flex !important; width:100%; height:auto; min-height:100vh; break-after:page; }
  .navhint { display:none; }
}
"""

JS = r"""
const slides=[...document.querySelectorAll('.slide')];
let n=Math.max(0, Math.min(slides.length-1, +(new URLSearchParams(location.search).get('n')||0)));
function show(i){ n=i; slides.forEach((s,k)=>s.classList.toggle('on', k===i)); }
document.addEventListener('keydown', (e)=>{
  if(['ArrowRight','PageDown',' '].includes(e.key)) show(Math.min(slides.length-1, n+1));
  if(['ArrowLeft','PageUp','Backspace'].includes(e.key)) show(Math.max(0, n-1));
  if(e.key==='Home') show(0);
  if(e.key==='End') show(slides.length-1);
});
show(n);
const bad=[];
slides.forEach((s,i)=>{
  const prev=s.classList.contains('on');
  s.classList.add('on');
  const over=s.scrollHeight-s.clientHeight;
  if(over>6) bad.push((i+1)+':'+over);
  if(!prev) s.classList.remove('on');
});
document.body.dataset.overflow=bad.join(',')||'none';
"""


def write_html(src: Path = SRC, out: Path = OUT) -> None:
    prs = Presentation(str(src))
    total = len(prs.slides)
    sections = [render(i, slide, total) for i, slide in enumerate(prs.slides, 1)]
    doc = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"/>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>"
        "<title>Asymchem UK · Sandwich Pilot Plant – Capital projects briefing, 12 October 2026</title>"
        f"<style>{CSS}</style></head><body><div class=\"stage\">{''.join(sections)}</div>"
        ""
        f"<script>{JS}</script></body></html>"
    )
    # Every PPT sentence should still be present.
    plain = html.unescape(re.sub(r"<[^>]+>", " ", doc))
    missing = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for line in para.text.splitlines():
                    text = line.strip().lstrip("\u2022").strip()
                    if len(text) < 8 or PAGE_RE.match(text):
                        continue
                    if text not in plain:
                        missing.append(text[:160])
    if missing:
        raise SystemExit("HTML dropped PPT text:\n" + "\n".join(missing[:20]))
    out.write_text(doc, encoding="utf-8")
    print("wrote", out, out.stat().st_size)


if __name__ == "__main__":
    write_html()
