"""Feasibility cost plan data (300291-CM-0001 A1) for extension briefing HTML."""

from __future__ import annotations

import json

# --- Totals (reconciled to OOM £78,108,089) ---
EXT_OOM = 78_108_089
BASE_SUBTOTAL = 47_591_969  # works + prelims + OH&P per cost plan
BASE_RISK_PCT = 20
BASE_RISK = round(BASE_SUBTOTAL * BASE_RISK_PCT / 100)  # 9,518,394
BASE_TOTAL = BASE_SUBTOTAL + BASE_RISK  # 57,110,363

OTHER_SUBTOTAL = 4_062_357
OTHER_CONT_PCT = 20
OTHER_CONTINGENCY = round(OTHER_SUBTOTAL * OTHER_CONT_PCT / 100)  # 812,471
OTHER_TOTAL = OTHER_SUBTOTAL + OTHER_CONTINGENCY  # 4,874,828

CONFIDENCE_BASE = BASE_SUBTOTAL + OTHER_SUBTOTAL  # 51,654,326
CONFIDENCE_PCT = 30
CONFIDENCE_CONTINGENCY = round(CONFIDENCE_BASE * CONFIDENCE_PCT / 100)  # 15,496,298
RISK_REGISTER = 626_600
GENERAL_RISK_TOTAL = CONFIDENCE_CONTINGENCY + RISK_REGISTER  # 16,122,898

# Chart / KPI helpers
CHART_STACK = {
    "base_total": BASE_TOTAL,
    "other_total": OTHER_TOTAL,
    "general_risk": GENERAL_RISK_TOTAL,
}

# Building works line items (CM-0001 BUILDING WORKS COST BREAKDOWN)
BASE_LINE_ITEMS = [
    {
        "id": "fac",
        "amount": 254_960,
        "lines": [(154_960, "0.1"), (50_000, "0.2"), (50_000, "0.3")],
    },
    {
        "id": "sub",
        "amount": 1_499_680,
        "lines": [(1_239_680, "1.1"), (150_000, "1.2"), (40_000, "1.3"), (70_000, "1.4")],
    },
    {"id": "sup", "amount": 3_942_636, "lines": []},
    {
        "id": "int",
        "amount": 1_270_672,
        "lines": [(309_920, "3.1"), (449_384, "3.2"), (511_368, "3.3")],
    },
    {"id": "fit", "amount": 154_960, "lines": []},
    {
        "id": "bld",
        "amount": 9_532_716,
        "lines": [
            (166_808, "5.1"),
            (4_165_824, "5.2"),
            (2_506_484, "5.3"),
            (627_200, "5.4"),
            (1_966_400, "5.5"),
        ],
    },
    {"id": "proc", "amount": 23_249_083, "lines": []},
    {"id": "prefab", "amount": 0, "lines": []},
    {
        "id": "exist",
        "amount": 204_000,
        "lines": [(80_000, "7.1"), (40_000, "7.2"), (84_000, "7.3")],
    },
    {"id": "ext", "amount": 1_859_520, "lines": []},
    {"id": "pre", "amount": 3_357_458, "lines": []},
    {"id": "ohp", "amount": 2_266_284, "lines": []},
]

OTHER_LINE_ITEMS = [
    {"id": "design", "amount": 3_807_357},
    {"id": "survey", "amount": 80_000},
    {"id": "breeam", "amount": 150_000},
    {"id": "plan", "amount": 25_000},
    {"id": "client", "amount": 0},
]

