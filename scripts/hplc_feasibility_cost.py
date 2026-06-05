"""Feasibility CapEx data (9802-RBP-ZZ-ZZ-CP-X-100001 P01) for HPLC/lyoph briefing HTML."""

from __future__ import annotations

import json

from ext_feasibility_cost import EXT_COST_CSS

# --- Totals (CP-X-100001) ---
FEAS_BASE = 3_783_000

DIRECT_SUB = 2_329_000  # A–E works subtotal
PRICE_RISK = 465_800  # F 价格风险（£2,329,000 × 20%）
SUBTOTAL_WITH_F = DIRECT_SUB + PRICE_RISK  # 2,794,800
DIRECT_CONT_PCT = 20
DIRECT_CONT = round(SUBTOTAL_WITH_F * DIRECT_CONT_PCT / 100)  # 558,960
DIRECT_TOTAL = SUBTOTAL_WITH_F + DIRECT_CONT  # 3,353,760

OTHER_SUB = 825_000  # FEED + design + CDM + commissioning
OTHER_CONT_PCT = 20
OTHER_CONT = round(OTHER_SUB * OTHER_CONT_PCT / 100)  # 165,000
OTHER_TOTAL = OTHER_SUB + OTHER_CONT  # 990,000

ACCURACY_BASE = DIRECT_SUB + OTHER_SUB  # 3,154,000 (excl. contingency lines)
ACCURACY_PCT = 30
ACCURACY_CONT = round(ACCURACY_BASE * ACCURACY_PCT / 100)  # 946,200
GEN_TOTAL = ACCURACY_CONT
HPLC_OOM = DIRECT_TOTAL + OTHER_TOTAL + GEN_TOTAL  # 4,731,000

CHART_STACK = {
    "direct_total": DIRECT_TOTAL,
    "other_total": OTHER_TOTAL,
    "gen_total": GEN_TOTAL,
}

DIRECT_LINE_ITEMS = [
    {"id": "a1", "amount": 200_000},
    {"id": "a2", "amount": 50_000},
    {"id": "a31", "amount": 358_000},
    {"id": "a32", "amount": 967_000},
    {"id": "b", "amount": 326_000},
    {"id": "c", "amount": 264_000},
    {"id": "d", "amount": 128_000},
    {"id": "e", "amount": 35_000},
]

OTHER_LINE_ITEMS = [
    {"id": "f", "amount": 225_000},
    {"id": "g", "amount": 289_000},
    {"id": "h", "amount": 235_000},
    {"id": "i", "amount": 76_000},
]

GEN_LINE_ITEMS = [{"id": "accuracy", "amount": ACCURACY_CONT}]

