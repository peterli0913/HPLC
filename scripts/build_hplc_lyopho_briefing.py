#!/usr/bin/env python3
"""Generate bilingual HPLC + Lyophilizer feasibility management briefing HTML."""

import json
from pathlib import Path

OUT = Path("/workspace/汇报/HPLC-Lyophilizer/HPLC_Lyophilizer_Management_Briefing_2026-05-28.html")

# FS §4.3 calendar milestones only; FEED/DD are duration-only (separate lane)
GANTT_CALENDAR = [
    ["gFs", "2026-05-19", "2026-05-19", "done",
     "Feasibility Study report P01 issued 19 May 2026 (FS).",
     "可行性研究报告 P01 发版：2026-05-19（FS）。"],
    ["gHplc", "2027-08-01", "2027-08-31", "build",
     "HPLC available for use by August 2027 — Q3 beneficial use target (FS §4.3).",
     "HPLC 可投入使用：2027 年 8 月（FS §4.3，Q3 效益目标）。"],
    ["gLy", "2027-11-01", "2027-11-30", "build",
     "Lyophiliser operational November 2027 (FS §4.3); earlier if lead time reduced.",
     "冻干机投运：2027 年 11 月（FS §4.3）；制造周期缩短可提前。"],
]
DURATION_ROWS = [
    ["gFeed", 12, 14, "FEED 12–14 weeks per FS §4.3 — no calendar start/end in FS.",
     "FEED 12–14 周（FS §4.3）— 未给出日历起止日。"],
    ["gDd", 18, 20, "Detailed design 18–20 weeks per FS §4.3 — no calendar start/end in FS.",
     "详细设计 18–20 周（FS §4.3）— 未给出日历起止日。"],
]

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
.gantt-bar.duration-only{background:repeating-linear-gradient(-45deg,#6d5b95,#6d5b95 5px,#8f7db8 5px,#8f7db8 10px)}
.gantt-row.duration-row .gantt-track{background:#edeaf3}
.gantt-foot{font-size:.68rem;color:var(--muted);margin-top:.45rem;line-height:1.45;border-top:1px solid #eef1f4;padding-top:.4rem}
.gantt-bar.warn{background:var(--accent)} .gantt-bar.build{background:#2e6da4}
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
k2:"£3.78M",k2d:"可行性阶段 Capex 估算（±50%）",
k3:"2027 Q3",k3d:"HPLC 目标投运（2027年8月）",
k4:"2027 Q4",k4d:"冻干机目标投运（2027年11月）",
s2b1:"范围：在既有 PDF footprint 内增设制备型 HPLC（DAC300/CP300）及冻干机（含隔离器、除湿、纯蒸汽发生器等），配套拆除/迁建、机电仪控与 HVAC。",
s2b2:"投资：直接工程 £2.33M + 设计/FEED/CDM/调试 £0.82M + 20% 总 contingency £0.63M = £3.783M（±50%）。",
s2b3:"周期：冻干机制造 8–10 个月为关键路径；当前排序优先采购冻干机再 HPLC，HPLC 仍可在 2027 年 8 月具备使用条件。",
s3t:"范围与布置",s3s:"",
hplcT:"HPLC",hplc1:"DAC300 色谱柱、浆料罐、CP300 泵撬（Asymchem 供货）",hplc2:"移动头罐 2×500 L（进料）+ 3×200 L（馏分）",hplc3:"2000 L 废液暂存罐",
lyoT:"冻干机",lyo1:"冻干腔、冷凝器、制冷、隔离器、双 CIP 罐、除湿机、纯蒸汽发生器（Asymchem 供货）",lyo2:"需新增更衣室/气闸",lyo3:"拆除/气闸/分区约 20 周（有望缩至约 14 周）",
s4t:"投资总览",s4s:"",
s4acc:"可行性阶段估算精度 ±50%；非最终 Capex，FEED 后更新。",
chartLeft:"项目总投资构成（£3.783M）",chartRight:"直接工程费 £2.329M 分项",
s5t:"主要设备采购价（费用计划）",s5s:"不含安装、土建、设计费 — 见 A 类合计 £1.575M",
s6t:"设计与管理费用",s6s:"费用计划 F–I 项 + RBPC 工时估算（供对照）",
s6n1:"费用计划中的 FEED（±30%）£225k、详细设计（±10%）£289k、CDM £235k、调试 £76k 为包干估算。",
s6n2:"RBPC 工程工时估算（9802-RBP-ZZ-ZZ-PL-R-050002）：可行性阶段约 £225k（2,258 h）；Concept/FEED 级约 £279k（2,786 h）— 与 F 项数量级一致。",
s7t:"周期与关键路径",s7s:"FS §4.3–4.4 · 冻干机长周期驱动",
s7k1:"冻干机制造",s7k1d:"8–10 个月",
s7k2:"HPLC 供货",s7k2d:"约 18 周（DQ+商务后）",
s7k3:"FEED",s7k3d:"12–14 周",
s7k4:"详细设计",s7k4d:"18–20 周",
ganttSub:"项目进度计划（高阶）",
gFs:"FS 完成",gFeed:"FEED",gDd:"详细设计",gLyOrder:"冻干下单窗口",gLyLead:"冻干制造周期",gHplcLead:"HPLC 周期",gPg12:"土建改造",gHplc:"HPLC 可用",gLy:"冻干投运",
legDone:"已完成",legPlan:"设计",legBuild:"里程碑/投运",legDur:"仅工期（FS 无日历日）",today:"约今",
s7foot:"注：日历轴仅标示 FS 明确给出的节点（2026-05-19 可行性完成；2027-08 HPLC 可用；2027-11 冻干投运）。紫色斜线条为 FEED（12–14 周）与详细设计（18–20 周），仅表示 FS 披露的工期长短，不代表实际起止日期。冻干机制造 8–10 个月、HPLC 约 18 周、改造约 20 周等工期见上方指标，排程将在 FEED 阶段细化。",
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
costRows:{
direct:"直接工程 (A–E)",feed:"FEED (F, ±30%)",detail:"详细设计 (G, ±10%)",cdm:"CDM (H)",comm:"调试 (I)",cont:"Contingency (J, 20%)",tot:"可行性阶段合计"
},
eqH:"HPLC 主机（Hanbon）",eqL:"冻干机+隔离器+除湿+纯蒸汽发生器",eqT:"储罐/泵组等",eqTot:"A 类设备合计"
},
en:{
footer:"Asymchem UK · PDF Prep & Lyophilizer",
nav:"← → to navigate",
tag:"Internal briefing",
s1t:"PDF HPLC & Lyophilizer Scheme",s1s:"Progress · Investment · Programme",
s2t:"Executive Summary",s2s:"",
k1:"Technically feasible",k1d:"HPLC and lyophilizer can be delivered",
k2:"£3.78M",k2d:"Feasibility-stage Capex (±50%)",
k3:"Q3 2027",k3d:"HPLC target (August 2027)",
k4:"Q4 2027",k4d:"Lyophilizer target (November 2027)",
s2b1:"Scope: in-situ PDF footprint — prep HPLC (DAC300/CP300) and lyophilizer (isolator, dehumidifier, pure steam generator, etc.) with disinvestment, MEP, EIC and HVAC.",
s2b2:"Investment: direct works £2.33M + design/FEED/CDM/commissioning £0.82M + 20% contingency £0.63M = £3.783M (±50%).",
s2b3:"Programme: lyophilizer 8–10 month lead is critical; current sequence prioritises lyophilizer procurement then HPLC; August 2027 HPLC use remains achievable.",
s3t:"Scope & Layout",s3s:"",
hplcT:"HPLC",hplc1:"DAC300 column, slurry tank, CP300 pump skid (Asymchem supply)",hplc2:"Mobile head tanks 2×500 L feed + 3×200 L fractions",hplc3:"2,000 L waste hold tank",
lyoT:"Lyophilizer",lyo1:"Dryer, condenser, refrigeration, isolator, twin CIP tanks, dehumidifier, pure steam generator (Asymchem supply)",lyo2:"New changing/airlock required",lyo3:"Enabling / airlock ~20 weeks (may reduce to ~14 weeks)",
s4t:"Investment Overview",s4s:"",
s4acc:"Feasibility accuracy ±50%; not final Capex — update at FEED.",
chartLeft:"Total project composition (£3.783M)",chartRight:"Direct works £2.329M breakdown",
s5t:"Major equipment (cost plan)",s5s:"Supply only — class A total £1.575M",
s6t:"Design & management fees",s6s:"Cost plan lines F–I vs RBPC hours estimate",
s6n1:"Cost plan: FEED (£225k, ±30%), detailed design (£289k, ±10%), CDM (£235k), commissioning (£76k).",
s6n2:"RBPC hours estimate (9802-RBP-ZZ-ZZ-PL-R-050002): FS stage ~£225k (2,258 h); concept/FEED ~£279k (2,786 h) — aligns with line F.",
s7t:"Programme & Critical Path",s7s:"FS §4.3–4.4 · lyophilizer lead drives",
s7k1:"Lyophilizer mfg",s7k1d:"8–10 months",
s7k2:"HPLC supply",s7k2d:"~18 weeks (post DQ)",
s7k3:"FEED",s7k3d:"12–14 weeks",
s7k4:"Detailed design",s7k4d:"18–20 weeks",
ganttSub:"High-level project programme",
gFs:"FS complete",gFeed:"FEED",gDd:"Detailed design",gLyOrder:"Lyoph order window",gLyLead:"Lyoph lead time",gHplcLead:"HPLC lead",gPg12:"Civils / enabling",gHplc:"HPLC available",gLy:"Lyoph operational",
legDone:"Complete",legPlan:"Design",legBuild:"Build/delivery",legMile:"Critical path",today:"~Today",
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
costRows:{
direct:"Direct works (A–E)",feed:"FEED (F, ±30%)",detail:"Detailed design (G, ±10%)",cdm:"CDM (H)",comm:"Commissioning (I)",cont:"Contingency (J, 20%)",tot:"Feasibility-stage total"
},
eqH:"HPLC package (Hanbon)",eqL:"Lyoph + isolator + dehum + pure steam gen.",eqT:"Tanks & pumps",eqTot:"Class A equipment total"
}
};
let lang="zh",idx=0,chartsBuilt=false;
function t(k){return I18N[lang][k]||k;}
function fm(n){return "£"+Math.round(n).toLocaleString("en-GB");}
function ganttHTML(){
const today=pct("2026-05-28");
const calKeys=["gFs","gHplc","gLy"];
let rows="";
GANTT_CALENDAR.forEach((g,i)=>{
const key=calKeys[i]||g[0];
const left=pct(g[1]),right=pct(g[2]),w=Math.max(1.2,right-left);
const d0=g[1].slice(0,7).replace("-","/"),d1=g[2].slice(0,7).replace("-","/");
const showToday=i===0;
rows+=`<div class="gantt-row"><div class="gantt-label">${t(key)}</div><div class="gantt-track">
${showToday?`<div class="today-line" style="left:${today}%"><span class="today-tag">${t("today")}</span></div>`:""}
<div class="gantt-bar ${g[3]}" style="left:${left}%;width:${w}%" data-en="${g[4].replace(/"/g,"&quot;")}" data-zh="${g[5].replace(/"/g,"&quot;")}" data-dates="${d0} – ${d1}"></div>
</div><div class="gantt-dates">${d0}–${d1}</div></div>`;
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
<span><i style="background:#2e6da4"></i>${t("legBuild")}</span>
<span><i style="background:#6d5b95"></i>${t("legDur")}</span></div>
<p class="gantt-foot">${t("s7foot")}</p></div>`;
});
return `<div class="gantt-wrap"><div class="chart-title">${t("ganttSub")}</div>
<div class="gantt-axis">${t("axis").map(y=>`<span>${y}</span>`).join("")}</div>
<div class="gantt-body">${rows}</div>
<div class="gantt-legend"><span><i style="background:var(--teal)"></i>${t("legDone")}</span>
<span><i style="background:#1a4a6e"></i>${t("legPlan")}</span>
<span><i style="background:#2e6da4"></i>${t("legBuild")}</span>
<span><i style="background:var(--accent)"></i>${t("legMile")}</span></div></div>`;
}
function deckHTML(){
const R=I18N[lang].costRows;
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

<section class="slide"><h1>${t("s4t")}</h1>
<div class="grid-2"><div class="card"><div class="chart-title">${t("chartLeft")}</div><div class="chart-wrap"><canvas id="c1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("chartRight")}</div><div class="chart-wrap"><canvas id="c2"></canvas></div></div></div>
<p class="note">${t("s4acc")}</p>
<table style="margin-top:.5rem"><thead><tr><th>${R.tot}</th><th>£K</th><th>±%</th></tr></thead><tbody>
<tr><td>${R.direct}</td><td>2,329</td><td>50</td></tr>
<tr><td>${R.feed}</td><td>225</td><td>30</td></tr>
<tr><td>${R.detail}</td><td>289</td><td>10</td></tr>
<tr><td>${R.cdm}</td><td>235</td><td>50</td></tr>
<tr><td>${R.comm}</td><td>76</td><td>50</td></tr>
<tr><td>${R.cont}</td><td>631</td><td>20</td></tr>
<tr style="font-weight:700"><td>${R.tot}</td><td>3,783</td><td>50</td></tr></tbody></table></section>

<section class="slide"><h1>${t("s5t")}</h1><h2>${t("s5s")}</h2>
<table><thead><tr><th>Item</th><th>£K</th><th></th></tr></thead><tbody>
<tr><td>${t("eqH")}</td><td>358</td><td>A3.1</td></tr>
<tr><td>${t("eqL")}</td><td>967</td><td>A3.2</td></tr>
<tr><td>${t("eqT")}</td><td>250</td><td>A1+A2</td></tr>
<tr style="font-weight:700"><td>${t("eqTot")}</td><td>1,575</td><td></td></tr>
<tr><td colspan="3" style="font-size:.74rem;color:var(--muted);padding-top:.4rem">+ ${lang==="zh"?"土建":"Civils"} 326 · ${lang==="zh"?"机管":"M&P"} 264 · ${lang==="zh"?"电仪控":"EIC"} 128 · HVAC 35 → ${lang==="zh"?"直接工程":"Direct works"} 2,329</td></tr>
</tbody></table></section>

<section class="slide"><h1>${t("s6t")}</h1><h2>${t("s6s")}</h2>
<table><tbody>
<tr><td>${R.feed}</td><td>${fm(225000)}</td></tr>
<tr><td>${R.detail}</td><td>${fm(289000)}</td></tr>
<tr><td>${R.cdm}</td><td>${fm(235000)}</td></tr>
<tr><td>${R.comm}</td><td>${fm(76000)}</td></tr></tbody></table>
<p class="note" style="margin-top:.6rem">${t("s6n1")}</p>
</section>

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
if(idx===3&&!chartsBuilt){buildCharts();chartsBuilt=true;}
}
function buildCharts(){
const zh=lang==="zh";
new Chart(document.getElementById("c1"),{type:"doughnut",data:{labels:[
zh?"直接工程 A–E":"Direct works A–E",
zh?"FEED (F)":"FEED (F)",zh?"详细设计 (G)":"Detail design (G)",
zh?"CDM (H)":"CDM (H)",zh?"调试 (I)":"Commissioning (I)",zh?"预备费 (J)":"Contingency (J)"
],datasets:[{data:[2329000,225000,289000,235000,76000,631000],backgroundColor:["#0f2b46","#1a4a6e","#2e6da4","#4a7ba8","#009688","#c9a227"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:9},boxWidth:10}}}}});
new Chart(document.getElementById("c2"),{type:"bar",data:{labels:[zh?"费用":"Cost"],datasets:[
{label:zh?"设备 A":"Equipment A",data:[1575000],backgroundColor:"#0f2b46"},
{label:zh?"土建 B":"Civils B",data:[326000],backgroundColor:"#1a4a6e"},
{label:zh?"机管 C":"M&P C",data:[264000],backgroundColor:"#2e6da4"},
{label:zh?"电仪控 D":"EIC D",data:[128000],backgroundColor:"#4a7ba8"},
{label:zh?"HVAC E":"HVAC E",data:[35000],backgroundColor:"#009688"}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true},y:{stacked:true,ticks:{callback:v=>"£"+(v/1000).toFixed(0)+"k"}}}}});
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

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML, encoding="utf-8")
print("Wrote", OUT, len(HTML), "bytes")