EXT_COST_I18N_ZH = {
    "oom": "项目 OOM 总价",
    "secBase": "基础建造成本",
    "secOther": "其他项目费",
    "secGen": "可行性阶段一般风险与预备费",
    "subtotal": "小计",
    "baseRisk": "施工与设备预备费（20%）",
    "otherCont": "预备费（20%）",
    "confidence": "信心预备费（30%）",
    "riskReg": "风险登记册（概率加权总和）",
    "secTotal": "本项合计",
    "fac": "开办工程",
    "sub": "下部结构",
    "sup": "上部结构",
    "int": "内部装修",
    "fit": "装置与设备",
    "bld": "建筑机电",
    "proc": "工艺设备",
    "prefab": "装配式建筑",
    "exist": "既有建筑改造",
    "ext": "室外工程",
    "pre": "临建",
    "ohp": "承包商管理费与利润",
    "design": "设计团队费",
    "survey": "勘测与调查",
    "breeam": "BREEAM",
    "plan": "规划与法定费用",
    "client": "业主直接费",
    "bullets": {
        "fac": ["拆除临建", "液氮罐移除", "加氢厂房拆除"],
        "sub": ["桩基基础", "设备地坪", "冷机基础", "台阶坡道"],
        "sup": ["框架楼板屋面", "防爆屋面墙", "楼梯钢构", "门窗"],
        "int": ["墙面饰面", "吊顶", "地面"],
        "fit": ["消毒清洁设施"],
        "bld": ["总包接口", "暖通空调", "电气", "EMS", "工艺控制"],
        "proc": ["搪玻璃釜", "过滤干燥机", "哈氏合金", "管道阀门", "真空等"],
        "prefab": ["本期不计"],
        "exist": ["烟囱加高", "钢构加固", "百叶整合"],
        "ext": ["场地建设、管网等"],
        "pre": ["现场管理临建"],
        "ohp": ["承包商 OH&P"],
        "design": ["设计团队费 8%"],
        "survey": ["勘测调查"],
        "breeam": ["BREEAM 评估"],
        "plan": ["规划法定费"],
        "client": ["可研阶段不计"],
    },
}

EXT_COST_I18N_EN = {
    "oom": "Total project OOM",
    "secBase": "Base construction cost",
    "secOther": "Other project costs",
    "secGen": "General risk & contingency at feasibility",
    "subtotal": "Subtotal",
    "baseRisk": "Construction & equipment contingency (20%)",
    "otherCont": "Contingency (20%)",
    "confidence": "Confidence contingency (30%)",
    "riskReg": "Risk register (probability-weighted total)",
    "secTotal": "Section total",
    "fac": "Facilitating works",
    "sub": "Substructure",
    "sup": "Superstructure",
    "int": "Internal finishes",
    "fit": "Fittings & equipment",
    "bld": "Building services",
    "proc": "Process equipment",
    "prefab": "Prefabricated buildings",
    "exist": "Work to existing buildings",
    "ext": "External works",
    "pre": "Preliminaries",
    "ohp": "Contractor OH&P",
    "design": "Design team fees",
    "survey": "Surveys & investigations",
    "breeam": "BREEAM",
    "plan": "Planning & statutory fees",
    "client": "Client direct costs",
    "bullets": {
        "fac": ["Demolition / enabling", "LN tank removal", "H₂ plant removal"],
        "sub": ["Piles & foundations", "Equipment slabs", "Chiller pads", "Steps / ramps"],
        "sup": ["Frame & envelope", "Blast roof/wall", "Stairs & steel", "Doors"],
        "int": ["Wall finishes", "Ceilings", "Floors"],
        "fit": ["Disinfection / cleaning facilities"],
        "bld": ["BWIC", "HVAC", "Electrical", "EMS", "Process control"],
        "proc": ["GL reactors", "Filter dryers", "Hastelloy", "Piping / valves", "Vacuum etc."],
        "prefab": ["Nil at this stage"],
        "exist": ["Flue extensions", "Steel support", "Louvres"],
        "ext": ["Site works, utilities, etc."],
        "pre": ["Site management & welfare"],
        "ohp": ["Contractor OH&P"],
        "design": ["Design team fees (8%)"],
        "survey": ["Surveys"],
        "breeam": ["BREEAM"],
        "plan": ["Planning & statutory"],
        "client": ["Excluded at feasibility"],
    },
}

CHART_I18N_ZH = {
    "stackBase": "基础建造成本",
    "stackOther": "其他项目费",
    "stackGen": "一般风险与预备费",
    "donutTitle": "基础建造成本分项",
}

CHART_I18N_EN = {
    "stackBase": "Base construction cost",
    "stackOther": "Other project costs",
    "stackGen": "General risk & contingency",
    "donutTitle": "Base construction breakdown",
}


