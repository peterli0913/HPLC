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
        today = f'<div class="gtoday" style="left:calc(15rem + (100% - 23.4rem) * {mark/100:.4f})"></div>'
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


def _kind(label: str) -> str:
    low = label.lower().strip()
    if low in {"total", "subtotal"} or low.startswith("of which") or low.startswith("phase 1 investment") or low.startswith("facilitating and building"):
        return "total"
    if re.match(r"^\d+\.\d+", label):
        return "leaf"
    if re.match(r"^\d+[\.\s]", label):
        return "group"
    if low.startswith(("direct cost", "indirect cost", "general risk", "direct construction", "other project", "main equipment (")):
        return "section"
    return "line"


def cost_tree(rows: list[list[str]]) -> str:
    blocks = []
    section = None
    group = None

    def flush_group():
        nonlocal group
        if group and section is not None:
            section[3].append(group)
            group = None

    def flush_section():
        nonlocal section
        flush_group()
        if section:
            blocks.append(section)
            section = None

    for row in rows:
        label, amt = row[0], row[-1]
        kind = _kind(label)
        if kind == "total":
            flush_section()
            blocks.append(["total", label, amt, []])
        elif kind == "section":
            flush_section()
            section = ["section", label, amt, []]
        elif kind == "group":
            if section is None:
                section = ["section", label, amt, []]
            else:
                flush_group()
                group = ["group", label, amt, []]
        else:
            if section is None:
                section = ["section", label, amt, []]
            elif group is not None and kind == "leaf":
                group[3].append((label, amt))
            else:
                flush_group()
                section[3].append(("line", label, amt, []))
    flush_section()
    parts = []
    for kind, label, amt, children in blocks:
        if kind == "total":
            parts.append(f'<div class="cost-subtotal"><span>{esc(label)}</span><span>{esc(amt)}</span></div>')
            continue
        inner = []
        for child in children:
            if child[0] == "group":
                leaves = "".join(
                    f'<div class="cost-leaf"><span>{esc(a)}</span><span>{esc(b)}</span></div>' for a, b in child[3]
                )
                body = f'<div class="cost-children">{leaves}</div>' if leaves else ""
                inner.append(
                    f'<details class="cost-item" open><summary><span class="cost-label">{esc(child[1])}</span>'
                    f'<span class="cost-amt">{esc(child[2])}</span></summary>{body}</details>'
                )
            else:
                inner.append(f'<div class="cost-leaf"><span>{esc(child[1])}</span><span>{esc(child[2])}</span></div>')
        title = f'<span class="cost-section-title">{esc(label)}</span>' if label else ""
        parts.append(
            f'<details class="cost-section" open><summary><span class="cost-section-title">{esc(label)}</span>'
            f'<span class="cost-section-amt">{esc(amt)}</span></summary><div class="cost-section-body">{"".join(inner)}</div></details>'
        )
    return '<div class="cost-scroll">' + "".join(parts) + "</div>"


