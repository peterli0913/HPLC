#!/usr/bin/env python3
"""Combined UK PDF portfolio briefing: B902 extension + HPLC/lyophilizer."""

import importlib.util
import json
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
from hplc_feasibility_cost import (
    CHART_I18N_EN as HPLC_CHART_I18N_EN,
    CHART_I18N_ZH as HPLC_CHART_I18N_ZH,
    DIRECT_TOTAL,
    GEN_TOTAL,
    HPLC_COST_I18N_EN,
    HPLC_COST_I18N_ZH,
    HPLC_COST_RENDER_JS,
    HPLC_OOM,
    OTHER_TOTAL as HPLC_OTHER_TOTAL,
    hplc_cost_data_json,
)

ROOT = Path(__file__).resolve().parent
OUT = Path("/workspace/汇报/UK-PDF-Portfolio/UK_PDF_Portfolio_Briefing_2026-05-28.html")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hplc = _load_module("hplc_brief", ROOT / "build_hplc_lyopho_briefing.py")
ext = _load_module("ext_brief", ROOT / "build_management_briefing.py")

# Extension OOM totals from ext_feasibility_cost (CM-0001)

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Asymchem UK — PDF Portfolio Briefing</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--navy:#0f2b46;--teal:#009688;--accent:#c9a227;--ext:#1a4a6e;--hplc:#5b6eae;--bg:#f4f6f8;--card:#fff;--text:#2c3e50;--muted:#5a6a7a;--warn:#b43a2a}
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
.tag.ext{background:var(--ext)} .tag.hplc{background:var(--hplc)}
ul{margin-left:1.1rem;line-height:1.55;font-size:.88rem} li{margin-bottom:.34rem}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem;flex:1;min-height:0}
.card{background:var(--card);border-radius:10px;padding:1rem;border:1px solid #e8ecf0;box-shadow:0 2px 12px rgba(15,43,70,.06)}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin-bottom:.65rem}
.kpi-row.cols3{grid-template-columns:repeat(3,1fr)}
.kpi{background:var(--card);border-radius:10px;padding:.6rem .7rem;border-left:4px solid var(--teal)}
.kpi.ext{border-left-color:var(--ext)} .kpi.hplc{border-left-color:var(--hplc)}
.kpi .val{font-size:1.02rem;font-weight:700;color:var(--navy)} .kpi .lbl{font-size:.66rem;color:var(--muted);margin-top:.1rem;line-height:1.28}
table{width:100%;border-collapse:collapse;font-size:.78rem} th,td{padding:.34rem .45rem;border-bottom:1px solid #eef1f4;text-align:left} th{color:var(--navy)}
.footer{position:fixed;bottom:0;left:0;right:0;padding:.4rem 2.8rem;font-size:.68rem;color:var(--muted);background:rgba(255,255,255,.96);border-top:1px solid #e8ecf0;display:flex;justify-content:space-between}
.title-slide{justify-content:center;text-align:center;padding-top:2.5rem} .title-slide h1{font-size:1.8rem}
.section-slide{justify-content:center;text-align:center} .section-slide h1{font-size:2rem}
.section-slide p{color:var(--muted);margin-top:.6rem;font-size:.95rem}
.chart-title{font-size:.8rem;font-weight:600;color:var(--navy);margin-bottom:.35rem;text-align:center}
.chart-wrap{height:200px;position:relative} .chart-wrap.tall{height:240px}
.invest-kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-bottom:.65rem}
.invest-kpi{background:linear-gradient(160deg,#f8fafb,#fff);border:1px solid #e8ecf0;border-radius:10px;padding:.5rem;text-align:center}
.invest-kpi.highlight{border-color:#d4b84a;background:linear-gradient(160deg,#fffdf5,#fff)}
.invest-kpi .ik-val{font-size:.95rem;font-weight:700;color:var(--navy)}
.invest-kpi .ik-lbl{font-size:.62rem;color:var(--muted);margin-top:.15rem}
.cost-scroll{flex:1;overflow-y:auto;min-height:0}
''' + EXT_COST_CSS + r'''
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
.gantt-axis{display:flex;justify-content:space-between;font-size:.63rem;color:var(--muted);padding:0 0 .22rem 7.5rem;border-bottom:1px solid #dde3e8;margin-bottom:.22rem}
.gantt-body{flex:1;overflow-y:auto}
.gantt-row{display:grid;grid-template-columns:7rem 1fr 4.6rem;gap:.3rem;margin-bottom:.3rem;align-items:center}
.gantt-label{font-size:.63rem;font-weight:600;color:var(--navy);text-align:right;line-height:1.1}
.gantt-track{position:relative;height:19px;background:#eef2f6;border-radius:4px}
.gantt-bar{position:absolute;top:2px;height:15px;border-radius:3px;min-width:3px;cursor:pointer}
.gantt-bar.done{background:var(--teal)} .gantt-bar.plan{background:#1a4a6e}
.gantt-bar.assume{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 5px,#8f7db8 5px,#8f7db8 10px)}
.gantt-bar.warn{background:var(--accent)} .gantt-bar.build{background:#2e6da4} .gantt-bar.staff{background:#5b6eae}
.gantt-dates{font-size:.58rem;color:var(--muted)}
.gantt-legend{font-size:.6rem;color:var(--muted);margin-top:.3rem;display:flex;gap:.55rem;flex-wrap:wrap}
.gantt-legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:.15rem;vertical-align:middle}
.today-line{position:absolute;top:0;bottom:0;width:2px;background:var(--warn);z-index:2;pointer-events:none}
.today-tag{position:absolute;top:-10px;font-size:.52rem;color:var(--warn);transform:translateX(-50%);white-space:nowrap}
#tip{position:fixed;z-index:300;max-width:360px;background:var(--navy);color:#fff;padding:.5rem .65rem;border-radius:8px;font-size:.72rem;line-height:1.45;pointer-events:none;opacity:0;transition:opacity .12s;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#tip.show{opacity:1} #tip .td{color:#8ecec6;font-size:.65rem;margin-bottom:.15rem}
.decision-list{list-style:none;margin:0;padding:0}
.decision-list li{border:1px solid #e8ecf0;border-left:4px solid var(--teal);padding:.7rem .9rem;margin-bottom:.45rem;border-radius:0 8px 8px 0;font-size:.86rem;background:var(--card)}
.decision-list li.ext{border-left-color:var(--ext)} .decision-list li.hplc{border-left-color:var(--hplc)}
</style>
</head>
<body>
<div class="top-bar"></div>
<div class="lang-switch"><button id="btnZh" class="active" type="button">中文</button><button id="btnEn" type="button">EN</button></div>
<div id="tip"><div class="td"></div><div class="tb"></div></div>
<div id="deck"></div>
<div class="footer"><span id="footerText"></span><span id="navHint"></span><span id="counter"></span></div>
<script>
const GANTT_EXT = ''' + json.dumps(ext.GANTT_JS) + r''';
const GANTT_HPLC = ''' + json.dumps(hplc.GANTT_CALENDAR) + r''';
const CAPEX = ''' + json.dumps(hplc.CAPEX) + r''';
const HPLC_RISK = ''' + json.dumps(hplc.RISK_ON_BASE) + r''';
const HPLC_COST_DATA = ''' + hplc_cost_data_json() + r''';
const EXT_OOM = ''' + str(EXT_OOM) + r''';
const EXT_COST_DATA = ''' + ext_cost_data_json() + r''';
''' + EXT_COST_RENDER_JS + HPLC_COST_RENDER_JS + r'''
let lang="zh", idx=0, chartsBuilt = {};

const I18N={
zh:{
footer:"凯莱英 UK · Sandwich PDF 资本项目",
nav:"← → 翻页", tag:"内部汇报 · 整体汇报",
p1t:"凯莱英 UK · Sandwich PDF", p1s:"资本项目汇报", p1m:"B902 东侧扩建 + 厂房内 HPLC/冻干改造 · 2026年5月",
p2t:"项目概览", p2s:"两条独立工作流 · 可行性阶段 OOM",
p2th1:"子项目", p2th2:"范围", p2th3:"OOM（可行性量级）", p2th4:"关键节点",
p2r1n:"B902 东侧扩建", p2r1s:"新建四层+夹层，反应/加氢/过滤干燥", p2r1o:"£78.1M", p2r1d:"2030-05 竣工",
p2r2n:"HPLC + 冻干", p2r2s:"既有 PDF  footprint 改造", p2r2o:"£5.67M", p2r2d:"2027-09 HPLC / 12 月冻干",
extTag:"扩建", hplcTag:"改造",
extSec:"一、B902 东侧扩建", extSecs:"Scitech · RIBA Stage 1 · 300291-RE-0001",
ext2t:"扩建 · 执行摘要", ext2s:"2026-05-22 · Issue A1",
extK1:"FS 完成", extK1d:"RIBA 1",
extK2:"£78.1M", extK2d:"项目 OOM",
extK3:"2030-05", extK3d:"总控完成",
extB1:"范围：东侧约 600 m²，四层+设备夹层，10 台反应釜、2500 L 加氢釜、3 套过滤干燥机及公用工程。",
extB2:"方案：Option 1 — 拆除/迁址原加氢厂房；与 902 低层楼面贯通。",
extB3:"进展：FS 完成；RIBA 2 概念设计计划 2026-07 启动。",
ext4t:"扩建 · 范围基线", ext4s:"Option 1",
ext4b1:"GIFA 约 3,099 m²；防洪抬升约 1.5 m", ext4b2:"第二疏散梯；加氢区泄压板", ext4b3:"BREEAM 预评估 Very Good 基线",
ext5t:"扩建 · 投资总览", ext5s:"300291-CM-0001",
ext5oom:"OOM 总价",
ext6t:"扩建 · 投资结构", ext6s:"OOM 构成与基础建造费分项",
ext6kOom:"OOM 总价", ext6kBase:"基础建造成本（含 20%）", ext6kRisk:"其他费及可行性风险",
extCost:''' + json.dumps(EXT_COST_I18N_ZH, ensure_ascii=False) + r''',extChart:''' + json.dumps(EXT_CHART_I18N_ZH, ensure_ascii=False) + r''',
extChL:"项目 OOM 三板块", extChR:"基础建造成本 — 分项",
ext8t:"扩建 · 整体周期", ext8s:"300291-PM-PR-0002",
extGSub:"总控时间轴（条块长度按日历比例）",
extGFs:"可行性 RIBA 1", extGR2:"概念 RIBA 2", extGR3:"方案 RIBA 3", extGPl:"规划",
extGR4:"详细 RIBA 4", extGEq:"长周期设备", extGMed:"中等周期设备", extGPre:"施工准备",
extGR5:"施工 RIBA 5", extGCo:"调试", extGEn:"验证/竣工",
extLegD:"已完成", extLegP:"设计", extLegB:"施工", extLegM:"节点", extToday:"约今",
ext9t:"扩建 · 决策事项", ext9d1:"是否批准进入 RIBA 2（概念设计）？",
ext9d2:"是否推进模块化建造方案比选？",
hplcSec:"二、厂房内 HPLC + 冻干", hplcSecs:"RBPC · Project 9802 · P01",
hplc2t:"改造 · 执行摘要", hplc2s:"9802-RBP-ZZ-ZZ-RP-X-100000",
hplcK1:"技术可行", hplcK1d:"FS P01",
hplcK2:"£5.67M", hplcK2d:"OOM（×1.5）",
hplcK3:"2027-09", hplcK3d:"HPLC 目标",
hplcK4:"2027-12", hplcK4d:"冻干目标",
hplcB1:"范围：制备 HPLC（DAC300/CP300）+ 冻干机（隔离器、除湿、纯蒸汽发生器等）及配套改造。",
hplcB2:"投资：基础 £3.78M + 风险预备费块；非最终 Capex。",
hplcB3:"周期：冻干机长周期驱动；优先冻干后 HPLC。",
hplc3t:"改造 · 范围", hplc3s:"",
hplcT1:"HPLC", hplcT1a:"DAC300/CP300 泵撬；移动头罐；2000 L 废液罐",
hplcT1b:"Hanbon 供货", hplcT1c:"PG.05 区域安装",
hplcT2:"冻干机", hplcT2a:"冻干腔、隔离器、双 CIP、除湿、PSG",
hplcT2b:"Asymchem 供货", hplcT2c:"气闸/改造约 20 周",
hplc5t:"改造 · 投资总览", hplc5s:"9802-RBP-ZZ-ZZ-CP-X-100001",
hplc5oom:"OOM 总价（可行性量级）",
hplc6t:"改造 · 投资结构", hplc6s:"与 CP-X-100001 一致",
hplc6kOom:"OOM 总价", hplc6kBase:"直接工程费（含 20%）", hplc6kRisk:"其他费及 OOM 预备费",
hplcCost:''' + json.dumps(HPLC_COST_I18N_ZH, ensure_ascii=False) + r''',hplcChart:''' + json.dumps(HPLC_CHART_I18N_ZH, ensure_ascii=False) + r''',
hplcChL:"项目 OOM 三板块", hplcChR:"直接工程费 — 分项",
hplc7t:"改造 · 周期", hplc7s:"FS §4.4 图 1",
hplc7k1:"冻干制造", hplc7k1d:"8–10 月",
hplc7k2:"HPLC 供货", hplc7k2d:"~18 周",
hplc7k3:"FEED", hplc7k3d:"12–14 周",
hplc7k4:"详细设计", hplc7k4d:"18–20 周",
hplcGSub:"High Level Programme",
gFs:"FS/基准", gEng:"Engineer就位", gFeed:"FEED（示意）", gDd:"详细设计（示意）",
gLySpec:"冻干规格/资金", gLyMfg:"冻干制造", gLyFat:"冻干 FAT", gLyShip:"冻干运输安装", gLyVal:"冻干验证→PQ",
gHplcSpec:"HPLC 规格/资金", gHplcMfg:"HPLC 制造", gHplcFat:"HPLC FAT", gHplcShip:"HPLC 运输安装",
gTanks:"移动头罐", gWaste:"废液罐", gRetrofit:"改造",
legDone:"完成", legStaff:"工程师就位", legPlan:"采购/制造", legBuild:"施工/验证",
legCrit:"关键路径", legAssume:"§4.3 示意", today:"约今",
hplc9t:"改造 · 决策", hplc9d1:"是否批准进入 FEED？",
hplc9d2:"是否批准长周期设备早期采购资金？",
pDecT:"组合 · 提请关注", pDecS:"",
pDec1:"两条线独立决策与资金路径；汇报 OOM 均为可行性量级。",
pDec2:"扩建：RIBA 2 与模块化比选。",
pDec3:"改造：FEED 启动与冻干/HPLC 长周期采购。",
pDec4:"费用对外材料需统一口径（勿直接递交设计方原报告）。",
pEnd:"谢谢", pEnds:"",
},
en:{
footer:"Asymchem UK · Sandwich PDF Portfolio",
nav:"← → navigate", tag:"Internal · Portfolio briefing",
p1t:"Asymchem UK · Sandwich PDF", p1s:"Capital Projects Briefing", p1m:"B902 extension + in-situ HPLC/lyoph · May 2026",
p2t:"Project overview", p2s:"Two workstreams · feasibility OOM",
p2th1:"Workstream", p2th2:"Scope", p2th3:"OOM (feasibility)", p2th4:"Milestone",
p2r1n:"B902 east extension", p2r1s:"New 4-floor + mezzanine", p2r1o:"£78.1M", p2r1d:"Complete May 2030",
p2r2n:"HPLC + lyophilizer", p2r2s:"Retrofit in existing PDF", p2r2o:"£5.67M", p2r2d:"HPLC Sep 2027 / lyoph Dec",
extTag:"Extension", hplcTag:"Retrofit",
extSec:"I. B902 East Extension", extSecs:"Scitech · RIBA 1 · 300291-RE-0001",
ext2t:"Extension · Summary", ext2s:"22 May 2026 · A1",
extK1:"FS done", extK1d:"RIBA 1",
extK2:"£78.1M", extK2d:"Project OOM",
extK3:"May 2030", extK3d:"Programme end",
extB1:"~600 m² east extension, 4 floors + mezzanine, reactors, H₂ suite, 3 filter dryers, utilities.",
extB2:"Option 1 — remove/relocate H₂ building; tie to B902 lower floors.",
extB3:"FS complete; RIBA 2 Concept from Jul 2026.",
ext4t:"Extension · Scope", ext4s:"Option 1",
ext4b1:"~3,099 m² GIFA; ~1.5 m flood lift", ext4b2:"Second escape stair; blast panels", ext4b3:"BREEAM pre-assessment baseline",
ext5t:"Extension · Investment", ext5s:"300291-CM-0001",
ext5oom:"Total OOM",
ext6t:"Extension · Structure", ext6s:"OOM build-up",
ext6kOom:"Total OOM", ext6kBase:"Base construction (incl. 20%)", ext6kRisk:"Other costs & feasibility risk",
extCost:''' + json.dumps(EXT_COST_I18N_EN, ensure_ascii=False) + r''',extChart:''' + json.dumps(EXT_CHART_I18N_EN, ensure_ascii=False) + r''',
extChL:"Project OOM — three blocks", extChR:"Base construction — line items",
ext8t:"Extension · Programme", ext8s:"300291-PM-PR-0002",
extGSub:"Master programme",
extGFs:"FS RIBA 1", extGR2:"Concept RIBA 2", extGR3:"Scheme RIBA 3", extGPl:"Planning",
extGR4:"Detail RIBA 4", extGEq:"Long-lead equip.", extGMed:"Medium-lead equip.", extGPre:"Pre-construction",
extGR5:"Construction RIBA 5", extGCo:"Commissioning", extGEn:"Validation/complete",
extLegD:"Done", extLegP:"Design", extLegB:"Build", extLegM:"Milestone", extToday:"~Today",
ext9t:"Extension · Decisions", ext9d1:"Approve RIBA 2 (Concept Design)?",
ext9d2:"Proceed with modular construction option study?",
hplcSec:"II. HPLC + Lyophilizer", hplcSecs:"RBPC · 9802 · P01",
hplc2t:"Retrofit · Summary", hplc2s:"9802-RBP-ZZ-ZZ-RP-X-100000",
hplcK1:"Feasible", hplcK1d:"FS P01",
hplcK2:"£5.67M", hplcK2d:"OOM (×1.5)",
hplcK3:"Sep 2027", hplcK3d:"HPLC target",
hplcK4:"Dec 2027", hplcK4d:"Lyoph target",
hplcB1:"Prep HPLC + lyophilizer (isolator, dehumidifier, PSG, etc.) and enabling works.",
hplcB2:"Base £3.78M + risk blocks; not final Capex.",
hplcB3:"Lyophilizer lead time drives; lyoph before HPLC.",
hplc3t:"Retrofit · Scope", hplc3s:"",
hplcT1:"HPLC", hplcT1a:"DAC300/CP300; mobile tanks; 2,000 L waste hold",
hplcT1b:"Hanbon supply", hplcT1c:"Install PG.05",
hplcT2:"Lyophilizer", hplcT2a:"Dryer, isolator, twin CIP, dehumidifier, PSG",
hplcT2b:"Asymchem supply", hplcT2c:"Airlock ~20 weeks",
hplc5t:"Retrofit · Investment", hplc5s:"9802-CP-X-100001",
hplc5oom:"Total OOM",
hplc6t:"Retrofit · Structure", hplc6s:"Aligned to CP-X-100001",
hplc6kOom:"Total OOM", hplc6kBase:"Direct works (incl. 20%)", hplc6kRisk:"Other costs & OOM contingency",
hplcCost:''' + json.dumps(HPLC_COST_I18N_EN, ensure_ascii=False) + r''',hplcChart:''' + json.dumps(HPLC_CHART_I18N_EN, ensure_ascii=False) + r''',
hplcChL:"Project OOM — three blocks", hplcChR:"Direct works — line items",
hplc7t:"Retrofit · Programme", hplc7s:"FS §4.4 Fig. 1",
hplc7k1:"Lyoph build", hplc7k1d:"8–10 mo",
hplc7k2:"HPLC supply", hplc7k2d:"~18 wk",
hplc7k3:"FEED", hplc7k3d:"12–14 wk",
hplc7k4:"Detail design", hplc7k4d:"18–20 wk",
hplcGSub:"High Level Programme",
gFs:"FS/baseline", gEng:"Engineer mobilised", gFeed:"FEED (illustrative)", gDd:"Detail design (illustrative)",
gLySpec:"Lyoph spec/funding", gLyMfg:"Lyoph build", gLyFat:"Lyoph FAT", gLyShip:"Lyoph ship/install", gLyVal:"Lyoph val.→PQ",
gHplcSpec:"HPLC spec/funding", gHplcMfg:"HPLC build", gHplcFat:"HPLC FAT", gHplcShip:"HPLC ship/install",
gTanks:"Mobile tanks", gWaste:"Waste tank", gRetrofit:"Retrofit",
legDone:"Complete", legStaff:"Engineer", legPlan:"Procure/build", legBuild:"Site/val.",
legCrit:"Critical", legAssume:"§4.3 illustrative", today:"~Today",
hplc9t:"Retrofit · Decisions", hplc9d1:"Approve progression to FEED?",
hplc9d2:"Approve early funding for long-lead packages?",
pDecT:"Portfolio · For attention", pDecS:"",
pDec1:"Separate decisions and funding; OOM = feasibility magnitude only.",
pDec2:"Extension: RIBA 2 and modular study.",
pDec3:"Retrofit: FEED and long-lead procurement.",
pDec4:"External packs need harmonised cost narrative (not raw consultant reports).",
pEnd:"Thank you", pEnds:"",
}
};

function t(k){return I18N[lang][k]||k;}
function fm(n){return "£"+Math.round(n).toLocaleString("en-GB");}

function ganttHTML(data,T0,T1,keys,axis,today,sub,leg){
const RANGE=T1-T0;
function pct(d){return Math.max(0,Math.min(100,((new Date(d)-T0)/RANGE)*100));}
let rows="";
data.forEach((g,i)=>{
const key=keys[i]||g[0];
const left=pct(g[1]),right=pct(g[2]),w=Math.max(1.2,right-left);
const d0=g[1].slice(0,7).replace("-","/"),d1=g[2].slice(0,7).replace("-","/");
rows+=`<div class="gantt-row"><div class="gantt-label">${t(key)}</div><div class="gantt-track">
${i===0?`<div class="today-line" style="left:${pct(today)}%"><span class="today-tag">${t(leg.today||"today")}</span></div>`:""}
<div class="gantt-bar ${g[3]}" style="left:${left}%;width:${w}%" data-en="${g[4].replace(/"/g,"&quot;")}" data-zh="${g[5].replace(/"/g,"&quot;")}" data-dates="${d0} – ${d1}"></div>
</div><div class="gantt-dates">${d0} – ${d1}</div></div>`;
});
return `<div class="gantt-wrap"><div class="chart-title">${t(sub)}</div>
<div class="gantt-axis">${axis.map(y=>`<span>${y}</span>`).join("")}</div>
<div class="gantt-body">${rows}</div>
<div class="gantt-legend">
<span><i style="background:var(--teal)"></i>${t(leg.d)}</span>
<span><i style="background:#1a4a6e"></i>${t(leg.p)}</span>
<span><i style="background:#2e6da4"></i>${t(leg.b)}</span>
<span><i style="background:var(--accent)"></i>${t(leg.c)}</span>
${leg.s?`<span><i style="background:#5b6eae"></i>${t(leg.s)}</span>`:""}
${leg.a?`<span><i style="background:#6d5b95"></i>${t(leg.a)}</span>`:""}
</div></div>`;
}

const EXT_KEYS=["extGFs","extGR2","extGR3","extGPl","extGR4","extGEq","extGMed","extGPre","extGR5","extGCo","extGEn"];
const HPLC_KEYS=["gFs","gEng","gFeed","gDd","gLySpec","gLyMfg","gLyFat","gLyShip","gLyVal","gHplcSpec","gHplcMfg","gHplcFat","gHplcShip","gTanks","gWaste","gRetrofit"];

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
</tbody></table></div></section>

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

<section class="slide">${ganttHTML(GANTT_EXT,new Date("2026-07-01"),new Date("2030-05-07"),EXT_KEYS,["2026","2027","2028","2029","2030"],"2026-05-28","extGSub",{d:"extLegD",p:"extLegP",b:"extLegB",c:"extLegM",today:"extToday"})}</section>

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
<ul><li>${t("hplcB1")}</li><li>${t("hplcB2")}</li><li>${t("hplcB3")}</li></ul></section>

<section class="slide"><h1>${t("hplc3t")}</h1><h2>${t("hplc3s")}</h2>
<div class="scope-grid">
<div class="card"><h3>${t("hplcT1")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("hplcT1a")}</li><li>${t("hplcT1b")}</li><li>${t("hplcT1c")}</li></ul></div>
<div class="card"><h3>${t("hplcT2")}</h3><ul style="font-size:.8rem;margin-top:.35rem"><li>${t("hplcT2a")}</li><li>${t("hplcT2b")}</li><li>${t("hplcT2c")}</li></ul></div></div></section>

<section class="slide"><h1>${t("hplc5t")}</h1><h2>${t("hplc5s")}</h2>
<div class="cost-scroll">${hplcCostHTML()}</div></section>

<section class="slide" data-charts="hplc"><h1>${t("hplc6t")}</h1><h2>${t("hplc6s")}</h2>
<div class="invest-kpi-row">
<div class="invest-kpi highlight"><div class="ik-val">${fm(''' + str(HPLC_OOM) + r''')}</div><div class="ik-lbl">${t("hplc6kOom")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(DIRECT_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kBase")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(''' + str(HPLC_OTHER_TOTAL + GEN_TOTAL) + r''')}</div><div class="ik-lbl">${t("hplc6kRisk")}</div></div></div>
<div class="grid-2">
<div class="card"><div class="chart-title">${t("hplcChL")}</div><div class="chart-wrap tall"><canvas id="cHplc1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("hplcChR")}</div><div class="chart-wrap tall"><canvas id="cHplc2"></canvas></div></div></div></section>

<section class="slide"><h1>${t("hplc7t")}</h1><h2>${t("hplc7s")}</h2>
<div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:.45rem">
<div class="kpi"><div class="val">${t("hplc7k1")}</div><div class="lbl">${t("hplc7k1d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k2")}</div><div class="lbl">${t("hplc7k2d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k3")}</div><div class="lbl">${t("hplc7k3d")}</div></div>
<div class="kpi"><div class="val">${t("hplc7k4")}</div><div class="lbl">${t("hplc7k4d")}</div></div></div>
${ganttHTML(GANTT_HPLC,new Date("2026-05-01"),new Date("2027-12-31"),HPLC_KEYS,["2026 H1","2026 H2","2027 H1","2027 H2"],"2026-05-28","hplcGSub",{d:"legDone",p:"legPlan",b:"legBuild",c:"legCrit",s:"legStaff",a:"legAssume",today:"today"})}</section>

<section class="slide"><h1>${t("hplc9t")}</h1>
<ul class="decision-list">
<li class="hplc">${t("hplc9d1")}</li><li class="hplc">${t("hplc9d2")}</li></ul></section>

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
