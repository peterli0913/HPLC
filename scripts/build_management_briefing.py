#!/usr/bin/env python3
"""Generate updated bilingual management briefing HTML."""

import json
from pathlib import Path

OUT = Path("/workspace/汇报/PDF-Extension-COO-CFO/PDF-Extension_Management_Briefing_2026-05-28.html")
OUT_LEGACY = Path("/workspace/汇报/PDF-Extension-COO-CFO/PDF-Extension_COO-CFO_Briefing_2026-05-28.html")

GANTT_JS = [
    ["gFs", "2026-05-01", "2026-05-31", "done",
     "RIBA 1 Feasibility complete. Report A1: 22 May 2026.",
     "RIBA 1 可行性研究完成；报告 A1：2026-05-22。"],
    ["gR2", "2026-07-15", "2027-02-23", "plan",
     "RIBA 2 Concept Design (160 days). Concept report & stage gate Feb 2027.",
     "RIBA 2 概念设计（160 天）；2027-02 概念报告与阶段评审。"],
    ["gR3", "2027-02-17", "2027-09-28", "plan",
     "RIBA 3 Scheme Design (8 months).",
     "RIBA 3 方案设计（8 个月）。"],
    ["gPlan", "2027-10-26", "2028-03-21", "warn",
     "Planning: submission Dec 2027, statutory period, consent target 21 Mar 2028.",
     "规划：2027-12 提交，法定审批期，目标许可 2028-03-21。"],
    ["gR4", "2027-10-27", "2028-06-06", "plan",
     "RIBA 4 Detailed Design.",
     "RIBA 4 详细设计。"],
    ["gEquip", "2028-03-08", "2029-07-24", "warn",
     "Long-lead procurement (18 mo): Hastelloy vessels, overheads, filter dryers, etc.",
     "长周期设备采购（18 个月）：Hastelloy 釜、桥架、过滤干燥机等。"],
    ["gMed", "2028-04-12", "2028-08-02", "plan",
     "Medium-lead procurement (4 mo): AHUs, valves, etc.",
     "中等周期设备采购（4 个月）：AHU、阀门等。"],
    ["gPre", "2028-07-05", "2028-08-01", "plan",
     "Pre-construction mobilisation & site set-up.",
     "施工前动员与现场临建。"],
    ["gR5", "2028-08-02", "2029-11-13", "build",
     "RIBA 5 Construction (335 days): enabling, piling, structure, fit-out.",
     "RIBA 5 施工（335 天）：拆除临建、桩基、结构、装修机电。"],
    ["gComm", "2029-11-14", "2029-12-18", "build",
     "Commissioning & setting to work (programme §1.13).",
     "调试与投运准备（进度计划 §1.13）。"],
    ["gEnd", "2029-12-19", "2030-05-07", "warn",
     "Validation, handover, project complete (07 May 2030).",
     "确认验证、移交；项目完成 2030-05-07。"],
]

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Asymchem UK B902 PDF Extension</title>
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
h1{font-size:1.7rem;color:var(--navy);font-weight:700;margin-bottom:.28rem}
h2{font-size:.94rem;color:var(--muted);font-weight:400;margin-bottom:.8rem}
.tag{display:inline-block;background:var(--navy);color:#fff;font-size:.66rem;padding:.16rem .48rem;border-radius:3px}
ul{margin-left:1.1rem;line-height:1.55;font-size:.9rem} li{margin-bottom:.36rem}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1rem;flex:1;min-height:0}
.card{background:var(--card);border-radius:10px;padding:1rem;border:1px solid #e8ecf0;box-shadow:0 2px 12px rgba(15,43,70,.06)}
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:.85rem}
.kpi{background:var(--card);border-radius:10px;padding:.75rem .9rem;border-left:4px solid var(--teal)}
.kpi .val{font-size:1.2rem;font-weight:700;color:var(--navy)} .kpi .lbl{font-size:.7rem;color:var(--muted);margin-top:.15rem}
table{width:100%;border-collapse:collapse;font-size:.8rem} th,td{padding:.36rem .5rem;border-bottom:1px solid #eef1f4;text-align:left} th{color:var(--navy)}
.footer{position:fixed;bottom:0;left:0;right:0;padding:.4rem 2.8rem;font-size:.68rem;color:var(--muted);background:rgba(255,255,255,.96);border-top:1px solid #e8ecf0;display:flex;justify-content:space-between}
.title-slide{justify-content:center;text-align:center;padding-top:2.5rem} .title-slide h1{font-size:1.9rem}
.chart-title{font-size:.82rem;font-weight:600;color:var(--navy);margin-bottom:.35rem;text-align:center;line-height:1.3}
.chart-wrap{height:220px;position:relative}
.cost-scroll{flex:1;overflow-y:auto;min-height:0}
.cost-total-bar{background:var(--navy);color:#fff;border-radius:8px;padding:.5rem .7rem;display:flex;justify-content:space-between;font-weight:700;margin-bottom:.45rem;font-size:.88rem}
.cost-item{border:1px solid #e8ecf0;border-radius:8px;margin-bottom:.3rem;background:#fff}
.cost-item>summary{display:flex;align-items:center;padding:.4rem .6rem;cursor:pointer;list-style:none;font-size:.8rem}
.cost-item>summary::-webkit-details-marker{display:none}
.cost-label{flex:1;font-weight:600;color:var(--navy)} .cost-amt{font-weight:700}
.cost-children{padding:0 .55rem .45rem .75rem;border-top:1px solid #f0f2f5}
.cost-leaf{display:flex;justify-content:space-between;font-size:.74rem;padding:.22rem 0;color:var(--muted)}
.cost-sub summary{display:flex;justify-content:space-between;font-size:.76rem;padding:.3rem 0;cursor:pointer;list-style:none;color:var(--muted)}
.cost-sub ul{list-style:none;padding:0 0 .2rem} .cost-sub li{display:flex;justify-content:space-between;font-size:.7rem;padding:.12rem 0}
.gantt-wrap{flex:1;min-height:0;background:var(--card);border-radius:10px;padding:.85rem;border:1px solid #e8ecf0;display:flex;flex-direction:column}
.gantt-axis{display:flex;justify-content:space-between;font-size:.65rem;color:var(--muted);padding:0 0 .28rem 8rem;border-bottom:1px solid #dde3e8;margin-bottom:.28rem}
.gantt-body{flex:1;overflow-y:auto}
.gantt-row{display:grid;grid-template-columns:7.8rem 1fr 5rem;gap:.4rem;margin-bottom:.38rem;align-items:center}
.gantt-label{font-size:.68rem;font-weight:600;color:var(--navy);text-align:right;line-height:1.15}
.gantt-track{position:relative;height:22px;background:#eef2f6;border-radius:4px}
.gantt-bar{position:absolute;top:2px;height:18px;border-radius:3px;min-width:3px;cursor:pointer}
.gantt-bar.done{background:var(--teal)} .gantt-bar.plan{background:#1a4a6e}
.gantt-bar.warn{background:var(--accent)} .gantt-bar.build{background:#2e6da4}
.gantt-dates{font-size:.62rem;color:var(--muted)}
.gantt-legend{font-size:.64rem;color:var(--muted);margin-top:.4rem;display:flex;gap:.7rem;flex-wrap:wrap}
.gantt-legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:.2rem;vertical-align:middle}
.today-line{position:absolute;top:0;bottom:0;width:2px;background:var(--warn);z-index:2;pointer-events:none}
.today-tag{position:absolute;top:-12px;font-size:.57rem;color:var(--warn);transform:translateX(-50%);white-space:nowrap}
#tip{position:fixed;z-index:300;max-width:340px;background:var(--navy);color:#fff;padding:.5rem .65rem;border-radius:8px;font-size:.74rem;line-height:1.45;pointer-events:none;opacity:0;transition:opacity .12s;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#tip.show{opacity:1} #tip .td{color:#8ecec6;font-size:.67rem;margin-bottom:.2rem}
.mitigate-box{background:#f8fafb;border:1px solid #e8ecf0;border-radius:8px;padding:.7rem .85rem;font-size:.8rem;line-height:1.5;margin-top:.45rem}
.mitigate-box h4{font-size:.84rem;color:var(--navy);margin-bottom:.3rem}
.decision-list{list-style:none;margin:0;padding:0}
.decision-list li{border:1px solid #e8ecf0;border-left:4px solid var(--teal);padding:.8rem 1rem;margin-bottom:.55rem;border-radius:0 8px 8px 0;font-size:.92rem;background:var(--card)}
</style>
</head>
<body>
<div class="top-bar"></div>
<div class="lang-switch"><button id="btnZh" class="active" type="button">中文</button><button id="btnEn" type="button">EN</button></div>
<div id="tip"><div class="td"></div><div class="tb"></div></div>
<div id="deck"></div>
<div class="footer"><span id="footerText"></span><span id="navHint"></span><span id="counter"></span></div>
<script>
const GANTT_DATA = ''' + json.dumps(GANTT_JS) + r''';
const T0=new Date("2026-07-01"),T1=new Date("2030-05-07"),RANGE=T1-T0;
function pct(d){return Math.max(0,Math.min(100,((new Date(d)-T0)/RANGE)*100));}
const I18N={
zh:{
footer:"凯莱英 UK · B902 PDF 扩建",
nav:"← → 翻页",
tag:"内部汇报",
s1t:"凯莱英 UK · B902 PDF 厂房扩建",s1s:"投资与周期汇报",s1m:"可行性研究（RIBA Stage 1）· Sandwich · 2026年5月",
s2t:"执行摘要",s2s:"Scitech 可行性研究成果（2026-05-22）",
k1:"可行性研究报告（FS）",k1d:"RIBA Stage 1 已完成",
k2:"£78.1M",k2d:"项目总投资 OOM",
k3:"2030年5月",k3d:"项目完成（总控计划）",
s2b1:"范围：东侧扩建 — 10 台反应釜、2500 L 加氢釜、3 套过滤干燥机及公用工程。",
s2b2:"投资：OOM £78,108,089 — 非最终 Capex；不含通胀、税、汇率、业主项目管理。",
s2b3:"进展：FS 已完成；RIBA 2 概念设计计划 2026-07-01 启动。",
s3t:"项目进展与阶段",s3s:"资本项目当前阶段",
s3done:"已完成",s3next:"进行中 / 下一步",
s3d1:"可行性报告及附录（费用、风险、进度、设备清单）",s3d2:"BREEAM 预评估",
s3n1:"RIBA 2 概念设计 2026-07-01",s3n2:"概念设计完成 2027-02-16（计划）",
s3n3:"待明确：采购分工、Stage 2 报价",
s3warn:"Stage 2/3 设计费未在 FS 中单列，需向 Scitech 索取阶段报价。",
s4t:"范围与设计基线",s4s:"Option 1 — 方案比选得分最高",
s4b1:"占地约 600 m²；4 层 + 设备夹层",s4b2:"前提：拆除/迁址原加氢厂房",s4b3:"消防：第二疏散梯；加氢区泄压板",
s4th1:"楼层",s4th2:"面积 m²",s4gf:"首层",s41f:"一层",s42f:"二层",s43f:"三层+夹层",s4tot:"合计 GIFA",
s5t:"投资总览（OOM）",s5s:"300291-CM-0001 · 基准日 2026-05-22",
s5oom:"OOM 总价（可行性量级）",
s6t:"投资结构",s6s:"总包构成与直接工程费",chartLeft:"项目总投资 OOM 构成",chartRight:"基础建造费构成（工程直接费 + 临时设施与员工设施 + 承包商管理费与利润）",
s7t:"预备费与风险",s7s:"可行性阶段（报告 §14）",
s7h:"缓解措施",
s7m1:"风险登记册对每项风险列出建议措施（如：勘查、设计阶段确认、纳入 OOM 估算、阶段评审等），并区分 Mitigate / Accept / Avoid 等响应方式。",
s7m2:"缓解前：登记册汇总的预估影响（报告 §14.3）— 成本约 £2.64m（加权 £1.76m）；进度累计 182 周（加权 131.8 周）。",
s7m3:"缓解后：实施上述措施及 FS 中已纳入的假设与费用预留后的预期影响 — 成本约 £1.13m（加权 £626k）；进度 107 周（加权 60.6 周）。",
s7m4:"报告 §14.4：部分风险（如电气升级、公用工程、冷却、应急电源等）已在 OOM 费用计划中计入 allowances，技术风险仍须在后续设计阶段关闭。",
s7c1:"设计发展准备金 (15%)",s7c2:"施工与设备风险 (25%)",s7c3:"业主预备费 (10%)",s7c4:"风险登记册（量化）",
s8t:"Capex 口径",s8s:"费用计划假设要点",
s8in:"已纳入 OOM",s8out:"未纳入 / 基准不含",
s8in1:"扩建及既有厂改造范围内的工程内容",s8in2:"预备费、承包商管理费与利润、设计费",
s8in3:"可行性阶段风险与预备费块",s8in4:"工艺设备费用计划分项（£23.25M）",
s8out2:"通胀、汇率、税费",
s8out3:"业主项目管理、运营、耗材",s8out4:"超出勘测 allowances 的治理费用",
s8disc:"OOM 仅供指引，不得直接用于最终 Capex；Concept 阶段更新估算。",
s9t:"整体周期与进度",s9s:"300291-PM-PR-0002 · 1,005 天（2026-07-01 — 2030-05-07）",
ganttSub:"时间轴（条块长度按日历比例；悬停查看说明）",s9eqNote:"设备采购：长周期 2028-03 — 2029-07（18 个月）；中等周期（AHU 等）2028-04 — 2028-08（4 个月）。",
gFs:"可行性 RIBA 1",gR2:"概念 RIBA 2",gR3:"方案 RIBA 3",gPlan:"规划审批",
gR4:"详细 RIBA 4",gEquip:"长周期设备采购",gMed:"中等周期设备采购",gPre:"施工准备",gR5:"施工 RIBA 5",gComm:"调试",gEnd:"验证/竣工",
legDone:"已完成",legPlan:"设计",legBuild:"施工/调试",legMile:"节点",today:"约今",
s10t:"设计—竣工阶段节奏",s10s:"2028 年 8 月开工前的关键阶段",
s10th1:"阶段",s10th2:"时间",s10th3:"说明",
s10r1p:"RIBA 2 概念",s10r1t:"2026-07 — 2027-02",s10r1n:"含勘测预算；设计费在 £3.81M 总包内",
s10r2p:"RIBA 3 方案",s10r2t:"2027-02 — 2027-09",s10r2n:"阶段间约 1 个月业主评审",
s10r3p:"规划",s10r3t:"2027-10 — 2028-03",s10r3n:"法定审批 65 天",
s10r4p:"RIBA 4 详细",s10r4t:"2027-10 — 2028-06",s10r4n:"与规划、采购并行",
s10eqL:"长周期设备采购",s10eqT:"2028-03 — 2029-07",s10eqN:"Hastelloy 釜、桥架、过滤干燥机等（进度计划 18 个月）",
s10eqM:"中等周期设备采购",s10eqMT:"2028-04 — 2028-08",s10eqMN:"AHU、阀门等（进度计划 4 个月）",
s10r5p:"施工准备",s10r5t:"2028-07",s10r5n:"动员/临建",
s10r6p:"施工 RIBA 5",s10r6t:"2028-08 — 2029-11",s10r6n:"土建、结构、装修机电（335 天）",
s10r7p:"调试",s10r7t:"2029-11 — 2029-12",s10r7n:"调试与投运准备",
s10r8p:"验证/竣工",s10r8t:"2029-12 — 2030-05",s10r8n:"验证、移交、项目完成",
s11t:"决策清单",s11s:"提请领导审议",
s11d1:"是否批准进入 RIBA 2（概念设计阶段）？",
s11d2:"是否推进模块化工厂设计（Modular / Design-for-Modularity）及对应方案比选？",
s12t:"谢谢",s12s:"",
axis:["2026","2027","2028","2029","2030"],
costLabels:{
w0:"0 促动/拆除",w1:"1 下部结构",w2:"2 上部结构",w3:"3 内装",w4:"4 装置器具",
w5:"5 建筑机电",w51:"5.1 预留洞/BWIC",w52:"5.2 暖通",w53:"5.3 电气",w54:"5.4 EMS",w55:"5.5 过程控制",w56:"5.6 工艺设备",
w7:"7 既有厂改造",w8:"8 外部工程",wsum:"工程费小计",
pre:"临时设施+员工设施 (8%)",ohp:"承包商管理费与利润 (5%)",base:"基础建造成本",
oth:"其他项目费",od:"设计费 (8%)",ob:"BREEAM",os:"勘测",op:"规划规费",
rr:"风险登记册",cont:"风险与预备费合计",c15:"设计发展 (15%)",c25:"施工设备 (25%)",c10:"业主 (10%)",tot:"OOM 总价"
}
},
en:{
footer:"Asymchem UK · B902 PDF Extension",
nav:"← → to navigate",
tag:"Internal briefing",
s1t:"Asymchem UK · B902 PDF Extension",s1s:"Investment & Programme Briefing",s1m:"Feasibility (RIBA 1) · Sandwich · May 2026",
s2t:"Executive Summary",s2s:"Scitech feasibility deliverables (22 May 2026)",
k1:"Feasibility Study (FS)",k1d:"RIBA Stage 1 complete",
k2:"£78.1M",k2d:"Total project OOM",
k3:"May 2030",k3d:"Project complete (programme)",
s2b1:"Scope: East extension — 10 reactors, 2,500 L H₂ reactor, 3 filter dryers, utilities.",
s2b2:"Investment: OOM £78,108,089 — not final Capex; excl. inflation, tax, FX, client project management.",
s2b3:"Progress: FS complete; RIBA 2 Concept from 1 Jul 2026.",
s3t:"Progress & Stages",s3s:"Current capital project position",
s3done:"Completed",s3next:"In progress / Next",
s3d1:"Feasibility report & appendices (cost, risk, programme, equipment)",s3d2:"BREEAM pre-assessment",
s3n1:"RIBA 2 Concept Design 1 Jul 2026",s3n2:"Concept design complete 16 Feb 2027 (planned)",
s3n3:"To confirm: procurement split, Stage 2 quotation",
s3warn:"RIBA 2/3 design fees not split in FS — request staged quote from Scitech.",
s4t:"Scope & Baseline",s4s:"Option 1 — highest appraisal score",
s4b1:"~600 m² footprint; 4 floors + plant mezzanine",s4b2:"Prerequisite: remove/relocate H₂ building",
s4b3:"Fire: second escape stair; blast panels at H₂ suite",
s4th1:"Floor",s4th2:"Area m²",s4gf:"Ground",s41f:"First",s42f:"Second",s43f:"Third + mezz",s4tot:"Total GIFA",
s5t:"Investment (OOM)",s5s:"300291-CM-0001 · Base 22 May 2026",
s5oom:"Total OOM (feasibility magnitude)",
s6t:"Investment Structure",s6s:"OOM build-up & direct works",chartLeft:"Total OOM composition",chartRight:"Base construction breakdown (direct works + site/staff prelims + contractor OH&P)",
s7t:"Contingency & Risk",s7s:"Feasibility stage (report §14)",
s7h:"Mitigation measures",
s7m1:"The risk register lists proposed actions per risk (surveys, early confirmation, OOM allowances, stage reviews) with Mitigate / Accept / Avoid responses.",
s7m2:"Pre-mitigation: aggregated register exposure (§14.3) — ~£2.64m cost (£1.76m factored); 182 weeks programme (131.8 weeks factored).",
s7m3:"Post-mitigation: after those actions and FS assumptions/allowances — ~£1.13m (£626k factored); 107 weeks (60.6 weeks factored).",
s7m4:"§14.4: some risks (power, utilities, cooling, emergency power, etc.) are partially allowed in the OOM; technical risks remain live through later design.",
s7c1:"Design development (15%)",s7c2:"Construction & equipment (25%)",s7c3:"Client contingency (10%)",s7c4:"Risk register (factored)",
s8t:"Capex Scope",s8s:"Cost plan assumptions",
s8in:"In OOM",s8out:"Out of base",
s8in1:"Extension & existing-building works in scope",s8in2:"Prelims, contractor OH&P, design fees",
s8in3:"Feasibility risk & contingency blocks",s8in4:"Process equipment line in cost plan (£23.25M)",
s8out2:"Inflation, FX, tax",
s8out3:"Client project management, operations, consumables",s8out4:"Survey remediation beyond allowances",
s8disc:"OOM for guidance only — not final Capex; updated at Concept.",
s9t:"Overall Cycle & Programme",s9s:"300291-PM-PR-0002 · 1,005 days (01 Jul 2026 – 07 May 2030)",
ganttSub:"Timeline (bar length ∝ calendar duration; hover for detail)",s9eqNote:"Procurement: long-lead Mar 2028 – Jul 2029 (18 mo); medium-lead (AHUs, etc.) Apr – Aug 2028 (4 mo).",
gFs:"Feasibility RIBA 1",gR2:"Concept RIBA 2",gR3:"Scheme RIBA 3",gPlan:"Planning",
gR4:"Detailed RIBA 4",gEquip:"Long-lead equipment procurement",gMed:"Medium-lead equipment procurement",gPre:"Pre-construction",gR5:"Construction RIBA 5",gComm:"Commissioning",gEnd:"Validation / complete",
legDone:"Complete",legPlan:"Design",legBuild:"Construction",legMile:"Milestone",today:"~Today",
s10t:"Stage Rhythm to Completion",s10s:"Key phases through handover",
s10th1:"Phase",s10th2:"Period",s10th3:"Notes",
s10r1p:"RIBA 2 Concept",s10r1t:"Jul 2026 – Feb 2027",s10r1n:"Surveys allowance; design fee in £3.81M pot",
s10r2p:"RIBA 3 Scheme",s10r2t:"Feb 2027 – Sep 2027",s10r2n:"~1 month client review between stages",
s10r3p:"Planning",s10r3t:"Oct 2027 – Mar 2028",s10r3n:"65-day statutory period",
s10r4p:"RIBA 4 Detailed",s10r4t:"Oct 2027 – Jun 2028",s10r4n:"Parallel with planning & procurement",
s10eqL:"Long-lead equipment procurement",s10eqT:"Mar 2028 – Jul 2029",s10eqN:"Hastelloy vessels, overheads, filter dryers, etc. (18 months per programme)",
s10eqM:"Medium-lead equipment procurement",s10eqMT:"Apr 2028 – Aug 2028",s10eqMN:"AHUs, valves, etc. (4 months per programme)",
s10r5p:"Pre-construction",s10r5t:"Jul 2028",s10r5n:"Mobilisation",
s10r6p:"RIBA 5 Construction",s10r6t:"Aug 2028 – Nov 2029",s10r6n:"335 days — civils, structure, fit-out",
s10r7p:"Commissioning",s10r7t:"Nov – Dec 2029",s10r7n:"Testing & setting to work",
s10r8p:"Validation / handover",s10r8t:"Dec 2029 – May 2030",s10r8n:"Validation, handover, project complete",
s11t:"Decision Checklist",s11s:"For leadership review",
s11d1:"Approve progression to RIBA 2 (Concept Design)?",
s11d2:"Proceed with modular facility design approach and related option studies?",
s12t:"Thank you",s12s:"",
axis:["2026","2027","2028","2029","2030"],
costLabels:{
w0:"0 Facilitating",w1:"1 Substructure",w2:"2 Superstructure",w3:"3 Internal finishes",w4:"4 Fittings",
w5:"5 Building services",w51:"5.1 BWIC",w52:"5.2 HVAC",w53:"5.3 Electrical",w54:"5.4 EMS",w55:"5.5 Controls",w56:"5.6 Process equipment",
w7:"7 Existing bldg",w8:"8 External works",wsum:"Works subtotal",
pre:"Site temp. + staff welfare (8%)",ohp:"Contractor OH&P (5%)",base:"Base construction",
oth:"Other project costs",od:"Design (8%)",ob:"BREEAM",os:"Surveys",op:"Planning",
rr:"Risk register",cont:"Risk & contingency",c15:"Design dev. (15%)",c25:"Constr./equip. (25%)",c10:"Client (10%)",tot:"Total OOM"
}
}
};
let lang="zh",idx=0,chartsBuilt=false;
function t(k){return I18N[lang][k]||k;}
function tc(k){return I18N[lang].costLabels[k];}
function fm(n){return "£"+n.toLocaleString("en-GB");}

function costHTML(){
const L=I18N[lang].costLabels;
return `<div class="cost-total-bar"><span>${t("s5oom")}</span><span>${fm(78108089)}</span></div>
<details class="cost-item" open><summary><span class="cost-label">${L.wsum}</span><span class="cost-amt">${fm(41968226)}</span></summary>
<div class="cost-children">
<details class="cost-sub"><summary><span>${L.w0}</span><span>${fm(254960)}</span></summary><ul>
<li><span>Demolition / enabling</span><span>${fm(154960)}</span></li>
<li><span>LN tank removal</span><span>${fm(50000)}</span></li>
<li><span>H₂ plant removal</span><span>${fm(50000)}</span></li></ul></details>
<details class="cost-sub"><summary><span>${L.w1}</span><span>${fm(1499680)}</span></summary><ul>
<li><span>Piles, foundations, GF slab</span><span>${fm(1239680)}</span></li>
<li><span>Equipment slabs</span><span>${fm(150000)}</span></li>
<li><span>Chiller pads</span><span>${fm(40000)}</span></li>
<li><span>Steps / ramps</span><span>${fm(70000)}</span></li></ul></details>
<div class="cost-leaf"><span>${L.w2}</span><span>${fm(3942636)}</span></div>
<div class="cost-leaf"><span>${L.w3}</span><span>${fm(1270672)}</span></div>
<div class="cost-leaf"><span>${L.w4}</span><span>${fm(154960)}</span></div>
<details class="cost-sub" open><summary><span>${L.w5}</span><span>${fm(9532716)}</span></summary><ul>
<li><span>${L.w51}</span><span>${fm(166808)}</span></li>
<li><span>${L.w52}</span><span>${fm(4165824)}</span></li>
<li><span>${L.w53}</span><span>${fm(2506484)}</span></li>
<li><span>${L.w54}</span><span>${fm(627200)}</span></li>
<li><span>${L.w55}</span><span>${fm(1966400)}</span></li>
<li><span>${L.w56}</span><span>${fm(23249083)}</span></li></ul></details>
<div class="cost-leaf"><span>${L.w7}</span><span>${fm(204000)}</span></div>
<div class="cost-leaf"><span>${L.w8}</span><span>${fm(1859520)}</span></div>
</div></details>
<div class="cost-leaf" style="padding:.35rem .6rem"><span>${L.pre}</span><span>${fm(3357458)}</span></div>
<div class="cost-leaf" style="padding:.35rem .6rem"><span>${L.ohp}</span><span>${fm(2266284)}</span></div>
<details class="cost-item" open><summary><span class="cost-label">${L.base}</span><span class="cost-amt">${fm(47591969)}</span></summary></details>
<details class="cost-item"><summary><span class="cost-label">${L.oth}</span><span class="cost-amt">${fm(4062357)}</span></summary>
<div class="cost-children">
<div class="cost-leaf"><span>${L.od}</span><span>${fm(3807357)}</span></div>
<div class="cost-leaf"><span>${L.ob}</span><span>${fm(150000)}</span></div>
<div class="cost-leaf"><span>${L.os}</span><span>${fm(80000)}</span></div>
<div class="cost-leaf"><span>${L.op}</span><span>${fm(25000)}</span></div>
</div></details>
<div class="cost-leaf" style="padding:.35rem .6rem"><span>${L.rr}</span><span>${fm(626600)}</span></div>
<details class="cost-item"><summary><span class="cost-label">${L.cont}</span><span class="cost-amt">${fm(25827163)}</span></summary>
<div class="cost-children">
<div class="cost-leaf"><span>${L.c15}</span><span>${fm(7748149)}</span></div>
<div class="cost-leaf"><span>${L.c25}</span><span>${fm(12913581)}</span></div>
<div class="cost-leaf"><span>${L.c10}</span><span>${fm(5165433)}</span></div>
</div></details>`;
}

function ganttHTML(){
const today=pct("2026-05-28");
const keys=["gFs","gR2","gR3","gPlan","gR4","gEquip","gMed","gPre","gR5","gComm","gEnd"];
let rows="";
GANTT_DATA.forEach((g,i)=>{
const key=keys[i]||g[0];
const l=t(key);
const left=pct(g[1]),right=pct(g[2]),w=Math.max(.4,right-left);
const d0=g[1].slice(0,7).replace("-","/"),d1=g[2].slice(0,7).replace("-","/");
const tipEn=g[4],tipZh=g[5];
rows+=`<div class="gantt-row"><div class="gantt-label">${l}</div><div class="gantt-track">
<div class="today-line" style="left:${today}%"><span class="today-tag">${t("today")}</span></div>
<div class="gantt-bar ${g[3]}" style="left:${left}%;width:${w}%" data-en="${tipEn.replace(/"/g,"&quot;")}" data-zh="${tipZh.replace(/"/g,"&quot;")}" data-dates="${d0} – ${d1}"></div>
</div><div class="gantt-dates">${d0}–${d1}</div></div>`;
});
return `<div class="gantt-wrap"><div class="gantt-title">${t("ganttSub")}</div>
<div class="gantt-axis">${t("axis").map(y=>`<span>${y}</span>`).join("")}</div>
<div class="gantt-body">${rows}</div>
<div class="gantt-legend"><span><i style="background:var(--teal)"></i>${t("legDone")}</span>
<span><i style="background:#1a4a6e"></i>${t("legPlan")}</span>
<span><i style="background:#2e6da4"></i>${t("legBuild")}</span>
<span><i style="background:var(--accent)"></i>${t("legMile")}</span></div></div>`;
}

function deckHTML(){
return `
<section class="slide active title-slide"><p><span class="tag">${t("tag")}</span></p>
<h1>${t("s1t")}</h1><h2>${t("s1s")}</h2><p style="color:var(--muted);margin-top:1rem;font-size:.9rem">${t("s1m")}</p></section>

<section class="slide"><h1>${t("s2t")}</h1><h2>${t("s2s")}</h2>
<div class="kpi-row">
<div class="kpi"><div class="val">${t("k1")}</div><div class="lbl">${t("k1d")}</div></div>
<div class="kpi"><div class="val">${t("k2")}</div><div class="lbl">${t("k2d")}</div></div>
<div class="kpi"><div class="val">${t("k3")}</div><div class="lbl">${t("k3d")}</div></div></div>
<ul><li>${t("s2b1")}</li><li>${t("s2b2")}</li><li>${t("s2b3")}</li></ul></section>

<section class="slide"><h1>${t("s3t")}</h1><h2>${t("s3s")}</h2>
<div class="grid-2"><div class="card"><h3 style="font-size:.9rem;color:var(--navy);margin-bottom:.5rem">${t("s3done")}</h3>
<ul style="font-size:.84rem"><li>${t("s3d1")}</li><li>${t("s3d2")}</li></ul></div>
<div class="card"><h3 style="font-size:.9rem;color:var(--navy);margin-bottom:.5rem">${t("s3next")}</h3>
<ul style="font-size:.84rem"><li>${t("s3n1")}</li><li>${t("s3n2")}</li><li>${t("s3n3")}</li></ul></div></div>
<p style="font-size:.8rem;color:var(--muted);margin-top:.6rem">${t("s3warn")}</p></section>

<section class="slide"><h1>${t("s4t")}</h1><h2>${t("s4s")}</h2>
<div class="grid-2"><ul><li>${t("s4b1")}</li><li>${t("s4b2")}</li><li>${t("s4b3")}</li></ul>
<div class="card"><table><thead><tr><th>${t("s4th1")}</th><th>${t("s4th2")}</th></tr></thead>
<tbody><tr><td>${t("s4gf")}</td><td>597</td></tr><tr><td>${t("s41f")}</td><td>642</td></tr>
<tr><td>${t("s42f")}</td><td>637</td></tr><tr><td>${t("s43f")}</td><td>1,224</td></tr>
<tr><th>${t("s4tot")}</th><th>3,099</th></tr></tbody></table></div></div></section>

<section class="slide"><h1>${t("s5t")}</h1><h2>${t("s5s")}</h2>
<div class="cost-scroll">${costHTML()}</div></section>

<section class="slide"><h1>${t("s6t")}</h1><h2>${t("s6s")}</h2>
<div class="grid-2"><div class="card"><div class="chart-title">${t("chartLeft")}</div><div class="chart-wrap"><canvas id="c1"></canvas></div></div>
<div class="card"><div class="chart-title">${t("chartRight")}</div><div class="chart-wrap"><canvas id="c2"></canvas></div></div></div></section>

<section class="slide"><h1>${t("s7t")}</h1><h2>${t("s7s")}</h2>
<div class="grid-2"><div class="card"><table><tbody>
<tr><td>${t("s7c1")}</td><td>${fm(7748149)}</td></tr>
<tr><td>${t("s7c2")}</td><td>${fm(12913581)}</td></tr>
<tr><td>${t("s7c3")}</td><td>${fm(5165433)}</td></tr>
<tr><td>${t("s7c4")}</td><td>${fm(626600)}</td></tr></tbody></table></div>
<div class="mitigate-box"><h4>${t("s7h")}</h4>
<p>${t("s7m1")}</p><p style="margin-top:.35rem">${t("s7m2")}</p>
<p style="margin-top:.35rem">${t("s7m3")}</p><p style="margin-top:.35rem">${t("s7m4")}</p></div></div></section>

<section class="slide"><h1>${t("s8t")}</h1><h2>${t("s8s")}</h2>
<div class="grid-2"><div class="card"><h3 style="font-size:.88rem;color:var(--teal);margin-bottom:.35rem">${t("s8in")}</h3>
<ul style="font-size:.82rem;margin-left:1rem"><li>${t("s8in1")}</li><li>${t("s8in2")}</li><li>${t("s8in3")}</li><li>${t("s8in4")}</li></ul></div>
<div class="card"><h3 style="font-size:.88rem;color:var(--warn);margin-bottom:.35rem">${t("s8out")}</h3>
<ul style="font-size:.82rem;margin-left:1rem"><li>${t("s8out2")}</li><li>${t("s8out3")}</li><li>${t("s8out4")}</li></ul></div></div>
<p style="font-size:.78rem;color:var(--muted);margin-top:.5rem">${t("s8disc")}</p></section>

<section class="slide"><h1>${t("s9t")}</h1><h2>${t("s9s")}</h2>${ganttHTML()}<p style="font-size:.78rem;color:var(--muted);margin-top:.45rem">${t("s9eqNote")}</p></section>

<section class="slide"><h1>${t("s10t")}</h1><h2>${t("s10s")}</h2>
<table><thead><tr><th>${t("s10th1")}</th><th>${t("s10th2")}</th><th>${t("s10th3")}</th></tr></thead><tbody>
<tr><td>${t("s10r1p")}</td><td>${t("s10r1t")}</td><td>${t("s10r1n")}</td></tr>
<tr><td>${t("s10r2p")}</td><td>${t("s10r2t")}</td><td>${t("s10r2n")}</td></tr>
<tr><td>${t("s10r3p")}</td><td>${t("s10r3t")}</td><td>${t("s10r3n")}</td></tr>
<tr><td>${t("s10r4p")}</td><td>${t("s10r4t")}</td><td>${t("s10r4n")}</td></tr>
<tr><td>${t("s10eqL")}</td><td>${t("s10eqT")}</td><td>${t("s10eqN")}</td></tr>
<tr><td>${t("s10eqM")}</td><td>${t("s10eqMT")}</td><td>${t("s10eqMN")}</td></tr>
<tr><td>${t("s10r5p")}</td><td>${t("s10r5t")}</td><td>${t("s10r5n")}</td></tr>
<tr><td>${t("s10r6p")}</td><td>${t("s10r6t")}</td><td>${t("s10r6n")}</td></tr>
<tr><td>${t("s10r7p")}</td><td>${t("s10r7t")}</td><td>${t("s10r7n")}</td></tr>
<tr><td>${t("s10r8p")}</td><td>${t("s10r8t")}</td><td>${t("s10r8n")}</td></tr>
</tbody></table></section>

<section class="slide"><h1>${t("s11t")}</h1><h2>${t("s11s")}</h2>
<ul class="decision-list"><li>${t("s11d2")}</li><li>${t("s11d1")}</li></ul></section>

<section class="slide title-slide"><h1>${t("s12t")}</h1></section>`;
}

function bindGanttTips(){
document.querySelectorAll(".gantt-bar").forEach(el=>{
el.addEventListener("mouseenter",e=>{
const tip=document.getElementById("tip");
tip.querySelector(".td").textContent=el.dataset.dates;
tip.querySelector(".tb").textContent=lang==="zh"?el.dataset.zh:el.dataset.en;
tip.classList.add("show");
moveTip(e);});
el.addEventListener("mousemove",moveTip);
el.addEventListener("mouseleave",()=>document.getElementById("tip").classList.remove("show"));
});
}
function moveTip(e){const tip=document.getElementById("tip");
let x=e.clientX+12,y=e.clientY+12;
if(x+340>innerWidth)x=e.clientX-320;
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
chartsBuilt=false;
bindGanttTips();
show(saved);
}

function slides(){return document.querySelectorAll(".slide");}
function show(n){
const s=slides();idx=(n+s.length)%s.length;
s.forEach((el,i)=>el.classList.toggle("active",i===idx));
document.getElementById("counter").textContent=(idx+1)+" / "+s.length;
if(idx===5&&!chartsBuilt){buildCharts();chartsBuilt=true;}
}
function buildCharts(){
const zh=lang==="zh";
const baseConstr=47591968;
new Chart(document.getElementById("c1"),{type:"bar",data:{labels:[zh?"项目总投资":"Total project"],datasets:[
{label:zh?"基础建造费":"Base construction",data:[baseConstr],backgroundColor:"#0f2b46"},
{label:zh?"其他项目费":"Other project costs",data:[4062357],backgroundColor:"#009688"},
{label:zh?"风险与预备费":"Risk & contingency",data:[26453763],backgroundColor:"#c9a227"}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true},y:{stacked:true,ticks:{callback:v=>"£"+(v/1e6).toFixed(1)+"M"}}}}});
new Chart(document.getElementById("c2"),{type:"doughnut",data:{labels:[
zh?"工程直接费（含工艺设备等）":"Direct works (incl. process equipment)",
zh?"临时设施+员工设施 (8%)":"Site temp. + staff welfare (8%)",
zh?"承包商管理费与利润（OH&P，5%）":"Contractor margin & profit (OH&P, 5%)"
],datasets:[{data:[41968226,3357458,2266284],backgroundColor:["#1a4a6e","#009688","#4db6ac"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:10}}}}}});
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

OUT.write_text(HTML, encoding="utf-8")
OUT_LEGACY.write_text(HTML, encoding="utf-8")
print("Wrote", OUT, len(HTML), "bytes")
