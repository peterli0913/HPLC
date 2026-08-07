#!/usr/bin/env python3
"""Fill 李涛绩效 completion status — style aligned with 李涛绩效_已填写.xlsx row 4."""

from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment

FILES = [
    Path("/workspace/李涛绩效_已填写.xlsx"),
    Path("/workspace/李涛绩效.xlsx"),
]

# Column O = 15 完成情况（参照连续氢化条目写法）
COMPLETION = {
    5: (
        "截至 2026 年上半年，作为国内项目管理支持，协调工程设备部与 UK Sandwich 两方，"
        "系统推动制备色谱及冻干机改造项目节奏，主要进展如下：\n"
        "• 组织并全程跟进英国侧可行性研究讲解及多轮专题会，推动方案布局与投资口径在英方与国内团队之间形成一致理解，"
        "可行性研究结论及投资框架已明确；\n"
        "• 汇总项目投资与进度信息，编制多版组合汇报材料，支撑管理层汇报与下阶段决策沟通；\n"
        "• 持续跟进设备供货与方案变更确认，协调国内团队经验输入，并统筹色谱冻干改造与 C1 模块升级、"
        "高活实验室等配套事项的接口对接，避免各子项割裂推进；\n"
        "• 建立与英国项目对口人的常规沟通机制，组织国内专题会并形成隔离器公用工程等问题的正式回复材料；\n"
        "下半年计划：推动项目进入下阶段设计、长周期设备采购决策及中外需求最终确认。"
        "项目整体节奏可控。"
    ),
    6: (
        "截至 2026 年上半年，作为国内项目管理支持，协调工程设备部与 UK Sandwich 及设计方，"
        "系统推动 902 东侧扩建项目节奏，主要进展如下：\n"
        "• 全程参与可行性研究讲解会，整理中文详细纪要及对内通报材料，推动国内团队理解推荐方案及关键前提假设；\n"
        "• 协助完成投资量级、风险与总控计划的梳理解读，编制管理层汇报材料，支撑扩建项目投资与进度决策；\n"
        "• 持续跟进加氢厂房处置、首层净高、长周期设备采购分工等需中外共同确认事项，促进信息对称、问题及时闭环；\n"
        "• 配合研发述职等管理场景，整理英国站点产能建设综合材料，支撑扩建与改造项目的统筹呈现；\n"
        "下半年计划：推动概念设计启动、关键方案国内确认及下阶段设计工作坊落地。项目整体节奏可控。"
    ),
    7: (
        "截至 2026 年上半年，按要求承担 Sandwich 站点预算及机器学习研讨小组相关支持，主要进展如下：\n"
        "• 参与 Sandwich 站点年度预算申请、执行跟踪相关数据整理与内外沟通支持；\n"
        "• 协调机器学习研讨小组交流安排，推动相关技术议题按计划开展；\n"
        "• 配合 Sandwich 站点多条资本项目的信息汇总与例行管理要求落实，保障预算与项目支持工作衔接；\n"
        "下半年计划：继续按节点完成月度概算与回顾等例行工作，并支持研讨小组后续交流安排。"
    ),
}

ANNUAL_TARGET_UPDATE = {
    5: (
        "2）HPLC和冻干机建设项目管理支持：\n"
        "目前项目已完成可行性研究及投资框架梳理。2026年将持续支持并协调工程设备部与 SW 方，"
        "推进下阶段设计、长周期设备采购决策及相关配套事项对接，保障项目有序实施。"
    ),
    6: (
        "3）902贴建项目管理支持：\n"
        "目前项目已完成东侧扩建可行性研究（2026年5月）。2026年将持续支持并协调工程设备部与 SW 方，"
        "推进概念设计、关键方案确认及与国内团队的信息闭环，确保项目按计划开展。"
    ),
}


def main():
    wrap = Alignment(wrap_text=True, vertical="top")
    for xlsx in FILES:
        if not xlsx.exists():
            print(f"Skip missing {xlsx}")
            continue
        wb = openpyxl.load_workbook(xlsx)
        ws = wb["李涛自评"]
        for row, text in COMPLETION.items():
            cell = ws.cell(row=row, column=15)
            cell.value = text
            cell.alignment = wrap
        for row, text in ANNUAL_TARGET_UPDATE.items():
            cell = ws.cell(row=row, column=7)
            cell.value = text
            cell.alignment = wrap
        wb.save(xlsx)
        print(f"Updated {xlsx}")


if __name__ == "__main__":
    main()
