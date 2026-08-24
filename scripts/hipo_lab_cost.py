"""HIPO lab (G-128 suite alterations) concept-stage data — portfolio briefing.

Sources (HIPO Feasibility Reports, no values derived outside these):
  * DPH_G-128 Suite Alterations Concept Cost Plan 260806
  * Asymchem Concept Programme_260727 (DRAFT CONCEPT PROGRAMME)
  * Asymchem G128 Alterations Concept Estimate Risk Register (raised 02/08/2026)
  * ILC Dover budget quotation JS26-11384-0, 22 Jul 2026 — reactor charging isolator
  * Howorth Q26543 budget isolator proposal, 11 Aug 2026 (email Darren Newsome → Clare Crook)
  * Reactor Charging Isolator Schematic - ASYMCHEM.docx (drawings only, no text)
  * Equipment List Costs for scoping 5 Aug.xlsx (client equipment; J95/K95 totals)
  * Fw External Proposed facility changes Asymchem Sandwich.msg
    (Paul Bax / DPML, 21 Aug 2026 — in-principle approval for PDF and DPH)
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------- areas
GIFA = 215  # m2, cost plan header
LAB_AREA = 182  # m2, rate basis for lab services lines
WRITEUP_AREA = 33  # m2, carpet allowance for write-up area

# ------------------------------------------------- 0 Facilitating Works
FW_STRIP_BUILD = 46_967  # 0.1 strip out, alterations and demolition
FW_STRIP_SERVICES = 18_600  # 0.2 strip out (services)
FACILITATING = 65_567

# ------------------------------------------------------ 2 Superstructure
SS_WALLS = 42_440  # 2.7 internal walls and partitions
SS_DOORS = 26_250  # 2.8 internal doors
SUPERSTRUCTURE = 68_690

# ------------------------------------------------------------ 3 Finishes
FIN_WALL = 9_810
FIN_FLOOR = 23_631
FIN_CEILING = 25_457
FINISHES = 58_898

# --------------------------------------- 4 Fittings, Furnishings & Equip
FFE_ISO_4NR = 600_000  # isolators; provisional allowance 4 nr x 150,000
FFE_ISO_1NR = 100_000  # isolators; provisional allowance 1 nr x 100,000
FFE_FUME = 20_000  # fume hoods assumed serviceable; servicing/repair allowance
FFE_SF6 = 20_000  # SF6 testing
FFE_FURN_GEN = 20_000  # lockers, step-over bench, mobile benches, BIBO bins
FFE_FURN_WRITEUP = 5_000
FFE = 765_000

# ------------------------------------------------------------ 5 Services
SV_DISPOSAL = 3_000  # 5.3 drainage connections (sinks & shower)
SV_WATER = 38_600  # 5.4 H&CWS, sink reinstatement, mist shower
SV_HVAC = 217_920  # 5.6 AHU, ductwork, bag-in/bag-out HEPA, BMS, balancing
SV_ELEC = 107_380  # 5.8 small power + lighting
SV_FIRE = 30_030  # 5.11 sprinklers
SV_COMMS = 51_345  # 5.12 access control, cabling, CCTV, fire alarm
SV_SPECIAL = 63_700  # 5.13 laboratory gas pipework
SV_BWIC = 25_599  # 5.14 builder's work in connection (5%)
SERVICES = 537_574

BUILDING_WORKS = 1_495_729  # Facilitating and Building Works (0+2+3+4+5)

# ------------------------------------------------------- 9 Preliminaries
PRE_TEMP = 10_500  # 9.1 temporary works
PRE_WELFARE = 21_000  # 9.2 site welfare and accommodation, 21 wks
PRE_DCM = 331_000  # 9.3 design and construction management
PRELIMS = 362_500

OHP_PCT = 5.0
OHP = 92_911  # 10 overheads and profit
TOTAL_BUILDING_WORKS = 1_951_140

# ------------------------------------------ 11-14 above building works
PROF_SERVICES = 141_800  # 11 professional services
SUBTOTAL_1 = 2_092_940
CLIENT_EQUIP = 1_975_045  # 12 equipment supplied and installed by the Client

# Equipment List Costs for scoping 5 Aug.xlsx — Sheet1 J95 / K95 and group sums.
# Cost-plan line remains CLIENT_EQUIP; do not substitute the list purchase total.
EQUIP_LIST_TOTAL = 2_428_245  # column J "Total Cost"
EQUIP_LIST_PURCHASE = 1_957_045  # column K "To Purchase Cos"
EQUIP_LIST_ARD_PURCH = 912_600
EQUIP_LIST_ISO_PURCH = 455_345
EQUIP_LIST_CRD_PURCH = 589_100
EQUIP_LIST_EXISTING = 471_200  # New or Existing = E; To Purchase = 0
assert (
    EQUIP_LIST_ARD_PURCH + EQUIP_LIST_ISO_PURCH + EQUIP_LIST_CRD_PURCH
    == EQUIP_LIST_PURCHASE
)
assert EQUIP_LIST_PURCHASE + EQUIP_LIST_EXISTING == EQUIP_LIST_TOTAL

# Line items from Equipment List Costs for scoping 5 Aug.xlsx (Total Cost > 0).
# Title falls back to Comments / Manufacturer when the Title cell is blank.
# Blank New/Existing cells are treated as New so the New ∩ Must-have total stays £1,957,045.
# ne: N = New, E = Existing, N/E = mixed.
EQUIP_ITEMS = [
    {"id": "eq3", "group": "ARD/QC", "title": "HPLC System", "titleZh": "HPLC 系统", "location": "Room 2", "mfr": "Aglient Technologies", "ne": "N", "cost": 300000},
    {"id": "eq9", "group": "ARD/QC", "title": "HPLC/Mass Spectrometer System", "titleZh": "HPLC/质谱系统", "location": "Bench top", "mfr": "Agilent Technologies", "ne": "N", "cost": 200000},
    {"id": "eq16", "group": "ARD/QC", "title": "GCMS", "titleZh": "GCMS", "location": "or GCMS", "mfr": "", "ne": "N", "cost": 120000},
    {"id": "eq17", "group": "ARD/QC", "title": "nitrogen gas generator", "titleZh": "氮气发生器", "location": "or GCMS", "mfr": "", "ne": "N", "cost": 8000},
    {"id": "eq18", "group": "ARD/QC", "title": "hydrogen gas generator", "titleZh": "氢气发生器", "location": "or GCMS", "mfr": "", "ne": "N", "cost": 8000},
    {"id": "eq19", "group": "ARD/QC", "title": "Electronic Pipette", "titleZh": "电动移液器", "location": "Benchtop", "mfr": "Handystep", "ne": "N", "cost": 1600},
    {"id": "eq20", "group": "ARD/QC", "title": "Milli-Q", "titleZh": "Milli-Q", "location": "Undersink", "mfr": "Millipore", "ne": "N", "cost": 20000},
    {"id": "eq21", "group": "ARD/QC", "title": "Prep HPLC", "titleZh": "制备 HPLC", "location": "Large Fumehood", "mfr": "Hanbon", "ne": "N", "cost": 50000},
    {"id": "eq23", "group": "ARD/QC", "title": "pH", "titleZh": "pH 计", "location": "Fumhood", "mfr": "Mettler Toledo", "ne": "N", "cost": 20000},
    {"id": "eq25", "group": "ARD/QC", "title": "SFC", "titleZh": "SFC", "location": "Bench top", "mfr": "Waters", "ne": "E", "cost": 150000},
    {"id": "eq27", "group": "ARD/QC", "title": "GC", "titleZh": "GC", "location": "Bench top (if sapce is limited, remove another FH?)", "mfr": "Aglient", "ne": "E", "cost": 80000},
    {"id": "eq29", "group": "ARD/QC", "title": "Mass Spec", "titleZh": "质谱", "location": "Bench top", "mfr": "Aglient", "ne": "N", "cost": 140000},
    {"id": "eq30", "group": "ARD/QC", "title": "KF Coulimetric", "titleZh": "库仑法 KF", "location": "Fumehood", "mfr": "Metrohm", "ne": "N", "cost": 45000},
    {"id": "eq36", "group": "Isolators", "title": "Huber TC45 with immersion cooler", "titleZh": "Huber TC45 浸入式冷却器", "location": "Under isolator 2", "mfr": "Huber", "ne": "N", "cost": 4345},
    {"id": "eq37", "group": "Isolators", "title": "Karl Fisher Titrator", "titleZh": "卡尔费休滴定仪", "location": "Isolator 1", "mfr": "Mettler Toledo", "ne": "N", "cost": 30000},
    {"id": "eq38", "group": "Isolators", "title": "Benchtop Powder X-ray Diffractor", "titleZh": "台式粉末 X 射线衍射仪", "location": "Benchtop", "mfr": "D2", "ne": "E", "cost": 200000},
    {"id": "eq39", "group": "Isolators", "title": "Particle Size", "titleZh": "粒度仪", "location": "Isolator 5", "mfr": "Malvern", "ne": "N", "cost": 160000},
    {"id": "eq40", "group": "Isolators", "title": "Lyophiliser", "titleZh": "冻干机", "location": "Benchtop", "mfr": "Tofflon", "ne": "N", "cost": 100000},
    {"id": "eq41", "group": "Isolators", "title": "Analytical Balance", "titleZh": "分析天平", "location": "Isolator 1", "mfr": "Mettler Toledo", "ne": "N", "cost": 20000},
    {"id": "eq42", "group": "Isolators", "title": "Microbalance", "titleZh": "微量天平", "location": "isolator 1", "mfr": "", "ne": "N", "cost": 25000},
    {"id": "eq43", "group": "Isolators", "title": "Easymax Reactor System", "titleZh": "EasyMax 反应系统", "location": "isolator 3", "mfr": "Mettler Toledo", "ne": "N", "cost": 80000},
    {"id": "eq45", "group": "Isolators", "title": "Chiller unit", "titleZh": "冷水机", "location": "under isolator 3", "mfr": "Julabo", "ne": "E", "cost": 12000},
    {"id": "eq47", "group": "Isolators", "title": "Drying Oven", "titleZh": "干燥箱", "location": "Isolator 4", "mfr": "Salvis", "ne": "N/E", "cost": 36000},
    {"id": "eq48", "group": "Isolators", "title": "FTIR", "titleZh": "FTIR", "location": "Isolator 2", "mfr": "Thermo", "ne": "E", "cost": 28000},
    {"id": "eq53", "group": "CRD", "title": "Laboratory Fridge", "titleZh": "实验室冰箱", "location": "Room 4", "mfr": "Lec", "ne": "N", "cost": 750},
    {"id": "eq54", "group": "CRD", "title": "Laboratory Freezer", "titleZh": "实验室冰柜", "location": "Room 4", "mfr": "Lec", "ne": "N", "cost": 750},
    {"id": "eq55", "group": "CRD", "title": "Reactor Ready Twin reactor", "titleZh": "Reactor Ready 双反应釜", "location": "FH1", "mfr": "Reactor Ready vessels", "ne": "N", "cost": 20000},
    {"id": "eq56", "group": "CRD", "title": "Mettler Toledo SP-50 Dosing units", "titleZh": "梅特勒 SP-50 加料单元", "location": "FH1", "mfr": "Mettler Toledo SP-50 Dosing units", "ne": "N", "cost": 1600},
    {"id": "eq57", "group": "CRD", "title": "RX10 Controller", "titleZh": "RX10 控制器", "location": "FH1", "mfr": "RX10 Controller", "ne": "N", "cost": 2400},
    {"id": "eq58", "group": "CRD", "title": "Heidolph Motors", "titleZh": "Heidolph 电机", "location": "FH1", "mfr": "Heidolph Motors", "ne": "N", "cost": 1600},
    {"id": "eq59", "group": "CRD", "title": "Reactor Ready Stand", "titleZh": "Reactor Ready 支架", "location": "FH1", "mfr": "Reactor Ready Stand", "ne": "N", "cost": 1000},
    {"id": "eq60", "group": "CRD", "title": "Vacuum Pump", "titleZh": "真空泵", "location": "FH1", "mfr": "Vacuubrand", "ne": "N", "cost": 5000},
    {"id": "eq61", "group": "CRD", "title": "Recirculating Chiller", "titleZh": "循环冷水机", "location": "FH1", "mfr": "Huber", "ne": "N", "cost": 23000},
    {"id": "eq62", "group": "CRD", "title": "Analytical Balance", "titleZh": "分析天平", "location": "Either/or", "mfr": "Mettler Toledo", "ne": "N", "cost": 20000},
    {"id": "eq63", "group": "CRD", "title": "Large Scale Balance", "titleZh": "大称量天平", "location": "Either/or", "mfr": "Sartorius", "ne": "N", "cost": 1000},
    {"id": "eq65", "group": "CRD", "title": "Easymax Reactor System", "titleZh": "EasyMax 反应系统", "location": "FH2", "mfr": "Mettler Toledo", "ne": "N", "cost": 160000},
    {"id": "eq67", "group": "CRD", "title": "Chiller unit", "titleZh": "冷水机", "location": "FH2", "mfr": "Julabo", "ne": "N", "cost": 24000},
    {"id": "eq70", "group": "CRD", "title": "Mettler Tolesdo SP-50 Dosing units", "titleZh": "梅特勒 SP-50 加料单元", "location": "FH3", "mfr": "Mettler Tolesdo SP-50 Dosing units", "ne": "N", "cost": 80000},
    {"id": "eq71", "group": "CRD", "title": "Chiller unit", "titleZh": "冷水机", "location": "FH3", "mfr": "Julabo", "ne": "N", "cost": 12000},
    {"id": "eq72", "group": "CRD", "title": "Stem blocks", "titleZh": "Stem 加热模块", "location": "FH3", "mfr": "Electrothermal", "ne": "N", "cost": 2000},
    {"id": "eq73", "group": "CRD", "title": "Stirrer hotplate", "titleZh": "搅拌加热板", "location": "FH3", "mfr": "IKA", "ne": "E", "cost": 1200},
    {"id": "eq76", "group": "CRD", "title": "Biotage", "titleZh": "Biotage", "location": "FH4 - Flexible", "mfr": "Biotage", "ne": "N", "cost": 12000},
    {"id": "eq77", "group": "CRD", "title": "Rotary Evaporator", "titleZh": "旋转蒸发仪", "location": "FH4 - Flexible", "mfr": "Heidolph", "ne": "N", "cost": 6000},
    {"id": "eq78", "group": "CRD", "title": "Vacuum Pump", "titleZh": "真空泵", "location": "FH4 - Flexible", "mfr": "Vacuubrand", "ne": "N", "cost": 5000},
    {"id": "eq82", "group": "CRD", "title": "Overhead stirrer", "titleZh": "顶置搅拌器", "location": "FH4 - Flexible", "mfr": "", "ne": "N", "cost": 1000},
    {"id": "eq84", "group": "CRD", "title": "Software", "titleZh": "软件", "location": "Software", "mfr": "", "ne": "N", "cost": 200000},
    {"id": "eq88", "group": "CRD", "title": "Dishwasher/glasswash", "titleZh": "器皿清洗机", "location": "Miscellaneous", "mfr": "Miele", "ne": "N", "cost": 10000},
]
assert sum(i["cost"] for i in EQUIP_ITEMS if i["ne"] != "E") == EQUIP_LIST_PURCHASE
assert sum(i["cost"] for i in EQUIP_ITEMS) == EQUIP_LIST_TOTAL

SUBTOTAL_2 = 4_067_985
RISK_ALLOWANCE = 397_875  # 13.1 design development risk (13.2 incl. above)
COST_LIMIT_EXCL_INF = 4_465_860
INFLATION_PCT = 2.15
INFLATION = 96_184  # 14 inflation
HIPO_TOTAL = 4_562_044  # COST LIMIT including inflation; VAT excluded

# Estimate accuracy block on cost plan summary
ACCURACY_UPPER = 4_990_000
ACCURACY_LOWER = 3_740_000

# Risk register totals
RISK_NET_TOTAL = 397_875
RISK_LOW_EST = 146_633
RISK_HIGH_EST = 649_117

# ------------------------------------------- isolator budget quotations (new)
# Howorth Q26543 — budget pricing, Ex Works Howorth; packing, delivery,
# installation and commissioning to be provided on confirmation of final designs.
HOWORTH_ISOLATOR = 250_000  # single chamber dispensing isolator
HOWORTH_RTP_OPTION = 18_000  # 1 x 190 RTP incl. 400 mm container (optional)
HOWORTH_MOCKUP = 17_000

# ILC Dover JS26-11384-0 — EXW CH-Rossens, Incoterm 2020, without VAT.
ILC_ENGINEERING = 10_370  # Pos 2 concept development, reactors R19-R22
ILC_FLEX_ISOLATOR = 94_700  # Pos 3 flexible isolator
ILC_DOCUMENTATION = 5_060  # Pos 4 documentation
ILC_SERVICES = 5_670  # Pos 5 services (FAT 3,270 + packing 2,400)
ILC_TOTAL = 115_800  # quotation total = Pos 2 + 3 + 4 + 5
ILC_CERTIFICATES = 2_750  # Pos 4.1, priced separately (outside the total above)
ILC_LEAD_WEEKS = 20  # from approval of the drawing

# Cost-plan isolator allowances, for like-for-like comparison with the quotes
ISO_ALLOWANCE_UNIT_4NR = 150_000
ISO_ALLOWANCE_UNIT_1NR = 100_000
ISO_ALLOWANCE_TOTAL = FFE_ISO_4NR + FFE_ISO_1NR  # 700,000

CHART_STACK = {
    "building": TOTAL_BUILDING_WORKS,
    "prof": PROF_SERVICES,
    "equip": CLIENT_EQUIP,
    "risk": RISK_ALLOWANCE,
    "inflation": INFLATION,
}

DONUT_ITEMS = [
    {"id": "sec0", "amount": FACILITATING},
    {"id": "sec2", "amount": SUPERSTRUCTURE},
    {"id": "sec3", "amount": FINISHES},
    {"id": "sec4", "amount": FFE},
    {"id": "sec5", "amount": SERVICES},
    {"id": "sec9", "amount": PRELIMS},
    {"id": "sec10", "amount": OHP},
]

# ------------------------------------------------------------- programme
# Asymchem Concept Programme_260727: 262 days, Tue 01/09/26 - Fri 17/09/27.
# Clare (21 Aug 2026) asked for +6 weeks to cover the time to start the work and
# the funding decision; that shift is applied in the build script, not here.
# g[1], g[2] = bar geometry.
PROGRAMME_DAYS = 262
SHIFT_WEEKS_CLARE = 6
GANTT_HIPO = [
    [
        "hFund",
        "2026-09-01",
        "2026-09-08",
        "warn",
        "Asymchem funding approval & decision to proceed — milestone 01 Sep 2026 (0 days).",
        "凯莱英资金批准与推进决定 — 节点 2026-09-01（0 天）。",
    ],
    [
        "hConsult",
        "2026-09-01",
        "2026-09-14",
        "plan",
        "Appoint consultant team (5 days); draft Basis of Design (10 days).",
        "顾问团队任命（5 天）；编制设计基础 BoD 草案（10 天）。",
    ],
    [
        "hContractor",
        "2026-09-15",
        "2026-10-19",
        "plan",
        "Engage and appoint principal contractor (25 days): draft contract, enquiry/ITT, "
        "negotiate contractor's fee.",
        "主承包商接洽与任命（25 天）：合同起草、招标询价（ITT）、承包商费率谈判。",
    ],
    [
        "hAward",
        "2026-10-19",
        "2026-11-16",
        "plan",
        "Contract award milestone 19 Oct 2026; mobilise & contract (20 days).",
        "合同授予节点 2026-10-19；动员与签约（20 天）。",
    ],
    [
        "hSurvey",
        "2026-11-17",
        "2027-01-13",
        "plan",
        "Design stage (35 days): specify and organise initial site surveys and investigations; "
        "prepare initial project control documents & PEP.",
        "设计阶段（35 天）：现场勘查与调查的界定、组织与执行；编制初版项目控制文件与 PEP。",
    ],
    [
        "hLabDesign",
        "2026-11-17",
        "2027-03-03",
        "plan",
        "Lab design (70 days): user meeting / RFI / BoD confirmation, concept & co-ordinated "
        "design, equipment specification & schedules, detailed design, cost estimate +/-10%, "
        "building control.",
        "实验室设计（70 天）：用户会议 / RFI / BoD 确认，概念与协调设计，设备规格与清单，"
        "详细设计，±10% 费用估算，建筑审批。",
    ],
    [
        "hCdm",
        "2026-11-17",
        "2027-08-19",
        "plan",
        "CDM (187 days): review/prepare PCI, submit F10, construction phase plan, H&S file / O&M.",
        "CDM（187 天）：PCI 审核与编制、F10 提交、施工阶段计划、健康安全档案 / O&M。",
    ],
    [
        "hIso",
        "2026-12-01",
        "2027-06-02",
        "warn",
        "Isolators (120 days): vendor shortlisting & T&Cs, tender & approval, order placed, "
        "drawings approved, manufacture [12 weeks?], delivery to site 02 Jun 2027.",
        "隔离器（120 天）：供应商短名单与商务条款、招标与批准、下单、图纸批准、"
        "制造（12 周？）、2027-06-02 到场。",
    ],
    [
        "hFume",
        "2026-12-01",
        "2027-06-02",
        "warn",
        "Fume cupboards (new? TBC) — 120 days, same procurement route as isolators.",
        "通风柜（是否新购待定）— 120 天，采购路径同隔离器。",
    ],
    [
        "hFurn",
        "2026-12-01",
        "2027-04-30",
        "warn",
        "Laboratory furniture (100 days): shortlist, tender, order, manufacture, "
        "delivery to site 30 Apr 2027.",
        "实验室家具（100 天）：短名单、招标、下单、制造、2027-04-30 到场。",
    ],
    [
        "hTrade",
        "2026-12-01",
        "2027-04-16",
        "warn",
        "Works procurement — trade contractors (90 days): shortlist/PQQ, tendering and "
        "approval in principle, final price and contract based on detailed design.",
        "分包工程采购（90 天）：短名单 / PQQ、招标与原则性批准、基于详细设计的最终价格与合同。",
    ],
    [
        "hConstr",
        "2027-04-19",
        "2027-08-05",
        "build",
        "Construction from 19 Apr 2027: strip out / MEP divestment and demolition, walls and "
        "doors, write-up area, 1st fix MEP, decoration, isolator installation, 2nd fix MEP, "
        "ceilings and floors, furniture and equipment.",
        "施工自 2027-04-19 起：拆除与机电撤除、墙体与门、书写区、一次机电、装饰、"
        "隔离器安装、二次机电、吊顶与地面、家具与设备安装。",
    ],
    [
        "hComm",
        "2027-08-06",
        "2027-08-26",
        "build",
        "Test & commission HVAC, isolators, fume cupboards and equipment (10 days); "
        "pharmaceutical clean and handover (5 days).",
        "暖通、隔离器、通风柜及设备测试调试（10 天）；药品级清洁与移交（5 天）。",
    ],
    [
        "hRisk",
        "2027-08-27",
        "2027-09-17",
        "warn",
        "Programme risk allowance (15 days); completion 17 Sep 2027.",
        "进度风险预留（15 天）；竣工 2027-09-17。",
    ],
]

# ------------------------------------------------------------------ i18n
HIPO_COST_I18N_ZH = {
    "capex": "项目投资（含通胀）",
    "secBuild": "建筑工程费合计 Total Building Works Estimate",
    "sec0": "1 改造工程 Facilitating Works",
    "fw1": "1.1 拆除、改造与拆砌（隔断等）",
    "fw2": "1.2 机电拆除（燃气、风管、电气、烟感、Crowcon 等）",
    "sec2": "2 上部结构 Superstructure",
    "ss1": "2.7 内墙与隔断（墙面衬板、新建隔断、氢气管道包封）",
    "ss2": "2.8 内门（5 单开 + 1 子母卫生门、2 木门、4 樘旧门翻新）",
    "sec3": "3 装饰 Finishes",
    "fin1": "3.1 墙面装饰（实验室 475 m²、办公区 70 m²）",
    "fin2": "3.2 地面（实验室卷材乙烯 173 m²、踢脚 136 m、办公区地毯 33 m²）",
    "fin3": "3.3 吊顶（实验室金属吊顶 173 m²、周边收口 136 m）",
    "sec4": "4 家具与设备 Fittings, Furnishings and Equipment",
    "ffeIso4": "隔离器 4 台 × £150,000",
    "ffeIso1": "隔离器 1 台 × £100,000",
    "ffeFume": "通风柜（假设现有可用，仅列维修保养）",
    "ffeSf6": "SF6 检漏测试",
    "ffeFurn": "家具（更衣柜、跨越凳、移动实验台、BIBO 桶）",
    "ffeWrite": "办公区家具",
    "sec5": "5 机电安装 Services",
    "sv3": "5.3 排水（水槽与淋浴接管）",
    "sv4": "5.4 给水（冷热水、水槽复装、雾化淋浴 £35,000）",
    "sv6": "5.6 暖通空调（AHU 恢复使用、全套风管、袋进袋出 HEPA 排风、BMS 升级、系统平衡）",
    "sv8": "5.8 电气（小动力 182 m²、照明 182 m²，含设备接电）",
    "sv11": "5.11 消防（实验室喷淋 182 m²）",
    "sv12": "5.12 通信、安防与控制（门禁 3 处、结构化布线、CCTV、火灾报警）",
    "sv13": "5.13 特殊安装（实验室气体管道 182 m²）",
    "sv14": "5.14 配合机电的土建工作（开洞、防火封堵、检修口，按 5%）",
    "subBuild": "改造与建筑工程小计 Facilitating and Building Works",
    "sec9": "6 临建与承包商设计 Preliminaries",
    "pre1": "6.1 临时工程（保留设备与公共区域防护、临时照明）",
    "pre2": "6.2 现场福利与临建（施工期 21 周）",
    "pre3": "6.3 设计与施工管理（勘查、RIBA 2/3 与 RIBA 4 承包商设计、RIBA 5 现场资源 22 周）",
    "sec10": "7 管理费与利润 Overheads and Profit（5.00%）",
    "secProf": "8 专业服务费 Professional Services",
    "prof": "项目管理（合同前 33 周 / 合同后 22 周 / 缺陷期）、设计支持、商务支持与合同管理",
    "secEquip": "9 业主（凯莱英）供货并安装设备 Equipment (supplied and installed by the Client)",
    "equip": "待采购（《Equipment List Costs for scoping 5 Aug》）",
    "secRisk": "10 风险预备费 Risk Allowance Estimate",
    "risk": "10.1 设计发展风险（依风险登记册）",
    "secInf": "11 通胀 Inflation（2.15%）",
    "inflation": "自基准日至施工期的通胀调整",
}

HIPO_COST_I18N_EN = {
    "capex": "COST LIMIT (including inflation)",
    "secBuild": "Total Building Works Estimate",
    "sec0": "1 Facilitating Works",
    "fw1": "1.1 Strip out, alterations and demolition (partitions and the like)",
    "fw2": "1.2 Strip out (services) — gas, ductwork, electrical, detectors, Crowcon",
    "sec2": "2 Superstructure",
    "ss1": "2.7 Internal walls and partitions (wall lining, new partitions, H₂ pipework boxing)",
    "ss2": "2.8 Internal doors (5 single-leaf + 1 leaf-and-half hygienic, 2 timber, 4 refurbished)",
    "sec3": "3 Finishes",
    "fin1": "3.1 Wall finishes (lab 475 m², write-up 70 m²)",
    "fin2": "3.2 Floor finishes (sheet vinyl 173 m², coved skirting 136 m, carpet 33 m²)",
    "fin3": "3.3 Ceiling finishes (metal suspended ceiling 173 m², perimeter detail 136 m)",
    "sec4": "4 Fittings, Furnishings and Equipment",
    "ffeIso4": "Isolators; 4 nr × £150,000",
    "ffeIso1": "Isolators; 1 nr × £100,000",
    "ffeFume": "Fume hoods — existing assumed serviceable; servicing/repair allowance",
    "ffeSf6": "SF6 testing allowance",
    "ffeFurn": "Furniture allowance (lockers, step-over bench, mobile benches, BIBO bins)",
    "ffeWrite": "Furniture for write-up space",
    "sec5": "5 Services",
    "sv3": "5.3 Disposal installations (sink & shower drainage connections)",
    "sv4": "5.4 Water installations (H&CWS, sink reinstatement, mist shower £35,000)",
    "sv6": "5.6 HVAC (AHU back into use, full ductwork, bag-in/bag-out HEPA, BMS upgrade, balancing)",
    "sv8": "5.8 Electrical installations (small power 182 m², lighting 182 m², equipment connections)",
    "sv11": "5.11 Fire and lightning protection (sprinklers 182 m²)",
    "sv12": "5.12 Communication, security and control (access control 3 nr, cabling, CCTV, fire alarm)",
    "sv13": "5.13 Special installations (laboratory gas pipework 182 m²)",
    "sv14": "5.14 Builder's work in connection with services (holes, fire stopping, hatches — 5%)",
    "subBuild": "Facilitating and Building Works",
    "sec9": "6 Preliminaries (incl. Contractor's design)",
    "pre1": "6.1 Temporary works (protection to retained equipment / common areas, lighting)",
    "pre2": "6.2 Site welfare and accommodation (21 weeks)",
    "pre3": "6.3 Design and construction management (surveys, RIBA 2/3 and RIBA 4 contractor's design, RIBA 5 resourcing 22 wks)",
    "sec10": "7 Overheads and Profit (5.00%)",
    "secProf": "8 Professional Services",
    "prof": "Project management (pre-contract 33 wks / post-contract 22 wks / defects), design support, commercial support & contract administration",
    "secEquip": "9 Equipment (supplied and installed by the Client)",
    "equip": "To purchase (Equipment List Costs for scoping 5 Aug)",
    "secRisk": "10 Risk Allowance Estimate",
    "risk": "10.1 Design development risk (refer to risk register)",
    "secInf": "11 Inflation (2.15%)",
    "inflation": "Inflation from base date through construction",
}

CHART_I18N_ZH = {
    "stackBuilding": "建筑工程费",
    "stackProf": "专业服务费",
    "stackEquip": "业主（凯莱英）供货设备",
    "stackRisk": "风险预备费",
    "stackInf": "通胀",
    "donutTitle": "建筑工程费 — 分项",
    "stackAxis": "项目投资",
}

CHART_I18N_EN = {
    "stackBuilding": "Building works",
    "stackProf": "Professional services",
    "stackEquip": "Client (Asymchem) equipment",
    "stackRisk": "Risk allowance",
    "stackInf": "Inflation",
    "donutTitle": "Building works — breakdown",
    "stackAxis": "Project investment",
}


def hipo_cost_data_json() -> str:
    return json.dumps(
        {
            "total": HIPO_TOTAL,
            "buildingWorks": TOTAL_BUILDING_WORKS,
            "facBuildSub": BUILDING_WORKS,
            "profServices": PROF_SERVICES,
            "clientEquip": CLIENT_EQUIP,
            "riskAllowance": RISK_ALLOWANCE,
            "inflation": INFLATION,
            "groups": {
                "sec0": FACILITATING,
                "sec2": SUPERSTRUCTURE,
                "sec3": FINISHES,
                "sec4": FFE,
                "sec5": SERVICES,
                "sec9": PRELIMS,
                "sec10": OHP,
            },
            "lines": {
                "fw1": FW_STRIP_BUILD,
                "fw2": FW_STRIP_SERVICES,
                "ss1": SS_WALLS,
                "ss2": SS_DOORS,
                "fin1": FIN_WALL,
                "fin2": FIN_FLOOR,
                "fin3": FIN_CEILING,
                "ffeIso4": FFE_ISO_4NR,
                "ffeIso1": FFE_ISO_1NR,
                "ffeFume": FFE_FUME,
                "ffeSf6": FFE_SF6,
                "ffeFurn": FFE_FURN_GEN,
                "ffeWrite": FFE_FURN_WRITEUP,
                "sv3": SV_DISPOSAL,
                "sv4": SV_WATER,
                "sv6": SV_HVAC,
                "sv8": SV_ELEC,
                "sv11": SV_FIRE,
                "sv12": SV_COMMS,
                "sv13": SV_SPECIAL,
                "sv14": SV_BWIC,
                "pre1": PRE_TEMP,
                "pre2": PRE_WELFARE,
                "pre3": PRE_DCM,
                "sec10": OHP,
                "prof": PROF_SERVICES,
                "equip": CLIENT_EQUIP,
                "risk": RISK_ALLOWANCE,
                "inflation": INFLATION,
            },
            "chartStack": CHART_STACK,
            "chartDonut": [i["amount"] for i in DONUT_ITEMS],
            "chartDonutIds": [i["id"] for i in DONUT_ITEMS],
        }
    )


HIPO_COST_RENDER_JS = r"""
function hipoCostLabels(){return I18N[lang].hipoCost;}
function hipoLeaf(id,amt,depth,amtId,lblId){
const L=hipoCostLabels();
const pad=depth===3?" cost-leaf-l3":"";
const idAttr=amtId?` id="${amtId}"`:"";
const lblAttr=lblId?` id="${lblId}"`:"";
return `<div class="cost-leaf cost-leaf-sub${pad}"><span${lblAttr}>${L[id]}</span><span${idAttr}>${fm(Number(amt)||0)}</span></div>`;
}
function hipoSectionHd(title,total,amtId){
const idAttr=amtId?` id="${amtId}"`:"";
return `<span class="cost-section-title">${title}</span><span class="cost-section-amt"${idAttr}>${fm(Number(total)||0)}</span>`;
}
function hipoSubHd(title,total){
return `<span class="cost-label">${title}</span><span class="cost-amt">${fm(Number(total)||0)}</span>`;
}
function hipoGroup(id,leaves){
const D=HIPO_COST_DATA,L=hipoCostLabels(),ln=D.lines||{};
const body=leaves.map(k=>hipoLeaf(k,ln[k],3)).join("");
return `<details class="cost-item cost-item-sub cost-item-l2" open><summary>${hipoSubHd(L[id],D.groups[id])}</summary>
<div class="cost-children">${body}</div></details>`;
}
function hipoGroupFlat(id){
const D=HIPO_COST_DATA,L=hipoCostLabels();
return `<details class="cost-item cost-item-sub cost-item-l2" data-no-body><summary>${hipoSubHd(L[id],D.groups[id])}</summary></details>`;
}
function hipoCostHTML(){
const D=HIPO_COST_DATA,L=hipoCostLabels(),ln=D.lines||{};
const buildBody=[
hipoGroup("sec0",["fw1","fw2"]),
hipoGroup("sec2",["ss1","ss2"]),
hipoGroup("sec3",["fin1","fin2","fin3"]),
hipoGroup("sec4",["ffeIso4","ffeIso1","ffeFume","ffeSf6","ffeFurn","ffeWrite"]),
hipoGroup("sec5",["sv3","sv4","sv6","sv8","sv11","sv12","sv13","sv14"]),
`<div class="cost-subtotal"><span>${L.subBuild}</span><span>${fm(D.facBuildSub)}</span></div>`,
hipoGroup("sec9",["pre1","pre2","pre3"]),
hipoGroupFlat("sec10"),
].join("");
const buildBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hipoSectionHd(L.secBuild,D.buildingWorks)}</summary>
<div class="cost-section-body">${buildBody}</div></details>`;
const profBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hipoSectionHd(L.secProf,D.profServices)}</summary>
<div class="cost-section-body">${hipoLeaf("prof",ln.prof,3)}</div></details>`;
const equipBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hipoSectionHd(L.secEquip,D.clientEquip,"hipoLiveEquipSec")}</summary>
<div class="cost-section-body">${hipoLeaf("equip",ln.equip,3,"hipoLiveEquipLeaf","hipoLiveEquipLabel")}</div></details>`;
const riskBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hipoSectionHd(L.secRisk,D.riskAllowance)}</summary>
<div class="cost-section-body">${hipoLeaf("risk",ln.risk,3)}</div></details>`;
const infBlock=`<details class="cost-section" open><summary class="cost-section-hd">${hipoSectionHd(L.secInf,D.inflation)}</summary>
<div class="cost-section-body">${hipoLeaf("inflation",ln.inflation,3)}</div></details>`;
return `<div class="cost-total-bar"><span>${L.capex}</span><span id="hipoLiveProjectBar">${fm(D.total)}</span></div>${buildBlock}${profBlock}${equipBlock}${riskBlock}${infBlock}`;
}
let _hipoBarChart=null;
function buildHipoInvestmentCharts(){
const D=HIPO_COST_DATA,Lc=I18N[lang].hipoChart||{};
const el1=document.getElementById("cHipo1"),el2=document.getElementById("cHipo2");
if(!el1||!el2)return;
if(_hipoBarChart){_hipoBarChart.destroy();_hipoBarChart=null;}
const S=D.chartStack;
_hipoBarChart=new Chart(el1,{type:"bar",data:{labels:[Lc.stackAxis],datasets:[
{label:Lc.stackBuilding,data:[S.building],backgroundColor:"#0f2b46"},
{label:Lc.stackProf,data:[S.prof],backgroundColor:"#2e6da4"},
{label:Lc.stackEquip,data:[S.equip],backgroundColor:"#1f7a6f"},
{label:Lc.stackRisk,data:[S.risk],backgroundColor:"#c9a227"},
{label:Lc.stackInf,data:[S.inflation],backgroundColor:"#9aa8b6"}]},
options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{font:{size:8},boxWidth:10}}},
scales:{x:{stacked:true,max:D.total*1.02,ticks:{callback:v=>"£"+(v/1e6).toFixed(2)+"M"}},y:{stacked:true,display:false}}}});
const ids=D.chartDonutIds,amts=D.chartDonut;
const labels=ids.map(id=>(I18N[lang].hipoCost[id]||id));
new Chart(el2,{type:"doughnut",data:{labels,datasets:[{data:amts,
backgroundColor:["#0f2b46","#1a4a6e","#2e6da4","#1f7a6f","#5b6eae","#c9a227","#9aa8b6"]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"right",labels:{font:{size:7.5},boxWidth:9}}}}});
syncHipoLiveTotals();
}
"""

HIPO_EQUIP_JS = r"""
let EQUIP_MUST={};
let EQUIP_FILTER="all";
function equipIsNew(it){return it.ne!=="E";}
function equipMust(id){return EQUIP_MUST[id]!==false;}
function equipTitle(it){return lang==="zh"?(it.titleZh||it.title):it.title;}
function equipGroupLabel(g){return lang==="zh"&&g==="Isolators"?"隔离器":g;}
function equipNeLabel(ne){
if(ne==="N")return t("hipoEqNew");
if(ne==="E")return t("hipoEqExist");
if(ne==="N/E")return t("hipoEqNE");
return t("hipoEqNew");
}
function equipNeClass(ne){return ne==="E"?"ne-E":"ne-N";}
function equipNewMustTotal(){
return EQUIP_ITEMS.reduce((s,it)=>s+(equipIsNew(it)&&equipMust(it.id)?it.cost:0),0);
}
function equipGroupNewMust(group){
return EQUIP_ITEMS.reduce((s,it)=>s+(it.group===group&&equipIsNew(it)&&equipMust(it.id)?it.cost:0),0);
}
function fmM(n){return "£"+(n/1e6).toFixed(2)+"M";}
function hipoLiveProject(){return HIPO_OTHER+equipNewMustTotal();}
function setTxt(id,v){const el=document.getElementById(id);if(el)el.textContent=v;}
function syncHipoLiveTotals(){
const equip=equipNewMustTotal();
const project=HIPO_OTHER+equip;
const inB=5.33+2.48+project/1e6;
const ard=equipGroupNewMust("ARD/QC");
const iso=equipGroupNewMust("Isolators");
const crd=equipGroupNewMust("CRD");
setTxt("equipTotalAmt",fm(equip));
setTxt("hipoLiveEquipSec",fm(equip));
setTxt("hipoLiveEquipLeaf",fm(equip));
setTxt("hipoLiveProjectBar",fm(project));
setTxt("hipoLiveKpiEquip",fm(equip));
setTxt("hipoLiveKpiProject",fm(project));
setTxt("hipoLiveP2Invest",fmM(project));
setTxt("hipoLiveK2",fmM(project));
const p2=document.getElementById("hipoLiveP2sum");
if(p2){
p2.textContent=lang==="zh"
?`厂房内三条线合计（改造 £5.33M + C1 £2.48M + 高活实验室 ${fmM(project)}）约 ${"£"+inB.toFixed(2)+"M"}，不含 902 东侧扩建。各线口径不同：扩建与改造为可行性量级，C1 为内部估算，高活实验室为概念阶段成本计划。`
:`The three in-building lines total ~${"£"+inB.toFixed(2)+"M"} (retrofit £5.33M + C1 £2.48M + HIPO lab ${fmM(project)}), excluding the B902 east extension. Estimate bases differ: extension and retrofit are feasibility level, C1 is an internal estimate, the HIPO lab is a concept cost plan.`;
}
const b2=document.getElementById("hipoLiveB2");
if(b2)b2.textContent=lang==="zh"
?`投资：项目投资（含通胀）${fm(project)}；不含增值税；估算精度区间 £3.74M – £4.99M。`
:`Investment: project investment (incl. inflation) ${fm(project)}; VAT excluded; estimate accuracy range £3.74M – £4.99M.`;
const b3=document.getElementById("hipoLiveB3");
if(b3)b3.textContent=lang==="zh"
?`构成：建筑工程费 £1.95M + 专业服务费 £0.14M + 业主（凯莱英）供货设备 ${fmM(equip)} + 风险预备费 £0.40M + 通胀 £0.10M。`
:`Build-up: building works £1.95M + professional services £0.14M + client (Asymchem) equipment ${fmM(equip)} + risk allowance £0.40M + inflation £0.10M.`;
const b6=document.getElementById("hipoLiveB6");
if(b6)b6.textContent=lang==="zh"
?`业主（凯莱英）供货并安装设备待采购 ${fm(equip)}。`
:`Client (Asymchem) supplied and installed equipment — to purchase ${fm(equip)}.`;
const s4c=document.getElementById("hipoLiveS4c");
if(s4c)s4c.textContent=lang==="zh"
?`业主（凯莱英）供货并安装设备待采购 ${fm(equip)}`
:`Client (Asymchem) supplied and installed equipment — to purchase ${fm(equip)}`;
const s4d=document.getElementById("hipoLiveS4d");
if(s4d)s4d.textContent=lang==="zh"
?`待采购分项：ARD/QC ${fm(ard)}、隔离器内仪器 ${fm(iso)}、CRD ${fm(crd)}`
:`To purchase by group: ARD/QC ${fm(ard)}; isolator instruments ${fm(iso)}; CRD ${fm(crd)}`;
const eqLbl=document.getElementById("hipoLiveEquipLabel");
if(eqLbl)eqLbl.textContent=lang==="zh"
?`待采购 ${fm(equip)}（《Equipment List Costs for scoping 5 Aug》）`
:`To purchase ${fm(equip)} (Equipment List Costs for scoping 5 Aug)`;
if(_hipoBarChart){
_hipoBarChart.data.datasets[2].data[0]=equip;
_hipoBarChart.options.scales.x.max=project*1.02;
_hipoBarChart.update();
}
}
function renderEquipPage(){
const wrap=document.getElementById("equipTableWrap");
if(!wrap)return;
const groups=[];
EQUIP_ITEMS.forEach(it=>{
if(EQUIP_FILTER==="new"&&!equipIsNew(it))return;
if(EQUIP_FILTER==="existing"&&equipIsNew(it))return;
const last=groups[groups.length-1];
if(!last||last.group!==it.group)groups.push({group:it.group,items:[it]});
else last.items.push(it);
});
let html=`<table class="equip-table"><thead><tr>
<th>${t("hipoEqColTitle")}</th><th>${t("hipoEqColLoc")}</th><th>${t("hipoEqColMfr")}</th>
<th>${t("hipoEqColNE")}</th><th class="cost">${t("hipoEqColCost")}</th>
<th class="chk">${t("hipoEqColMust")}</th></tr></thead><tbody>`;
groups.forEach(g=>{
html+=`<tr class="grp"><td colspan="6">${equipGroupLabel(g.group)}</td></tr>`;
g.items.forEach(it=>{
const checked=equipMust(it.id)?" checked":"";
html+=`<tr data-id="${it.id}">
<td>${equipTitle(it)}</td><td>${it.location||"—"}</td><td>${it.mfr||"—"}</td>
<td class="${equipNeClass(it.ne)}">${equipNeLabel(it.ne)}</td>
<td class="cost">${fm(it.cost)}</td>
<td class="chk"><input type="checkbox" data-equip="${it.id}"${checked}></td>
</tr>`;
});
});
html+="</tbody></table>";
wrap.innerHTML=html;
document.querySelectorAll(".equip-filters button").forEach(btn=>{
btn.classList.toggle("active",btn.dataset.filter===EQUIP_FILTER);
});
wrap.querySelectorAll("input[data-equip]").forEach(box=>{
box.addEventListener("change",()=>{
EQUIP_MUST[box.dataset.equip]=box.checked;
syncHipoLiveTotals();
});
});
syncHipoLiveTotals();
}
function bindEquipPage(){
document.querySelectorAll(".equip-filters button").forEach(btn=>{
btn.onclick=()=>{EQUIP_FILTER=btn.dataset.filter;renderEquipPage();};
});
renderEquipPage();
}
"""

HIPO_COST_CSS = """
.kpi.hipo{border-left-color:var(--hipo)}
.tag.hipo{background:var(--hipo)}
.invest-kpi-row.cols5{grid-template-columns:repeat(5,1fr)}
.decision-list li.hipo{border-left-color:var(--hipo)}
.equip-toolbar{display:flex;align-items:center;justify-content:space-between;gap:.7rem;margin-bottom:.45rem;flex-wrap:wrap}
.equip-filters{display:flex;gap:.35rem}
.equip-filters button{border:1px solid #dde3e8;background:#fff;color:var(--muted);font-size:.72rem;font-weight:600;padding:.28rem .7rem;border-radius:6px;cursor:pointer}
.equip-filters button.active{background:var(--hipo);color:#fff;border-color:var(--hipo)}
.equip-total{margin:0;flex:1;min-width:220px}
.equip-table-wrap{flex:1;min-height:0;overflow:auto;background:#fff;border:1px solid #e8ecf0;border-radius:10px}
.equip-table{width:100%;border-collapse:collapse;font-size:.68rem}
.equip-table th{position:sticky;top:0;background:#f3f6f8;z-index:1;font-size:.64rem;color:var(--navy);padding:.32rem .4rem}
.equip-table td{padding:.26rem .4rem;vertical-align:middle}
.equip-table .grp td{background:#e8f2f0;color:var(--navy);font-weight:700;font-size:.7rem}
.equip-table .ne-N{color:#1f7a6f;font-weight:600}
.equip-table .ne-E{color:#8a6d3b;font-weight:600}
.equip-table .cost{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.equip-table .chk{text-align:center;width:4.2rem}
.equip-table input[type=checkbox]{width:14px;height:14px;accent-color:#1f7a6f;cursor:pointer}
"""
