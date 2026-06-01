#!/usr/bin/env python3
"""Generate bilingual HPLC + Lyophilizer feasibility management briefing HTML."""

import json
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path("/workspace/汇报/HPLC-Lyophilizer/HPLC_Lyophilizer_Management_Briefing_2026-05-28.html")

GANTT_SHIFT_WEEKS = 4  # calendar offset applied to FEED → last row (not shown in UI copy)


def _add_weeks(date_str: str, weeks: int) -> str:
    return (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(weeks=weeks)).strftime(
        "%Y-%m-%d"
    )


def _shift_gantt_row(row: list, weeks: int = GANTT_SHIFT_WEEKS) -> list:
    return [row[0], _add_weeks(row[1], weeks), _add_weeks(row[2], weeks), *row[3:]]


# Fig. 1 dates (§4.4); engineer mobilisation Jun–Jul 2026
_GANTT_BASE = [
    ["gFs", "2026-05-19", "2026-05-26", "done",
     "FS report P01 (19 May 2026); programme baseline from 26 May 2026 (Fig. 1).",
     "可行性研究 P01（2026-05-19）；进度基准自 2026-05-26 起（图 1）。"],
    ["gFeed", "2026-06-15", "2026-09-20", "assume",
     "FEED 12–14 weeks (§4.3): illustrative, after engineer mobilisation.",
     "FEED 12–14 周（§4.3）：示意，工程师就位后启动。"],
    ["gDd", "2026-09-21", "2027-02-07", "assume",
     "Detailed design 18–20 weeks (§4.3): assumed after FEED, bar shows 20 weeks.",
     "详细设计 18–20 周（§4.3）：假设接 FEED 后启动，条块按 20 周示意。"],
    ["gLySpec", "2026-05-26", "2026-07-20", "warn",
     "Lyoph spec + funding/deposit (Fig. 1).",
     "冻干机规格确定和资金审批（图 1）。"],
    ["gLyMfg", "2026-07-28", "2027-04-05", "warn",
     "Lyophiliser build: 9 months (Fig. 1).",
     "冻干机制造：9 个月（图 1）。"],
    ["gLyFat", "2027-04-06", "2027-05-10", "warn",
     "Lyoph FAT + remediation (Fig. 1).",
     "冻干机 FAT（图 1）。"],
    ["gLyShip", "2027-05-11", "2027-08-30", "warn",
     "Lyoph shipping + installation (Fig. 1).",
     "冻干机运输安装（图 1）。"],
    ["gLyVal", "2027-08-31", "2027-11-08", "warn",
     "Lyoph validation to PQ complete (Fig. 1).",
     "冻干验证至 PQ 完成（图 1）。"],
    ["gHplcSpec", "2026-08-18", "2026-10-12", "plan",
     "HPLC spec + funding/deposit (Fig. 1).",
     "HPLC 规格确定和资金审批（图 1）。"],
    ["gHplcMfg", "2026-10-20", "2027-02-22", "plan",
     "HPLC manufacture: 18 weeks (Fig. 1).",
     "HPLC 制造：18 周（图 1）。"],
    ["gHplcFat", "2027-02-23", "2027-03-22", "plan",
     "HPLC FAT + remediation (Fig. 1).",
     "HPLC FAT（图 1）。"],
    ["gHplcShip", "2027-03-30", "2027-05-31", "plan",
     "HPLC shipping + installation (Fig. 1).",
     "HPLC 运输安装（图 1）。"],
    ["gTanks", "2026-07-21", "2027-05-03", "plan",
     "Procure mobile head tanks — RB Plant (Fig. 1).",
     "移动头罐采购（RB Plant）（图 1）。"],
    ["gWaste", "2026-07-21", "2027-04-19", "plan",
     "Procure waste tank — RB Plant (Fig. 1).",
     "废液罐采购（RB Plant）（图 1）。"],
    ["gRetrofit", "2026-12-24", "2027-04-15", "build",
     "Retrofit / demolition / airlock (Fig. 1; §4.3 ~20 wk).",
     "改造（拆除、气闸、分区等）（图 1；§4.3 约 20 周）。"],
]

GANTT_CALENDAR = [_GANTT_BASE[0]]
GANTT_CALENDAR.append(
    [
        "gEng",
        "2026-06-01",
        "2026-07-01",
        "staff",
        "Await SW engineer Keith to complete continuous hydrogenation project duties before transferring to this project.",
        "等待 SW 工程师 Keith 完成连续氢化项目相关事务后转入本项目。",
    ]
)
GANTT_CALENDAR.extend(_shift_gantt_row(r) for r in _GANTT_BASE[1:])
DURATION_ROWS = []

