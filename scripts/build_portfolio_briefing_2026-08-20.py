#!/usr/bin/env python3
"""Portfolio briefing 2026-08-20.

Four workstreams: B902 extension + HPLC/lyophilizer retrofit + C1 OEB5 upgrade
+ OEB5 HIPO lab (G-128 alterations).

Changes vs the 2026-06-12 pack:
  * the first three programmes are re-baselined from a June 2026 start to a
    September 2026 start (+3 calendar months); scope and cost are untouched;
  * the HIPO lab line is added from the 2026-08 concept-stage documents.
"""

import calendar
import importlib.util
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from ext_feasibility_cost import (
    BASE_TOTAL,
    CHART_I18N_EN as EXT_CHART_I18N_EN,
    CHART_I18N_ZH as EXT_CHART_I18N_ZH,
    EXT_COST_CSS,
    EXT_COST_I18N_EN,
    EXT_COST_I18N_ZH,
    EXT_COST_RENDER_JS,
    EXT_OOM,
    GENERAL_RISK_TOTAL,
    OTHER_TOTAL,
    ext_cost_data_json,
)
from c1_oeb5_cost import (
    C1_COST_I18N_EN,
    C1_COST_I18N_ZH,
    C1_COST_RENDER_JS,
    C1_OOM,
    CHART_I18N_EN as C1_CHART_I18N_EN,
    CHART_I18N_ZH as C1_CHART_I18N_ZH,
    EQUIP_SUB as C1_EQUIP_SUB,
    GANTT_C1,
    PROJECT_CONT as C1_PROJECT_CONT,
    c1_cost_data_json,
)
from hplc_capex_v2 import (
    CAPEX,
    CHART_I18N_EN as HPLC_CHART_I18N_EN,
    CHART_I18N_ZH as HPLC_CHART_I18N_ZH,
    DIRECT_TOTAL,
    HPLC_COST_CSS,
    HPLC_COST_I18N_EN,
    HPLC_COST_I18N_ZH,
    HPLC_COST_RENDER_JS,
    HPLC_OOM,
    GEN_TOTAL,
    INDIRECT_TOTAL,
    INFRA_TOTAL,
    MAIN_EQUIP_TOTAL,
    PROJECT_CONT,
    RISK_ON_BASE,
    hplc_cost_data_json,
)
from hipo_lab_cost import (
    ACCURACY_LOWER,
    ACCURACY_UPPER,
    CHART_I18N_EN as HIPO_CHART_I18N_EN,
    CHART_I18N_ZH as HIPO_CHART_I18N_ZH,
    CLIENT_EQUIP as HIPO_CLIENT_EQUIP,
    GANTT_HIPO,
    HIPO_COST_CSS,
    HIPO_COST_I18N_EN,
    HIPO_COST_I18N_ZH,
    HIPO_COST_RENDER_JS,
    HIPO_TOTAL,
    RISK_ALLOWANCE as HIPO_RISK_ALLOWANCE,
    RISK_HIGH_EST,
    RISK_LOW_EST,
    SHIFT_WEEKS_CLARE,
    TOTAL_BUILDING_WORKS as HIPO_BUILDING_WORKS,
    hipo_cost_data_json,
)

ROOT = Path(__file__).resolve().parent
OUT = Path("/workspace/汇报/UK-PDF-Portfolio/UK_PDF_Portfolio_Briefing_2026-08-20.html")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hplc = _load_module("hplc_brief", ROOT / "build_hplc_lyopho_briefing.py")
ext = _load_module("ext_brief", ROOT / "build_management_briefing.py")

# --------------------------------------------------------------------------
# Re-baseline: the retrofit and C1 programmes assumed a June 2026 start; they
# now start in September 2026, so every not-yet-started bar moves by three
# calendar months. Completed bars ("done") stay where they are.
#
# The extension keeps the Scitech master programme unchanged: group direction
# is to hold the May 2030 completion date, so it is excluded from the shift.
# --------------------------------------------------------------------------
SHIFT_MONTHS = 3
TODAY = "2026-08-21"


def _add_months(date_str: str, months: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    total = d.year * 12 + (d.month - 1) + months
    year, month = divmod(total, 12)
    month += 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return f"{year:04d}-{month:02d}-{day:02d}"


def _shift_label(label: str, months: int) -> str:
    """Shift every YYYY/MM token inside a display label."""

    def repl(m: re.Match) -> str:
        total = int(m.group(1)) * 12 + int(m.group(2)) - 1 + months
        year, month = divmod(total, 12)
        return f"{year:04d}/{month + 1:02d}"

    return re.sub(r"(\d{4})/(\d{2})", repl, label)


def shift_gantt(rows: list, months: int = SHIFT_MONTHS) -> list:
    shifted = []
    for row in rows:
        r = list(row)
        if r[3] == "done":
            shifted.append(r)
            continue
        r[1] = _add_months(r[1], months)
        r[2] = _add_months(r[2], months)
        if len(r) > 6 and isinstance(r[6], str):
            r[6] = _shift_label(r[6], months)
        if len(r) > 7 and isinstance(r[7], str):
            r[7] = _add_months(r[7], months)
        shifted.append(r)
    return shifted


GANTT_EXT_HELD = [list(r) for r in ext.GANTT_JS]  # unshifted — May 2030 held
GANTT_HPLC_SHIFTED = shift_gantt(hplc.GANTT_CALENDAR)
GANTT_C1_SHIFTED = shift_gantt(GANTT_C1)


# --------------------------------------------------------------------------
# HIPO lab: Clare (21 Aug 2026) asked for +6 weeks on the concept programme to
# cover the time to start the work and the funding decision.
# --------------------------------------------------------------------------
HIPO_SHIFT_DAYS = SHIFT_WEEKS_CLARE * 7


def _add_days(date_str: str, days: int) -> str:
    return (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)).strftime(
        "%Y-%m-%d"
    )


def shift_gantt_days(rows: list, days: int) -> list:
    shifted = []
    for row in rows:
        r = list(row)
        r[1] = _add_days(r[1], days)
        r[2] = _add_days(r[2], days)
        shifted.append(r)
    return shifted


def _patch_tooltips(rows: list, patch: dict) -> list:
    out = []
    for row in rows:
        r = list(row)
        if r[0] in patch:
            r[4], r[5] = patch[r[0]]
        out.append(r)
    return out


# Tooltips quoting absolute dates need the same +6 weeks applied to the text.
HIPO_TOOLTIP_PATCH = {
    "hFund": (
        "Asymchem funding approval & decision to proceed — milestone 13 Oct 2026 (0 days).",
        "凯莱英资金批准与推进决定 — 节点 2026-10-13（0 天）。",
    ),
    "hAward": (
        "Contract award milestone 30 Nov 2026; mobilise & contract (20 days).",
        "合同授予节点 2026-11-30；动员与签约（20 天）。",
    ),
    "hIso": (
        "Isolators (120 days): vendor shortlisting & T&Cs, tender & approval, order placed, "
        "drawings approved, manufacture [12 weeks?], delivery to site 14 Jul 2027.",
        "隔离器（120 天）：供应商短名单与商务条款、招标与批准、下单、图纸批准、"
        "制造（12 周？）、2027-07-14 到场。",
    ),
    "hFurn": (
        "Laboratory furniture (100 days): shortlist, tender, order, manufacture, "
        "delivery to site 11 Jun 2027.",
        "实验室家具（100 天）：短名单、招标、下单、制造、2027-06-11 到场。",
    ),
    "hConstr": (
        "Construction from 31 May 2027: strip out / MEP divestment and demolition, walls and "
        "doors, write-up area, 1st fix MEP, decoration, isolator installation, 2nd fix MEP, "
        "ceilings and floors, furniture and equipment.",
        "施工自 2027-05-31 起：拆除与机电撤除、墙体与门、办公区、一次机电、装饰、"
        "隔离器安装、二次机电、吊顶与地面、家具与设备安装。",
    ),
    "hRisk": (
        "Programme risk allowance (15 days); concept programme end 29 Oct 2027. "
        "Delivery target stated as November 2027 to cover the start-up and funding decision.",
        "进度风险预留（15 天）；概念进度落点 2027-10-29。"
        "考虑启动准备与资金决策时间，交付目标按 2027 年 11 月。",
    ),
}

GANTT_HIPO_SHIFTED = _patch_tooltips(
    shift_gantt_days(GANTT_HIPO, HIPO_SHIFT_DAYS), HIPO_TOOLTIP_PATCH
)