def ext_cost_data_json() -> str:
    return json.dumps(
        {
            "oom": EXT_OOM,
            "baseSub": BASE_SUBTOTAL,
            "baseRisk": BASE_RISK,
            "baseTotal": BASE_TOTAL,
            "baseRiskPct": BASE_RISK_PCT,
            "otherSub": OTHER_SUBTOTAL,
            "otherCont": OTHER_CONTINGENCY,
            "otherTotal": OTHER_TOTAL,
            "otherContPct": OTHER_CONT_PCT,
            "confBase": CONFIDENCE_BASE,
            "confidence": CONFIDENCE_CONTINGENCY,
            "confPct": CONFIDENCE_PCT,
            "riskReg": RISK_REGISTER,
            "genTotal": GENERAL_RISK_TOTAL,
            "baseItems": BASE_LINE_ITEMS,
            "otherItems": OTHER_LINE_ITEMS,
            "chartStack": CHART_STACK,
            "chartDonut": [i["amount"] for i in BASE_LINE_ITEMS if i["amount"] > 0],
            "chartDonutIds": [i["id"] for i in BASE_LINE_ITEMS if i["amount"] > 0],
        }
    )


EXT_COST_RENDER_JS = r"""
function extCostLabels(){return I18N[lang].extCost;}
function extBullets(id){const b=I18N[lang].extCost.bullets;return (b&&b[id])?b[id]:[];}
function extCostItemHTML(id,amt){
const L=extCostLabels();
const bullets=extBullets(id);
const bl=bullets.length?`<ul class="cost-bullets">${bullets.map(x=>`<li>${x}</li>`).join("")}</ul>`:"";
const body=bl?`<div class="cost-children">${bl}</div>`:"";
const hideAmt=amt===0?" cost-amt-zero":"";
return `<details class="cost-item cost-item-sub"${bl?"":" data-no-body"}><summary><span class="cost-label">${L[id]}</span><span class="cost-amt${hideAmt}">${fm(amt)}</span></summary>${body}</details>`;
}
function extSectionHd(title,total){
return `<span class="cost-section-title">${title}</span><span class="cost-section-amt">${fm(total)}</span>`;
}
function extCostHTML(){
const D=EXT_COST_DATA,L=extCostLabels();
let baseItems=D.baseItems.map(it=>extCostItemHTML(it.id,it.amount)).join("");
const baseBlock=`<details class="cost-section" open><summary class="cost-section-hd">${extSectionHd(L.secBase,D.baseTotal)}</summary>
<div class="cost-section-body">${baseItems}
<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.baseSub)}</span></div>
<div class="cost-risk-line"><span>${L.baseRisk}</span><span>${fm(D.baseRisk)}</span></div>
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.baseTotal)}</span></div></div></details>`;
let otherItems=D.otherItems.filter(it=>it.amount>0||it.id==="client").map(it=>extCostItemHTML(it.id,it.amount)).join("");
const otherBlock=`<details class="cost-section" open><summary class="cost-section-hd">${extSectionHd(L.secOther,D.otherTotal)}</summary>
<div class="cost-section-body">${otherItems}
<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.otherSub)}</span></div>
<div class="cost-risk-line"><span>${L.otherCont}</span><span>${fm(D.otherCont)}</span></div>
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.otherTotal)}</span></div></div></details>`;
const genBlock=`<details class="cost-section" open><summary class="cost-section-hd">${extSectionHd(L.secGen,D.genTotal)}</summary>
<div class="cost-section-body">
<div class="cost-leaf cost-leaf-sub"><span>${L.confidence}</span><span>${fm(D.confidence)}</span></div>
<div class="cost-leaf cost-leaf-sub"><span>${L.riskReg}</span><span>${fm(D.riskReg)}</span></div>
<div class="cost-section-total"><span>${L.secTotal}</span><span>${fm(D.genTotal)}</span></div></div></details>`;
return `<div class="cost-total-bar"><span>${L.oom}</span><span>${fm(D.oom)}</span></div>${baseBlock}${otherBlock}${genBlock}`;
}
function buildExtInvestmentCharts(){
const zh=lang==="zh",D=EXT_COST_DATA,Lc=I18N[lang].extChart||{};
const el1=document.getElementById("cExt1")||document.getElementById("c1");
const el2=document.getElementById("cExt2")||document.getElementById("c2");
if(!el1||!el2)return;
new Chart(el1,{type:"bar",data:{labels:[zh?"项目 OOM":"Project OOM"],datasets:[
{label:Lc.stackBase||"Base",data:[D.baseTotal],backgroundColor:"#0f2b46"},
{label:Lc.stackOther||"Other",data:[D.otherTotal],backgroundColor:"#009688"},
{label:Lc.stackGen||"Risk",data:[D.genTotal],backgroundColor:"#c9a227"}]},
options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true,max:D.oom*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(1)+"M"}},y:{stacked:true,display:false}}}});
const ids=D.chartDonutIds,amts=D.chartDonut;
const labels=ids.map(id=>(I18N[lang].extCost[id]||id));
new Chart(el2,{type:"doughnut",data:{labels,datasets:[{data:amts,backgroundColor:["#1a4a6e","#2e6da4","#5a8ab8","#4a7ba8","#009688","#4db6ac","#c9a227","#8a9bae","#6d8ea8","#3d6a8e","#7eb8b0","#5c7a94"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:8},boxWidth:10}}}}});
}
"""

