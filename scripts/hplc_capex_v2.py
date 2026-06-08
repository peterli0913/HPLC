"""Retrofit CapEx estimate (portfolio v2) — direct/indirect + 30% price risk & project contingency."""

from __future__ import annotations

import json

from ext_feasibility_cost import EXT_COST_CSS

# Amounts in £ (from estimate sheet, values originally in £k)
LYO = 967_000
HPLC_SKID = 358_000
TANKS = 200_000
PUMPS = 50_000
MAIN_EQUIP_SUB = LYO + HPLC_SKID + TANKS + PUMPS  # 1,575,000
MAIN_PRICE_RISK_PCT = 30
MAIN_PRICE_RISK = round(MAIN_EQUIP_SUB * MAIN_PRICE_RISK_PCT / 100)  # 472,500
MAIN_EQUIP_TOTAL = MAIN_EQUIP_SUB + MAIN_PRICE_RISK  # 2,047,500

CIVIL = 326_000
MECH = 264_000
ELEC = 128_000
HVAC = 35_300
INFRA_SUB = CIVIL + MECH + ELEC + HVAC  # 753,300
INFRA_PRICE_RISK = 226_000  # 753.3 × 30% ≈ 226 (£k)
INFRA_TOTAL = INFRA_SUB + INFRA_PRICE_RISK  # 979,300

DIRECT_TOTAL = MAIN_EQUIP_TOTAL + INFRA_TOTAL  # 3,026,800

FEED = 225_000
DETAIL_DESIGN = 289_000
CDM = 235_000
COMMISSION = 76_000
INDIRECT_SUB = FEED + DETAIL_DESIGN + CDM + COMMISSION  # 825,000
INDIRECT_PRICE_RISK = round(INDIRECT_SUB * MAIN_PRICE_RISK_PCT / 100)  # 247,500
INDIRECT_TOTAL = INDIRECT_SUB + INDIRECT_PRICE_RISK  # 1,072,500

SUBTOTAL = DIRECT_TOTAL + INDIRECT_TOTAL  # 4,099,300
PROJECT_CONT_PCT = 30
PROJECT_CONT = 1_229_800  # 4,099.3 × 30% ≈ 1,229.8 (£k)
HPLC_OOM = SUBTOTAL + PROJECT_CONT  # 5,329,100

FEAS_BASE = 3_783_000

CHART_STACK = {
    "direct_total": DIRECT_TOTAL,
    "indirect_total": INDIRECT_TOTAL,
    "project_cont": PROJECT_CONT,
}

CAPEX = {"total": HPLC_OOM, "feasBase": FEAS_BASE}
RISK_ON_BASE = {
    "base": FEAS_BASE,
    "oom": HPLC_OOM,
    "subtotal": SUBTOTAL,
    "project_cont": PROJECT_CONT,
}

HPLC_COST_I18N_ZH = {
    "capex": "Total CAPEX Estimate",
    "secDirect": "Total Direct Cost",
    "secIndirect": "Total Indirect Cost",
    "sec1": "1. Main Equipment",
    "lyo": "1.1 Lyo",
    "hplc": "1.2 HPLC skid",
    "tanks": "1.3 Tanks/Vessels",
    "pumps": "1.4 Pumps",
    "mainPrice": "1.5 Price Risk (30%)",
    "sec2": "2. Infrastructure Modification",
    "civil": "2.1 Civil & Structure",
    "mech": "2.2 Mechanical & Piping",
    "elec": "2.3 Electrical & Instrumentation",
    "hvac": "2.4 HVAC",
    "infraPrice": "2.5 Price Risk (30%)",
    "feed": "3. FEED Study",
    "design": "4. Detailed Design",
    "cdm": "5. CDM Fee",
    "comm": "6. Commission",
    "indirectPrice": "7. Price Risk (30%)",
    "subtotal": "Direct + Indirect Costs",
    "projectCont": "Whole Project contingency (30%)",
}

HPLC_COST_I18N_EN = dict(HPLC_COST_I18N_ZH)

CHART_I18N_ZH = {
    "stackDirect": "直接费用",
    "stackIndirect": "间接费用",
    "stackCont": "项目预备费",
    "donutTitle": "直接费用 — 设备与改造分项",
}

CHART_I18N_EN = {
    "stackDirect": "Direct cost",
    "stackIndirect": "Indirect cost",
    "stackCont": "Project contingency",
    "donutTitle": "Direct cost — equipment & infra",
}

DONUT_ITEMS = [
    {"id": "lyo", "amount": LYO},
    {"id": "hplc", "amount": HPLC_SKID},
    {"id": "tanks", "amount": TANKS},
    {"id": "pumps", "amount": PUMPS},
    {"id": "civil", "amount": CIVIL},
    {"id": "mech", "amount": MECH},
    {"id": "elec", "amount": ELEC},
    {"id": "hvac", "amount": HVAC},
]