# Extension OOM totals from ext_feasibility_cost (CM-0001)

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Asymchem UK — PDF Portfolio Briefing</title>
<!-- build: portfolio-2026-08-20 rev 2026-08-20-hipo-lab-v1 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--navy:#0f2b46;--teal:#009688;--accent:#c9a227;--ext:#1a4a6e;--hplc:#5b6eae;--c1:#8b6914;--hipo:#1f7a6f;--bg:#f4f6f8;--card:#fff;--text:#2c3e50;--muted:#5a6a7a;--warn:#b43a2a}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);overflow:hidden;height:100vh}
.slide{display:none;height:100vh;padding:2rem 2.8rem 3.2rem;flex-direction:column;animation:fade .3s ease}
.slide.active{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
.top-bar{position:fixed;top:0;left:0;right:0;height:6px;background:linear-gradient(90deg,var(--navy),var(--teal),var(--accent));z-index:100}
.lang-switch{position:fixed;top:.9rem;right:1.2rem;z-index:101;display:flex;border-radius:6px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.12);border:1px solid #dde3e8}
.lang-switch button{border:none;padding:.38rem .8rem;font-size:.78rem;cursor:pointer;background:#fff;color:var(--muted);font-weight:600}
.lang-switch button.active{background:var(--navy);color:#fff}
h1{font-size:1.65rem;color:var(--navy);font-weight:700;margin-bottom:.28rem}
h2{font-size:.92rem;color:var(--muted);font-weight:400;margin-bottom:.7rem}
.tag{display:inline-block;background:var(--navy);color:#fff;font-size:.66rem;padding:.16rem .48rem;border-radius:3px}
.tag.ext{background:var(--ext)} .tag.hplc{background:var(--hplc)} .tag.c1{background:var(--c1)} .tag.hipo{background:var(--hipo)}
ul{margin-left:1.1rem;line-height:1.55;font-size:.88rem} li{margin-bottom:.34rem}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem;flex:1;min-height:0}
.card{background:var(--card);border-radius:10px;padding:1rem;border:1px solid #e8ecf0;box-shadow:0 2px 12px rgba(15,43,70,.06)}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin-bottom:.65rem}
.kpi-row.cols3{grid-template-columns:repeat(3,1fr)}
.kpi{background:var(--card);border-radius:10px;padding:.6rem .7rem;border-left:4px solid var(--teal)}
.kpi.ext{border-left-color:var(--ext)} .kpi.hplc{border-left-color:var(--hplc)} .kpi.c1{border-left-color:var(--c1)} .kpi.hipo{border-left-color:var(--hipo)}
.kpi .val{font-size:1.02rem;font-weight:700;color:var(--navy)} .kpi .lbl{font-size:.66rem;color:var(--muted);margin-top:.1rem;line-height:1.28}
table{width:100%;border-collapse:collapse;font-size:.78rem} th,td{padding:.34rem .45rem;border-bottom:1px solid #eef1f4;text-align:left} th{color:var(--navy)}
.footer{position:fixed;bottom:0;left:0;right:0;padding:.4rem 2.8rem;font-size:.68rem;color:var(--muted);background:rgba(255,255,255,.96);border-top:1px solid #e8ecf0;display:flex;justify-content:space-between}
.title-slide{justify-content:center;text-align:center;padding-top:2.5rem} .title-slide h1{font-size:1.8rem}
.section-slide{justify-content:center;text-align:center} .section-slide h1{font-size:2rem}
.section-slide p{color:var(--muted);margin-top:.6rem;font-size:.95rem}
.chart-title{font-size:.8rem;font-weight:600;color:var(--navy);margin-bottom:.35rem;text-align:center}
.chart-wrap{height:200px;position:relative} .chart-wrap.tall{height:240px}
.invest-kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-bottom:.65rem}
.invest-kpi-row.cols4{grid-template-columns:repeat(4,1fr)}
.invest-kpi-row.cols2{grid-template-columns:repeat(2,1fr)}
.invest-kpi{background:linear-gradient(160deg,#f8fafb,#fff);border:1px solid #e8ecf0;border-radius:10px;padding:.5rem;text-align:center}
.invest-kpi.highlight{border-color:#d4b84a;background:linear-gradient(160deg,#fffdf5,#fff)}
.invest-kpi .ik-val{font-size:.95rem;font-weight:700;color:var(--navy)}
.invest-kpi .ik-lbl{font-size:.62rem;color:var(--muted);margin-top:.15rem}
.cost-scroll{flex:1;overflow-y:auto;min-height:0}
''' + EXT_COST_CSS + HPLC_COST_CSS + HIPO_COST_CSS + r'''
.cost-total-bar{background:var(--navy);color:#fff;border-radius:8px;padding:.5rem .7rem;margin-bottom:.4rem;font-size:.86rem;display:flex;justify-content:space-between;align-items:center}
.cost-item{border:1px solid #e8ecf0;border-radius:8px;margin-bottom:.28rem;background:#fff}
.cost-item>summary{display:flex;align-items:center;padding:.38rem .55rem;cursor:pointer;list-style:none;font-size:.78rem}
.cost-item>summary::-webkit-details-marker{display:none}
.cost-label{flex:1;font-weight:600;color:var(--navy)} .cost-amt{font-weight:700}
.cost-children{padding:0 .5rem .4rem .7rem;border-top:1px solid #f0f2f5}
.cost-leaf{display:flex;justify-content:space-between;font-size:.72rem;padding:.2rem 0;color:var(--muted)}
.cost-sub summary{display:flex;justify-content:space-between;font-size:.74rem;padding:.28rem 0;cursor:pointer;list-style:none;color:var(--muted)}
.cost-sub ul{list-style:none;padding:0} .cost-sub li{display:flex;justify-content:space-between;font-size:.68rem;padding:.1rem 0}
.note{font-size:.72rem;color:var(--muted);margin-top:.35rem;line-height:1.4}
.scope-grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem}
.scope-grid h3{font-size:.84rem;color:var(--navy);margin-bottom:.3rem}
.compare-table td:last-child,.compare-table th:last-child{text-align:right;font-weight:600}
.gantt-wrap{flex:1;min-height:0;background:var(--card);border-radius:10px;padding:.7rem;border:1px solid #e8ecf0;display:flex;flex-direction:column}
.gantt-axis{display:flex;justify-content:space-between;font-size:.63rem;color:var(--muted);padding:0 .15rem .22rem 7.5rem;border-bottom:1px solid #dde3e8;margin-bottom:.22rem}
.gantt-body{flex:1;overflow-y:auto}
.gantt-row{display:grid;grid-template-columns:7rem 1fr 6rem;gap:.35rem;margin-bottom:.35rem;align-items:center}
.gantt-label{font-size:.63rem;font-weight:600;color:var(--navy);text-align:right;line-height:1.1}
.gantt-track{position:relative;height:19px;background:#eef2f6;border-radius:4px}
.gantt-bar{position:absolute;top:2px;height:15px;border-radius:3px;min-width:3px;cursor:pointer}
.gantt-bar.done{background:var(--teal)} .gantt-bar.plan{background:#1a4a6e}
.gantt-bar.assume{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 5px,#8f7db8 5px,#8f7db8 10px)}
.gantt-bar.warn{background:var(--accent)} .gantt-bar.build{background:#2e6da4} .gantt-bar.staff{background:#5b6eae}
.gantt-dates{font-size:.58rem;color:var(--muted);white-space:nowrap;line-height:1.2;text-align:right}
.gantt-legend{font-size:.6rem;color:var(--muted);margin-top:.3rem;display:flex;gap:.55rem;flex-wrap:wrap}
.gantt-legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:.15rem;vertical-align:middle}
.today-line{position:absolute;top:0;bottom:0;width:2px;background:var(--warn);z-index:2;pointer-events:none}
.today-tag{position:absolute;top:-10px;font-size:.52rem;color:var(--warn);transform:translateX(-50%);white-space:nowrap}
#tip{position:fixed;z-index:300;max-width:360px;background:var(--navy);color:#fff;padding:.5rem .65rem;border-radius:8px;font-size:.72rem;line-height:1.45;pointer-events:none;opacity:0;transition:opacity .12s;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#tip.show{opacity:1} #tip .td{color:#8ecec6;font-size:.65rem;margin-bottom:.15rem}
.decision-list{list-style:none;margin:0;padding:0}
.decision-list li{border:1px solid #e8ecf0;border-left:4px solid var(--teal);padding:.7rem .9rem;margin-bottom:.45rem;border-radius:0 8px 8px 0;font-size:.86rem;background:var(--card)}
.decision-list li.ext{border-left-color:var(--ext)} .decision-list li.hplc{border-left-color:var(--hplc)} .decision-list li.c1{border-left-color:var(--c1)} .decision-list li.hipo{border-left-color:var(--hipo)}
.callout{border-left:4px solid var(--warn);background:linear-gradient(90deg,#fff8f6,#fff);border-radius:0 8px 8px 0;padding:.65rem .85rem;margin-top:.55rem;font-size:.82rem;line-height:1.5;color:var(--text)}
</style>
</head>
<body>
<div class="top-bar"></div>
<div class="lang-switch"><button id="btnZh" class="active" type="button">中文</button><button id="btnEn" type="button">EN</button></div>
<div id="tip"><div class="td"></div><div class="tb"></div></div>
<div id="deck"></div>
<div class="footer"><span id="footerText"></span><span id="navHint"></span><span id="counter"></span></div>
<script>
const GANTT_EXT = ''' + json.dumps(GANTT_EXT_HELD) + r''';
const GANTT_HPLC = ''' + json.dumps(GANTT_HPLC_SHIFTED) + r''';
const CAPEX = ''' + json.dumps(CAPEX) + r''';
const HPLC_RISK = ''' + json.dumps(RISK_ON_BASE) + r''';
const HPLC_COST_DATA = ''' + hplc_cost_data_json() + r''';
const EXT_OOM = ''' + str(EXT_OOM) + r''';
const EXT_COST_DATA = ''' + ext_cost_data_json() + r''';
const C1_COST_DATA = ''' + c1_cost_data_json() + r''';
const GANTT_C1 = ''' + json.dumps(GANTT_C1_SHIFTED) + r''';
const HIPO_COST_DATA = ''' + hipo_cost_data_json() + r''';
const GANTT_HIPO = ''' + json.dumps(GANTT_HIPO_SHIFTED) + r''';
''' + EXT_COST_RENDER_JS + HPLC_COST_RENDER_JS + C1_COST_RENDER_JS + HIPO_COST_RENDER_JS + r'''
let lang="zh", idx=0, chartsBuilt = {};

const I18N={
zh:{
footer:"凯莱英 UK · Sandwich PDF 资本项目",
nav:"← → 翻页", tag:"内部汇报 · 整体汇报",
p1t:"凯莱英 UK · Sandwich PDF", p1s:"资本项目汇报", p1m:"B902 东侧扩建 + 厂房内 HPLC/冻干改造 + C1 模块 OEB5 升级 + OEB5 高活实验室 · 2026年8月",
p2t:"项目概览", p2s:"四条独立工作流 · 可行性 / 概念 / 内部估算量级",
p2th1:"子项目", p2th2:"范围", p2th3:"投资（估算量级）", p2th4:"关键节点",
p2r1n:"B902 东侧扩建", p2r1s:"新建四层+夹层，反应/加氢/过滤干燥", p2r1o:"£78.1M", p2r1d:"2030-05 竣工（保持）",
p2r2n:"HPLC + 冻干", p2r2s:"既有 PDF footprint 改造", p2r2o:"£5.33M", p2r2d:"2027-12 HPLC / 2028-03 冻干",
p2r3n:"C1 模块 OEB5 升级", p2r3s:"现有 C1 模块 OEB5 日常运行能力", p2r3o:"£2.48M", p2r3d:"2027-10 安装确认",
p2r4n:"OEB5 高活实验室", p2r4s:"既有 G-128 套间改造；GIFA 215 m²；4+1 台隔离器", p2r4o:"£4.56M", p2r4d:"计划 2027-11 交付",
p2link:"交付关联：厂房内改造（制备 HPLC + 冻干）与 C1 模块升级须同步完成，方能为制备 HPLC 操作提供 OEB5 能力；制备 HPLC 单元驱动整体交付时间线。",
p2rebase:"进度口径：厂房内改造与 C1 模块升级原按 2026 年 6 月启动估算，现以 2026 年 9 月启动重新基线（顺延 3 个月），范围与费用不变。高活实验室在概念进度基础上另增 6 周，用于启动准备与资金决策，交付目标 2027 年 11 月。902 东侧扩建按集团口径保持 2030-05 竣工，沿用设计方总控计划不作顺延，启动延后需在阶段内消化。",
p2sum:"厂房内三条线合计（改造 £5.33M + C1 £2.48M + 高活实验室 £4.56M）约 £12.37M，不含 902 东侧扩建。各线口径不同：扩建与改造为可行性量级，C1 为内部估算，高活实验室为概念阶段成本计划。",
extTag:"扩建", hplcTag:"改造", c1Tag:"C1 OEB5", hipoTag:"高活实验室",
extSec:"一、B902 东侧扩建", extSecs:"Scitech · RIBA Stage 1 · 300291-RE-0001",
ext2t:"扩建 · 执行摘要", ext2s:"2026-05-22 · Issue A1",
extK1:"FS 完成", extK1d:"RIBA 1",
extK2:"£78.1M", extK2d:"项目 OOM",
extK3:"2030-05", extK3d:"总控完成（集团口径保持）",
extB1:"范围：东侧约 600 m²，四层+设备夹层，10 台反应釜、2500 L 加氢釜、3 套过滤干燥机及公用工程。",
extB2:"方案：Option 1 — 拆除/迁址原加氢厂房；与 902 低层楼面贯通。",
extB3:"进展：FS 完成；按集团口径保持 2030-05 竣工，沿用设计方总控计划；RIBA 2 概念设计启动延后需在阶段内消化。",
ext4t:"扩建 · 范围基线", ext4s:"Option 1",
ext4b1:"GIFA 约 3,099 m²；防洪抬升约 1.5 m", ext4b2:"第二疏散梯；加氢区泄压板", ext4b3:"BREEAM 预评估 Very Good 基线",
ext5t:"扩建 · 投资总览", ext5s:"300291-CM-0001",
ext5oom:"OOM 总价",
ext6t:"扩建 · 投资结构", ext6s:"OOM 构成与直接工程费分项",
ext6kOom:"OOM 总价", ext6kBase:"直接工程费（含 25%）", ext6kRisk:"其他费及可行性风险",
extCost:''' + json.dumps(EXT_COST_I18N_ZH, ensure_ascii=False) + r''',extChart:''' + json.dumps(EXT_CHART_I18N_ZH, ensure_ascii=False) + r''',
extChL:"项目 OOM 三板块", extChR:"直接工程费 — 分项",
ext8t:"扩建 · 整体周期", ext8s:"300291-PM-PR-0002",
extGSub:"总控时间轴（条块长度按日历比例）· 沿用设计方总控计划，按集团口径保持 2030-05 竣工",
extGFs:"可行性 RIBA 1", extGR2:"概念 RIBA 2", extGR3:"方案 RIBA 3", extGPl:"规划",
extGR4:"详细 RIBA 4", extGEq:"长周期设备", extGMed:"中等周期设备", extGPre:"施工准备",
extGR5:"施工 RIBA 5", extGCo:"调试", extGEn:"验证/竣工",
extLegD:"已完成", extLegP:"设计", extLegB:"施工", extLegM:"节点", extToday:"约今",
ext9t:"扩建 · 决策事项", ext9d1:"是否批准进入 RIBA 2（概念设计）？",
ext9d2:"是否推进模块化建造方案比选？",
hplcSec:"二、厂房内 HPLC + 冻干", hplcSecs:"RBPC · Project 9802 · P01",
hplc2t:"改造 · 执行摘要", hplc2s:"9802-RBP-ZZ-ZZ-RP-X-100000",
hplcK1:"技术可行", hplcK1d:"FS P01",
hplcK2:"£5.33M", hplcK2d:"项目总投资估算",
hplcK3:"2027-12", hplcK3d:"HPLC 目标（+3 个月）",
hplcK4:"2028-03", hplcK4d:"冻干目标（+3 个月）",
hplcB1:"范围：制备 HPLC（DAC300/CP300）+ 冻干机（隔离器、除湿、纯蒸汽发生器等）及配套改造。",
hplcB2:"投资：Total CAPEX Estimate £5.33M（直接+间接+30% 项目预备费）；非最终 Capex。",
hplcB3:"周期：冻干机长周期驱动；优先冻干后 HPLC。",
hplcB4:"关联：须与 C1 模块 OEB5 升级同步交付，方可实现制备 HPLC 的 OEB5 运行能力。",
hplc3t:"改造 · 范围",
hplcT1:"HPLC", hplcT1a:"DAC300/CP300 泵撬；移动头罐；2000 L 废液罐",
hplcT1b:"Hanbon 供货", hplcT1c:"PG.05 区域安装",
hplcT2:"冻干机", hplcT2a:"冻干腔、隔离器、双 CIP、除湿、PSG",
hplcT2b:"供货方待确认（Asymchem / 东富龙 Tofflon）", hplcT2c:"气闸/改造约 20 周",
hplc5t:"改造 · 投资总览", hplc5s:"9802-RBP-ZZ-ZZ-CP-X-100001",
hplc5oom:"项目总投资估算",
hplc6t:"改造 · 投资结构", hplc6s:"直接 / 间接 / 一般风险与预备费",
hplc6kOom:"项目总投资", hplc6kDirect:"直接费用合计", hplc6kIndirect:"间接费用合计", hplc6kGen:"一般风险与预备费",
hplc6kMain:"1. 主工艺设备", hplc6kInfra:"2. 基础设施改造",
hplcCost:''' + json.dumps(HPLC_COST_I18N_ZH, ensure_ascii=False) + r''',hplcChart:''' + json.dumps(HPLC_CHART_I18N_ZH, ensure_ascii=False) + r''',
hplcChL:"项目总投资构成", hplcChR:"直接费用 — 分项",
hplc7t:"改造 · 周期", hplc7s:"FS §4.4 图 1 · 以 2026-09 启动重新基线（原 6 月口径 +3 个月）",
hplc7k1:"冻干制造", hplc7k1d:"8–10 月",
hplc7k2:"HPLC 供货", hplc7k2d:"~18 周",
hplc7k3:"FEED", hplc7k3d:"12–14 周",
hplc7k4:"详细设计", hplc7k4d:"18–20 周",
hplcGSub:"High Level Programme · 以 2026-09 启动重新基线（+3 个月）",
gFs:"FS/基准", gEng:"Engineer就位", gFeed:"FEED（示意）", gDd:"详细设计（示意）",
gLySpec:"冻干规格/资金", gLyMfg:"冻干制造", gLyFat:"冻干 FAT", gLyShip:"冻干运输安装", gLyVal:"冻干验证→PQ",
gHplcSpec:"HPLC 规格/资金", gHplcMfg:"HPLC 制造", gHplcFat:"HPLC FAT", gHplcShip:"HPLC 运输安装",
gTanks:"移动头罐", gWaste:"废液罐", gRetrofit:"改造",
legDone:"完成", legStaff:"工程师就位", legPlan:"采购/制造", legBuild:"施工/验证",
legCrit:"关键路径", legAssume:"§4.3 示意", today:"约今",
hplc9t:"改造 · 决策", hplc9d1:"是否批准进入 FEED？",
hplc9d2:"是否批准长周期设备早期采购资金？",
c1Sec:"三、C1 模块 OEB5 升级", c1Secs:"Sandwich PDF · 内部估算",
c12t:"C1 · 执行摘要", c12s:"现有 C1 模块 OEB5 日常运行能力",
c1K1:"OEB5 日常运行", c1K1d:"升级目标",
c1K2:"£2.48M", c1K2d:"项目总投资估算",
c1K3:"2027-10", c1K3d:"安装与确认目标（+3 个月）",
c1B1:"范围：二层物料分装与首层最终包装固定隔离器；HVAC 升级；进出气闸联锁及雾化淋浴；覆盖各单元操作与废物流的定制柔性隔离器。",
c1B2:"估算：已取得供应商预算报价 —— ILC Dover 反应釜投料柔性隔离器整包 £115,800（含 R19–R22 投料方案概念设计）；Howorth 单腔分装隔离器 £250,000/台。两者均为 Ex Works 口径，不含包装、运输、安装与调试。",
c1B5:"报价前提：以上为预算价，最终费用取决于项目范围最终确认的密闭等级（ILC Dover 现报价按 OEB 4、1–10 µg/m³）。",
c1B3:"交付关联：须与厂房内改造（制备 HPLC + 冻干）同步完成，方能为制备 HPLC 操作提供 OEB5 能力。",
c1B4:"周期：假设与改造项目一并批准；制备 HPLC 单元驱动 C1 模块升级交付时间线。",
c13t:"C1 · 范围",
c1S1:"固定隔离器", c1S1a:"三层（second floor）：物料分装", c1S1b:"一层（ground floor）：最终包装",
c1S2:"HVAC 与气闸", c1S2a:"HVAC 升级，支持日常 OEB5 运行", c1S2b:"进出气闸联锁升级，含雾化淋浴",
c1S3:"柔性隔离", c1S3a:"多台定制柔性隔离器", c1S3b:"覆盖模块内各单元操作及废物流",
c1S4:"估价依据（供应商报价）",
c1S4a:"柔性隔离器：ILC Dover JS26-11384-0（2026-07-22）整包 £115,800，EXW，不含运输安装；交期约 20 周（图纸批准后）",
c1S4b:"固定隔离器：Howorth Q26543（2026-08-11）单腔分装隔离器 £250,000/台；选项 190 RTP £18,000、样机 £17,000",
c1S4c:"均为预算价，最终费用取决于范围确认的密闭等级；HVAC 与气闸尚无详细报价支撑",
c15t:"C1 · 投资总览", c15s:"内部估算 · 主设备 + 30% 项目预备费",
c15oom:"项目总投资估算",
c16t:"C1 · 投资结构", c16s:"主设备小计 / 全项目预备费",
c16kOom:"项目总投资", c16kEquip:"主设备小计", c16kCont:"全项目预备费",
c1Cost:''' + json.dumps(C1_COST_I18N_ZH, ensure_ascii=False) + r''',c1Chart:''' + json.dumps(C1_CHART_I18N_ZH, ensure_ascii=False) + r''',
c1ChL:"项目总投资构成", c1ChR:"主设备 — 分项",
c17t:"C1 · 周期", c17s:"假设与改造项目一并批准 · 以 2026-09 启动重新基线（原 6 月口径 +3 个月）",
c17k1:"范围定稿", c17k1d:"8 周",
c17k2:"详细设计", c17k2d:"12 周",
c17k3:"下单/制造", c17k3d:"20 周",
c17k4:"安装确认", c17k4d:"8 周",
c1GSub:"C1 OEB5 升级时间轴 · 以 2026-09 启动重新基线（+3 个月）",
c1Scope:"范围定稿", c1Dd:"详细设计", c1Build:"下单及设备制造", c1IQ:"安装与确认",
c1LegP:"设计/准备", c1LegWarn:"下单+制造", c1LegB:"施工/确认", c1Today:"约今",
c19t:"C1 · 决策", c19d1:"是否批准 C1 OEB5 升级与改造项目一并推进？",
c19d2:"是否授权启动 ILC Dover 柔性隔离器及固定隔离器供货方案深化？",
hipoSec:"四、OEB5 高活实验室（G-128 套间改造）", hipoSecs:"Concept 阶段 · 成本计划 260806 / 概念进度 260727 / 风险登记册",
hipo2t:"高活实验室 · 执行摘要", hipo2s:"DPH_G-128 Suite Alterations Concept Cost Plan 260806",
hipoK1:"概念阶段", hipoK1d:"成本计划 / 概念进度 / 风险登记册",
hipoK2:"£4.56M", hipoK2d:"项目总投资估算",
hipoK3:"2027-11", hipoK3d:"计划交付（概念进度 +6 周）",
hipoK4:"215 m²", hipoK4d:"GIFA（实验室约 182 + 办公区约 33）",
hipoB1:"范围：既有 G-128 套间改造为实验室与办公区，GIFA 215 m²；隔离器在成本计划中计列 4 台 × £150,000 + 1 台 × £100,000。",
hipoB2:"投资：项目投资（含通胀）£4,562,044；不含增值税；估算精度区间 £3.74M – £4.99M。",
hipoB3:"构成：建筑工程费 £1.95M + 专业服务费 £0.14M + 业主（凯莱英）供货设备 £1.98M + 风险预备费 £0.40M + 通胀 £0.10M。",
hipoB4:"周期：概念进度（草案）自资金批准与推进决定起 262 个工作日；按 Clare 意见另增 6 周用于启动准备与资金决策，计划交付 2027 年 11 月；隔离器 2027-07-14 到场。",
hipoB5:"隔离器费用：为基于与供应商沟通的估算，最终取决于项目范围最终确认的密闭等级。",
hipo3t:"高活实验室 · 范围", hipo3s:"依据 G-128 概念成本计划分项",
hipoS1:"范围与面积", hipoS1a:"既有 G-128 套间（G128 及 G128A–D）改造；GIFA 215 m²",
hipoS1b:"实验室区约 182 m²（机电费率基准）+ 办公区约 33 m²（地毯量）",
hipoS1c:"拆除 G128 与 G128D 之间砌块墙；混凝土墙新开 2 处传递窗洞、2 处门洞",
hipoS2:"隔离器与实验设备", hipoS2a:"成本计划：4 台 × £150,000 + 1 台 × £100,000（合计 £700,000）",
hipoS2b:"费用性质：基于与供应商沟通的估算，最终取决于项目范围最终确认的密闭等级（ILC Dover 与 Howorth 现有报价对应 C1 模块改造，见 C1 章节）",
hipoS2c:"通风柜：假设现有可继续使用，仅列 £20,000 维修保养费用；是否新购为进度中待定项",
hipoS2d:"SF6 检漏测试 £20,000；家具含更衣柜、跨越凳、移动实验台、BIBO 桶",
hipoS3:"土建与装饰改造", hipoS3a:"拆除：家具与实验设备清空、地面与吊顶拆除、燃气/风管/电气/烟感/Crowcon 撤除",
hipoS3b:"新建：墙面衬板 475 m²、新隔断 40 m²；5 樘单开 + 1 樘子母卫生门、2 樘木门、4 樘旧门翻新",
hipoS3c:"装饰：实验室卷材乙烯地面 173 m²、金属吊顶 173 m²、办公区地毯 33 m²",
hipoS4:"机电、安全与业主供货", hipoS4a:"暖通 £217,920：AHU 恢复使用、全套风管与送回风、袋进袋出 HEPA 排风过滤、BMS 升级、系统平衡",
hipoS4b:"电气 £107,380、消防喷淋 £30,030、门禁/布线/CCTV/火警 £51,345、实验室气体管道 £63,700、雾化淋浴 £35,000",
hipoS4c:"业主（凯莱英）供货并安装设备 £1,975,045",
hipoScopeNote:"风险与前提：正在就厂房改造事宜征求 DPML 同意 —— 改造完成后实验室将无法按当前运行状态交还 DPML，该沟通进展由 Clare 跟进。另一项前提是与 DPH 签署租赁协议前可接受的支出水平，以及协议签署前能否开始厂房改造，目前为本项目最大的不确定性。",
hipo5t:"高活实验室 · 投资总览", hipo5s:"G-128 Concept Cost Plan · 报告日期 2026-08-06 · GIFA 215 m²",
hipo6t:"高活实验室 · 投资结构", hipo6s:"项目投资构成与建筑工程费分项",
hipo6kTotal:"项目投资（含通胀）", hipo6kBuild:"建筑工程费合计", hipo6kEquip:"业主（凯莱英）供货设备",
hipo6kRisk:"风险预备费", hipo6kRange:"估算精度区间",
hipoCost:''' + json.dumps(HIPO_COST_I18N_ZH, ensure_ascii=False) + r''',hipoChart:''' + json.dumps(HIPO_CHART_I18N_ZH, ensure_ascii=False) + r''',
hipoChL:"项目投资构成", hipoChR:"建筑工程费 — 分项",
hipo7t:"高活实验室 · 周期", hipo7s:"Asymchem Concept Programme_260727（DRAFT CONCEPT PROGRAMME）· 按 Clare 意见整体顺延 6 周",
hipo7k1:"262 天", hipo7k1d:"总工期（工作日，不含新增 6 周）",
hipo7k2:"2026-10-13", hipo7k2d:"资金批准与推进决定（+6 周）",
hipo7k3:"2027-07-14", hipo7k3d:"隔离器到场",
hipo7k4:"2027-11", hipo7k4d:"计划交付（含 15 天进度风险预留）",
hipoGSub:"概念进度（草案）· 整体顺延 6 周后示意，条块落点至 2027-10-29",
hipoProgNote:"进度说明：为覆盖启动准备与资金决策所需时间，概念进度整体顺延 6 周（Clare，2026-08-21），交付目标定为 2027 年 11 月。后续设计推进中部分工作有并行压缩的空间，但取决于最终确认的风险处理方式与可接受的风险水平。",
hFund:"资金批准节点", hConsult:"顾问任命 + BoD", hContractor:"主承包商招标任命", hAward:"合同授予与动员",
hSurvey:"勘查与项目控制", hLabDesign:"实验室设计", hCdm:"CDM", hIso:"隔离器采购制造",
hFume:"通风柜采购（待定）", hFurn:"实验室家具采购", hTrade:"分包工程招标",
hConstr:"施工", hComm:"调试与移交", hRisk:"进度风险预留→竣工",
hipoLegP:"设计/合约", hipoLegW:"采购/制造/预留", hipoLegB:"施工/调试", hipoToday:"约今",
hipo9t:"高活实验室 · 决策", hipo9s:"",
hipo9d1:"是否批准资金与推进决定节点？概念进度以此为起点，262 个工作日加 6 周启动与决策时间，计划交付 2027 年 11 月。",
hipo9d2:"是否安排 AHU 状况核查与既有通风柜可用性确认？二者为风险登记册中金额最高的两项。",
hipo9d3:"在与 DPH 签署租赁协议前，可接受的支出水平如何界定？协议签署前能否开始厂房改造？同时需取得 DPML 对改造的同意（改造后实验室无法按当前运行状态交还）。",
pEnd:"谢谢", pEnds:"",
},
en:{
footer:"Asymchem UK · Sandwich PDF Portfolio",
nav:"← → navigate", tag:"Internal · Portfolio briefing",
p1t:"Asymchem UK · Sandwich PDF", p1s:"Capital Projects Briefing", p1m:"B902 extension + HPLC/lyoph retrofit + C1 OEB5 upgrade + OEB5 HIPO lab · August 2026",
p2t:"Project overview", p2s:"Four workstreams · feasibility / concept / internal estimate",
p2th1:"Workstream", p2th2:"Scope", p2th3:"Investment (estimate level)", p2th4:"Milestone",
p2r1n:"B902 east extension", p2r1s:"New 4-floor + mezzanine", p2r1o:"£78.1M", p2r1d:"Complete May 2030 (held)",
p2r2n:"HPLC + lyophilizer", p2r2s:"Retrofit in existing PDF", p2r2o:"£5.33M", p2r2d:"HPLC Dec 2027 / lyoph Mar 2028",
p2r3n:"C1 module OEB5 upgrade", p2r3s:"Routine OEB5 ops in existing C1 module", p2r3o:"£2.48M", p2r3d:"IQ complete Oct 2027",
p2r4n:"OEB5 HIPO lab", p2r4s:"Existing G-128 suite alterations; 215 m² GIFA; 4+1 isolators", p2r4o:"£4.56M", p2r4d:"Planned delivery Nov 2027",
p2link:"Delivery link: in-situ retrofit (prep HPLC + lyophilizer) and C1 upgrade must be delivered together to provide OEB5 capability for prep HPLC; prep HPLC drives the overall timeline.",
p2rebase:"Programme basis: the retrofit and C1 upgrade were estimated from a June 2026 start and are now re-baselined to a September 2026 start (+3 calendar months); scope and cost are unchanged. The HIPO lab carries a further 6 weeks on top of the concept programme for start-up and the funding decision, giving a delivery target of November 2027. The B902 east extension holds its May 2030 completion per group direction and keeps the consultant master programme unshifted — the later start must be absorbed within the stages.",
p2sum:"The three in-building lines total ~£12.37M (retrofit £5.33M + C1 £2.48M + HIPO lab £4.56M), excluding the B902 east extension. Estimate bases differ: extension and retrofit are feasibility level, C1 is an internal estimate, the HIPO lab is a concept cost plan.",
extTag:"Extension", hplcTag:"Retrofit", c1Tag:"C1 OEB5", hipoTag:"HIPO lab",
extSec:"I. B902 East Extension", extSecs:"Scitech · RIBA 1 · 300291-RE-0001",
ext2t:"Extension · Summary", ext2s:"22 May 2026 · A1",
extK1:"FS done", extK1d:"RIBA 1",
extK2:"£78.1M", extK2d:"Project OOM",
extK3:"May 2030", extK3d:"Programme end (held per group)",
extB1:"~600 m² east extension, 4 floors + mezzanine, reactors, H₂ suite, 3 filter dryers, utilities.",
extB2:"Option 1 — remove/relocate H₂ building; tie to B902 lower floors.",
extB3:"FS complete; May 2030 completion held per group direction on the consultant master programme — the later RIBA 2 start must be absorbed within the stages.",
ext4t:"Extension · Scope", ext4s:"Option 1",
ext4b1:"~3,099 m² GIFA; ~1.5 m flood lift", ext4b2:"Second escape stair; blast panels", ext4b3:"BREEAM pre-assessment baseline",
ext5t:"Extension · Investment", ext5s:"300291-CM-0001",
ext5oom:"Total OOM",
ext6t:"Extension · Structure", ext6s:"OOM build-up",
ext6kOom:"Total OOM", ext6kBase:"Direct works (incl. 25%)", ext6kRisk:"Other costs & feasibility risk",
extCost:''' + json.dumps(EXT_COST_I18N_EN, ensure_ascii=False) + r''',extChart:''' + json.dumps(EXT_CHART_I18N_EN, ensure_ascii=False) + r''',
extChL:"Project OOM — three blocks", extChR:"Direct works — line items",
ext8t:"Extension · Programme", ext8s:"300291-PM-PR-0002",
extGSub:"Master programme · consultant programme retained; May 2030 completion held per group direction",
extGFs:"FS RIBA 1", extGR2:"Concept RIBA 2", extGR3:"Scheme RIBA 3", extGPl:"Planning",
extGR4:"Detail RIBA 4", extGEq:"Long-lead equip.", extGMed:"Medium-lead equip.", extGPre:"Pre-construction",
extGR5:"Construction RIBA 5", extGCo:"Commissioning", extGEn:"Validation/complete",
extLegD:"Done", extLegP:"Design", extLegB:"Build", extLegM:"Milestone", extToday:"~Today",
ext9t:"Extension · Decisions", ext9d1:"Approve RIBA 2 (Concept Design)?",
ext9d2:"Proceed with modular construction option study?",
hplcSec:"II. HPLC + Lyophilizer", hplcSecs:"RBPC · 9802 · P01",
hplc2t:"Retrofit · Summary", hplc2s:"9802-RBP-ZZ-ZZ-RP-X-100000",
hplcK1:"Feasible", hplcK1d:"FS P01",
hplcK2:"£5.33M", hplcK2d:"Total CAPEX Estimate",
hplcK3:"Dec 2027", hplcK3d:"HPLC target (+3 months)",
hplcK4:"Mar 2028", hplcK4d:"Lyoph target (+3 months)",
hplcB1:"Prep HPLC + lyophilizer (isolator, dehumidifier, PSG, etc.) and enabling works.",
hplcB2:"Total CAPEX Estimate £5.33M (direct + indirect + 30% project contingency); not final Capex.",
hplcB3:"Lyophilizer lead time drives; lyoph before HPLC.",
hplcB4:"Link: must be delivered together with C1 OEB5 upgrade for prep HPLC OEB5 capability.",
hplc3t:"Retrofit · Scope",
hplcT1:"HPLC", hplcT1a:"DAC300/CP300; mobile tanks; 2,000 L waste hold",
hplcT1b:"Hanbon supply", hplcT1c:"Install PG.05",
hplcT2:"Lyophilizer", hplcT2a:"Dryer, isolator, twin CIP, dehumidifier, PSG",
hplcT2b:"Vendor to be confirmed (Asymchem / Tofflon)", hplcT2c:"Airlock ~20 weeks",
hplc5t:"Retrofit · Investment", hplc5s:"9802-CP-X-100001",
hplc5oom:"Total OOM",
hplc6t:"Retrofit · Structure", hplc6s:"Direct / indirect / general risk & contingency",
hplc6kOom:"Total CAPEX", hplc6kDirect:"Total Direct Cost", hplc6kIndirect:"Total Indirect Cost", hplc6kGen:"General risk & contingency",
hplc6kMain:"1. Main Equipment", hplc6kInfra:"2. Infrastructure Modification",
hplcCost:''' + json.dumps(HPLC_COST_I18N_EN, ensure_ascii=False) + r''',hplcChart:''' + json.dumps(HPLC_CHART_I18N_EN, ensure_ascii=False) + r''',
hplcChL:"Total CAPEX composition", hplcChR:"Total Direct Cost — breakdown",
hplc7t:"Retrofit · Programme", hplc7s:"FS §4.4 Fig. 1 · re-baselined to a Sep 2026 start (+3 months)",
hplc7k1:"Lyoph build", hplc7k1d:"8–10 mo",
hplc7k2:"HPLC supply", hplc7k2d:"~18 wk",
hplc7k3:"FEED", hplc7k3d:"12–14 wk",
hplc7k4:"Detail design", hplc7k4d:"18–20 wk",
hplcGSub:"High Level Programme · re-baselined to a Sep 2026 start (+3 months)",
gFs:"FS/baseline", gEng:"Engineer mobilised", gFeed:"FEED (illustrative)", gDd:"Detail design (illustrative)",
gLySpec:"Lyoph spec/funding", gLyMfg:"Lyoph build", gLyFat:"Lyoph FAT", gLyShip:"Lyoph ship/install", gLyVal:"Lyoph val.→PQ",
gHplcSpec:"HPLC spec/funding", gHplcMfg:"HPLC build", gHplcFat:"HPLC FAT", gHplcShip:"HPLC ship/install",
gTanks:"Mobile tanks", gWaste:"Waste tank", gRetrofit:"Retrofit",
legDone:"Complete", legStaff:"Engineer", legPlan:"Procure/build", legBuild:"Site/val.",
legCrit:"Critical", legAssume:"§4.3 illustrative", today:"~Today",
hplc9t:"Retrofit · Decisions", hplc9d1:"Approve progression to FEED?",
hplc9d2:"Approve early funding for long-lead packages?",
c1Sec:"III. C1 Module OEB5 Upgrade", c1Secs:"Sandwich PDF · internal estimate",
c12t:"C1 · Summary", c12s:"Routine OEB5 operational capability",
c1K1:"OEB5 routine ops", c1K1d:"Upgrade objective",
c1K2:"£2.48M", c1K2d:"Total CAPEX estimate",
c1K3:"Oct 2027", c1K3d:"Install & qualification target (+3 months)",
c1B1:"Scope: fixed isolators (2nd floor dispensing, GF pack-off); HVAC upgrades; entry/exit airlock interlocks incl. mist showers; bespoke flexible isolators for unit ops and waste streams.",
c1B2:"Estimate: supplier budget costs now received — ILC Dover reactor charging flexible isolator package £115,800 (incl. concept development for the R19–R22 charging scheme); Howorth single chamber dispensing isolator £250,000 per unit. Both Ex Works, excluding packing, delivery, installation and commissioning.",
c1B5:"Basis: these are budget prices; the final cost will depend on the level of containment agreed in the project scope (ILC Dover currently quoted at OEB 4, 1–10 µg/m³).",
c1B3:"Delivery link: must be delivered with retrofit (prep HPLC + lyoph) for OEB5 prep HPLC capability.",
c1B4:"Programme: assumes joint approval with retrofit; prep HPLC unit drives C1 module upgrade delivery timeline.",
c13t:"C1 · Scope",
c1S1:"Fixed isolators", c1S1a:"2nd floor: material dispensing", c1S1b:"Ground floor: final pack-off",
c1S2:"HVAC & airlocks", c1S2a:"HVAC upgrades for routine OEB5 operation", c1S2b:"Entry/exit airlock interlocks incl. mist showers",
c1S3:"Flexible isolation", c1S3a:"Multiple bespoke flexible isolator systems", c1S3b:"All unit operations and waste streams within module",
c1S4:"Pricing basis (supplier quotations)",
c1S4a:"Flexible isolators: ILC Dover JS26-11384-0 (22 Jul 2026), £115,800 package, EXW, excl. delivery and installation; ~20 weeks from drawing approval",
c1S4b:"Fixed isolators: Howorth Q26543 (11 Aug 2026), single chamber dispensing isolator £250,000 per unit; options 190 RTP £18,000, mock-up £17,000",
c1S4c:"Both are budget prices; final cost depends on the containment level agreed in scope. HVAC and airlocks have no detailed quotes yet",
c15t:"C1 · Investment", c15s:"Internal estimate · equipment + 30% project contingency",
c15oom:"Total CAPEX Estimate",
c16t:"C1 · Structure", c16s:"Equipment subtotal / project contingency",
c16kOom:"Total CAPEX", c16kEquip:"Equipment subtotal", c16kCont:"Project contingency",
c1Cost:''' + json.dumps(C1_COST_I18N_EN, ensure_ascii=False) + r''',c1Chart:''' + json.dumps(C1_CHART_I18N_EN, ensure_ascii=False) + r''',
c1ChL:"Total CAPEX composition", c1ChR:"Main equipment — breakdown",
c17t:"C1 · Programme", c17s:"Assumes joint approval with retrofit · re-baselined to a Sep 2026 start (+3 months)",
c17k1:"Finalise scope", c17k1d:"8 wk · Oct–Dec 2026",
c17k2:"Detailed design", c17k2d:"12 wk · Dec 2026–Mar 2027",
c17k3:"Orders / build", c17k3d:"20 wk · Mar–Aug 2027",
c17k4:"Install & IQ", c17k4d:"8 wk · Aug–Oct 2027",
c1GSub:"C1 OEB5 upgrade timeline · re-baselined to a Sep 2026 start (+3 months)",
c1Scope:"Finalise scope", c1Dd:"Detailed design", c1Build:"Orders & equipment build", c1IQ:"Installation & qualification",
c1LegP:"Design / prep", c1LegWarn:"Orders + build", c1LegB:"Install / IQ", c1Today:"~Today",
c19t:"C1 · Decisions", c19d1:"Approve C1 OEB5 upgrade in parallel with retrofit?",
c19d2:"Authorise ILC Dover flexible isolator work and fixed-isolator option development?",
hipoSec:"IV. OEB5 HIPO Lab (G-128 Suite Alterations)", hipoSecs:"Concept stage · cost plan 260806 / concept programme 260727 / risk register",
hipo2t:"HIPO lab · Summary", hipo2s:"DPH_G-128 Suite Alterations Concept Cost Plan 260806",
hipoK1:"Concept stage", hipoK1d:"Cost plan / programme / risk register",
hipoK2:"£4.56M", hipoK2d:"Total project investment estimate",
hipoK3:"Nov 2027", hipoK3d:"Planned delivery (concept programme +6 weeks)",
hipoK4:"215 m²", hipoK4d:"GIFA (lab ~182 + write-up ~33)",
hipoB1:"Scope: alterations to the existing G-128 suite forming lab and write-up areas, 215 m² GIFA; isolators carried in the cost plan at 4 nr × £150,000 + 1 nr × £100,000.",
hipoB2:"Investment: project investment (incl. inflation) £4,562,044; VAT excluded; estimate accuracy range £3.74M – £4.99M.",
hipoB3:"Build-up: building works £1.95M + professional services £0.14M + client (Asymchem) equipment £1.98M + risk allowance £0.40M + inflation £0.10M.",
hipoB4:"Programme: draft concept programme runs 262 working days from the funding approval and decision to proceed; a further 6 weeks is added per Clare's comment to allow for start-up and the funding decision, giving planned delivery in November 2027; isolators delivered to site 14 Jul 2027.",
hipoB5:"Isolator costs: estimates based on supplier discussions; they will depend on the level of containment agreed in the project scope.",
hipo3t:"HIPO lab · Scope", hipo3s:"Per the G-128 concept cost plan line items",
hipoS1:"Scope & areas", hipoS1a:"Alterations to the existing G-128 suite (G128 and G128A–D); 215 m² GIFA",
hipoS1b:"Lab area ~182 m² (services rate basis) + write-up area ~33 m² (carpet quantity)",
hipoS1c:"Blockwork wall between G128 and G128D taken down; 2 pass-through hatches and 2 doorways formed through reinforced concrete wall",
hipoS2:"Isolators & lab equipment", hipoS2a:"Cost plan: 4 nr × £150,000 + 1 nr × £100,000 (£700,000 total)",
hipoS2b:"Basis: estimates from supplier discussions, dependent on the containment level agreed in the project scope (the ILC Dover and Howorth quotations cover the C1 module modifications — see the C1 section)",
hipoS2c:"Fume cupboards: existing assumed serviceable, only a £20,000 servicing/repair allowance; new units remain a TBC item on the programme",
hipoS2d:"SF6 testing £20,000; furniture covers lockers, step-over bench, mobile benches, BIBO bins",
hipoS3:"Building & finishes", hipoS3a:"Strip out: furniture and lab equipment clearance, floor and ceiling removal, gas / ductwork / electrical / detectors / Crowcon removal",
hipoS3b:"New works: wall lining 475 m², new partitions 40 m²; 5 single-leaf + 1 leaf-and-half hygienic doorsets, 2 timber doors, 4 doors refurbished",
hipoS3c:"Finishes: sheet vinyl floor 173 m², metal suspended ceiling 173 m², carpet to write-up area 33 m²",
hipoS4:"Services, safety & client equipment", hipoS4a:"HVAC £217,920: AHU back into use, full ductwork with supply diffusers and extract grilles, bag-in/bag-out HEPA on extract, BMS upgrade, balancing",
hipoS4b:"Electrical £107,380; sprinklers £30,030; access control / cabling / CCTV / fire alarm £51,345; laboratory gas pipework £63,700; mist shower £35,000",
hipoS4c:"Client (Asymchem) supplied and installed equipment £1,975,045",
hipoScopeNote:"Risk and prerequisite: agreement is being sought from DPML for the facility modifications — once complete, the lab could not be returned to DPML in its current operational state; Clare is following up on the status of that conversation. The other prerequisite is the level of spending acceptable ahead of a lease agreement with DPH, and whether facility changes can begin before an agreement is signed — currently the largest area of uncertainty on this project.",
hipo5t:"HIPO lab · Investment", hipo5s:"G-128 Concept Cost Plan · report date 06 Aug 2026 · 215 m² GIFA",
hipo6t:"HIPO lab · Structure", hipo6s:"Project investment build-up and building works breakdown",
hipo6kTotal:"Project investment (incl. inflation)", hipo6kBuild:"Total Building Works", hipo6kEquip:"Client (Asymchem) equipment",
hipo6kRisk:"Risk allowance", hipo6kRange:"Estimate accuracy range",
hipoCost:''' + json.dumps(HIPO_COST_I18N_EN, ensure_ascii=False) + r''',hipoChart:''' + json.dumps(HIPO_CHART_I18N_EN, ensure_ascii=False) + r''',
hipoChL:"Project investment build-up", hipoChR:"Building works — breakdown",
hipo7t:"HIPO lab · Programme", hipo7s:"Asymchem Concept Programme_260727 (DRAFT CONCEPT PROGRAMME) · shifted out 6 weeks per Clare's comment",
hipo7k1:"262 days", hipo7k1d:"Total duration (working days, excl. the added 6 weeks)",
hipo7k2:"13 Oct 2026", hipo7k2d:"Funding approval & decision to proceed (+6 weeks)",
hipo7k3:"14 Jul 2027", hipo7k3d:"Isolators delivered to site",
hipo7k4:"Nov 2027", hipo7k4d:"Planned delivery (incl. 15 days programme risk)",
hipoGSub:"Draft concept programme · shown shifted out 6 weeks; bars run to 29 Oct 2027",
hipoProgNote:"Programme note: the concept programme is shifted out 6 weeks to cover the time to start the work and the funding decision (Clare, 21 Aug 2026), giving a delivery target of November 2027. There may be opportunities to run some activities in parallel as the programme develops, but this will depend on the risk approach agreed and the level of acceptable risk.",
hFund:"Funding approval", hConsult:"Consultants + BoD", hContractor:"Principal contractor tender", hAward:"Contract award & mobilise",
hSurvey:"Surveys & project control", hLabDesign:"Lab design", hCdm:"CDM", hIso:"Isolator procurement & build",
hFume:"Fume cupboards (TBC)", hFurn:"Laboratory furniture", hTrade:"Trade contractor procurement",
hConstr:"Construction", hComm:"Commissioning & handover", hRisk:"Programme risk → completion",
hipoLegP:"Design / contract", hipoLegW:"Procurement / build / float", hipoLegB:"Construction / commissioning", hipoToday:"~Today",
hipo9t:"HIPO lab · Decisions", hipo9s:"",
hipo9d1:"Approve the funding approval and decision-to-proceed milestone? The concept programme runs 262 working days from it plus 6 weeks for start-up and the funding decision, giving planned delivery in November 2027.",
hipo9d2:"Commission the AHU condition survey and confirm whether the existing fume cupboards can be re-used? These are the two largest items in the risk register.",
hipo9d3:"What level of spending is acceptable ahead of a lease agreement with DPH, and can facility changes begin before an agreement is signed? DPML agreement for the modifications is also required, since the lab could not then be returned in its current operational state.",
pEnd:"Thank you", pEnds:"",
}
};

function t(k){return I18N[lang][k]||k;}
function fm(n){return "£"+Math.round(n).toLocaleString("en-GB");}

function ganttDateLabel(g){
if(g[6]&&String(g[6]).includes("–"))return g[6];
const dispStart=g[6]||g[1],dispEnd=g[7]||g[2];
const d0=dispStart.slice(0,7).replace("-","/"),d1=dispEnd.slice(0,7).replace("-","/");
return d0+" – "+d1;
}
function ganttHTML(data,T0,T1,keys,axis,today,sub,leg){
const RANGE=T1-T0;
function pct(d){return Math.max(0,Math.min(100,((new Date(d)-T0)/RANGE)*100));}
let rows="";
data.forEach((g,i)=>{
const key=keys[i]||g[0];
const left=pct(g[1]),right=pct(g[2]),w=Math.max(1.2,right-left);
const dateLabel=ganttDateLabel(g);
rows+=`<div class="gantt-row"><div class="gantt-label">${t(key)}</div><div class="gantt-track">
${i===0?`<div class="today-line" style="left:${pct(today)}%"><span class="today-tag">${t(leg.today||"today")}</span></div>`:""}
<div class="gantt-bar ${g[3]}" style="left:${left}%;width:${w}%" data-en="${g[4].replace(/"/g,"&quot;")}" data-zh="${g[5].replace(/"/g,"&quot;")}" data-dates="${dateLabel}"></div>
</div><div class="gantt-dates">${dateLabel}</div></div>`;
});
return `<div class="gantt-wrap"><div class="chart-title">${t(sub)}</div>
<div class="gantt-axis">${axis.map(y=>`<span>${y}</span>`).join("")}</div>
<div class="gantt-body">${rows}</div>
<div class="gantt-legend">
${leg.d?`<span><i style="background:var(--teal)"></i>${t(leg.d)}</span>`:""}
${leg.p?`<span><i style="background:#1a4a6e"></i>${t(leg.p)}</span>`:""}
${leg.b?`<span><i style="background:#2e6da4"></i>${t(leg.b)}</span>`:""}
${leg.w?`<span><i style="background:var(--accent)"></i>${t(leg.w)}</span>`:""}
${leg.c?`<span><i style="background:var(--accent)"></i>${t(leg.c)}</span>`:""}
${leg.s?`<span><i style="background:#5b6eae"></i>${t(leg.s)}</span>`:""}
${leg.a?`<span><i style="background:#6d5b95"></i>${t(leg.a)}</span>`:""}
</div></div>`;
}

const EXT_KEYS=["extGFs","extGR2","extGR3","extGPl","extGR4","extGEq","extGMed","extGPre","extGR5","extGCo","extGEn"];
const HPLC_KEYS=["gFs","gEng","gFeed","gDd","gLySpec","gLyMfg","gLyFat","gLyShip","gLyVal","gHplcSpec","gHplcMfg","gHplcFat","gHplcShip","gTanks","gWaste","gRetrofit"];
const C1_KEYS=["c1Scope","c1Dd","c1Build","c1IQ"];
const HIPO_KEYS=["hFund","hConsult","hContractor","hAward","hSurvey","hLabDesign","hCdm","hIso","hFume","hFurn","hTrade","hConstr","hComm","hRisk"];

function deckHTML(){
return `
<section class="slide active title-slide"><p><span class="tag">${t("tag")}</span></p>
<h1>${t("p1t")}</h1><h2>${t("p1s")}</h2><p style="color:var(--muted);margin-top:.8rem;font-size:.88rem">${t("p1m")}</p></section>

<section class="slide"><h1>${t("p2t")}</h1><h2>${t("p2s")}</h2>
<div class="card" style="flex:1;overflow:auto"><table class="compare-table"><thead><tr>
<th>${t("p2th1")}</th><th>${t("p2th2")}</th><th>${t("p2th3")}</th><th>${t("p2th4")}</th>
</tr></thead><tbody>
<tr><td><strong>${t("p2r1n")}</strong></td><td>${t("p2r1s")}</td><td>${t("p2r1o")}</td><td>${t("p2r1d")}</td></tr>
<tr><td><strong>${t("p2r2n")}</strong></td><td>${t("p2r2s")}</td><td>${t("p2r2o")}</td><td>${t("p2r2d")}</td></tr>
<tr><td><strong>${t("p2r3n")}</strong></td><td>${t("p2r3s")}</td><td>${t("p2r3o")}</td><td>${t("p2r3d")}</td></tr>
<tr><td><strong>${t("p2r4n")}</strong></td><td>${t("p2r4s")}</td><td>${t("p2r4o")}</td><td>${t("p2r4d")}</td></tr>
</tbody></table>
<div class="callout">${t("p2link")}</div>
<div class="callout">${t("p2rebase")}</div>
<div class="note">${t("p2sum")}</div></div></section>

<section class="slide section-slide"><p><span class="tag ext">${t("extTag")}</span></p>
<h1>${t("extSec")}</h1><p>${t("extSecs")}</p></section>

<section class="slide"><h1>${t("ext2t")}</h1><h2>${t("ext2s")}</h2>
<div class="kpi-row cols3">
<div class="kpi ext"><div class="val">${t("extK1")}</div><div class="lbl">${t("extK1d")}</div></div>
<div class="kpi ext"><div class="val">${t("extK2")}</div><div class="lbl">${t("extK2d")}</div></div>
<div class="kpi ext"><div class="val">${t("extK3")}</div><div class="lbl">${t("extK3d")}</div></div></div>
<ul><li>${t("extB1")}</li><li>${t("extB2")}</li><li>${t("extB3")}</li></ul></section>

<section class="slide"><h1>${t("ext5t")}</h1><h2>${t("ext5s")}</h2>
<div class="cost-scroll">${extCostHTML()}</div></section>

<section class="slide" data-charts="ext"><h1>${t("ext6t")}</h1><h2>${t("ext6s")}</h2>
<div class="invest-kpi-row">
<div class="invest-kpi highlight"><div class="ik-val">${fm(EXT_OOM)}</div><div class="ik-lbl">${t("ext6kOom")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(BASE_TOTAL) + r''')}</div><div class="ik-lbl">${t("ext6kBase")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(OTHER_TOTAL + GENERAL_RISK_TOTAL) + r''')}</div><div class="ik-lbl">${t("ext6kRisk")}</div></div></div>
<div class="grid-2">
<div class="card"><div class="chart-title">${t("extChL")}</div><div class="chart-wrap tall"><canvas id="cExt1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("extChR")}</div><div class="chart-wrap tall"><canvas id="cExt2"></canvas></div></div></div></section>

<section class="slide">${ganttHTML(GANTT_EXT,new Date("2026-07-01"),new Date("2030-05-07"),EXT_KEYS,["2026","2027","2028","2029","2030"],"''' + TODAY + r'''","extGSub",{d:"extLegD",p:"extLegP",b:"extLegB",c:"extLegM",today:"extToday"})}</section>

<section class="slide"><h1>${t("ext9t")}</h1>
<ul class="decision-list">
<li class="ext">${t("ext9d1")}</li><li class="ext">${t("ext9d2")}</li></ul></section>

<section class="slide section-slide"><p><span class="tag hplc">${t("hplcTag")}</span></p>
<h1>${t("hplcSec")}</h1><p>${t("hplcSecs")}</p></section>

<section class="slide"><h1>${t("hplc2t")}</h1><h2>${t("hplc2s")}</h2>
<div class="kpi-row">
<div class="kpi hplc"><div class="val">${t("hplcK1")}</div><div class="lbl">${t("hplcK1d")}</div></div>
<div class="kpi hplc"><div class="val">${t("hplcK2")}</div><div class="lbl">${t("hplcK2d")}</div></div>
<div class="kpi hplc"><div class="val">${t("hplcK3")}</div><div class="lbl">${t("hplcK3d")}</div></div>
<div class="kpi hplc"><div class="val">${t("hplcK4")}</div><div class="lbl">${t("hplcK4d")}</div></div></div>
<ul><li>${t("hplcB1")}</li><li>${t("hplcB2")}</li><li>${t("hplcB3")}</li><li>${t("hplcB4")}</li></ul></section>

<section class="slide"><h1>${t("hplc3t")}</h1>
<div class="scope-grid">
<div class="card"><h3>${t("hplcT1")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("hplcT1a")}</li><li>${t("hplcT1b")}</li><li>${t("hplcT1c")}</li></ul></div>
<div class="card"><h3>${t("hplcT2")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("hplcT2a")}</li><li>${t("hplcT2b")}</li><li>${t("hplcT2c")}</li></ul></div></div></section>

<section class="slide"><h1>${t("hplc5t")}</h1><h2>${t("hplc5s")}</h2>
<div class="cost-scroll">${hplcCostHTML()}</div></section>

<section class="slide" data-charts="hplc"><h1>${t("hplc6t")}</h1><h2>${t("hplc6s")}</h2>
<div class="invest-kpi-row cols4">
<div class="invest-kpi highlight"><div class="ik-val">${fm(''' + str(HPLC_OOM) + r''')}</div><div class="ik-lbl">${t("hplc6kOom")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(DIRECT_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kDirect")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(INDIRECT_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kIndirect")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(GEN_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kGen")}</div></div></div>
<div class="invest-kpi-row cols2 direct-sub">
<div class="invest-kpi invest-kpi-mid"><div class="ik-val">${fm(''' + str(MAIN_EQUIP_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kMain")}</div></div>
<div class="invest-kpi invest-kpi-mid"><div class="ik-val">${fm(''' + str(INFRA_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kInfra")}</div></div></div>
<div class="grid-2">
<div class="card"><div class="chart-title">${t("hplcChL")}</div><div class="chart-wrap tall"><canvas id="cHplc1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("hplcChR")}</div><div class="chart-wrap tall"><canvas id="cHplc2"></canvas></div></div></div></section>

<section class="slide"><h1>${t("hplc7t")}</h1><h2>${t("hplc7s")}</h2>
<div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:.45rem">
<div class="kpi"><div class="val">${t("hplc7k1")}</div><div class="lbl">${t("hplc7k1d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k2")}</div><div class="lbl">${t("hplc7k2d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k3")}</div><div class="lbl">${t("hplc7k3d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k4")}</div><div class="lbl">${t("hplc7k4d")}</div></div></div>
${ganttHTML(GANTT_HPLC,new Date("2026-05-01"),new Date("2028-03-31"),HPLC_KEYS,["2026 H1","2026 H2","2027 H1","2027 H2","2028 H1"],"''' + TODAY + r'''","hplcGSub",{d:"legDone",p:"legPlan",b:"legBuild",c:"legCrit",s:"legStaff",a:"legAssume",today:"today"})}</section>

<section class="slide"><h1>${t("hplc9t")}</h1>
<ul class="decision-list">
<li class="hplc">${t("hplc9d1")}</li><li class="hplc">${t("hplc9d2")}</li></ul></section>

<section class="slide section-slide"><p><span class="tag c1">${t("c1Tag")}</span></p>
<h1>${t("c1Sec")}</h1><p>${t("c1Secs")}</p></section>

<section class="slide"><h1>${t("c12t")}</h1><h2>${t("c12s")}</h2>
<div class="kpi-row cols3">
<div class="kpi c1"><div class="val">${t("c1K1")}</div><div class="lbl">${t("c1K1d")}</div></div>
<div class="kpi c1"><div class="val">${t("c1K2")}</div><div class="lbl">${t("c1K2d")}</div></div>
<div class="kpi c1"><div class="val">${t("c1K3")}</div><div class="lbl">${t("c1K3d")}</div></div></div>
<ul><li>${t("c1B1")}</li><li>${t("c1B2")}</li><li>${t("c1B5")}</li><li>${t("c1B3")}</li><li>${t("c1B4")}</li></ul></section>

<section class="slide"><h1>${t("c13t")}</h1>
<div class="scope-grid">
<div class="card"><h3>${t("c1S1")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("c1S1a")}</li><li>${t("c1S1b")}</li></ul></div>
<div class="card"><h3>${t("c1S2")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("c1S2a")}</li><li>${t("c1S2b")}</li></ul></div>
<div class="card"><h3>${t("c1S3")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("c1S3a")}</li><li>${t("c1S3b")}</li></ul></div>
<div class="card"><h3>${t("c1S4")}</h3><ul style="font-size:.78rem;margin-top:.35rem"><li>${t("c1S4a")}</li><li>${t("c1S4b")}</li><li>${t("c1S4c")}</li></ul></div></div></section>

<section class="slide"><h1>${t("c15t")}</h1><h2>${t("c15s")}</h2>
<div class="cost-scroll">${c1CostHTML()}</div></section>

<section class="slide" data-charts="c1"><h1>${t("c16t")}</h1><h2>${t("c16s")}</h2>
<div class="invest-kpi-row cols3">
<div class="invest-kpi highlight"><div class="ik-val">${fm(''' + str(C1_OOM) + r''')}</div><div class="ik-lbl">${t("c16kOom")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(C1_EQUIP_SUB) + r''')}</div><div class="ik-lbl">${t("c16kEquip")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(C1_PROJECT_CONT) + r''')}</div><div class="ik-lbl">${t("c16kCont")}</div></div></div>
<div class="grid-2">
<div class="card"><div class="chart-title">${t("c1ChL")}</div><div class="chart-wrap tall"><canvas id="cC11"></canvas></div></div>
<div class="card"><div class="chart-title">${t("c1ChR")}</div><div class="chart-wrap tall"><canvas id="cC12"></canvas></div></div></div></section>

<section class="slide"><h1>${t("c17t")}</h1><h2>${t("c17s")}</h2>
<div class="kpi-row cols3" style="margin-bottom:.45rem">
<div class="kpi"><div class="val">${t("c17k1")}</div><div class="lbl">${t("c17k1d")}</div></div>
<div class="kpi"><div class="val">${t("c17k2")}</div><div class="lbl">${t("c17k2d")}</div></div>
<div class="kpi"><div class="val">${t("c17k3")}</div><div class="lbl">${t("c17k3d")}</div></div></div>
<div class="kpi-row cols3" style="margin-bottom:.5rem">
<div class="kpi"><div class="val">${t("c17k4")}</div><div class="lbl">${t("c17k4d")}</div></div></div>
${ganttHTML(GANTT_C1,new Date("2026-08-01"),new Date("2027-10-31"),C1_KEYS,["2026 H2","2027 H1","2027 H2"],"''' + TODAY + r'''","c1GSub",{p:"c1LegP",w:"c1LegWarn",b:"c1LegB",today:"c1Today"})}</section>

<section class="slide"><h1>${t("c19t")}</h1>
<ul class="decision-list">
<li class="c1">${t("c19d1")}</li><li class="c1">${t("c19d2")}</li></ul></section>

<section class="slide section-slide"><p><span class="tag hipo">${t("hipoTag")}</span></p>
<h1>${t("hipoSec")}</h1><p>${t("hipoSecs")}</p></section>

<section class="slide"><h1>${t("hipo2t")}</h1><h2>${t("hipo2s")}</h2>
<div class="kpi-row">
<div class="kpi hipo"><div class="val">${t("hipoK1")}</div><div class="lbl">${t("hipoK1d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipoK2")}</div><div class="lbl">${t("hipoK2d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipoK3")}</div><div class="lbl">${t("hipoK3d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipoK4")}</div><div class="lbl">${t("hipoK4d")}</div></div></div>
<ul><li>${t("hipoB1")}</li><li>${t("hipoB2")}</li><li>${t("hipoB3")}</li><li>${t("hipoB4")}</li><li>${t("hipoB5")}</li></ul></section>

<section class="slide"><h1>${t("hipo3t")}</h1><h2>${t("hipo3s")}</h2>
<div class="scope-grid">
<div class="card"><h3>${t("hipoS1")}</h3><ul style="font-size:.78rem;margin-top:.35rem"><li>${t("hipoS1a")}</li><li>${t("hipoS1b")}</li><li>${t("hipoS1c")}</li></ul></div>
<div class="card"><h3>${t("hipoS2")}</h3><ul style="font-size:.78rem;margin-top:.35rem"><li>${t("hipoS2a")}</li><li>${t("hipoS2b")}</li><li>${t("hipoS2c")}</li><li>${t("hipoS2d")}</li></ul></div>
<div class="card"><h3>${t("hipoS3")}</h3><ul style="font-size:.78rem;margin-top:.35rem"><li>${t("hipoS3a")}</li><li>${t("hipoS3b")}</li><li>${t("hipoS3c")}</li></ul></div>
<div class="card"><h3>${t("hipoS4")}</h3><ul style="font-size:.78rem;margin-top:.35rem"><li>${t("hipoS4a")}</li><li>${t("hipoS4b")}</li><li>${t("hipoS4c")}</li></ul></div></div>
<div class="callout">${t("hipoScopeNote")}</div></section>

<section class="slide"><h1>${t("hipo5t")}</h1><h2>${t("hipo5s")}</h2>
<div class="cost-scroll">${hipoCostHTML()}</div></section>

<section class="slide" data-charts="hipo"><h1>${t("hipo6t")}</h1><h2>${t("hipo6s")}</h2>
<div class="invest-kpi-row cols5">
<div class="invest-kpi highlight"><div class="ik-val">${fm(''' + str(HIPO_TOTAL) + r''')}</div><div class="ik-lbl">${t("hipo6kTotal")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(HIPO_BUILDING_WORKS) + r''')}</div><div class="ik-lbl">${t("hipo6kBuild")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(HIPO_CLIENT_EQUIP) + r''')}</div><div class="ik-lbl">${t("hipo6kEquip")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(HIPO_RISK_ALLOWANCE) + r''')}</div><div class="ik-lbl">${t("hipo6kRisk")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(ACCURACY_LOWER) + r''')} – ${fm(''' + str(ACCURACY_UPPER) + r''')}</div><div class="ik-lbl">${t("hipo6kRange")}</div></div></div>
<div class="grid-2">
<div class="card"><div class="chart-title">${t("hipoChL")}</div><div class="chart-wrap"><canvas id="cHipo1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("hipoChR")}</div><div class="chart-wrap"><canvas id="cHipo2"></canvas></div></div></div></section>

<section class="slide"><h1>${t("hipo7t")}</h1><h2>${t("hipo7s")}</h2>
<div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:.45rem">
<div class="kpi hipo"><div class="val">${t("hipo7k1")}</div><div class="lbl">${t("hipo7k1d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipo7k2")}</div><div class="lbl">${t("hipo7k2d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipo7k3")}</div><div class="lbl">${t("hipo7k3d")}</div></div>
<div class="kpi hipo"><div class="val">${t("hipo7k4")}</div><div class="lbl">${t("hipo7k4d")}</div></div></div>
${ganttHTML(GANTT_HIPO,new Date("2026-09-01"),new Date("2027-12-15"),HIPO_KEYS,["2026 H2","2027 H1","2027 H2"],"''' + TODAY + r'''","hipoGSub",{p:"hipoLegP",w:"hipoLegW",b:"hipoLegB",today:"hipoToday"})}
<div class="note">${t("hipoProgNote")}</div></section>

<section class="slide"><h1>${t("hipo9t")}</h1>
<ul class="decision-list">
<li class="hipo">${t("hipo9d1")}</li><li class="hipo">${t("hipo9d2")}</li><li class="hipo">${t("hipo9d3")}</li></ul></section>

<section class="slide title-slide"><h1>${t("pEnd")}</h1></section>`;
}

function bindGanttTips(){
document.querySelectorAll(".gantt-bar").forEach(el=>{
el.addEventListener("mouseenter",e=>{
const tip=document.getElementById("tip");
tip.querySelector(".td").textContent=el.dataset.dates;
tip.querySelector(".tb").textContent=lang==="zh"?el.dataset.zh:el.dataset.en;
tip.classList.add("show");moveTip(e);});
el.addEventListener("mousemove",moveTip);
el.addEventListener("mouseleave",()=>document.getElementById("tip").classList.remove("show"));
});
}
function moveTip(e){const tip=document.getElementById("tip");
let x=e.clientX+12,y=e.clientY+12;
if(x+360>innerWidth)x=e.clientX-340;
if(y+80>innerHeight)y=e.clientY-70;
tip.style.left=x+"px";tip.style.top=y+"px";}

function buildCharts(which){
const zh=lang==="zh";
if(which==="ext"&&!chartsBuilt.ext){buildExtInvestmentCharts();chartsBuilt.ext=true;}
if(which==="hplc"&&!chartsBuilt.hplc){buildHplcInvestmentCharts();chartsBuilt.hplc=true;}
if(which==="c1"&&!chartsBuilt.c1){buildC1InvestmentCharts();chartsBuilt.c1=true;}
if(which==="hipo"&&!chartsBuilt.hipo){buildHipoInvestmentCharts();chartsBuilt.hipo=true;}
}

function applyLang(){
document.documentElement.lang=lang==="zh"?"zh-CN":"en";
const saved=idx;
chartsBuilt={};
document.getElementById("deck").innerHTML=deckHTML();
document.getElementById("footerText").textContent=t("footer");
document.getElementById("navHint").textContent=t("nav");
document.getElementById("btnZh").classList.toggle("active",lang==="zh");
document.getElementById("btnEn").classList.toggle("active",lang==="en");
bindGanttTips();
show(saved);
}
function slides(){return document.querySelectorAll(".slide");}
function show(n){
const s=slides();idx=(n+s.length)%s.length;
s.forEach((el,i)=>el.classList.toggle("active",i===idx));
document.getElementById("counter").textContent=(idx+1)+" / "+s.length;
const ch=s[idx].dataset.charts;
if(ch)buildCharts(ch);
}
document.getElementById("btnZh").onclick=()=>{if(lang!=="zh"){lang="zh";applyLang();}};
document.getElementById("btnEn").onclick=()=>{if(lang!=="en"){lang="en";applyLang();}};
document.addEventListener("keydown",e=>{
if(e.key==="ArrowRight"||e.key===" "||e.key==="PageDown"){e.preventDefault();show(idx+1);}
if(e.key==="ArrowLeft"||e.key==="PageUp"){e.preventDefault();show(idx-1);}
});
applyLang();
</script>
</body>
</html>'''

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HTML, encoding="utf-8")
    print("Wrote", OUT, len(HTML), "bytes")