def table_html(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    if len(rows[0]) == 2 and moneyish(rows[0][-1]):
        return cost_tree(rows)
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
    table = "<table>" + "".join(body) + "</table>"
    if header and len(rows) > 6:
        return f'<div class="demand-wrap">{table}</div>'
    return table


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
    import json as _json
    cats, series = box.chart
    if len(cats) <= 1 and len(series) > 1:
        spec = {"kind": "bar", "series": [{"name": name, "value": (vals[0] if vals else 0)} for name, vals in series]}
    elif len(series) == 1 and len(cats) > 1:
        vals = series[0][1]
        spec = {"kind": "doughnut", "labels": cats, "values": [vals[i] if i < len(vals) else 0 for i in range(len(cats))]}
    else:
        return ""
    cap = f'<div class="chart-title">{esc(caption)}</div>' if caption else ""
    return f'<div class="chart-card">{cap}<div class="chart-wrap"><canvas data-chart="{esc(_json.dumps(spec))}"></canvas></div></div>'


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
            elif box.top > 5.9 and box.height <= 0.6 and 2.5 < box.left < 11 and box.width < 4.2 and len(box.text) < 60:
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
:root{--navy:#0f2b46;--teal:#009688;--accent:#c9a227;--ext:#1a4a6e;--hplc:#5b6eae;--c1:#8b6914;--hipo:#1f7a6f;--bg:#f4f6f8;--card:#fff;--text:#2c3e50;--muted:#5a6a7a;--warn:#b43a2a;--line:#e8ecf0}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font-family:"Segoe UI",Calibri,"PingFang SC","Microsoft YaHei",sans-serif;overflow:hidden}
.slide{display:none;height:100vh;padding:1.7rem 2.6rem 3rem;flex-direction:column;animation:fade .28s ease}
.slide.on{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
.top-bar{position:fixed;top:0;left:0;right:0;height:6px;background:linear-gradient(90deg,var(--navy),var(--teal),var(--accent));z-index:100}
h2{font-size:1.55rem;color:var(--navy);font-weight:700;margin:0 0 .15rem;line-height:1.2}
.sub{font-size:.92rem;color:var(--muted);font-weight:400;margin:0 0 .7rem}
.badge{display:inline-block;background:var(--navy);color:#fff;font-size:.72rem;font-weight:700;padding:.18rem .5rem;border-radius:3px;margin-bottom:.35rem}
.main{flex:1;min-height:0;display:flex;flex-direction:column;gap:.6rem}
.scroll-page{flex:1;min-height:0;overflow:auto;display:flex;flex-direction:column;gap:.8rem;padding-right:.2rem}
.joined{display:flex;flex-direction:column;gap:.6rem}
.split-next{margin-top:.2rem}
.split-next h2{font-size:1.25rem}
.kpis{display:grid;gap:.55rem}
.kpis.n2{grid-template-columns:repeat(2,1fr)}
.kpis.n3{grid-template-columns:repeat(3,1fr)}
.kpis.n4{grid-template-columns:repeat(4,1fr)}
.kpis.n5{grid-template-columns:repeat(5,1fr)}
.kpis.n6{grid-template-columns:repeat(3,1fr)}
.kpi{background:var(--card);border-radius:10px;padding:.6rem .75rem;border-left:4px solid var(--teal);box-shadow:0 2px 12px rgba(15,43,70,.05)}
.kpi b{display:block;color:var(--navy);font-size:1.15rem;line-height:1.2}
.kpi span{display:block;color:var(--muted);font-size:.74rem;margin-top:.12rem;line-height:1.3}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;min-height:0;flex:1}
.panel{min-height:0;overflow:auto;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;box-shadow:0 2px 12px rgba(15,43,70,.05)}
.cards{display:grid;gap:.6rem;min-height:0}
.cards.n2{grid-template-columns:1fr 1fr}
.cards.n3{grid-template-columns:repeat(3,1fr)}
.cards.n4{grid-template-columns:1fr 1fr}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:.75rem .85rem;box-shadow:0 2px 12px rgba(15,43,70,.05);overflow:auto}
.card h3{margin:0 0 .35rem;color:var(--navy);font-size:.92rem}
.card ul,.note ul{margin:.15rem 0 0 1.05rem;padding:0}
.card li,.note li{margin:.22rem 0;font-size:.86rem;line-height:1.45}
.note{background:#fff;border-left:4px solid var(--accent);border-radius:0 8px 8px 0;padding:.55rem .8rem;font-size:.86rem;line-height:1.45;box-shadow:0 1px 6px rgba(15,43,70,.04)}
.note p{margin:.12rem 0}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:.55rem}
.stats div{background:#fff;border:1px solid var(--line);border-radius:8px;padding:.45rem .7rem;font-weight:700;color:var(--navy);font-size:.9rem}
.demand-wrap{flex:1;min-height:0;overflow:auto;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 2px 12px rgba(15,43,70,.05)}
table{width:100%;border-collapse:collapse;font-size:.8rem}
th{position:sticky;top:0;background:#f3f6f8;color:var(--navy);font-size:.74rem;font-weight:700;text-align:left;z-index:1}
th,td{padding:.42rem .5rem;border-bottom:1px solid #eef1f4;vertical-align:top;line-height:1.4}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600}
td.strong{font-weight:700;color:var(--navy)}
td.leaf{color:#607080}
td.total{font-weight:700;color:var(--navy);background:#e8eef4}
tr:nth-child(even) td{background:#f8fafb}
.pill{display:inline-block;border-radius:99px;padding:.08rem .48rem;font-weight:700;font-size:.72rem;white-space:nowrap}
.pill.lost{background:#f8e6e3;color:var(--warn)}
.pill.live{background:#e7eef5;color:#1a4a6e}
.pill.sw,.pill.p1{background:#e5f4f2;color:#1f7a6f}
.pill.enq,.pill.later{background:#eef2f6;color:#5a6a7a}
.pill.listed{background:#eef3f8;color:#1a4a6e}
.pill.p2{background:#fbf3dc;color:#8a6a12}
.cost-scroll{flex:1;min-height:0;overflow:auto;padding-right:.15rem}
.cost-total-bar{background:var(--navy);color:#fff;border-radius:8px;padding:.55rem .75rem;margin:.35rem 0;font-size:.9rem;display:flex;justify-content:space-between;align-items:center}
.cost-section{border:1px solid #c5d0dc;border-radius:10px;margin-bottom:.45rem;background:#fff;box-shadow:0 1px 6px rgba(15,43,70,.05)}
.cost-section>summary{display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding:.55rem .75rem;cursor:pointer;list-style:none;background:linear-gradient(180deg,#eef3f8,#f8fafb)}
.cost-section>summary::-webkit-details-marker{display:none}
.cost-section-title{font-size:.9rem;font-weight:700;color:var(--navy);flex:1}
.cost-section-amt{font-size:.9rem;font-weight:700;color:#fff;background:var(--navy);padding:.22rem .6rem;border-radius:6px;white-space:nowrap}
.cost-section-body{padding:.15rem .45rem .45rem}
.cost-item{border-top:1px solid #f0f3f6}
.cost-item>summary{display:flex;justify-content:space-between;gap:.5rem;padding:.38rem .4rem .38rem .7rem;cursor:pointer;list-style:none;font-size:.8rem}
.cost-item>summary::-webkit-details-marker{display:none}
.cost-label{font-weight:600;color:var(--navy)}
.cost-amt{font-weight:700;color:var(--navy);white-space:nowrap}
.cost-children{padding:0 .4rem .35rem 1.2rem}
.cost-leaf{display:flex;justify-content:space-between;gap:.6rem;font-size:.78rem;color:var(--muted);padding:.22rem 0}
.cost-leaf span:last-child{font-weight:600;color:#5c6b7a;white-space:nowrap}
.cost-subtotal{display:flex;justify-content:space-between;padding:.45rem .65rem;margin:.25rem 0;font-size:.82rem;font-weight:700;color:var(--navy);background:#e8eef4;border-radius:6px}
.cols.charts .panel{height:100%;display:flex;padding:0;border:none;background:transparent;box-shadow:none;overflow:visible}
.chart-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem .5rem;box-shadow:0 2px 12px rgba(15,43,70,.05);display:flex;flex-direction:column;min-height:0;flex:1}
.chart-title{font-size:.84rem;font-weight:700;color:var(--navy);text-align:center;margin-bottom:.25rem}
.chart-wrap{position:relative;flex:1;min-height:320px}
.gantt{position:relative;flex:1;min-height:0;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.65rem .75rem .45rem;display:flex;flex-direction:column;box-shadow:0 2px 12px rgba(15,43,70,.05)}
.gantt-body{flex:1;overflow:auto;min-height:0}
.grow{display:grid;grid-template-columns:14.5rem 1fr 7.2rem;gap:.45rem;align-items:center;margin:.28rem 0}
.gl{font-size:.72rem;font-weight:700;color:var(--navy);text-align:right;line-height:1.25;overflow-wrap:anywhere}
.gtrack{position:relative;height:16px;background:#eef2f6;border-radius:4px}
.gbar{position:absolute;top:2px;height:12px;border-radius:3px}
.gbar.done{background:var(--teal)} .gbar.plan{background:#1a4a6e} .gbar.build{background:#2e6da4}
.gbar.warn{background:var(--accent)} .gbar.staff{background:#5b6eae}
.gbar.assume{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 4px,#8f7db8 4px,#8f7db8 8px)}
.gd{font-size:.68rem;color:var(--muted);text-align:right;white-space:nowrap}
.gtoday{position:absolute;top:.7rem;bottom:2rem;width:2px;background:var(--warn);z-index:2;pointer-events:none}
.legend{display:flex;flex-wrap:wrap;gap:.35rem .7rem;font-size:.7rem;color:var(--muted);margin-top:.35rem}
.legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:.22rem;vertical-align:middle}
.legend i.done{background:var(--teal)} .legend i.plan{background:#1a4a6e} .legend i.build{background:#2e6da4}
.legend i.warn{background:var(--accent)} .legend i.staff{background:#5b6eae}
.legend i.assume{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 3px,#8f7db8 3px,#8f7db8 6px)}
.slide>footer{margin-top:auto;display:flex;justify-content:space-between;color:var(--muted);font-size:.72rem;padding-top:.35rem}
.cover{justify-content:center}
.cover-inner{max-width:1100px;margin:0 auto;width:100%}
.cover h1{font-size:2.15rem;color:var(--navy);margin:.55rem 0 .2rem}
.lede{color:var(--muted);font-size:1.05rem;margin:0}
.cover-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin-top:1.6rem}
.cover-card{background:#fff;border-radius:12px;padding:1rem 1.05rem 1.1rem;border:1px solid var(--line);box-shadow:0 8px 24px rgba(15,43,70,.06)}
.cover-card h3{margin:0;color:var(--navy);font-size:1rem;min-height:2.5rem}
.cover-card b{display:block;margin:.35rem 0;font-size:2rem;color:var(--hipo)}
.cover-card:nth-child(1) b{color:var(--hplc)}
.cover-card:nth-child(3) b{color:var(--ext)}
.cover-card p{margin:0;display:flex;flex-direction:column;gap:.12rem;color:var(--muted);font-size:.88rem;line-height:1.35}
.date{margin-top:1.1rem;color:var(--muted);font-size:.9rem}
.thanks{background:var(--navy);color:#fff;align-items:center;justify-content:center;text-align:center}
.thanks h2{color:#fff;font-size:3rem}
.thanks p{color:#d5dee6;font-size:1.05rem}
.thanks .fine{color:#8aa0b5;font-size:.9rem}
.thanks footer{display:none}
@media print{
  body{overflow:auto;height:auto}
  .slide{display:flex !important;height:auto;min-height:100vh;break-after:page}
  .top-bar{position:absolute}
}
"""

JS = r"""
const slides=[...document.querySelectorAll(".slide")];
let n=Math.max(0, Math.min(slides.length-1, +(new URLSearchParams(location.search).get("n")||0)));
function show(i){ n=i; slides.forEach((s,k)=>s.classList.toggle("on", k===i)); }
document.addEventListener("keydown", (e)=>{
  if(["ArrowRight","PageDown"," "].includes(e.key)) show(Math.min(slides.length-1, n+1));
  if(["ArrowLeft","PageUp","Backspace"].includes(e.key)) show(Math.max(0, n-1));
  if(e.key==="Home") show(0);
  if(e.key==="End") show(slides.length-1);
});
show(n);
const COLORS=["#0f2b46","#1a4a6e","#009688","#c9a227","#5b6eae","#2e6da4","#8a9bae","#1f7a6f"];
document.querySelectorAll("canvas[data-chart]").forEach((el)=>{
  const spec=JSON.parse(el.dataset.chart);
  const opts={responsive:true,maintainAspectRatio:false,animation:false,plugins:{legend:{position:spec.legend||"bottom",labels:{boxWidth:12,font:{size:12}}}}};
  if(spec.kind==="bar"){
    opts.indexAxis="y";
    opts.scales={x:{stacked:true,ticks:{callback:(v)=>"\u00a3"+(v/1e6).toFixed(2)+"M"}},y:{stacked:true,display:false}};
    new Chart(el,{type:"bar",data:{labels:[" "],datasets:spec.series.map((s,i)=>({label:s.name,data:[s.value],backgroundColor:COLORS[i%COLORS.length]}))},options:opts});
  } else {
    opts.plugins.legend.position="right";
    new Chart(el,{type:"doughnut",data:{labels:spec.labels,datasets:[{data:spec.values,backgroundColor:COLORS}]},options:opts});
  }
});
"""


def slide_heads(slide) -> tuple[str, str]:
    found = []
    for shape in slide.shapes:
        if not shape.has_text_frame or shape.top.inches > 1.25 or shape.width.inches < 6:
            continue
        text = shape.text_frame.text.strip().split("\n")[0].strip()
        if text:
            found.append((shape.top.inches, text))
    found.sort()
    title = found[0][1] if found else ""
    sub = found[1][1] if len(found) > 1 else ""
    return title, sub


def combine_sections(first: str, second: str) -> str:
    def piece(html, start, end):
        a = html.find(start)
        b = html.find(end, a if a >= 0 else 0)
        if a < 0 or b < 0:
            return ""
        return html[a:b]

    head = piece(first, "<header", '<div class="main">')
    main_a = piece(first, '<div class="main">', "<footer>").replace('<div class="main">', '<div class="joined">', 1)
    head_b = piece(second, "<header", '<div class="main">')
    main_b = piece(second, '<div class="main">', "<footer>").replace('<div class="main">', '<div class="joined">', 1)
    foot = piece(first, "<footer>", "</section>") + "</section>"
    head_b = head_b.replace("<header", '<header class="split-next"', 1)
    return (
        '<section class="slide"><div class="rule"></div>'
        + head
        + '<div class="main scroll-page">'
        + main_a
        + head_b
        + main_b
        + "</div>"
        + foot
    )


def should_join(title: str, sub: str, title2: str, sub2: str) -> bool:
    if "(1/2)" in title and "(2/2)" in title2:
        return True
    if "CRD" in sub and "CRD" in sub2 and "1/2" in sub and "2/2" in sub2:
        return True
    return False


def write_html(src: Path = SRC, out: Path = OUT) -> None:
    prs = Presentation(str(src))
    slides = list(prs.slides)
    sections = []
    i = 0
    while i < len(slides):
        title, sub = slide_heads(slides[i])
        title2, sub2 = slide_heads(slides[i + 1]) if i + 1 < len(slides) else ("", "")
        if i + 1 < len(slides) and should_join(title, sub, title2, sub2):
            first = render(i + 1, slides[i], len(slides))
            second = render(i + 2, slides[i + 1], len(slides))
            sections.append(combine_sections(first, second))
            i += 2
        else:
            sections.append(render(i + 1, slides[i], len(slides)))
            i += 1
    total = len(sections)
    numbered = []
    for n, section in enumerate(sections, 1):
        numbered.append(re.sub(r"\d+ / \d+", f"{n} / {total}", section, count=1))
    sections = numbered
    doc = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"/>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>"
        "<title>Asymchem UK · Sandwich Pilot Plant – Capital projects briefing, 12 October 2026</title>"
        "<script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js\"></script>"
        f"<style>{CSS}</style></head><body><div class=\"top-bar\"></div>{''.join(sections)}"
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