# 9802-RBP-ZZ-ZZ-CP-X-100001 (P01, 15 May 2026) — values in £
CAPEX = {
    "total": 3_783_000,
    "direct": 2_329_000,
    "A": 1_575_000,
    "A1": 200_000,
    "A2": 50_000,
    "A31": 358_000,
    "A32": 967_000,
    "B": 326_000,
    "C": 264_000,
    "D": 128_000,
    "E": 35_000,
    "F": 225_000,
    "G": 289_000,
    "H": 235_000,
    "I": 76_000,
    "J": 631_000,
}
# Extension-style OOM uplift on feasibility base (CapEx total)
RISK_ON_BASE = {
    "base": CAPEX["total"],
    "oom": round(CAPEX["total"] * 1.5),
    "c15": round(CAPEX["total"] * 0.15),
    "c25": round(CAPEX["total"] * 0.25),
    "c10": round(CAPEX["total"] * 0.10),
    "cont_total": round(CAPEX["total"] * 0.50),
}

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Asymchem UK — HPLC & Lyophilizer</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--navy:#0f2b46;--teal:#009688;--accent:#c9a227;--bg:#f4f6f8;--card:#fff;--text:#2c3e50;--muted:#5a6a7a;--warn:#b43a2a}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);overflow:hidden;height:100vh}
.slide{display:none;height:100vh;padding:2rem 2.8rem 3.2rem;flex-direction:column;animation:fade .3s ease}
.slide.active{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
.top-bar{position:fixed;top:0;left:0;right:0;height:6px;background:linear-gradient(90deg,var(--navy),var(--teal));z-index:100}
.lang-switch{position:fixed;top:.9rem;right:1.2rem;z-index:101;display:flex;border-radius:6px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.12);border:1px solid #dde3e8}
.lang-switch button{border:none;padding:.38rem .8rem;font-size:.78rem;cursor:pointer;background:#fff;color:var(--muted);font-weight:600}
.lang-switch button.active{background:var(--navy);color:#fff}
h1{font-size:1.65rem;color:var(--navy);font-weight:700;margin-bottom:.28rem}
h2{font-size:.92rem;color:var(--muted);font-weight:400;margin-bottom:.75rem}
.tag{display:inline-block;background:var(--navy);color:#fff;font-size:.66rem;padding:.16rem .48rem;border-radius:3px}
ul{margin-left:1.1rem;line-height:1.55;font-size:.88rem} li{margin-bottom:.34rem}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem;flex:1;min-height:0}
.card{background:var(--card);border-radius:10px;padding:1rem;border:1px solid #e8ecf0;box-shadow:0 2px 12px rgba(15,43,70,.06)}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin-bottom:.75rem}
.kpi{background:var(--card);border-radius:10px;padding:.65rem .75rem;border-left:4px solid var(--teal)}
.kpi .val{font-size:1.05rem;font-weight:700;color:var(--navy)} .kpi .lbl{font-size:.68rem;color:var(--muted);margin-top:.12rem;line-height:1.3}
table{width:100%;border-collapse:collapse;font-size:.78rem} th,td{padding:.34rem .45rem;border-bottom:1px solid #eef1f4;text-align:left} th{color:var(--navy)}
.footer{position:fixed;bottom:0;left:0;right:0;padding:.4rem 2.8rem;font-size:.68rem;color:var(--muted);background:rgba(255,255,255,.96);border-top:1px solid #e8ecf0;display:flex;justify-content:space-between}
.title-slide{justify-content:center;text-align:center;padding-top:2.5rem} .title-slide h1{font-size:1.85rem}
.chart-title{font-size:.8rem;font-weight:600;color:var(--navy);margin-bottom:.35rem;text-align:center}
.chart-wrap{height:210px;position:relative}
.chart-wrap.tall{height:248px}
.invest-kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.55rem;margin-bottom:.7rem}
.invest-kpi{background:linear-gradient(160deg,#f8fafb 0%,#fff 100%);border:1px solid #e8ecf0;border-radius:10px;padding:.55rem .6rem;text-align:center;box-shadow:0 1px 8px rgba(15,43,70,.04)}
.invest-kpi.highlight{border-color:#d4b84a;background:linear-gradient(160deg,#fffdf5 0%,#fff 100%);box-shadow:0 2px 12px rgba(201,162,39,.15)}
.invest-kpi .ik-val{font-size:1rem;font-weight:700;color:var(--navy);letter-spacing:-.02em}
.invest-kpi .ik-lbl{font-size:.64rem;color:var(--muted);margin-top:.18rem;line-height:1.25}
.cost-scroll{flex:1;overflow-y:auto;min-height:0}
.cost-total-bar{background:var(--navy);color:#fff;border-radius:8px;padding:.5rem .7rem;margin-bottom:.45rem;font-size:.88rem}
.cost-total-bar{display:flex;justify-content:space-between;align-items:center}
.cost-item{border:1px solid #e8ecf0;border-radius:8px;margin-bottom:.3rem;background:#fff}
.cost-item>summary{display:flex;align-items:center;padding:.4rem .6rem;cursor:pointer;list-style:none;font-size:.8rem}
.cost-item>summary::-webkit-details-marker{display:none}
.cost-label{flex:1;font-weight:600;color:var(--navy)} .cost-amt{font-weight:700}
.cost-pct{font-size:.68rem;color:var(--muted);margin-left:.35rem;font-weight:500}
.cost-children{padding:0 .55rem .45rem .75rem;border-top:1px solid #f0f2f5}
.cost-leaf{display:flex;justify-content:space-between;font-size:.74rem;padding:.22rem 0;color:var(--muted)}
.cost-sub summary{display:flex;justify-content:space-between;font-size:.76rem;padding:.3rem 0;cursor:pointer;list-style:none;color:var(--muted)}
.cost-sub ul{list-style:none;padding:0 0 .2rem} .cost-sub li{display:flex;justify-content:space-between;font-size:.7rem;padding:.12rem 0}
.note{font-size:.74rem;color:var(--muted);margin-top:.4rem;line-height:1.45}
.scope-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
.scope-grid h3{font-size:.85rem;color:var(--navy);margin-bottom:.35rem}
.gantt-wrap{flex:1;min-height:0;background:var(--card);border-radius:10px;padding:.75rem;border:1px solid #e8ecf0;display:flex;flex-direction:column}
.gantt-axis{display:flex;justify-content:space-between;font-size:.64rem;color:var(--muted);padding:0 0 .25rem 7.5rem;border-bottom:1px solid #dde3e8;margin-bottom:.25rem}
.gantt-body{flex:1;overflow-y:auto}
.gantt-row{display:grid;grid-template-columns:7.2rem 1fr 4.8rem;gap:.35rem;margin-bottom:.32rem;align-items:center}
.gantt-label{font-size:.65rem;font-weight:600;color:var(--navy);text-align:right;line-height:1.12}
.gantt-track{position:relative;height:20px;background:#eef2f6;border-radius:4px}
.gantt-bar{position:absolute;top:2px;height:16px;border-radius:3px;min-width:3px;cursor:pointer}
.gantt-bar.done{background:var(--teal)} .gantt-bar.plan{background:#1a4a6e}
.gantt-bar.duration-only,.gantt-bar.assume{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 5px,#8f7db8 5px,#8f7db8 10px)}
.gantt-row.duration-row .gantt-track{background:#edeaf3}
.gantt-foot{font-size:.68rem;color:var(--muted);margin-top:.45rem;line-height:1.45;border-top:1px solid #eef1f4;padding-top:.4rem}
.gantt-bar.warn{background:var(--accent)} .gantt-bar.build{background:#2e6da4}
.gantt-bar.staff{background:#5b6eae}
.gantt-dates{font-size:.6rem;color:var(--muted)}
.gantt-legend{font-size:.62rem;color:var(--muted);margin-top:.35rem;display:flex;gap:.65rem;flex-wrap:wrap}
.gantt-legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:.18rem;vertical-align:middle}
.today-line{position:absolute;top:0;bottom:0;width:2px;background:var(--warn);z-index:2;pointer-events:none}
.today-tag{position:absolute;top:-11px;font-size:.55rem;color:var(--warn);transform:translateX(-50%);white-space:nowrap}
#tip{position:fixed;z-index:300;max-width:360px;background:var(--navy);color:#fff;padding:.5rem .65rem;border-radius:8px;font-size:.72rem;line-height:1.45;pointer-events:none;opacity:0;transition:opacity .12s;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#tip.show{opacity:1} #tip .td{color:#8ecec6;font-size:.66rem;margin-bottom:.18rem}
.risk-high{color:var(--warn);font-weight:600}
.decision-list{list-style:none;margin:0;padding:0}
.decision-list li{border:1px solid #e8ecf0;border-left:4px solid var(--teal);padding:.75rem .95rem;margin-bottom:.5rem;border-radius:0 8px 8px 0;font-size:.88rem;background:var(--card)}
</style>
</head>
<body>
<div class="top-bar"></div>
<div class="lang-switch"><button id="btnZh" class="active" type="button">中文</button><button id="btnEn" type="button">EN</button></div>
<div id="tip"><div class="td"></div><div class="tb"></div></div>
<div id="deck"></div>
<div class="footer"><span id="footerText"></span><span id="navHint"></span><span id="counter"></span></div>
<script>
const GANTT_CALENDAR = ''' + json.dumps(GANTT_CALENDAR) + r''';
const DURATION_ROWS = ''' + json.dumps(DURATION_ROWS) + r''';
const CAPEX = ''' + json.dumps(CAPEX) + r''';
const RISK = ''' + json.dumps(RISK_ON_BASE) + r''';
const T0=new Date("2026-05-01"),T1=new Date("2027-12-31"),RANGE=T1-T0;
function pct(d){return Math.max(0,Math.min(100,((new Date(d)-T0)/RANGE)*100));}
const I18N={
zh:{
footer:"凯莱英 UK · PDF 制备与冻干改造",
nav:"← → 翻页",
tag:"内部汇报",
s1t:"PDF 厂房 HPLC 与冻干机改造",s1s:"进展 · 投资 · 周期",
s2t:"执行摘要",s2s:"",
k1:"技术可行",k1d:"HPLC 与冻干机均可落地",
k2:"£3.78M",k2d:"可行性 Capex OOM（±50%）",
k3:"2027 Q3",k3d:"HPLC 目标投运（2027年8月）",
k4:"2027 Q4",k4d:"冻干机目标投运（2027年11月）",
s2b1:"范围：在既有 PDF footprint 内增设制备型 HPLC（DAC300/CP300）及冻干机（含隔离器、除湿、纯蒸汽发生器等），配套拆除/迁建、机电仪控与 HVAC。",
s2b2:"投资：可行性 Capex OOM £3,783,000（±50%，约 £1.9M–£5.7M）— 非最终 Capex；不含通胀、税、汇率及业主项目管理。",
s2b3:"周期：冻干机制造 8–10 个月为关键路径；当前排序优先采购冻干机再 HPLC，HPLC 仍可在 2027 年 8 月具备使用条件。",
s3t:"范围与布置",s3s:"",
hplcT:"HPLC",hplc1:"DAC300 色谱柱、浆料罐、CP300 泵撬（Asymchem 供货）",hplc2:"移动头罐 2×500 L（进料）+ 3×200 L（馏分）",hplc3:"2000 L 废液暂存罐",
lyoT:"冻干机",lyo1:"冻干腔、冷凝器、制冷、隔离器、双 CIP 罐、除湿机、纯蒸汽发生器（Asymchem 供货）",lyo2:"需新增更衣室/气闸",lyo3:"拆除/气闸/分区约 20 周（有望缩至约 14 周）",
s5t:"投资总览（OOM）",s5s:"9802-RBP-ZZ-ZZ-CP-X-100001 · 基准 2026-05-15",
s5oom:"OOM 总价（可行性量级）",
s6t:"投资结构",s6s:"OOM 构成与直接工程费分项",
s6kOom:"OOM 总价（可行性量级）",s6kBase:"基础项目成本",s6kRisk:"风险与预备费",
chartLeft:"OOM 总价构成",chartRight:"直接工程费 £2.329M 分项（A–E）",
s7t:"周期与关键路径",s7s:"FS §4.3–4.4 · 冻干机长周期驱动",
s7k1:"冻干机制造",s7k1d:"8–10 个月",
s7k2:"HPLC 供货",s7k2d:"约 18 周（DQ+商务后）",
s7k3:"FEED",s7k3d:"12–14 周",
s7k4:"详细设计",s7k4d:"18–20 周",
ganttSub:"FS §4.4 图 1 · High Level Project Programme",
gFs:"FS / 进度基准",gEng:"Engineer就位",gFeed:"FEED（示意）",gDd:"详细设计（示意）",
gLySpec:"冻干机规格与资金",gLyMfg:"冻干机制造",gLyFat:"冻干机 FAT",gLyShip:"冻干机运输安装",gLyVal:"冻干验证→PQ",
gHplcSpec:"HPLC 规格与资金",gHplcMfg:"HPLC 制造",gHplcFat:"HPLC FAT",gHplcShip:"HPLC 运输安装",
gTanks:"移动头罐采购",gWaste:"废液罐采购",gRetrofit:"改造",
legDone:"已完成",legStaff:"工程师就位",legPlan:"采购/制造",legBuild:"施工/验证",legCrit:"关键路径",legAssume:"§4.3 示意",today:"约今",
s7note:"",
s8t:"主要风险（节选）",s8s:"9802-RBP-ZZ-ZZ-RP-R-050000 · P01 · 2026-05-05",
s8h:"缓解后仍须关注",
s8r1:"进度：未在 2027 Q3 前投入效益使用（缓解后评级 10）— 尽早下单长周期设备。",
s8r2:"进度：长周期设备拖期（缓解后 10）— 与供应商排产对接、管理到货。",
s8r3:"合规：新废液罐排放点需环境许可变更（缓解后 5）— 提前与 EA 沟通申报。",
s8r4:"费用：资金策略不明确（评级 12，§4.5）— 集团/现场明确 CapEx 批复路径。",
s8r5:"运营：PG.12 拆除期 filter dryer 运行与 HPLC 区域 spray dryer 调度（评级 20→需 FEED 细化）。",
s9t:"建议决策事项",s9s:"",
s9d1:"是否批准由可行性阶段进入 FEED？",
s9d2:"是否批准长周期设备（冻干机包 £967k + HPLC £358k）的早期采购资金？",
s9d3:"是否同意按 FS 建议优先冻干机、次 HPLC 的采购排序，并接受 PG.10–12 气闸/改造方案？",
s9d4:"是否指令提前启动环境许可变更及公用工程负荷复核（FEED 输入）？",
s10t:"谢谢",s10s:"",
axis:["2026 H1","2026 H2","2027 H1","2027 H2"],
costLabels:{
direct:"直接工程费 (A–E)",A:"A 设备",A1:"A1 储罐/容器",A2:"A2 泵组",A31:"A3.1 HPLC（Hanbon）",A32:"A3.2 冻干机+隔离器+除湿+纯蒸汽发生器",
B:"B 土建",C:"C 机管",D:"D 电仪控",E:"E HVAC",
oth:"其他项目费",F:"F FEED",G:"G 详细设计",H:"H CDM",I:"I 调试",J:"J 预备金（20%）",
base:"基础项目成本",cont:"风险与预备费合计",c15:"设计发展 (15%)",c25:"施工设备 (25%)",c10:"业主 (10%)"
}
},
en:{
footer:"Asymchem UK · PDF Prep & Lyophilizer",
nav:"← → to navigate",
tag:"Internal briefing",
s1t:"PDF HPLC & Lyophilizer Scheme",s1s:"Progress · Investment · Programme",
s2t:"Executive Summary",s2s:"",
k1:"Technically feasible",k1d:"HPLC and lyophilizer can be delivered",
k2:"£3.78M",k2d:"Feasibility Capex OOM (±50%)",
k3:"Q3 2027",k3d:"HPLC target (August 2027)",
k4:"Q4 2027",k4d:"Lyophilizer target (November 2027)",
s2b1:"Scope: in-situ PDF footprint — prep HPLC (DAC300/CP300) and lyophilizer (isolator, dehumidifier, pure steam generator, etc.) with disinvestment, MEP, EIC and HVAC.",
s2b2:"Investment: feasibility Capex OOM £3,783,000 (±50%, approx. £1.9M–£5.7M) — not final Capex; excl. inflation, tax, FX, client PM.",
s2b3:"Programme: lyophilizer 8–10 month lead is critical; current sequence prioritises lyophilizer procurement then HPLC; August 2027 HPLC use remains achievable.",
s3t:"Scope & Layout",s3s:"",
hplcT:"HPLC",hplc1:"DAC300 column, slurry tank, CP300 pump skid (Asymchem supply)",hplc2:"Mobile head tanks 2×500 L feed + 3×200 L fractions",hplc3:"2,000 L waste hold tank",
lyoT:"Lyophilizer",lyo1:"Dryer, condenser, refrigeration, isolator, twin CIP tanks, dehumidifier, pure steam generator (Asymchem supply)",lyo2:"New changing/airlock required",lyo3:"Enabling / airlock ~20 weeks (may reduce to ~14 weeks)",
s5t:"Investment (OOM)",s5s:"9802-RBP-ZZ-ZZ-CP-X-100001 · base 15 May 2026",
s5oom:"Total OOM (feasibility magnitude)",
s6t:"Investment structure",s6s:"OOM build-up & direct works split",
s6kOom:"Total OOM (feasibility magnitude)",s6kBase:"Base project cost",s6kRisk:"Risk & contingency",
chartLeft:"Total OOM composition",chartRight:"Direct works £2.329M (A–E)",
s7t:"Programme & Critical Path",s7s:"FS §4.3–4.4 · lyophilizer lead drives",
s7k1:"Lyophilizer mfg",s7k1d:"8–10 months",
s7k2:"HPLC supply",s7k2d:"~18 weeks (post DQ)",
s7k3:"FEED",s7k3d:"12–14 weeks",
s7k4:"Detailed design",s7k4d:"18–20 weeks",
ganttSub:"FS §4.4 Fig. 1 · High Level Project Programme",
gFs:"FS / baseline",gEng:"Engineer mobilised",gFeed:"FEED (illustrative)",gDd:"Detail design (illustrative)",
gLySpec:"Lyoph spec & funding",gLyMfg:"Lyoph build",gLyFat:"Lyoph FAT",gLyShip:"Lyoph ship & install",gLyVal:"Lyoph val.→PQ",
gHplcSpec:"HPLC spec & funding",gHplcMfg:"HPLC build",gHplcFat:"HPLC FAT",gHplcShip:"HPLC ship & install",
gTanks:"Mobile tanks",gWaste:"Waste tank",gRetrofit:"Retrofit",
legDone:"Complete",legStaff:"Engineer mobilisation",legPlan:"Procure / build",legBuild:"Site / validation",legCrit:"Critical path",legAssume:"§4.3 illustrative",today:"~Today",
s7note:"",
s8t:"Key Risks (extract)",s8s:"9802-RBP-ZZ-ZZ-RP-R-050000 · P01 · 05 May 2026",
s8h:"Post-mitigation focus",
s8r1:"Schedule: not in beneficial use by Q3 2027 (mitigated rating 10) — order long-lead items early.",
s8r2:"Schedule: long-lead slippage (mitigated 10) — supplier engagement and delivery control.",
s8r3:"Compliance: environmental permit for new waste tank vent (mitigated 5) — early EA engagement.",
s8r4:"Cost: funding strategy unclear (rating 12, §4.5) — confirm CapEx approval path.",
s8r5:"Operations: filter dryer during PG.12 works & spray dryer vs HPLC in PG.05 (20 mitigated — refine at FEED).",
s9t:"Decisions for Review",s9s:"",
s9d1:"Approve progression from feasibility to FEED?",
s9d2:"Approve early funding for long-lead packages (lyoph £967k + HPLC £358k)?",
s9d3:"Confirm procurement sequence (lyophilizer first, then HPLC) and PG.10–12 airlock/works strategy?",
s9d4:"Mandate early environmental permit change and utilities load review for FEED?",
s10t:"Thank you",s10s:"",
axis:["2026 H1","2026 H2","2027 H1","2027 H2"],
costLabels:{
direct:"Direct works (A–E)",A:"A Equipment",A1:"A1 Tanks/vessels",A2:"A2 Pumps",A31:"A3.1 HPLC (Hanbon)",A32:"A3.2 Lyoph + isolator + dehum + PSG",
B:"B Civils",C:"C M&P",D:"D EIC",E:"E HVAC",
oth:"Other project costs",F:"F FEED",G:"G Detailed design",H:"H CDM",I:"I Commissioning",J:"J Contingency reserve (20%)",
base:"Base project cost",cont:"Risk & contingency (total)",c15:"Design development (15%)",c25:"Construction & equipment (25%)",c10:"Client (10%)"
}
}
};
let lang="zh",idx=0,chartsBuilt=false;
function t(k){return I18N[lang][k]||k;}
function tc(k){return I18N[lang].costLabels[k];}
function fm(n){return "£"+Math.round(n).toLocaleString("en-GB");}
function fmtRange(central,pct){const lo=Math.round(central*(1-pct)),hi=Math.round(central*(1+pct));return fm(lo)+" – "+fm(hi);}
function costHTML(){
const L=I18N[lang].costLabels,C=CAPEX,R=RISK;
const otherFj=C.F+C.G+C.H+C.I+C.J;
return `<div class="cost-total-bar"><span>${t("s5oom")}</span><span>${fm(R.oom)}</span></div>
<details class="cost-item" open><summary><span class="cost-label">${L.direct}</span><span class="cost-amt">${fm(C.direct)}</span></summary>
<div class="cost-children">
<details class="cost-sub" open><summary><span>${L.A}</span><span>${fm(C.A)}</span></summary><ul>
<li><span>${L.A1}</span><span>${fm(C.A1)}</span></li>
<li><span>${L.A2}</span><span>${fm(C.A2)}</span></li>
<li><span>${L.A31}</span><span>${fm(C.A31)}</span></li>
<li><span>${L.A32}</span><span>${fm(C.A32)}</span></li></ul></details>
<div class="cost-leaf"><span>${L.B}</span><span>${fm(C.B)}</span></div>
<div class="cost-leaf"><span>${L.C}</span><span>${fm(C.C)}</span></div>
<div class="cost-leaf"><span>${L.D}</span><span>${fm(C.D)}</span></div>
<div class="cost-leaf"><span>${L.E}</span><span>${fm(C.E)}</span></div>
</div></details>
<details class="cost-item"><summary><span class="cost-label">${L.oth}</span><span class="cost-amt">${fm(otherFj)}</span></summary>
<div class="cost-children">
<div class="cost-leaf"><span>${L.F}</span><span>${fm(C.F)}</span></div>
<div class="cost-leaf"><span>${L.G}</span><span>${fm(C.G)}</span></div>
<div class="cost-leaf"><span>${L.H}</span><span>${fm(C.H)}</span></div>
<div class="cost-leaf"><span>${L.I}</span><span>${fm(C.I)}</span></div>
<div class="cost-leaf"><span>${L.J}</span><span>${fm(C.J)}</span></div>
</div></details>
<details class="cost-item" open><summary><span class="cost-label">${L.base}</span><span class="cost-amt">${fm(C.total)}</span></summary></details>
<details class="cost-item"><summary><span class="cost-label">${L.cont}</span><span class="cost-amt">${fm(R.cont_total)}</span></summary>
<div class="cost-children">
<div class="cost-leaf"><span>${L.c15}</span><span>${fm(R.c15)}</span></div>
<div class="cost-leaf"><span>${L.c25}</span><span>${fm(R.c25)}</span></div>
<div class="cost-leaf"><span>${L.c10}</span><span>${fm(R.c10)}</span></div>
</div></details>`;
}
function ganttHTML(){
const today=pct("2026-05-28");
let rows="";
GANTT_CALENDAR.forEach((g,i)=>{
const key=g[0];
const left=pct(g[1]),right=pct(g[2]),w=Math.max(1.2,right-left);
const d0=g[1].slice(0,7).replace("-","/"),d1=g[2].slice(0,7).replace("-","/");
const dateLbl=d0+" – "+d1;
const showToday=i===0;
rows+=`<div class="gantt-row"><div class="gantt-label">${t(key)}</div><div class="gantt-track">
${showToday?`<div class="today-line" style="left:${today}%"><span class="today-tag">${t("today")}</span></div>`:""}
<div class="gantt-bar ${g[3]}" style="left:${left}%;width:${w}%" data-en="${g[4].replace(/"/g,"&quot;")}" data-zh="${g[5].replace(/"/g,"&quot;")}" data-dates="${d0} – ${d1}"></div>
</div><div class="gantt-dates">${dateLbl}</div></div>`;
});
const durMax=20;
DURATION_ROWS.forEach(d=>{
const key=d[0],wMin=d[1],wMax=d[2],mid=(wMin+wMax)/2;
const wPct=Math.max(18,(mid/durMax)*88);
const range=lang==="zh"?`${wMin}–${wMax} 周`:`${wMin}–${wMax} wk`;
rows+=`<div class="gantt-row duration-row"><div class="gantt-label">${t(key)}</div><div class="gantt-track">
<div class="gantt-bar duration-only" style="left:0;width:${wPct}%" data-en="${d[3].replace(/"/g,"&quot;")}" data-zh="${d[4].replace(/"/g,"&quot;")}" data-dates="${range}"></div>
</div><div class="gantt-dates">${range}</div></div>`;
});
return `<div class="gantt-wrap"><div class="chart-title">${t("ganttSub")}</div>
<div class="gantt-axis">${t("axis").map(y=>`<span>${y}</span>`).join("")}</div>
<div class="gantt-body">${rows}</div>
<div class="gantt-legend"><span><i style="background:var(--teal)"></i>${t("legDone")}</span>
<span><i style="background:#1a4a6e"></i>${t("legPlan")}</span>
<span><i style="background:#2e6da4"></i>${t("legBuild")}</span>
<span><i style="background:var(--accent)"></i>${t("legCrit")}</span>
<span><i style="background:#5b6eae"></i>${t("legStaff")}</span>
<span><i style="background:#6d5b95"></i>${t("legAssume")}</span></div></div>`;
}
function deckHTML(){
return `
<section class="slide active title-slide"><p><span class="tag">${t("tag")}</span></p>
<h1>${t("s1t")}</h1><h2>${t("s1s")}</h2></section>

<section class="slide"><h1>${t("s2t")}</h1>
<div class="kpi-row">
<div class="kpi"><div class="val">${t("k1")}</div><div class="lbl">${t("k1d")}</div></div>
<div class="kpi"><div class="val">${t("k2")}</div><div class="lbl">${t("k2d")}</div></div>
<div class="kpi"><div class="val">${t("k3")}</div><div class="lbl">${t("k3d")}</div></div>
<div class="kpi"><div class="val">${t("k4")}</div><div class="lbl">${t("k4d")}</div></div></div>
<ul><li>${t("s2b1")}</li><li>${t("s2b2")}</li><li>${t("s2b3")}</li></ul></section>

<section class="slide"><h1>${t("s3t")}</h1>
<div class="scope-grid">
<div class="card"><h3>${t("hplcT")}</h3><ul style="margin-top:.4rem;font-size:.82rem"><li>${t("hplc1")}</li><li>${t("hplc2")}</li><li>${t("hplc3")}</li></ul></div>
<div class="card"><h3>${t("lyoT")}</h3><ul style="margin-top:.4rem;font-size:.82rem"><li>${t("lyo1")}</li><li>${t("lyo2")}</li><li>${t("lyo3")}</li></ul></div></div></section>

<section class="slide"><h1>${t("s5t")}</h1><h2>${t("s5s")}</h2>
<div class="cost-scroll">${costHTML()}</div></section>

<section class="slide"><h1>${t("s6t")}</h1><h2>${t("s6s")}</h2>
<div class="invest-kpi-row">
<div class="invest-kpi highlight"><div class="ik-val">${fm(RISK.oom)}</div><div class="ik-lbl">${t("s6kOom")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(CAPEX.total)}</div><div class="ik-lbl">${t("s6kBase")}</div></div>
<div class="invest-kpi"><div class="ik-val">${fm(RISK.cont_total)}</div><div class="ik-lbl">${t("s6kRisk")}</div></div></div>
<div class="grid-2"><div class="card"><div class="chart-title">${t("chartLeft")}</div><div class="chart-wrap tall"><canvas id="c1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("chartRight")}</div><div class="chart-wrap tall"><canvas id="c2"></canvas></div></div></div></section>

<section class="slide"><h1>${t("s7t")}</h1><h2>${t("s7s")}</h2>
<div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:.5rem">
<div class="kpi"><div class="val">${t("s7k1")}</div><div class="lbl">${t("s7k1d")}</div></div>
<div class="kpi"><div class="val">${t("s7k2")}</div><div class="lbl">${t("s7k2d")}</div></div>
<div class="kpi"><div class="val">${t("s7k3")}</div><div class="lbl">${t("s7k3d")}</div></div>
<div class="kpi"><div class="val">${t("s7k4")}</div><div class="lbl">${t("s7k4d")}</div></div></div>
${ganttHTML()}
</section>


<section class="slide"><h1>${t("s9t")}</h1>
<ul class="decision-list"><li>${t("s9d1")}</li><li>${t("s9d2")}</li></ul></section>

<section class="slide title-slide"><h1>${t("s10t")}</h1></section>`;
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
function applyLang(){
document.documentElement.lang=lang==="zh"?"zh-CN":"en";
const saved=idx;
document.getElementById("deck").innerHTML=deckHTML();
document.getElementById("footerText").textContent=t("footer");
document.getElementById("navHint").textContent=t("nav");
document.getElementById("btnZh").classList.toggle("active",lang==="zh");
document.getElementById("btnEn").classList.toggle("active",lang==="en");
chartsBuilt=false;bindGanttTips();show(saved);
}
function slides(){return document.querySelectorAll(".slide");}
function show(n){
const s=slides();idx=(n+s.length)%s.length;
s.forEach((el,i)=>el.classList.toggle("active",i===idx));
document.getElementById("counter").textContent=(idx+1)+" / "+s.length;
if(idx===4&&!chartsBuilt){buildCharts();chartsBuilt=true;}
}
function buildCharts(){
const zh=lang==="zh";
const otherFj=CAPEX.F+CAPEX.G+CAPEX.H+CAPEX.I+CAPEX.J;
const oom=RISK.oom;
const lblDirect=zh?"直接工程费 (A–E)":"Direct works (A–E)";
const lblOther=zh?"其他项目费":"Other project costs";
const lblRisk=zh?"风险与预备费":"Risk & contingency";
new Chart(document.getElementById("c1"),{type:"bar",data:{
labels:[zh?"项目投资 OOM":"Project OOM"],
datasets:[
{label:lblDirect,data:[CAPEX.direct],backgroundColor:"#0f2b46",borderRadius:4},
{label:lblOther,data:[otherFj],backgroundColor:"#009688",borderRadius:4},
{label:lblRisk,data:[RISK.cont_total],backgroundColor:"#c9a227",borderRadius:4}
]},options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,
plugins:{legend:{position:"bottom",labels:{font:{size:10},padding:14,usePointStyle:true,pointStyle:"rectRounded"}},
tooltip:{callbacks:{label:c=>{const v=c.raw,pct=(v/oom*100).toFixed(1);return c.dataset.label+": "+fm(v)+" ("+pct+"%)";}}}},
scales:{x:{stacked:true,max:oom*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M",font:{size:10}},grid:{color:"#eef1f4"}},
y:{stacked:true,display:false}}}});
new Chart(document.getElementById("c2"),{type:"bar",data:{labels:[zh?"直接工程费":"Direct works"],datasets:[
{label:zh?"设备 A":"Equipment A",data:[CAPEX.A],backgroundColor:"#0f2b46"},
{label:zh?"土建 B":"Civils B",data:[CAPEX.B],backgroundColor:"#1a4a6e"},
{label:zh?"机管 C":"M&P C",data:[CAPEX.C],backgroundColor:"#2e6da4"},
{label:zh?"电仪控 D":"EIC D",data:[CAPEX.D],backgroundColor:"#4a7ba8"},
{label:zh?"HVAC E":"HVAC E",data:[CAPEX.E],backgroundColor:"#009688"}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{font:{size:9},usePointStyle:true}}},
tooltip:{callbacks:{label:c=>{const v=c.raw,pct=(v/CAPEX.direct*100).toFixed(1);return c.dataset.label+": "+fm(v)+" ("+pct+"%)";}}}},
scales:{x:{stacked:true,display:false},y:{stacked:true,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M",font:{size:10}},grid:{color:"#eef1f4"}}}});
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