# Legacy dicts for portfolio imports / charts
CAPEX = {
    "total": FEAS_BASE,
    "direct": DIRECT_SUB,
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

RISK_ON_BASE = {
    "base": FEAS_BASE,
    "oom": HPLC_OOM,
    "accuracy": ACCURACY_CONT,
    "cont_total": GEN_TOTAL,
}

HPLC_COST_I18N_ZH = {
    "oom": "项目 OOM 总价",
    "secDirect": "直接工程费",
    "secOther": "其他项目费",
    "secGen": "可行性阶段一般风险与预备费",
    "subtotal": "小计",
    "otherCont": "预备费（20%）",
    "secTotal": "本项合计",
    "a1": "A1 储罐/容器",
    "a2": "A2 泵组",
    "a31": "A3.1 HPLC（Hanbon）",
    "a32": "A3.2 冻干机包",
    "b": "B 土建",
    "c": "C 安装及管路",
    "d": "D 电器仪表",
    "e": "E HVAC",
    "fprice": "F 价格风险",
    "f": "F FEED（±30%）",
    "g": "G 详细设计（±10%）",
    "h": "H CDM",
    "i": "I 调试",
    "accuracy": "Accuracy contingency（30%）",
    "bullets": {
        "a1": ["500 L 头罐×2", "200 L 头罐×3", "2000 L 废液罐"],
        "a2": ["HPLC 输送泵", "HPLC 废液泵", "冻干 CIP 泵", "冻干废液泵"],
        "a31": ["Hanbon 报价", "含空运"],
        "a32": ["冻干+隔离器", "除湿+PSG", "含 FAT/SAT"],
        "b": ["C&J 拆除迁建", "土建杂项"],
        "c": ["设备安装", "管道阀门", "消防 provisional"],
        "d": ["电缆桥架", "照明小动力", "仪表", "调试"],
        "e": ["风管改造", "除湿管道", "HEPA 迁移"],
        "f": ["FEED 费估算"],
        "g": ["详细设计费"],
        "h": ["CDM 顾问费"],
        "i": ["调试人工"],
    },
}

HPLC_COST_I18N_EN = {
    "oom": "Total project OOM",
    "secDirect": "Direct works",
    "secOther": "Other project costs",
    "secGen": "General risk & contingency at feasibility",
    "subtotal": "Subtotal",
    "directCont": "Contingency (20%)",
    "otherCont": "Contingency (20%)",
    "secTotal": "Section total",
    "a1": "A1 Tanks / vessels",
    "a2": "A2 Pumps",
    "a31": "A3.1 HPLC (Hanbon)",
    "a32": "A3.2 Lyophilizer package",
    "b": "B Civils",
    "c": "C Installation & pipework",
    "d": "D Electrical & instrumentation",
    "e": "E HVAC",
    "fprice": "F Price risk",
    "f": "F FEED study (±30%)",
    "g": "G Detailed design (±10%)",
    "h": "H CDM fees",
    "i": "I Commissioning",
    "accuracy": "Accuracy contingency (30%)",
    "bullets": {
        "a1": ["500 L head tanks ×2", "200 L head tanks ×3", "2,000 L waste tank"],
        "a2": ["HPLC transfer", "HPLC waste", "Lyoph CIP", "Lyoph waste"],
        "a31": ["Hanbon quote", "incl. air freight"],
        "a32": ["Lyoph + isolator", "dehum + PSG", "incl. FAT/SAT"],
        "b": ["C&J enabling", "misc. civils"],
        "c": ["Equipment install", "piping / valves", "fire protection PS"],
        "d": ["Cable containment", "power / lighting", "instruments", "testing"],
        "e": ["Ductwork mods", "dehum ducting", "HEPA relocation"],
        "f": ["FEED fee estimate"],
        "g": ["Detail design fees"],
        "h": ["CDM consultant"],
        "i": ["Commissioning labour"],
    },
}

CHART_I18N_ZH = {
    "stackDirect": "直接工程费",
    "stackOther": "其他项目费",
    "stackGen": "一般风险与预备费",
    "donutTitle": "直接工程费分项",
}

CHART_I18N_EN = {
    "stackDirect": "Direct works",
    "stackOther": "Other project costs",
    "stackGen": "General risk & contingency",
    "donutTitle": "Direct works breakdown",
}


def hplc_cost_data_json() -> str:
    return json.dumps(
        {
            "oom": HPLC_OOM,
            "feasBase": FEAS_BASE,
            "directSub": DIRECT_SUB,
            "priceRisk": PRICE_RISK,
            "directTotal": DIRECT_TOTAL,
            "otherSub": OTHER_SUB,
            "otherCont": OTHER_CONT,
            "otherTotal": OTHER_TOTAL,
            "otherContPct": OTHER_CONT_PCT,
            "accuracyBase": ACCURACY_BASE,
            "accuracy": ACCURACY_CONT,
            "accuracyPct": ACCURACY_PCT,
            "genTotal": GEN_TOTAL,
            "directItems": DIRECT_LINE_ITEMS,
            "otherItems": OTHER_LINE_ITEMS,
            "genItems": GEN_LINE_ITEMS,
            "chartStack": CHART_STACK,
            "chartDonut": [i["amount"] for i in DIRECT_LINE_ITEMS],
            "chartDonutIds": [i["id"] for i in DIRECT_LINE_ITEMS],
        }
    )


HPLC_COST_RENDER_JS = r"""
function hplcCostLabels(){return I18N[lang].hplcCost;}
function hplcBullets(id){const b=I18N[lang].hplcCost.bullets;return (b&&b[id])?b[id]:[];}
function hplcCostItemHTML(id,amt){
const L=hplcCostLabels();
const bullets=hplcBullets(id);
const bl=bullets.length?`<ul class="cost-bullets">${bullets.map(x=>`<li>${x}</li>`).join("")}</ul>`:"";
const body=bl?`<div class="cost-children">${bl}</div>`:"";
return `<details class="cost-item cost-item-sub"${bl?"":" data-no-body"}><summary><span class="cost-label">${L[id]}</span><span class="cost-amt">${fm(amt)}</span></summary>${body}</details>`;
}
function hplcSectionHd(title,total){
return `<span class="cost-section-title">${title}</span><span class="cost-section-amt">${fm(total)}</span>`;
}
function hplcCostHTML(){
const D=HPLC_COST_DATA,L=hplcCostLabels();
let directItems=D.directItems.filter(it=>it.amount>0).map(it=>hplcCostItemHTML(it.id,it.amount)).join("");
const directBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.secDirect,D.directTotal)}</summary>
<div class="cost-section-body">${directItems}
<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.subtotalWithF)}</span></div>
<div class="cost-risk-line"><span>${L.directCont}</span><span>${fm(D.directCont)}</span></div>
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.directTotal)}</span></div></div></details>`;
let otherItems=D.otherItems.filter(it=>it.amount>0).map(it=>hplcCostItemHTML(it.id,it.amount)).join("");
const otherBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.secOther,D.otherTotal)}</summary>
<div class="cost-section-body">${otherItems}
<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.otherSub)}</span></div>
<div class="cost-risk-line"><span>${L.otherCont}</span><span>${fm(D.otherCont)}</span></div>
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.otherTotal)}</span></div></div></details>`;
const genLines=D.genItems.map(it=>`<div class="cost-leaf cost-leaf-sub"><span>${L[it.id]}</span><span>${fm(it.amount)}</span></div>`).join("");
const genBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.secGen,D.genTotal)}</summary>
<div class="cost-section-body">${genLines}
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.genTotal)}</span></div></div></details>`;
return `<div class="cost-total-bar"><span>${L.oom}</span><span>${fm(D.oom)}</span></div>${directBlock}${otherBlock}${genBlock}`;
}
function buildHplcInvestmentCharts(){
const zh=lang==="zh",D=HPLC_COST_DATA,Lc=I18N[lang].hplcChart||{};
const el1=document.getElementById("cHplc1")||document.getElementById("c1");
const el2=document.getElementById("cHplc2")||document.getElementById("c2");
if(!el1||!el2)return;
new Chart(el1,{type:"bar",data:{labels:[zh?"项目 OOM":"Project OOM"],datasets:[
{label:Lc.stackDirect||"Direct",data:[D.directTotal],backgroundColor:"#0f2b46"},
{label:Lc.stackOther||"Other",data:[D.otherTotal],backgroundColor:"#009688"},
{label:Lc.stackGen||"Contingency",data:[D.genTotal],backgroundColor:"#c9a227"}]},
options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true,max:D.oom*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M"}},y:{stacked:true,display:false}}}});
const ids=D.chartDonutIds,amts=D.chartDonut;
const labels=ids.map(id=>(I18N[lang].hplcCost[id]||id));
new Chart(el2,{type:"doughnut",data:{labels,datasets:[{data:amts,backgroundColor:["#0f2b46","#1a4a6e","#2e6da4","#5b6eae","#4a7ba8","#009688","#4db6ac","#7eb8b0"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:8},boxWidth:10}}}}});
}
"""

HPLC_COST_CSS = EXT_COST_CSS