EXT_COST_CSS = """
.cost-section{border:1px solid #c5d0dc;border-radius:10px;margin-bottom:.5rem;background:#fff;box-shadow:0 1px 6px rgba(15,43,70,.05)}
.cost-section>summary.cost-section-hd{display:flex;justify-content:space-between;align-items:center;gap:.65rem;padding:.55rem .7rem;cursor:pointer;list-style:none;background:linear-gradient(180deg,#eef3f8,#f8fafb)}
.cost-section>summary::-webkit-details-marker{display:none}
.cost-section-title{font-size:.86rem;font-weight:700;color:var(--navy);line-height:1.3;flex:1;min-width:0}
.cost-section-amt{flex-shrink:0;font-size:.9rem;font-weight:700;color:#fff;background:var(--navy);padding:.28rem .65rem;border-radius:6px;white-space:nowrap}
.cost-section-body{padding:0 .4rem .4rem}
.cost-item.cost-item-sub{border:none;border-radius:0;margin-bottom:0;background:transparent;box-shadow:none}
.cost-item.cost-item-sub>summary{padding:.26rem .5rem .26rem .85rem;font-size:.74rem;font-weight:400;background:transparent}
.cost-item.cost-item-sub>summary .cost-label{color:#9aa8b6;font-weight:500}
.cost-item.cost-item-sub>summary .cost-amt{color:#8b98a6;font-weight:600;font-size:.72rem}
.cost-item.cost-item-sub>summary .cost-amt-zero{color:#b8c2cc}
.cost-item.cost-item-sub .cost-children{padding:.1rem .5rem .25rem 1.35rem;border-top:none}
.cost-item.cost-item-sub[data-no-body]>summary{cursor:default}
.cost-subtotal,.cost-risk-line{display:flex;justify-content:space-between;padding:.32rem .55rem;font-size:.74rem;color:#7a8794;border-top:1px dashed #e2e8ee;margin-top:.15rem}
.cost-risk-line{font-style:italic}
.cost-section-total{display:flex;justify-content:space-between;padding:.4rem .55rem;margin-top:.2rem;border-radius:6px;background:linear-gradient(90deg,#0f2b46,#1a4a6e);color:#fff;font-size:.8rem;font-weight:700}
.cost-leaf.cost-leaf-sub{display:flex;justify-content:space-between;padding:.28rem .55rem .28rem .85rem;font-size:.74rem;color:#9aa8b6}
.cost-leaf.cost-leaf-sub span:last-child{color:#8b98a6;font-weight:600}
.cost-bullets{list-style:none;margin:.05rem 0 0;padding:0;font-size:.67rem;color:#a8b4c0;line-height:1.4}
.cost-bullets li{margin-bottom:.12rem;padding-left:.55rem;position:relative}
.cost-bullets li::before{content:"·";position:absolute;left:0;color:#c5cdd6}
.invest-kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-bottom:.65rem}
.invest-kpi{background:linear-gradient(160deg,#f8fafb,#fff);border:1px solid #e8ecf0;border-radius:10px;padding:.5rem;text-align:center}
.invest-kpi.highlight{border-color:#d4b84a;background:linear-gradient(160deg,#fffdf5,#fff)}
.invest-kpi .ik-val{font-size:.95rem;font-weight:700;color:var(--navy)}
.invest-kpi .ik-lbl{font-size:.62rem;color:var(--muted);margin-top:.15rem}
"""
