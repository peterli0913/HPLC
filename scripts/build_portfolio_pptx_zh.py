#!/usr/bin/env python3
"""Build an editable Chinese 16:9 PPT from the 0907 portfolio briefing.

Text, tables, charts and Gantt bars are native PowerPoint objects.
HIPO owner equipment follows Equipment List Costs for scoping 0911
(phased purchase). Cost-plan building-works lines are unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from c1_oeb5_cost import (  # noqa: E402
    AIRLOCK,
    C1_OOM,
    C1_COST_I18N_ZH,
    EQUIP_SUB as C1_EQUIP_SUB,
    FLEX_ISO,
    HVAC_GROUP,
    HVAC_UPG,
    ISO_2F,
    ISO_FIXED,
    ISO_GF,
    PROJECT_CONT as C1_CONT,
)
from ext_feasibility_cost import (  # noqa: E402
    BASE_LINE_ITEMS,
    BASE_RISK,
    BASE_SUBTOTAL,
    BASE_TOTAL,
    CONFIDENCE_CONTINGENCY,
    EXT_COST_I18N_ZH,
    EXT_OOM,
    GENERAL_RISK_TOTAL,
    OTHER_CONTINGENCY,
    OTHER_LINE_ITEMS,
    OTHER_SUBTOTAL,
    OTHER_TOTAL,
    RISK_REGISTER,
)
from hipo_demand import DEMAND_ROWS  # noqa: E402
from hipo_lab_cost import (  # noqa: E402
    ACCURACY_LOWER,
    ACCURACY_UPPER,
    BUILDING_WORKS,
    CLIENT_EQUIP,
    EQUIP_0911_ARD_P1,
    EQUIP_0911_ARD_PURCH,
    EQUIP_0911_CRD_P1,
    EQUIP_0911_CRD_PURCH,
    EQUIP_0911_ISO_P1,
    EQUIP_0911_ISO_PURCH,
    EQUIP_0911_PHASE1,
    EQUIP_0911_PHASE2,
    EQUIP_0911_PURCHASE,
    EQUIP_ITEMS_0911,
    FACILITATING,
    FFE,
    FINISHES,
    HIPO_COST_I18N_ZH,
    HIPO_TOTAL,
    INFLATION,
    OHP,
    PRELIMS,
    PROF_SERVICES,
    RISK_ALLOWANCE,
    SERVICES,
    SUPERSTRUCTURE,
    TOTAL_BUILDING_WORKS,
)
from pptx_gantt import GANTT_SPECS, draw_gantt  # noqa: E402
from hplc_capex_v2 import (  # noqa: E402
    CDM,
    CIVIL,
    COMMISSION,
    DETAIL_DESIGN,
    DIRECT_TOTAL,
    ELEC,
    FEED,
    GEN_TOTAL,
    HPLC_COST_I18N_ZH,
    HPLC_OOM,
    HPLC_SKID,
    HVAC,
    INDIRECT_TOTAL,
    INFRA_PRICE_RISK,
    INFRA_TOTAL,
    LYO,
    MAIN_EQUIP_TOTAL,
    MAIN_PRICE_RISK,
    MECH,
    PROJECT_CONT as HPLC_CONT,
    PUMPS,
    TANKS,
)

ROOT = Path("/workspace")
OUT = ROOT / "汇报/UK-PDF-Portfolio/UK_PDF_Portfolio_Briefing_2026-09-07.pptx"
OUT_V2 = ROOT / "汇报/UK-PDF-Portfolio/UK_PDF_Portfolio_Briefing_2026-09-07-v2.pptx"
OUT_V3 = ROOT / "汇报/UK-PDF-Portfolio/UK_PDF_Portfolio_Briefing_2026-09-07-v3.pptx"

# Cost-plan building works / risk / inflation stay on the 260806 plan.
# Owner equipment uses the 0911 phased list (to-purchase), not the cost-plan
# client-equipment line (£1,975,045) or the 5 Aug list (£1,957,045).
HIPO_OTHER = HIPO_TOTAL - CLIENT_EQUIP  # 2,586,999
HIPO_EQUIP = EQUIP_0911_PURCHASE  # 1,713,045
HIPO_PHASE1 = EQUIP_0911_PHASE1  # 963,445
HIPO_PHASE2 = EQUIP_0911_PHASE2  # 749,600
HIPO_PROJECT = HIPO_OTHER + HIPO_EQUIP  # 4,300,044
EQUIP_ITEMS = EQUIP_ITEMS_0911

NAVY = RGBColor(0x0F, 0x2B, 0x46)
TEAL = RGBColor(0x00, 0x96, 0x88)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
EXT_C = RGBColor(0x1A, 0x4A, 0x6E)
HPLC_C = RGBColor(0x5B, 0x6E, 0xAE)
C1_C = RGBColor(0x8B, 0x69, 0x14)
HIPO_C = RGBColor(0x1F, 0x7A, 0x6F)
TEXT = RGBColor(0x2C, 0x3E, 0x50)
MUTED = RGBColor(0x5A, 0x6A, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF4, 0xF6, 0xF8)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xE2, 0xE8, 0xEE)
WARN = RGBColor(0xB4, 0x3A, 0x2A)
ROW_ALT = RGBColor(0xF6, 0xF8, 0xFA)
FONT = "微软雅黑"

SW = 13.333
SH = 7.5
ML = 0.42
MR = 0.42
CW = SW - ML - MR
FOOTER = "凯莱英 UK · Sandwich PDF 资本项目"

STATUS_ZH = {
    "lost": "已丢失",
    "live2nd": "在谈 · 第二供",
    "liveSw": "在谈 · 转至 SW",
    "listed": "已列需求",
    "enquiry": "询盘",
}
STATUS_COLOR = {
    "lost": WARN,
    "live2nd": EXT_C,
    "liveSw": HIPO_C,
    "listed": TEAL,
    "enquiry": MUTED,
}

CHART_COLORS = [
    RGBColor(0x0F, 0x2B, 0x46),
    RGBColor(0x1A, 0x4A, 0x6E),
    RGBColor(0x00, 0x96, 0x88),
    RGBColor(0xC9, 0xA2, 0x27),
    RGBColor(0x5B, 0x6E, 0xAE),
    RGBColor(0x2E, 0x6D, 0xA4),
    RGBColor(0x8A, 0x9B, 0xAE),
]


def gbp(n: int) -> str:
    return f"£{n:,}"


def gbp_m(n: float | int, digits: int = 2) -> str:
    return f"£{n / 1e6:.{digits}f}M"


def rgb_hex(c: RGBColor) -> str:
    return f"{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}"


def set_run_font(run, size: int, bold: bool = False, color: RGBColor = TEXT, name: str = FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", name)


def add_run(p, text, size, bold=False, color=TEXT):
    r = p.add_run()
    r.text = text
    set_run_font(r, size, bold, color)
    return r


def set_anchor(tf, anchor="t"):
    bodyPr = tf._txBody.find(qn("a:bodyPr"))
    if bodyPr is not None:
        bodyPr.set("anchor", anchor)


def no_line(shape):
    shape.line.fill.background()


def add_rect(slide, l, t, w, h, fill, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    no_line(s)
    return s


def add_round(slide, l, t, w, h, fill, adj=0.08):
    s = add_rect(slide, l, t, w, h, fill, MSO_SHAPE.ROUNDED_RECTANGLE)
    try:
        s.adjustments[0] = adj
    except Exception:
        pass
    return s


def shape_text(shape, lines, size=14, bold=False, color=TEXT, align=PP_ALIGN.LEFT, anchor="t", after=6):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.clear()
    set_anchor(tf, anchor)
    for i, item in enumerate(lines):
        if isinstance(item, tuple):
            txt, sz, b, col = item
        else:
            txt, sz, b, col = item, size, bold, color
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(after)
        add_run(p, txt, sz, b, col)
    return tf


def add_tb(slide, l, t, w, h, text, size=14, bold=False, color=TEXT, align=PP_ALIGN.LEFT, anchor="t"):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    set_anchor(tf, anchor)
    p = tf.paragraphs[0]
    p.alignment = align
    add_run(p, text, size, bold, color)
    return box


def add_tb_multi(slide, l, t, w, h, items, align=PP_ALIGN.LEFT, anchor="t", after=8):
    """items: list of (text, size, bold, color)."""
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    set_anchor(tf, anchor)
    for i, (txt, sz, b, col) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(after)
        add_run(p, txt, sz, b, col)
    return box


def new_slide(prs, page: int, total: list[int] | None = None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(s, 0, 0, SW, SH, BG)
    add_rect(s, 0, 0, 5.4, 0.07, NAVY)
    add_rect(s, 5.4, 0, 4.4, 0.07, TEAL)
    add_rect(s, 9.8, 0, 3.533, 0.07, GOLD)
    add_rect(s, 0, 7.18, SW, 0.32, WHITE)
    add_rect(s, 0, 7.18, SW, 0.012, LINE)
    add_tb(s, ML, 7.20, 9.2, 0.26, FOOTER, 11, False, MUTED)
    n = total[0] if total else page
    add_tb(s, SW - MR - 1.6, 7.20, 1.6, 0.26, f"{page} / {n}", 11, False, MUTED, PP_ALIGN.RIGHT)
    return s


def title_block(slide, title, subtitle="", accent=NAVY):
    add_rect(slide, ML, 0.18, 0.09, 0.78 if subtitle else 0.50, accent)
    add_tb(slide, ML + 0.20, 0.16, CW - 0.2, 0.48, title, 26, True, NAVY)
    if subtitle:
        add_tb(slide, ML + 0.20, 0.64, CW - 0.2, 0.34, subtitle, 13, False, MUTED)
        return 1.08
    return 0.78


def kpi_row(slide, items, y, h=1.05, accent=TEAL):
    n = len(items)
    gap = 0.16
    w = (CW - gap * (n - 1)) / n
    for i, (val, lbl) in enumerate(items):
        x = ML + i * (w + gap)
        card = add_round(slide, x, y, w, h, WHITE, 0.10)
        card.shadow.inherit = False
        add_rect(slide, x, y, 0.09, h, accent)
        add_tb(slide, x + 0.20, y + max(0.14, h * 0.18), w - 0.30, 0.50, val, 20 if h < 1.4 else 22, True, NAVY)
        add_tb(slide, x + 0.20, y + max(0.62, h * 0.52), w - 0.30, min(0.80, h * 0.40), lbl, 12 if h < 1.4 else 13, False, MUTED)
    return y + h


def bullets(slide, lines, l, t, w, h, size=15, color=TEXT, after=10):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(after)
        add_run(p, "•  " + line, size, False, color)
    return box


def set_cell_fill(cell, color: RGBColor):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("a:solidFill")):
        tcPr.remove(old)
    solid = etree.SubElement(tcPr, qn("a:solidFill"))
    srgb = etree.SubElement(solid, qn("a:srgbClr"))
    srgb.set("val", rgb_hex(color))


def set_cell_border(cell, color_hex="E2E8EE"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    ln = etree.SubElement(tcPr, qn("a:lnB"))
    ln.set("w", "6350")
    sf = etree.SubElement(ln, qn("a:solidFill"))
    c = etree.SubElement(sf, qn("a:srgbClr"))
    c.set("val", color_hex)


def fill_cell(cell, text, size=12, bold=False, color=TEXT, fill=None, align="left", vcenter=True):
    cell.text = ""
    tf = cell.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    if vcenter:
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}[align]
    add_run(p, text, size, bold, color)
    if fill is not None:
        set_cell_fill(cell, fill)
    set_cell_border(cell)


def add_table(slide, data, l, t, w, h, col_w=None, sizes=None, aligns=None, header=True, font=12):
    rows, cols = len(data), len(data[0])
    tbl_shape = slide.shapes.add_table(rows, cols, Inches(l), Inches(t), Inches(w), Inches(h))
    table = tbl_shape.table
    table.first_row = header
    if col_w:
        for i, cw in enumerate(col_w):
            table.columns[i].width = Inches(cw)
    for r, row in enumerate(data):
        is_h = header and r == 0
        is_sec = (not is_h) and len(row) >= 1 and str(row[0]).startswith("§")
        for c, val in enumerate(row):
            txt = str(val)
            if is_sec and txt.startswith("§"):
                txt = txt[1:]
            sz = (sizes[c] if sizes else font)
            if is_h:
                fill_cell(cell := table.cell(r, c), txt, sz, True, WHITE, NAVY, aligns[c] if aligns else ("center" if c else "left"))
            elif is_sec:
                fill_cell(table.cell(r, c), txt, sz, True, WHITE, EXT_C if c == 0 or True else EXT_C, aligns[c] if aligns else "left")
                fill_cell(table.cell(r, c), txt, sz, True, WHITE, RGBColor(0x1A, 0x3A, 0x55), aligns[c] if aligns else ("right" if c == cols - 1 else "left"))
            else:
                bg = ROW_ALT if r % 2 == 0 else WHITE
                al = aligns[c] if aligns else ("right" if c == cols - 1 else "left")
                fill_cell(table.cell(r, c), txt, sz, False, TEXT, bg, al)
    return table


def add_cost_table(slide, data, l, t, w, h, font=13):
    """2-col 项目/金额; rows starting with '=' are section totals, '-' subtotals."""
    rows, cols = len(data), 2
    table = slide.shapes.add_table(rows, cols, Inches(l), Inches(t), Inches(w), Inches(h)).table
    table.columns[0].width = Inches(w * 0.72)
    table.columns[1].width = Inches(w * 0.28)
    for r, (name, amt, kind) in enumerate(data):
        if kind == "head":
            f0, f1, c0, c1, b = NAVY, NAVY, WHITE, WHITE, True
        elif kind == "sec":
            f0, f1, c0, c1, b = RGBColor(0x1A, 0x3A, 0x55), RGBColor(0x1A, 0x3A, 0x55), WHITE, WHITE, True
        elif kind == "sub":
            f0, f1, c0, c1, b = RGBColor(0xE8, 0xEE, 0xF4), RGBColor(0xE8, 0xEE, 0xF4), NAVY, NAVY, True
        elif kind == "leaf":
            f0 = ROW_ALT if r % 2 == 0 else WHITE
            f1, c0, c1, b = f0, MUTED, MUTED, False
        else:
            f0 = ROW_ALT if r % 2 == 0 else WHITE
            f1, c0, c1, b = f0, TEXT, TEXT, False
        fill_cell(table.cell(r, 0), name, font if kind != "leaf" else font - 1, b, c0, f0, "left")
        fill_cell(table.cell(r, 1), amt, font if kind != "leaf" else font - 1, b, c1, f1, "right")
    return table


def color_series(chart, colors):
    for i, series in enumerate(chart.series):
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = colors[i % len(colors)]


def color_points(chart, colors):
    series = chart.series[0]
    for i, pt in enumerate(series.points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = colors[i % len(colors)]


def add_stack_bar(slide, l, t, w, h, labels, series, title=""):
    data = CategoryChartData()
    data.categories = [title or " "]
    for name, val in series:
        data.add_series(name, (val,))
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_STACKED, Inches(l), Inches(t), Inches(w), Inches(h), data
    ).chart
    chart.has_legend = True
    chart.legend.include_in_layout = False
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    color_series(chart, CHART_COLORS)
    return chart


def add_doughnut(slide, l, t, w, h, items):
    data = CategoryChartData()
    data.categories = [n for n, _ in items]
    data.add_series("£", tuple(v for _, v in items))
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT, Inches(l), Inches(t), Inches(w), Inches(h), data
    ).chart
    chart.has_legend = True
    chart.legend.include_in_layout = False
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    color_points(chart, CHART_COLORS)
    return chart


def _decision(prs, n, total, title, items, accent):
    s = new_slide(prs, n, total)
    y = title_block(s, title, "", accent)
    decision_cards(s, items, y + 0.15, accent)
    return s


def decision_cards(slide, items, y, accent):
    h = (6.95 - y - 0.14 * (len(items) - 1)) / len(items)
    for i, text in enumerate(items):
        top = y + i * (h + 0.12)
        add_round(slide, ML, top, CW, h, WHITE, 0.06)
        add_rect(slide, ML, top, 0.12, h, accent)
        badge = add_round(slide, ML + 0.32, top + (h - 0.56) / 2, 0.78, 0.56, accent, 0.16)
        shape_text(badge, [(f"{i + 1:02d}", 20, True, WHITE)], align=PP_ALIGN.CENTER, anchor="ctr", after=0)
        add_tb(slide, ML + 1.30, top + 0.20, CW - 1.70, h - 0.40, text, 20, False, TEXT, anchor="ctr")


# --------------------------------------------------------------------------- slides
def s_cover(prs, n, total):
    s = new_slide(prs, n, total)
    add_rect(s, 0, 0.07, 0.22, 7.11, NAVY)
    tag = add_round(s, 0.55, 1.15, 2.55, 0.38, NAVY, 0.18)
    shape_text(tag, [("内部汇报 · 整体汇报", 12, True, WHITE)], align=PP_ALIGN.CENTER, anchor="ctr", after=0)
    add_tb(s, 0.55, 1.70, 12.2, 0.70, "凯莱英 UK · Sandwich PDF", 34, True, NAVY)
    add_tb(s, 0.55, 2.40, 12.2, 0.40, "资本项目汇报", 20, False, MUTED)
    add_rect(s, 0.55, 2.92, 1.6, 0.06, GOLD)
    cards = [
        ("HPLC + 冻干", "£5.33M", "2027-12 / 2028-06", HPLC_C),
        ("C1 模块 OEB5", "£2.48M", "2027-10 安装确认", C1_C),
        ("OEB5 高活实验室", gbp_m(HIPO_PROJECT), "计划 2027-11 交付", HIPO_C),
        ("B902 东侧扩建", "£78.1M", "2030-05 竣工", EXT_C),
    ]
    gap, w, h = 0.18, 2.95, 3.05
    for i, (name, val, when, col) in enumerate(cards):
        x = 0.55 + i * (w + gap)
        add_round(s, x, 3.15, w, h, WHITE, 0.08)
        add_rect(s, x, 3.15, w, 0.10, col)
        add_tb(s, x + 0.18, 3.45, w - 0.36, 0.70, name, 16, True, NAVY)
        add_tb(s, x + 0.18, 4.30, w - 0.36, 0.70, val, 28, True, col)
        add_tb(s, x + 0.18, 5.15, w - 0.36, 0.70, when, 14, False, MUTED)
    add_tb(s, 0.55, 6.40, 12.2, 0.35, "四条独立工作流  ·  2026年9月11日", 14, False, MUTED)
    return s


def s_overview(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "项目概览", "四条独立工作流 · 可行性 / 概念 / 内部估算量级")
    rows = [
        ["子项目", "范围", "投资（估算量级）", "关键节点"],
        ["HPLC + 冻干", "既有 PDF footprint 改造", "£5.33M", "2027-12 HPLC / 2028-06 冻干"],
        ["C1 模块 OEB5 升级", "现有 C1 模块 OEB5 日常运行能力", "£2.48M", "2027-10 安装确认"],
        ["OEB5 高活实验室", "既有 G-128 套间改造；GIFA 215 m²；4+1 台隔离器", gbp_m(HIPO_PROJECT), "计划 2027-11 交付"],
        ["B902 东侧扩建", "新建四层+夹层，反应/加氢/过滤干燥", "£78.1M", "2030-05 竣工"],
    ]
    add_table(s, rows, ML, 1.15, CW, 3.35, col_w=[2.6, 4.7, 2.5, 2.633], font=14, aligns=["left", "left", "center", "left"])
    inb = 5.33 + 2.48 + HIPO_PROJECT / 1e6
    notes = [
        (
            ML,
            4.65,
            CW,
            0.95,
            WARN,
            "交付关联：厂房内改造（制备 HPLC + 冻干）与 C1 模块升级须同步完成，方能为制备 HPLC 操作提供 OEB5 能力；制备 HPLC 单元驱动整体交付时间线。",
        ),
        (
            ML,
            5.70,
            CW,
            0.70,
            TEAL,
            "产能依据：欧洲商务已整理面向 Sandwich 的高活需求与机会（2027–2030）。已列名 AZ、Genmab、BioNTech、NCC，另有 Roche、信达、宜联询盘海外高活产能。",
        ),
        (
            ML,
            6.48,
            CW,
            0.55,
            MUTED,
            f"厂房内三条线合计（改造 £5.33M + C1 £2.48M + 高活实验室 {gbp_m(HIPO_PROJECT)}）约 {gbp_m(inb * 1e6)}，不含 902 东侧扩建。各线口径不同：扩建与改造为可行性量级，C1 为内部估算，高活实验室为概念阶段成本计划。",
        ),
    ]
    for x, y, w, h, col, txt in notes:
        add_round(s, x, y, w, h, WHITE, 0.08)
        add_rect(s, x, y, 0.09, h, col)
        add_tb(s, x + 0.22, y + 0.08, w - 0.34, h - 0.12, txt, 13, False, TEXT)
    return s


def s_demand_why(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活需求：客户在问产能", "欧洲商务整理 · Sandwich 高活项目需求与机会（2027–2030）")
    kpis = [
        ("4 家列名客户", "AZ · Genmab · BioNTech · NCC"),
        ("3 家询盘", "Roche · 信达 · 宜联（无量）"),
        ("2 条已丢失", "AZ Exatecan + linker GMP"),
        ("明确问扩建", "AZ、Genmab 已表示关注 SW 计划"),
    ]
    y = kpi_row(s, kpis, 1.15, 1.12, HIPO_C)
    bullets(
        s,
        [
            "欧洲商务已列出面向 Sandwich 的高活需求与机会。",
            "已列名客户为 AZ、Genmab、BioNTech、NCC；另有 Roche、信达、宜联询问高活海外产能。",
            "AZ、Genmab 明确希望了解 SW 高活扩建计划。部分项目的诉求是欧美第二供，用于对冲供应风险。",
            "BioNTech 希望把现由中国支持的早期项目延伸到 Sandwich，并列明能力要求：与 TJ4 相当的高活密闭（1 ng/m³）、实验室至公斤级、适用的高活色谱、高活冻干、与常规分析分开的高活分析。",
        ],
        ML,
        y + 0.14,
        CW,
        2.00,
        15,
        after=7,
    )
    maps = [
        ("密闭与高活分析", "BioNTech 要求与 TJ4 相当的密闭（1 ng/m³），以及与常规分析分开的高活分析。对应 G-128 高活实验室。", HIPO_C),
        ("高活色谱与冻干", "同一客户列明 fit-for-purpose 高活色谱与高活冻干。对应厂房内 HPLC + 冻干改造。", HPLC_C),
        ("第二供窗口", "Genmab 计划 2026 年底报 BLA，天津已进入商业批次，正在评估欧美第二供。AZ 多个 API 亦以第二供为前提。", EXT_C),
    ]
    gap, w, h = 0.16, (CW - 0.32) / 3, 1.70
    top = 5.28
    for i, (ti, body, col) in enumerate(maps):
        x = ML + i * (w + gap)
        add_round(s, x, top, w, h, WHITE, 0.08)
        add_rect(s, x, top, w, 0.08, col)
        add_tb(s, x + 0.16, top + 0.16, w - 0.32, 0.34, ti, 15, True, NAVY)
        add_tb(s, x + 0.16, top + 0.50, w - 0.32, 0.95, body, 12, False, TEXT)
    return s


def s_demand_table(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活需求 · 客户与项目")
    header = ["客户", "项目", "状态", "2027–2030 量", "商务产值口径", "要点"]
    data = [header]
    for r in DEMAND_ROWS:
        data.append([r["customer"], r["project_zh"], STATUS_ZH[r["status"]], r["qty"], r["value"], r["note_zh"]])
    rows, cols = len(data), 6
    table = slide_table = s.shapes.add_table(rows, cols, Inches(ML), Inches(1.05), Inches(CW), Inches(5.95)).table
    widths = [1.55, 2.85, 1.45, 1.25, 1.25, 4.083]
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(w)
    aligns = ["left", "left", "center", "center", "center", "left"]
    for r, row in enumerate(data):
        for c, val in enumerate(row):
            if r == 0:
                fill_cell(table.cell(r, c), val, 12, True, WHITE, NAVY, aligns[c])
            else:
                st = DEMAND_ROWS[r - 1]["status"]
                color = STATUS_COLOR[st] if c == 2 else TEXT
                bold = c == 2
                bg = ROW_ALT if r % 2 == 0 else WHITE
                fill_cell(table.cell(r, c), val, 11, bold, color, bg, aligns[c])
    return s


def s_section(prs, n, total, tag, title, sub, kpis, accent):
    s = new_slide(prs, n, total)
    add_round(s, ML, 0.28, CW, 2.90, WHITE, 0.06)
    add_rect(s, ML, 0.28, 0.14, 2.90, accent)
    badge = add_round(s, ML + 0.40, 0.55, 2.15, 0.40, accent, 0.18)
    shape_text(badge, [(tag, 13, True, WHITE)], align=PP_ALIGN.CENTER, anchor="ctr", after=0)
    add_tb(s, ML + 0.40, 1.15, CW - 0.70, 0.85, title, 32, True, NAVY)
    add_tb(s, ML + 0.40, 2.10, CW - 0.70, 0.50, sub, 16, False, MUTED)
    add_rect(s, ML + 0.40, 2.75, 1.8, 0.07, GOLD)
    kpi_row(s, kpis, 3.40, 3.50, accent)
    return s


def s_exec(prs, n, total, title, sub, kpis, lines, accent):
    s = new_slide(prs, n, total)
    title_block(s, title, sub, accent)
    y = kpi_row(s, kpis, 1.15, 1.12, accent)
    bullets(s, lines, ML + 0.05, y + 0.22, CW - 0.10, 4.55, 16, after=11)
    return s


def s_scope_cards(prs, n, total, title, sub, cards, accent, note=""):
    s = new_slide(prs, n, total)
    y0 = title_block(s, title, sub, accent)
    note_h = 0.95 if note else 0
    avail = 7.05 - y0 - 0.12 - note_h
    cols = 2
    rows_n = (len(cards) + 1) // 2
    gap = 0.16
    cw = (CW - gap) / 2
    ch = (avail - gap * (rows_n - 1)) / rows_n
    for i, (ti, items) in enumerate(cards):
        r, c = divmod(i, cols)
        x = ML + c * (cw + gap)
        y = y0 + 0.08 + r * (ch + gap)
        add_round(s, x, y, cw, ch, WHITE, 0.07)
        add_rect(s, x, y, 0.10, ch, accent)
        add_tb(s, x + 0.24, y + 0.12, cw - 0.36, 0.38, ti, 16, True, NAVY)
        bullets(s, items, x + 0.20, y + 0.52, cw - 0.32, ch - 0.62, 13, after=6)
    if note:
        add_round(s, ML, 7.05 - note_h, CW, note_h - 0.04, WHITE, 0.08)
        add_rect(s, ML, 7.05 - note_h, 0.09, note_h - 0.04, GOLD)
        add_tb(s, ML + 0.22, 7.07 - note_h, CW - 0.34, note_h - 0.10, note, 11, False, TEXT)
    return s


def s_ext_cost(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "扩建 · 投资总览", "300291-CM-0001")
    add_round(s, ML, 1.12, CW, 0.52, NAVY, 0.08)
    add_tb(s, ML + 0.22, 1.18, 6.5, 0.40, "项目 OOM 总价", 16, True, WHITE)
    add_tb(s, ML + 7.0, 1.18, 5.2, 0.40, gbp(EXT_OOM), 18, True, WHITE, PP_ALIGN.RIGHT)
    L = EXT_COST_I18N_ZH
    left = [("head", L["secBase"], gbp(BASE_TOTAL))]
    for it in BASE_LINE_ITEMS:
        if it["amount"] <= 0:
            continue
        left.append(("row", L[it["id"]], gbp(it["amount"])))
    left.append(("sub", L["subtotal"], gbp(BASE_SUBTOTAL)))
    left.append(("sub", L["baseRisk"], gbp(BASE_RISK)))
    right = [("head", L["secOther"], gbp(OTHER_TOTAL))]
    for it in OTHER_LINE_ITEMS:
        if it["amount"] <= 0:
            continue
        right.append(("row", L[it["id"]], gbp(it["amount"])))
    right.append(("sub", L["subtotal"], gbp(OTHER_SUBTOTAL)))
    right.append(("sub", L["otherCont"], gbp(OTHER_CONTINGENCY)))
    right.append(("head", L["secGen"], gbp(GENERAL_RISK_TOTAL)))
    right.append(("row", L["confidence"], gbp(CONFIDENCE_CONTINGENCY)))
    right.append(("row", L["riskReg"], gbp(RISK_REGISTER)))
    def pack(kind_rows):
        out = []
        for k, a, b in kind_rows:
            out.append((a, b, {"head": "sec", "sub": "sub"}.get(k, "row")))
        return out
    add_cost_table(s, pack(left), ML, 1.78, 6.10, 5.15, 12)
    add_cost_table(s, pack(right), ML + 6.28, 1.78, 6.153, 5.15, 12)
    return s


def s_ext_charts(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "扩建 · 投资结构", "OOM 构成与直接工程费分项", EXT_C)
    kpi_row(
        s,
        [
            (gbp(EXT_OOM), "OOM 总价"),
            (gbp(BASE_TOTAL), "直接工程费（含 25%）"),
            (gbp(OTHER_TOTAL + GENERAL_RISK_TOTAL), "其他费及可行性风险"),
        ],
        1.15,
        1.05,
        EXT_C,
    )
    add_round(s, ML, 2.38, 6.10, 4.55, WHITE, 0.06)
    add_tb(s, ML + 0.20, 2.46, 5.7, 0.32, "项目 OOM 三板块", 14, True, NAVY, PP_ALIGN.CENTER)
    add_stack_bar(
        s,
        ML + 0.10,
        2.78,
        5.90,
        4.05,
        [],
        [
            (EXT_COST_I18N_ZH["secBase"], BASE_TOTAL),
            (EXT_COST_I18N_ZH["secOther"], OTHER_TOTAL),
            (EXT_COST_I18N_ZH["secGen"], GENERAL_RISK_TOTAL),
        ],
        "项目 OOM",
    )
    add_round(s, ML + 6.28, 2.38, 6.153, 4.55, WHITE, 0.06)
    add_tb(s, ML + 6.48, 2.46, 5.75, 0.32, "直接工程费 — 分项", 14, True, NAVY, PP_ALIGN.CENTER)
    donut = [(EXT_COST_I18N_ZH[it["id"]], it["amount"]) for it in BASE_LINE_ITEMS if it["amount"] > 0]
    add_doughnut(s, ML + 6.38, 2.78, 5.95, 4.05, donut)
    return s


def s_gantt(prs, n, total, title, sub, kpis, spec: dict, accent, note=""):
    s = new_slide(prs, n, total)
    y = title_block(s, title, sub, accent)
    if kpis:
        y = kpi_row(s, kpis, y, 0.88, accent) + 0.08
    else:
        y += 0.04
    note_h = 0.56 if note else 0
    gh = 7.10 - y - note_h
    draw_gantt(s, ML, y, CW, gh - 0.02, spec)
    if note:
        add_tb(s, ML, 7.10 - note_h, CW, note_h - 0.02, note, 12, False, MUTED)
    return s


def s_hplc_cost(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "改造 · 投资总览", "9802-RBP-ZZ-ZZ-CP-X-100001", HPLC_C)
    add_round(s, ML, 1.12, CW, 0.50, NAVY, 0.08)
    add_tb(s, ML + 0.22, 1.18, 6.5, 0.38, "项目总投资估算", 16, True, WHITE)
    add_tb(s, ML + 7.0, 1.18, 5.2, 0.38, gbp(HPLC_OOM), 18, True, WHITE, PP_ALIGN.RIGHT)
    L = HPLC_COST_I18N_ZH
    left = [
        (L["secDirect"], gbp(DIRECT_TOTAL), "sec"),
        (L["sec1"], gbp(MAIN_EQUIP_TOTAL), "row"),
        (L["lyo"], gbp(LYO), "leaf"),
        (L["hplc"], gbp(HPLC_SKID), "leaf"),
        (L["tanks"], gbp(TANKS), "leaf"),
        (L["pumps"], gbp(PUMPS), "leaf"),
        (L["mainPrice"], gbp(MAIN_PRICE_RISK), "leaf"),
        (L["sec2"], gbp(INFRA_TOTAL), "row"),
        (L["civil"], gbp(CIVIL), "leaf"),
        (L["mech"], gbp(MECH), "leaf"),
        (L["elec"], gbp(ELEC), "leaf"),
        (L["hvac"], gbp(HVAC), "leaf"),
        (L["infraPrice"], gbp(INFRA_PRICE_RISK), "leaf"),
    ]
    right = [
        (L["secIndirect"], gbp(INDIRECT_TOTAL), "sec"),
        (L["feed"], gbp(FEED), "row"),
        (L["design"], gbp(DETAIL_DESIGN), "row"),
        (L["cdm"], gbp(CDM), "row"),
        (L["comm"], gbp(COMMISSION), "row"),
        (L["indirectPrice"], gbp(247_500), "row"),
        (L["secGen"], gbp(GEN_TOTAL), "sec"),
        (L["projectCont"], gbp(HPLC_CONT), "row"),
    ]
    add_cost_table(s, left, ML, 1.76, 6.10, 5.18, 12)
    add_cost_table(s, right, ML + 6.28, 1.76, 6.153, 5.18, 13)
    return s


def s_hplc_charts(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "改造 · 投资结构", "直接 / 间接 / 一般风险与预备费", HPLC_C)
    kpi_row(
        s,
        [
            (gbp(HPLC_OOM), "项目总投资"),
            (gbp(DIRECT_TOTAL), "直接费用合计"),
            (gbp(INDIRECT_TOTAL), "间接费用合计"),
            (gbp(GEN_TOTAL), "一般风险与预备费"),
        ],
        1.12,
        0.95,
        HPLC_C,
    )
    add_round(s, ML, 2.20, CW, 0.72, WHITE, 0.08)
    add_tb(s, ML + 0.25, 2.28, 5.8, 0.55, f"1. 主工艺设备    {gbp(MAIN_EQUIP_TOTAL)}", 16, True, NAVY)
    add_tb(s, ML + 6.4, 2.28, 5.8, 0.55, f"2. 基础设施改造    {gbp(INFRA_TOTAL)}", 16, True, NAVY)
    add_round(s, ML, 3.05, 6.10, 3.88, WHITE, 0.06)
    add_tb(s, ML + 0.15, 3.10, 5.8, 0.30, "项目总投资构成", 14, True, NAVY, PP_ALIGN.CENTER)
    add_stack_bar(
        s,
        ML + 0.05,
        3.38,
        6.00,
        3.45,
        [],
        [("直接费用合计", DIRECT_TOTAL), ("间接费用合计", INDIRECT_TOTAL), ("一般风险与预备费", GEN_TOTAL)],
        "项目总投资",
    )
    add_round(s, ML + 6.28, 3.05, 6.153, 3.88, WHITE, 0.06)
    add_tb(s, ML + 6.48, 3.10, 5.75, 0.30, "直接费用 — 分项", 14, True, NAVY, PP_ALIGN.CENTER)
    add_doughnut(
        s,
        ML + 6.38,
        3.38,
        5.95,
        3.45,
        [
            ("冻干机", LYO),
            ("HPLC 撬装", HPLC_SKID),
            ("储罐/容器", TANKS),
            ("泵组", PUMPS),
            ("土建结构", CIVIL),
            ("机械与管道", MECH),
            ("电气仪表", ELEC),
            ("暖通空调", HVAC),
        ],
    )
    return s


def s_c1_cost(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "C1 · 投资总览", "内部估算 · 主设备 + 30% 项目预备费", C1_C)
    add_round(s, ML, 1.12, CW, 0.50, NAVY, 0.08)
    add_tb(s, ML + 0.22, 1.18, 6.5, 0.38, "项目总投资估算", 16, True, WHITE)
    add_tb(s, ML + 7.0, 1.18, 5.2, 0.38, gbp(C1_OOM), 18, True, WHITE, PP_ALIGN.RIGHT)
    L = C1_COST_I18N_ZH
    rows = [
        (L["secEquip"], gbp(C1_EQUIP_SUB), "sec"),
        (L["sec1"], gbp(ISO_FIXED), "row"),
        (L["iso2f"], gbp(ISO_2F), "leaf"),
        (L["isoGF"], gbp(ISO_GF), "leaf"),
        (L["sec2"], gbp(HVAC_GROUP), "row"),
        (L["hvac"], gbp(HVAC_UPG), "leaf"),
        (L["airlock"], gbp(AIRLOCK), "leaf"),
        (L["sec3"], gbp(FLEX_ISO), "row"),
        (L["flex"], gbp(FLEX_ISO), "leaf"),
        (L["secGen"], gbp(C1_CONT), "sec"),
        (L["projectCont"], gbp(C1_CONT), "row"),
    ]
    add_cost_table(s, rows, ML, 1.78, CW, 5.15, 15)
    return s


def s_c1_charts(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "C1 · 投资结构", "主设备小计 / 全项目预备费", C1_C)
    kpi_row(
        s,
        [(gbp(C1_OOM), "项目总投资"), (gbp(C1_EQUIP_SUB), "主设备小计"), (gbp(C1_CONT), "全项目预备费")],
        1.15,
        1.08,
        C1_C,
    )
    add_round(s, ML, 2.42, 6.10, 4.50, WHITE, 0.06)
    add_tb(s, ML + 0.15, 2.50, 5.8, 0.30, "项目总投资构成", 14, True, NAVY, PP_ALIGN.CENTER)
    add_stack_bar(s, ML + 0.05, 2.82, 6.00, 3.95, [], [("主设备小计", C1_EQUIP_SUB), ("全项目预备费", C1_CONT)], "项目总投资")
    add_round(s, ML + 6.28, 2.42, 6.153, 4.50, WHITE, 0.06)
    add_tb(s, ML + 6.48, 2.50, 5.75, 0.30, "主设备 — 分项", 14, True, NAVY, PP_ALIGN.CENTER)
    add_doughnut(s, ML + 6.38, 2.82, 5.95, 3.95, [("1. 固定隔离器", ISO_FIXED), ("2. HVAC 与气闸", HVAC_GROUP), ("3. 柔性隔离", FLEX_ISO)])
    return s


def s_hipo_cost_a(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活实验室 · 投资总览（1/2）", "G-128 Concept Cost Plan · 2026-08-06 · GIFA 215 m²", HIPO_C)
    add_round(s, ML, 1.12, CW, 0.48, NAVY, 0.08)
    add_tb(s, ML + 0.22, 1.16, 6.5, 0.38, "项目投资（含通胀）", 15, True, WHITE)
    add_tb(s, ML + 7.0, 1.16, 5.2, 0.38, gbp(HIPO_PROJECT), 17, True, WHITE, PP_ALIGN.RIGHT)
    L = HIPO_COST_I18N_ZH
    left = [
        (L["secBuild"], gbp(TOTAL_BUILDING_WORKS), "sec"),
        (L["sec0"], gbp(FACILITATING), "row"),
        (L["fw1"], gbp(46_967), "leaf"),
        (L["fw2"], gbp(18_600), "leaf"),
        (L["sec2"], gbp(SUPERSTRUCTURE), "row"),
        (L["ss1"], gbp(42_440), "leaf"),
        (L["ss2"], gbp(26_250), "leaf"),
        (L["sec3"], gbp(FINISHES), "row"),
        (L["fin1"], gbp(9_810), "leaf"),
        (L["fin2"], gbp(23_631), "leaf"),
        (L["fin3"], gbp(25_457), "leaf"),
    ]
    right = [
        (L["sec4"], gbp(FFE), "sec"),
        (L["ffeIso4"], gbp(600_000), "leaf"),
        (L["ffeIso1"], gbp(100_000), "leaf"),
        (L["ffeFume"], gbp(20_000), "leaf"),
        (L["ffeSf6"], gbp(20_000), "leaf"),
        (L["ffeFurn"], gbp(20_000), "leaf"),
        (L["ffeWrite"], gbp(5_000), "leaf"),
        (L["sec5"], gbp(SERVICES), "sec"),
        (L["sv6"], gbp(217_920), "leaf"),
        (L["sv8"], gbp(107_380), "leaf"),
        (L["sv4"], gbp(38_600), "leaf"),
        ("改造与建筑工程小计", gbp(BUILDING_WORKS), "sub"),
    ]
    add_cost_table(s, left, ML, 1.72, 6.10, 5.22, 11)
    add_cost_table(s, right, ML + 6.28, 1.72, 6.153, 5.22, 11)
    return s


def s_hipo_cost_b(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活实验室 · 投资总览（2/2）", "G-128 Concept Cost Plan · 续", HIPO_C)
    L = HIPO_COST_I18N_ZH
    rows = [
        (L["sec9"], gbp(PRELIMS), "sec"),
        (L["pre1"], gbp(10_500), "leaf"),
        (L["pre2"], gbp(21_000), "leaf"),
        (L["pre3"], gbp(331_000), "leaf"),
        (L["sec10"], gbp(OHP), "sec"),
        (L["secProf"], gbp(PROF_SERVICES), "sec"),
        (L["prof"], gbp(PROF_SERVICES), "leaf"),
        (L["secEquip"], gbp(HIPO_EQUIP), "sec"),
        (f"待采购合计（《Equipment List Costs for scoping 0911》）", gbp(HIPO_EQUIP), "row"),
        (f"一期 {gbp(HIPO_PHASE1)}", gbp(HIPO_PHASE1), "leaf"),
        (f"二期及后续 {gbp(HIPO_PHASE2)}", gbp(HIPO_PHASE2), "leaf"),
        (L["secRisk"], gbp(RISK_ALLOWANCE), "sec"),
        (L["risk"], gbp(RISK_ALLOWANCE), "leaf"),
        (L["secInf"], gbp(INFLATION), "sec"),
        (L["inflation"], gbp(INFLATION), "leaf"),
        ("项目投资（含通胀）", gbp(HIPO_PROJECT), "sub"),
    ]
    add_cost_table(s, rows, ML, 1.15, CW, 5.80, 13)
    return s


def s_hipo_charts(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活实验室 · 投资结构", "项目投资构成与建筑工程费分项", HIPO_C)
    kpi_row(
        s,
        [
            (gbp(HIPO_PROJECT), "项目投资（含通胀）"),
            (gbp(TOTAL_BUILDING_WORKS), "建筑工程费合计"),
            (gbp(HIPO_EQUIP), "业主（凯莱英）供货设备"),
            (gbp(RISK_ALLOWANCE), "风险预备费"),
            (f"{gbp(ACCURACY_LOWER)} – {gbp(ACCURACY_UPPER)}", "估算精度区间"),
        ],
        1.12,
        1.00,
        HIPO_C,
    )
    add_round(s, ML, 2.30, 6.10, 4.62, WHITE, 0.06)
    add_tb(s, ML + 0.15, 2.36, 5.8, 0.30, "项目投资构成", 14, True, NAVY, PP_ALIGN.CENTER)
    add_stack_bar(
        s,
        ML + 0.05,
        2.68,
        6.00,
        4.12,
        [],
        [
            ("建筑工程费", TOTAL_BUILDING_WORKS),
            ("专业服务费", PROF_SERVICES),
            ("业主（凯莱英）供货设备", HIPO_EQUIP),
            ("风险预备费", RISK_ALLOWANCE),
            ("通胀", INFLATION),
        ],
        "项目投资",
    )
    add_round(s, ML + 6.28, 2.30, 6.153, 4.62, WHITE, 0.06)
    add_tb(s, ML + 6.48, 2.36, 5.75, 0.30, "建筑工程费 — 分项", 14, True, NAVY, PP_ALIGN.CENTER)
    add_doughnut(
        s,
        ML + 6.38,
        2.68,
        5.95,
        4.12,
        [
            ("1. 改造工程", FACILITATING),
            ("2. 上部结构", SUPERSTRUCTURE),
            ("3. 装饰", FINISHES),
            ("4. 家具与设备", FFE),
            ("5. 机电安装", SERVICES),
            ("6. 临建与承包商设计", PRELIMS),
            ("7. 管理费与利润", OHP),
        ],
    )
    return s


def _ne_zh(ne: str) -> str:
    return {"E": "既有", "N/E": "新购/既有"}.get(ne, "新购")


def _phase_zh(phase) -> str:
    if phase == 1:
        return "一期"
    if phase == 2:
        return "二期"
    return "后续"


def s_c1_isolator(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "C1 · 隔离器选型", "不建议采用国内隔离器方案", C1_C)
    kpi_row(
        s,
        [
            ("须 CE 标志", "英国落地前提"),
            ("+3–4 个月", "事后补认证下限"),
            ("成品高完整性", "本项目所需类型"),
        ],
        1.15,
        1.08,
        C1_C,
    )
    bullets(
        s,
        [
            "英国落地须符合 UK 标准并取得 CE 标志。国内既有方案（天俱时）未按 UK 标准设计，不具备 CE。",
            "事后补做 CE：按已有项目经验至少增加 3–4 个月；若认证要求改设计，周期还会延长。",
            "CE 所需设计与测试文件，国内方案设计时未按该标准准备，补齐工作量大。",
            "本项目需要成品高完整性隔离器。已接触的国内供应商资料难以直接用于本项目；东富龙以设备定制隔离器为主，与本需求不匹配。",
            "推荐路径：按已取得的 Howorth、ILC Dover 预算报价推进供货方案深化。",
        ],
        ML + 0.05,
        2.40,
        CW - 0.10,
        4.55,
        16,
        after=10,
    )
    return s


def s_hipo_phase(prs, n, total):
    s = new_slide(prs, n, total)
    title_block(s, "高活实验室 · 业主设备分阶段", "Equipment List Costs for scoping 0911", HIPO_C)
    kpi_row(
        s,
        [
            (gbp(HIPO_EQUIP), "待采购合计"),
            (gbp(HIPO_PHASE1), "一期"),
            (gbp(HIPO_PHASE2), "二期及后续"),
            (gbp(HIPO_PROJECT), "项目投资（待采购全口径）"),
        ],
        1.12,
        1.00,
        HIPO_C,
    )
    gap, w = 0.16, (CW - 0.16) / 2
    add_round(s, ML, 2.26, w, 2.28, WHITE, 0.08)
    add_rect(s, ML, 2.26, 0.09, 2.28, HIPO_C)
    add_tb(s, ML + 0.22, 2.34, w - 0.36, 0.32, "一期", 15, True, NAVY)
    bullets(
        s,
        [
            "开业配置：分析 HPLC 先购 1 套；质谱及气源纳入一期",
            "隔离器内固体操作仪器原则上纳入一期",
            "同期按一个项目配置反应系统（EasyMax 等先购 1 套）",
        ],
        ML + 0.18,
        2.70,
        w - 0.30,
        1.72,
        13,
        after=6,
    )
    add_round(s, ML + w + gap, 2.26, w, 2.28, WHITE, 0.08)
    add_rect(s, ML + w + gap, 2.26, 0.09, 2.28, GOLD)
    add_tb(s, ML + w + gap + 0.22, 2.34, w - 0.36, 0.32, "二期及后续", 15, True, NAVY)
    bullets(
        s,
        [
            "制备 HPLC、粒度仪、自动滴定仪",
            "结晶筛选与部分反应配套、器皿清洗",
            "软件 £200,000 尚未分阶段，计入后续",
        ],
        ML + w + gap + 0.18,
        2.70,
        w - 0.30,
        1.72,
        13,
        after=6,
    )
    rows = [
        ["分组", "待采购", "一期", "二期及后续"],
        ["ARD / QC", gbp(EQUIP_0911_ARD_PURCH), gbp(EQUIP_0911_ARD_P1), gbp(EQUIP_0911_ARD_PURCH - EQUIP_0911_ARD_P1)],
        ["隔离器内仪器", gbp(EQUIP_0911_ISO_PURCH), gbp(EQUIP_0911_ISO_P1), gbp(EQUIP_0911_ISO_PURCH - EQUIP_0911_ISO_P1)],
        ["CRD", gbp(EQUIP_0911_CRD_PURCH), gbp(EQUIP_0911_CRD_P1), gbp(EQUIP_0911_CRD_PURCH - EQUIP_0911_CRD_P1)],
        ["合计", gbp(HIPO_EQUIP), gbp(HIPO_PHASE1), gbp(HIPO_PHASE2)],
    ]
    add_table(
        s,
        rows,
        ML,
        4.68,
        CW,
        1.72,
        col_w=[3.80, 2.877, 2.877, 2.879],
        font=13,
        aligns=["left", "right", "right", "right"],
    )
    add_tb(
        s,
        ML,
        6.50,
        CW,
        0.58,
        "SFC、GC 先利旧既有仪器。成本计划原文业主设备 £1,975,045、项目投资 £4,562,044；本期按 0911 待采购计入项目投资，未改写成本计划。",
        12,
        False,
        MUTED,
    )
    return s


def s_equip(prs, n0, total, items, title_extra, gantt_unused=None):
    s = new_slide(prs, n0, total)
    title_block(s, "业主（凯莱英）供货并安装设备", title_extra, HIPO_C)
    grp = items[0]["group"] if items else None
    src = [it for it in EQUIP_ITEMS if it["group"] == grp] if grp else items
    g_purch = sum(it.get("purch", 0) or 0 for it in src)
    g_p1 = sum(it.get("phase1", 0) or 0 for it in src)
    add_round(s, ML, 1.10, CW, 0.46, NAVY, 0.08)
    add_tb(s, ML + 0.22, 1.16, 7.4, 0.34, f"本组待采购 {gbp(g_purch)}  ·  一期 {gbp(g_p1)}", 14, True, WHITE)
    add_tb(s, ML + 7.6, 1.16, 4.6, 0.34, f"清单合计 {gbp(HIPO_EQUIP)}", 15, True, WHITE, PP_ALIGN.RIGHT)
    header = ["设备", "位置", "厂家", "新购 / 既有", "阶段", "待采购", "一期"]
    data = [header]
    for it in items:
        purch = it.get("purch", 0) or 0
        p1 = it.get("phase1", 0) or 0
        data.append(
            [
                it["titleZh"],
                it["location"] or "—",
                it["mfr"] or "—",
                _ne_zh(it["ne"]),
                _phase_zh(it.get("phase")),
                gbp(purch) if purch else "—",
                gbp(p1) if p1 else "—",
            ]
        )
    n_rows = len(data)
    max_h = 5.36
    row_h = min(0.38, max_h / n_rows)
    table_h = row_h * n_rows
    font = 11 if n_rows > 14 else 12
    tbl_shape = s.shapes.add_table(n_rows, 7, Inches(ML), Inches(1.68), Inches(CW), Inches(table_h))
    table = tbl_shape.table
    widths = [2.70, 1.85, 2.15, 1.20, 0.95, 1.80, 1.783]
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(w)
    for row in table.rows:
        row.height = Inches(row_h)
    aligns = ["left", "left", "left", "center", "center", "right", "right"]
    for r, row in enumerate(data):
        if r == 0:
            for c, val in enumerate(row):
                fill_cell(table.cell(r, c), val, 11, True, WHITE, NAVY, aligns[c])
            continue
        bg = ROW_ALT if r % 2 == 0 else WHITE
        ne = row[3]
        phase = row[4]
        for c, val in enumerate(row):
            if c == 3:
                col = MUTED if ne == "既有" else HIPO_C
            elif c == 4:
                col = HIPO_C if phase == "一期" else (GOLD if phase == "二期" else MUTED)
            else:
                col = TEXT
            fill_cell(table.cell(r, c), val, font, c in (3, 4, 5, 6), col, bg, aligns[c])
    return s


def s_thanks(prs, n, total):
    s = new_slide(prs, n, total)
    add_rect(s, 0, 0.07, SW, 7.11, NAVY)
    add_rect(s, 0, 0, 5.4, 0.07, TEAL)
    add_rect(s, 5.4, 0, 4.4, 0.07, GOLD)
    add_rect(s, 9.8, 0, 3.533, 0.07, WHITE)
    add_tb(s, 1.0, 2.05, 11.3, 1.10, "谢谢", 54, True, WHITE, PP_ALIGN.CENTER)
    add_rect(s, 5.9, 3.25, 1.5, 0.07, GOLD)
    add_tb(s, 1.0, 3.55, 11.3, 0.45, "Asymchem UK  ·  Sandwich  ·  2026年9月11日", 18, False, RGBColor(0xB8, 0xC5, 0xD6), PP_ALIGN.CENTER)
    add_tb(s, 1.0, 4.10, 11.3, 0.40, "UK PDF 资本项目", 16, False, RGBColor(0x8A, 0x9B, 0xAE), PP_ALIGN.CENTER)
    chips = ["HPLC + 冻干  £5.33M", "C1 OEB5  £2.48M", f"高活实验室  {gbp_m(HIPO_PROJECT)}", "B902 扩建  £78.1M"]
    w = 2.70
    for i, t in enumerate(chips):
        x = 1.15 + i * (w + 0.18)
        chip = add_round(s, x, 5.00, w, 0.70, RGBColor(0x1A, 0x3A, 0x55), 0.18)
        shape_text(chip, [(t, 12, True, WHITE)], align=PP_ALIGN.CENTER, anchor="ctr", after=0)
    add_tb(s, ML, 7.20, 9.2, 0.26, FOOTER, 11, False, RGBColor(0x8A, 0x9B, 0xAE))
    add_tb(s, SW - MR - 1.6, 7.20, 1.6, 0.26, f"{n} / {total[0]}", 11, False, RGBColor(0x8A, 0x9B, 0xAE), PP_ALIGN.RIGHT)
    return s


def build():
    gantts = GANTT_SPECS
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    total = [0]
    pages = []

    def add(fn, *a, **k):
        pages.append((fn, a, k))

    add(s_cover)
    add(s_overview)
    add(s_demand_why)
    add(s_demand_table)

    add(
        s_section,
        "改造",
        "一、厂房内 HPLC + 冻干",
        "RBPC · Project 9802 · P01",
        [("技术可行", "FS P01"), ("£5.33M", "项目总投资估算"), ("2027-12", "HPLC 目标（+3 个月）"), ("2028-06", "冻干目标（+3 个月）")],
        HPLC_C,
    )
    add(
        s_exec,
        "改造 · 执行摘要",
        "9802-RBP-ZZ-ZZ-RP-X-100000",
        [("技术可行", "FS P01"), ("£5.33M", "项目总投资估算"), ("2027-12", "HPLC 目标（+3 个月）"), ("2028-06", "冻干目标（+3 个月）")],
        [
            "范围：制备 HPLC（DAC300/CP300）+ 冻干机（隔离器、除湿、纯蒸汽发生器等）及配套改造。",
            "投资：Total CAPEX Estimate £5.33M（直接+间接+30% 项目预备费）；非最终 Capex。",
            "周期：冻干机长周期驱动；优先冻干后 HPLC。",
            "关联：须与 C1 模块 OEB5 升级同步交付，方可实现制备 HPLC 的 OEB5 运行能力。",
            "需求对应：欧洲商务清单中，BioNTech 将高活色谱与高活冻干列为转至 Sandwich 长期供货的能力要求。",
        ],
        HPLC_C,
    )
    add(
        s_scope_cards,
        "改造 · 范围",
        "",
        [
            ("HPLC", ["DAC300/CP300 泵撬；移动头罐；2000 L 废液罐", "国内汉邦供货", "PG.05 区域安装"]),
            ("冻干机", ["冻干腔、隔离器、双 CIP、除湿、PSG", "东富龙（Tofflon）供货", "气闸/改造约 20 周"]),
        ],
        HPLC_C,
    )
    add(s_hplc_cost)
    add(s_hplc_charts)
    add(
        s_gantt,
        "改造 · 周期",
        "FS §4.4 图 1 · 以 2026-09 启动重新基线（原 6 月口径 +3 个月）",
        [("冻干制造", "8–10 月"), ("HPLC 供货", "~18 周"), ("FEED", "12–14 周"), ("详细设计", "18–20 周")],
        gantts["hplc"],
        HPLC_C,
    )
    add(lambda prs, n, total: _decision(prs, n, total, "改造 · 决策", [
        "是否批准进入 FEED？",
        "是否批准长周期设备早期采购资金？",
    ], HPLC_C))

    add(
        s_section,
        "C1 OEB5",
        "二、C1 模块 OEB5 升级",
        "Sandwich PDF · 内部估算",
        [("OEB5 日常运行", "升级目标"), ("£2.48M", "项目总投资估算"), ("2027-10", "安装与确认目标（+3 个月）")],
        C1_C,
    )
    add(
        s_exec,
        "C1 · 执行摘要",
        "现有 C1 模块 OEB5 日常运行能力",
        [("OEB5 日常运行", "升级目标"), ("£2.48M", "项目总投资估算"), ("2027-10", "安装与确认目标（+3 个月）")],
        [
            "范围：二层物料分装与首层最终包装固定隔离器；HVAC 升级；进出气闸联锁及雾化淋浴；覆盖各单元操作与废物流的定制柔性隔离器。",
            "估算：已取得供应商预算报价 —— ILC Dover 反应釜投料柔性隔离器整包 £115,800（含 R19–R22 投料方案概念设计）；Howorth 单腔分装隔离器 £250,000/台。两者均为 Ex Works 口径，不含包装、运输、安装与调试。",
            "选型：不建议采用国内隔离器方案；英国落地须符合 UK 标准并取得 CE 标志，补认证至少增加 3–4 个月，且本项目需要成品高完整性隔离器。",
            "交付关联：须与厂房内改造（制备 HPLC + 冻干）同步完成，方能为制备 HPLC 操作提供 OEB5 能力。",
            "周期：假设与改造项目一并批准；制备 HPLC 单元驱动 C1 模块升级交付时间线。",
        ],
        C1_C,
    )
    add(
        s_scope_cards,
        "C1 · 范围",
        "",
        [
            ("固定隔离器", ["三层（second floor）：物料分装", "一层（ground floor）：最终包装"]),
            ("HVAC 与气闸", ["HVAC 升级，支持日常 OEB5 运行", "进出气闸联锁升级，含雾化淋浴"]),
            ("柔性隔离", ["多台定制柔性隔离器", "覆盖模块内各单元操作及废物流"]),
            (
                "估价依据（供应商报价）",
                [
                    "柔性隔离器：ILC Dover JS26-11384-0（2026-07-22）整包 £115,800，EXW，不含运输安装；交期约 20 周（图纸批准后）",
                    "固定隔离器：Howorth Q26543（2026-08-11）单腔分装隔离器 £250,000/台；选项 190 RTP £18,000、样机 £17,000",
                ],
            ),
        ],
        C1_C,
    )
    add(s_c1_isolator)
    add(s_c1_cost)
    add(s_c1_charts)
    add(
        s_gantt,
        "C1 · 周期",
        "假设与改造项目一并批准 · 以 2026-09 启动重新基线（原 6 月口径 +3 个月）",
        [("范围定稿", "8 周"), ("详细设计", "12 周"), ("下单/制造", "20 周"), ("安装确认", "8 周")],
        gantts["c1"],
        C1_C,
    )
    add(lambda prs, n, total: _decision(prs, n, total, "C1 · 决策", [
        "是否批准 C1 OEB5 升级与改造项目一并推进？",
        "确认不采用国内隔离器方案，按已取得的 Howorth / ILC Dover 预算报价深化供货。",
    ], C1_C))

    add(
        s_section,
        "高活实验室",
        "三、OEB5 高活实验室（G-128 套间改造）",
        "Concept 阶段 · 成本计划 260806 / 概念进度 260727 / 风险登记册",
        [("概念阶段", "成本计划 / 概念进度 / 风险登记册"), (gbp_m(HIPO_PROJECT), "项目总投资估算"), ("2027-11", "计划交付（概念进度 +6 周）"), ("215 m²", "GIFA（实验室约 182 + 办公区约 33）")],
        HIPO_C,
    )
    add(
        s_exec,
        "高活实验室 · 执行摘要",
        "DPH_G-128 Suite Alterations Concept Cost Plan 260806",
        [
            ("概念阶段", "成本计划 / 概念进度 / 风险登记册"),
            (gbp_m(HIPO_PROJECT), "项目总投资估算"),
            ("2027-11", "计划交付（概念进度 +6 周）"),
            ("215 m²", "GIFA（实验室约 182 + 办公区约 33）"),
        ],
        [
            "范围：既有 G-128 套间改造为实验室与办公区，GIFA 215 m²；隔离器在成本计划中计列 4 台 × £150,000 + 1 台 × £100,000。",
            f"投资：项目投资（含通胀）{gbp(HIPO_PROJECT)}；不含增值税；估算精度区间 £3.74M – £4.99M。",
            f"构成：建筑工程费 £1.95M + 专业服务费 £0.14M + 业主（凯莱英）供货设备 {gbp_m(HIPO_EQUIP)} + 风险预备费 £0.40M + 通胀 £0.10M。",
            "周期：概念进度（草案）自资金批准与推进决定起 262 个工作日，计划交付 2027 年 11 月；隔离器 2027-07-14 到场。",
            "隔离器费用：为基于与供应商沟通的估算，最终取决于项目范围最终确认的密闭等级。",
            f"业主设备按 0911 分阶段清单待采购 {gbp(HIPO_EQUIP)}：一期 {gbp(HIPO_PHASE1)}，二期及后续 {gbp(HIPO_PHASE2)}。成本计划原文设备行 £1,975,045，未改写。",
            "需求对应：欧洲商务已列 AZ、Genmab、BioNTech、NCC 等对 SW 高活能力的需求或询盘；BioNTech 明确要求与 TJ4 相当的密闭及独立高活分析。",
        ],
        HIPO_C,
    )
    add(
        s_scope_cards,
        "高活实验室 · 范围",
        "依据 G-128 概念成本计划分项",
        [
            (
                "范围与面积",
                [
                    "既有 G-128 套间（G128 及 G128A–D）改造；GIFA 215 m²",
                    "实验室区约 182 m²（机电费率基准）+ 办公区约 33 m²（地毯量）",
                    "拆除 G128 与 G128D 之间砌块墙；混凝土墙新开 2 处传递窗洞、2 处门洞",
                ],
            ),
            (
                "隔离器与实验设备",
                [
                    "成本计划：4 台 × £150,000 + 1 台 × £100,000（合计 £700,000）",
                    "费用性质：基于与供应商沟通的估算，最终取决于项目范围最终确认的密闭等级",
                    "通风柜：假设现有可继续使用，仅列 £20,000 维修保养费用；是否新购为进度中待定项",
                    "SF6 检漏测试 £20,000；家具含更衣柜、跨越凳、移动实验台、BIBO 桶",
                ],
            ),
            (
                "土建与装饰改造",
                [
                    "拆除：家具与实验设备清空、地面与吊顶拆除、燃气/风管/电气/烟感/Crowcon 撤除",
                    "新建：墙面衬板 475 m²、新隔断 40 m²；5 樘单开 + 1 樘子母卫生门、2 樘木门、4 樘旧门翻新",
                    "装饰：实验室卷材乙烯地面 173 m²、金属吊顶 173 m²、办公区地毯 33 m²",
                ],
            ),
            (
                "机电、安全与业主供货",
                [
                    "暖通 £217,920：AHU 恢复使用、全套风管与送回风、袋进袋出 HEPA 排风过滤、BMS 升级、系统平衡",
                    "电气 £107,380、消防喷淋 £30,030、门禁/布线/CCTV/火警 £51,345、实验室气体管道 £63,700、雾化淋浴 £35,000",
                    f"业主（凯莱英）供货并安装设备待采购 {gbp(HIPO_EQUIP)}（0911 清单）",
                    f"待采购分项：ARD/QC {gbp(EQUIP_0911_ARD_PURCH)}、隔离器内仪器 {gbp(EQUIP_0911_ISO_PURCH)}、CRD {gbp(EQUIP_0911_CRD_PURCH)}",
                ],
            ),
        ],
        HIPO_C,
        "风险与前提：正在就厂房改造事宜征求 DPML 同意 —— 改造完成后实验室将无法按当前运行状态交还 DPML，该沟通进展由 Clare 跟进。目前 DPML（Paul Bax，2026-08-21）原则上同意 PDF 与 DPH（含 G.128）拟议改造，最终以设计审查为准；可启动两项 Licence for Alteration，范围与图纸随设计深化补充。",
    )
    add(s_hipo_phase)
    add(s_hipo_cost_a)
    add(s_hipo_cost_b)
    add(
        lambda prs, n, total: s_equip(
            prs, n, total, [it for it in EQUIP_ITEMS if it["group"] == "ARD/QC"], "ARD / QC"
        )
    )
    add(
        lambda prs, n, total: s_equip(
            prs, n, total, [it for it in EQUIP_ITEMS if it["group"] == "Isolators"], "隔离器内仪器"
        )
    )
    add(
        lambda prs, n, total: s_equip(
            prs, n, total, [it for it in EQUIP_ITEMS if it["group"] == "CRD"][:12], "CRD（1/2）"
        )
    )
    add(
        lambda prs, n, total: s_equip(
            prs, n, total, [it for it in EQUIP_ITEMS if it["group"] == "CRD"][12:], "CRD（2/2）"
        )
    )
    add(s_hipo_charts)
    add(
        s_gantt,
        "高活实验室 · 周期",
        "Asymchem Concept Programme_260727（DRAFT CONCEPT PROGRAMME）",
        [
            ("262 天", "总工期（工作日）"),
            ("2026-10-13", "资金批准与推进决定"),
            ("2027-07-14", "隔离器到场"),
            ("2027-11-12", "计划交付（含进度风险预留）"),
        ],
        gantts["hipo"],
        HIPO_C,
        "进度说明：各项活动于 2027 年 10 月下旬完成，余量计入末段进度风险预留，交付目标 2027 年 11 月。后续设计推进中部分工作有并行压缩的空间，但取决于最终确认的风险处理方式与可接受的风险水平。",
    )
    add(
        lambda prs, n, total: _decision(
            prs,
            n,
            total,
            "高活实验室 · 决策",
            [
                "是否批准资金与推进决定节点？概念进度以此为起点，262 个工作日加 6 周启动与决策时间，计划交付 2027 年 11 月。",
                "是否按 0911 分阶段清单批准一期业主设备采购？",
                "是否安排 AHU 状况核查与既有通风柜可用性确认？二者为风险登记册中金额最高的两项。",
            ],
            HIPO_C,
        )
    )
    add(
        s_exec,
        "扩建 · 可研结论",
        "四、B902 东侧扩建  ·  Scitech RIBA 1  ·  300291-RE-0001  ·  2026-05-22 Issue A1",
        [("FS 完成", "RIBA 1"), ("£78.1M", "项目 OOM"), ("2030-05", "总控完成")],
        [
            "范围：东侧约 600 m²，四层+设备夹层，10 台反应釜、2500 L 加氢釜、3 套过滤干燥机及公用工程。",
            "方案：Option 1 — 拆除/迁址原加氢厂房；与 902 低层楼面贯通。",
            "进展：FS 完成；计划 2030-05 竣工，沿用设计方总控计划；RIBA 2 概念设计启动延后需在阶段内消化。",
        ],
        EXT_C,
    )
    add(s_ext_cost)
    add(s_thanks)

    total[0] = len(pages)
    for i, (fn, a, k) in enumerate(pages, 1):
        fn(prs, i, total, *a, **k)
    OUT_V3.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT_V3))
    print("wrote", OUT_V3, "slides", len(prs.slides), "bytes", OUT_V3.stat().st_size)


if __name__ == "__main__":
    build()
