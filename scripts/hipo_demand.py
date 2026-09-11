"""EU BD high-potency demand list for Sandwich — facts only.

Source file (do not invent beyond these cells):
  HIPO Feasilbility Reports/
  High Potency Project demands or opportunities for Sandwich site_by EU BD team.xlsx

Rules used when summarising:
  * I2:I3 is merged, so the “opportunity lost / Procos GMP” comment applies to
    both Exatecan (ASYM-128214) and the ADC linker that uses it (ASYM-147285).
  * Values and kilograms are BD estimates, not signed orders. They are not summed.
  * Camizestrant “$5M per year?” is shown with the question mark from the sheet.
  * Camizestrant API kg is estimated by BD from intermediate demand; last step only
    is high-potency.
  * Roche / 信达 / 宜联 are enquiry-only (I10); no volumes.
"""

from __future__ import annotations

SOURCE_FILE = (
    "High Potency Project demands or opportunities for Sandwich site_by EU BD team.xlsx"
)
SOURCE_TEAM = "EU BD"
HORIZON = "2027-2030"

NAMED_CUSTOMERS = ["AZ", "Genmab", "BioNTech", "NCC"]
ENQUIRY_CUSTOMERS = ["Roche", "信达", "宜联"]

# status: lost | live2nd | liveSw | listed | enquiry
DEMAND_ROWS = [
    {
        "customer": "AZ",
        "status": "lost",
        "project_zh": "Exatecan（ASYM-128214）",
        "project_en": "Exatecan (ASYM-128214)",
        "qty": "43.2 kg",
        "value": "$5–6M",
        "note_zh": "2025-09 询盘。GMP payload-linker 已选 Procos（意大利）；非 GMP 仍在药明康德宁波。",
        "note_en": "Sept 2025 enquiry. GMP payload-linker awarded to Procos (Italy); non-GMP remains at Pharmaron Ningbo.",
    },
    {
        "customer": "AZ",
        "status": "lost",
        "project_zh": "ADC linker AZ14374332（ASYM-147285，Exatecan 为中间体）",
        "project_en": "ADC linker AZ14374332 (ASYM-147285; Exatecan intermediate)",
        "qty": "37 kg",
        "value": "$18M",
        "note_zh": "与上一行同一组丢失机会。",
        "note_en": "Same lost-opportunity group as the row above.",
    },
    {
        "customer": "AZ",
        "status": "live2nd",
        "project_zh": "AZD5305（ASYM-124995）",
        "project_en": "AZD5305 (ASYM-124995)",
        "qty": "TBD",
        "value": "—",
        "note_zh": "SW 已有部分研发活动；AZ 未提供商业量。商务：若 SW 扩展高活产能，可争取第二供。",
        "note_en": "Some R&D already at Sandwich; AZ has not shared bulk demand. BD: second-source possible if SW HP capacity is extended.",
    },
    {
        "customer": "AZ",
        "status": "live2nd",
        "project_zh": "Camizestrant / AZD9833（ASYM-147692）",
        "project_en": "Camizestrant / AZD9833 (ASYM-147692)",
        "qty": "~8,800 kg",
        "value": "$5M/yr?",
        "note_zh": "仅末步为高活。现供 Cambrex US。公斤数由中间体年需求估算，不是 AZ 确认的 API 订单。",
        "note_en": "Last step only is HP. Current API supplier: Cambrex US. Kg estimated from intermediate demand, not an AZ-confirmed API order.",
    },
    {
        "customer": "AZ",
        "status": "enquiry",
        "project_zh": "其他 ADC 管线",
        "project_en": "Other ADC opportunities",
        "qty": "—",
        "value": "—",
        "note_zh": "AZ ADC payload-linker 管线较多；近期沟通中表示希望了解 SW 高活扩建计划。",
        "note_en": "Further AZ ADC payload-linker pipelines; recent discussion: interested in the SW HP expansion plan.",
    },
    {
        "customer": "Genmab",
        "status": "live2nd",
        "project_zh": "LD038.TFA（ASYM-129959）",
        "project_en": "LD038.TFA (ASYM-129959)",
        "qty": "71.8 kg",
        "value": "$86M",
        "note_zh": "Payload-linker。计划 2026 年底报 BLA。天津已完成 PPQ、商业批次进行中。客户评估欧美第二供，关注 SW 扩建计划。",
        "note_en": "Payload-linker. BLA planned end-2026. TJ has completed PPQ; commercial batches ongoing. Client evaluating a Europe/US second source and asked to see the SW HP plan.",
    },
    {
        "customer": "BioNTech",
        "status": "liveSw",
        "project_zh": "BNT3214（ASYM-139154）",
        "project_en": "BNT3214 (ASYM-139154)",
        "qty": "8 kg",
        "value": "$15–20M",
        "note_zh": "现由中国支持早期研究；希望项目推进后由 Sandwich 长期供货。",
        "note_en": "China currently supports early-phase supply; client wants a long-term Sandwich route as the programme progresses.",
    },
    {
        "customer": "NCC",
        "status": "listed",
        "project_zh": "Exatecan mesylate",
        "project_en": "Exatecan mesylate",
        "qty": "6 kg（2027）",
        "value": "TBD",
        "note_zh": "仅列 2027 年 6 kg，其后年份与产值为 TBD。",
        "note_en": "6 kg listed for 2027 only; later years and value TBD.",
    },
    {
        "customer": "Roche / 信达 / 宜联",
        "status": "enquiry",
        "project_zh": "高活海外产能询盘",
        "project_en": "Overseas HP capacity enquiry",
        "qty": "—",
        "value": "—",
        "note_zh": "三家亦在询问高活海外产能。",
        "note_en": "Also asking about overseas HP capacity.",
    },
]