def hplc_cost_data_json() -> str:
    return json.dumps(
        {
            "oom": HPLC_OOM,
            "directTotal": DIRECT_TOTAL,
            "indirectTotal": INDIRECT_TOTAL,
            "subtotal": SUBTOTAL,
            "projectCont": PROJECT_CONT,
            "projectContPct": PROJECT_CONT_PCT,
            "mainEquipSub": MAIN_EQUIP_SUB,
            "mainEquipTotal": MAIN_EQUIP_TOTAL,
            "mainPriceRisk": MAIN_PRICE_RISK,
            "infraSub": INFRA_SUB,
            "infraTotal": INFRA_TOTAL,
            "infraPriceRisk": INFRA_PRICE_RISK,
            "indirectSub": INDIRECT_SUB,
            "indirectPriceRisk": INDIRECT_PRICE_RISK,
            "lines": {
                "lyo": LYO,
                "hplc": HPLC_SKID,
                "tanks": TANKS,
                "pumps": PUMPS,
                "civil": CIVIL,
                "mech": MECH,
                "elec": ELEC,
                "hvac": HVAC,
                "feed": FEED,
                "design": DETAIL_DESIGN,
                "cdm": CDM,
                "comm": COMMISSION,
            },
            "chartStack": CHART_STACK,
            "chartDonut": [i["amount"] for i in DONUT_ITEMS],
            "chartDonutIds": [i["id"] for i in DONUT_ITEMS],
        }
    )


HPLC_COST_RENDER_JS = r"""
function hplcCostLabels(){return I18N[lang].hplcCost;}
function hplcLeaf(id,amt){
const L=hplcCostLabels();
return `<div class="cost-leaf cost-leaf-sub"><span>${L[id]}</span><span>${fm(Number(amt)||0)}</span></div>`;
}
function hplcSectionHd(title,total){
return `<span class="cost-section-title">${title}</span><span class="cost-section-amt">${fm(Number(total)||0)}</span>`;
}
function hplcCostHTML(){
const D=HPLC_COST_DATA,L=hplcCostLabels(),ln=D.lines||{};
const mainBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.sec1,D.mainEquipTotal)}</summary>
<div class="cost-section-body">
${hplcLeaf("lyo",ln.lyo)}${hplcLeaf("hplc",ln.hplc)}${hplcLeaf("tanks",ln.tanks)}${hplcLeaf("pumps",ln.pumps)}
${hplcLeaf("mainPrice",D.mainPriceRisk)}
</div></details>`;
const infraBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.sec2,D.infraTotal)}</summary>
<div class="cost-section-body">
${hplcLeaf("civil",ln.civil)}${hplcLeaf("mech",ln.mech)}${hplcLeaf("elec",ln.elec)}${hplcLeaf("hvac",ln.hvac)}
${hplcLeaf("infraPrice",D.infraPriceRisk)}
</div></details>`;
const directHdr=`<div class="cost-subtotal" style="margin-top:.35rem"><span>${L.secDirect}</span><span>${fm(D.directTotal)}</span></div>`;
const indirectItems=`${hplcLeaf("feed",ln.feed)}${hplcLeaf("design",ln.design)}${hplcLeaf("cdm",ln.cdm)}${hplcLeaf("comm",ln.comm)}${hplcLeaf("indirectPrice",D.indirectPriceRisk)}`;
const indirectBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hplcSectionHd(L.secIndirect,D.indirectTotal)}</summary>
<div class="cost-section-body">${indirectItems}</div></details>`;
const rollup=`<div class="cost-subtotal"><span>${L.subtotal}</span><span>${fm(D.subtotal)}</span></div>
<div class="cost-risk-line"><span>${L.projectCont}</span><span>${fm(D.projectCont)}</span></div>`;
return `<div class="cost-total-bar"><span>${L.capex}</span><span>${fm(D.oom)}</span></div>
${mainBlock}${infraBlock}${directHdr}${indirectBlock}${rollup}`;
}
function buildHplcInvestmentCharts(){
const zh=lang==="zh",D=HPLC_COST_DATA,Lc=I18N[lang].hplcChart||{};
const el1=document.getElementById("cHplc1")||document.getElementById("c1");
const el2=document.getElementById("cHplc2")||document.getElementById("c2");
if(!el1||!el2)return;
new Chart(el1,{type:"bar",data:{labels:[zh?"项目 OOM":"Project OOM"],datasets:[
{label:Lc.stackDirect||"Direct",data:[D.directTotal],backgroundColor:"#0f2b46"},
{label:Lc.stackIndirect||"Indirect",data:[D.indirectTotal],backgroundColor:"#009688"},
{label:Lc.stackCont||"Contingency",data:[D.projectCont],backgroundColor:"#c9a227"}]},
options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}},
scales:{x:{stacked:true,max:D.oom*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M"}},y:{stacked:true,display:false}}}});
const ids=D.chartDonutIds,amts=D.chartDonut;
const labels=ids.map(id=>(I18N[lang].hplcCost[id]||id));
new Chart(el2,{type:"doughnut",data:{labels,datasets:[{data:amts,backgroundColor:["#0f2b46","#1a4a6e","#2e6da4","#5b6eae","#4a7ba8","#009688","#4db6ac","#7eb8b0"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:8},boxWidth:10}}}}});
}
"""

HPLC_COST_CSS = EXT_COST_CSS
