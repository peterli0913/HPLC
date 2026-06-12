"""C1 module OEB5 upgrade estimate (Scott, Jun 2026) — portfolio briefing."""

from __future__ import annotations

import json

from ext_feasibility_cost import EXT_COST_CSS

# Main equipment & design (Scott estimate, £k → £)
ISO_2F = 500_000
ISO_GF = 500_000
HVAC_UPG = 350_000
AIRLOCK = 225_000
FLEX_ISO = 330_000
EQUIP_SUB = ISO_2F + ISO_GF + HVAC_UPG + AIRLOCK + FLEX_ISO  # 1,905,000
CONT_PCT = 30
PROJECT_CONT = 571_500
C1_OOM = EQUIP_SUB + PROJECT_CONT  # 2,476,500

CHART_STACK = {"equip_sub": EQUIP_SUB, "project_cont": PROJECT_CONT}

GANTT_C1 = [
    [
        "c1Scope",
        "2026-07-01",
        "2026-08-31",
        "plan",
        "Finalise scope (8 weeks), aligned with retrofit approval.",
        "范围定稿（8 周），假设与改造项目一并批准。",
    ],
    [
        "c1Dd",
        "2026-09-01",
        "2026-11-30",
        "plan",
        "Detailed design (12 weeks).",
        "详细设计（12 周）。",
    ],
    [
        "c1Build",
        "2026-12-01",
        "2027-04-30",
        "warn",
        "Place orders & equipment build (20 weeks).",
        "下单及设备制造（20 周）。",
    ],
    [
        "c1IQ",
        "2027-05-01",
        "2027-06-30",
        "build",
        "Installation & qualification (8 weeks).",
        "安装与确认（8 周）。",
    ],
]

C1_COST_I18N_ZH = {
    "capex": "项目总投资估算",
    "secEquip": "主设备（设备与设计费）",
    "iso2f": "二层物料分装固定隔离器",
    "isoGF": "首层最终包装固定隔离器",
    "hvac": "HVAC 系统改造/升级",
    "airlock": "气闸联锁及雾化淋浴",
    "flex": "各单元操作定制柔性隔离器",
    "subtotal": "小计",
    "projectCont": "全项目预备费（30%）",
}

C1_COST_I18N_EN = {
    "capex": "Total CAPEX Estimate",
    "secEquip": "Main equipment (equipment & design costs)",
    "iso2f": "2nd floor isolator — material dispensing",
    "isoGF": "Ground floor isolator — final pack-off",
    "hvac": "HVAC system modifications / upgrades",
    "airlock": "Airlock interlocking & mist shower installation",
    "flex": "Bespoke flexible isolators — unit operations",
    "subtotal": "Subtotal",
    "projectCont": "Whole Project contingency (30%)",
}

CHART_I18N_ZH = {
    "stackEquip": "主设备小计",
    "stackCont": "全项目预备费",
    "donutTitle": "主设备 — 分项",
}

CHART_I18N_EN = {
    "stackEquip": "Equipment subtotal",
    "stackCont": "Project contingency",
    "donutTitle": "Main equipment — breakdown",
}

DONUT_ITEMS = [
    {"id": "iso2f", "amount": ISO_2F},
    {"id": "isoGF", "amount": ISO_GF},
    {"id": "hvac", "amount": HVAC_UPG},
    {"id": "airlock", "amount": AIRLOCK},
    {"id": "flex", "amount": FLEX_ISO},
]


def c1_cost_data_json() -> str:
    return json.dumps(
        {
            "oom": C1_OOM,
            "equipSub": EQUIP_SUB,
            "projectCont": PROJECT_CONT,
            "contPct": CONT_PCT,
            "lines": {
                "iso2f": ISO_2F,
                "isoGF": ISO_GF,
                "hvac": HVAC_UPG,
                "airlock": AIRLOCK,
                "flex": FLEX_ISO,
            },
            "chartStack": CHART_STACK,
            "chartDonut": [i["amount"] for i in DONUT_ITEMS],
            "chartDonutIds": [i["id"] for i in DONUT_ITEMS],
        }
    )


C1_COST_RENDER_JS = r"""
function c1CostLabels(){return I18N[lang].c1Cost;}
function c1Leaf(id,amt){
const L=c1CostLabels();
return `<div class="cost-leaf cost-leaf-sub"><span>${L[id]}</span><span>${fm(Number(amt)||0)}</span></div>`;
}
function c1SectionHd(title,total){
return `<span class="cost-section-title">${title}</span><span class="cost-section-amt">${fm(Number(total)||0)}</span>`;
}
function c1CostHTML(){
const D=C1_COST_DATA,L=c1CostLabels(),ln=D.lines||{};
const items=`${c1Leaf("iso2f",ln.iso2f)}${c1Leaf("isoGF",ln.isoGF)}${c1Leaf("hvac",ln.hvac)}${c1Leaf("airlock",ln.airlock)}${c1Leaf("flex",ln.flex)}`;
const equipBlock=`<details class="cost-section" open><summary class="cost-section-hd">${c1SectionHd(L.secEquip,D.equipSub)}</summary>
<div class="cost-section-body">${items}
<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.equipSub)}</span></div></div></details>`;
const contLine=`<div class="cost-risk-line"><span>${L.projectCont}</span><span>${fm(D.projectCont)}</span></div>`;
return `<div class="cost-total-bar"><span>${L.capex}</span><span>${fm(D.oom)}</span></div>${equipBlock}${contLine}`;
}
function buildC1InvestmentCharts(){
const zh=lang==="zh",D=C1_COST_DATA,Lc=I18N[lang].c1Chart||{};
const el1=document.getElementById("cC11")||document.getElementById("c1");
const el2=document.getElementById("cC12")||document.getElementById("c2");
if(!el1||!el2)return;
new Chart(el1,{type:"bar",data:{labels:[zh?"项目总投资":"Total CAPEX"],datasets:[
{label:Lc.stackEquip||"Equipment",data:[D.equipSub],backgroundColor:"#0f2b46"},
{label:Lc.stackCont||"Contingency",data:[D.projectCont],backgroundColor:"#c9a227"}]},
options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true,max:D.oom*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M"}},y:{stacked:true,display:false}}}});
const ids=D.chartDonutIds,amts=D.chartDonut;
const labels=ids.map(id=>(I18N[lang].c1Cost[id]||id));
new Chart(el2,{type:"doughnut",data:{labels,datasets:[{data:amts,backgroundColor:["#0f2b46","#1a4a6e","#2e6da4","#5b6eae","#7eb8b0"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:8},boxWidth:10}}}}});
}
"""

C1_COST_CSS = ""
