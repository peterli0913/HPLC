#!/usr/bin/env python3
"""Fill 李涛绩效.xlsx completion status from Sandwich project work."""

from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment

XLSX = Path("/workspace/李涛绩效.xlsx")

# Column O = 15 完成情况
COMPLETION = {
    4: (
        "1. 跟进连续氢化项目例会及中外方沟通，整理会议纪要并跟踪行动项落实；\n"
        "2. 协调 CFCT、IEPE 与英国站点在 HAZOP 后设计、采购等事项上的信息对齐；\n"
        "3. 项目整体处于 HAZOP 完成后的设计实施准备阶段，按节点推进。"
    ),
    5: (
        "1. 组织并参与英国侧可行性研究讲解及多轮会议，跟进工程设备部与英国站点需求确认与方案讨论；\n"
        "2. 整理项目投资与进度材料，编制组合汇报文件，支撑管理层汇报与决策沟通；\n"
        "3. 协调国内团队为英国侧提供经验输入，跟进高活实验室等配套事项对接；\n"
        "4. 项目可行性研究已完成，投资与建设节奏框架已明确，准备进入下阶段。"
    ),
    6: (
        "1. 参加 902 东侧扩建可行性研究讲解会，整理中文纪要并向内通报进展与待决事项；\n"
        "2. 协助梳理项目投资与总控计划，编制管理层汇报材料；\n"
        "3. 跟进中外团队在扩建方案、关键假设及需国内确认事项上的沟通闭环；\n"
        "4. 扩建可行性研究已完成（2026年5月），正推进概念设计。"
    ),
    7: (
        "1. 参与 Sandwich 站点预算相关沟通与数据整理；\n"
        "2. 协调机器学习研讨小组相关交流安排。"
    ),
    8: (
        "1. 按部门安排配合电算化等生产管理重点工作，完成交办支持任务。"
    ),
}

# 年度目标：同步更新为当前阶段表述（简洁）
ANNUAL_TARGET_UPDATE = {
    4: (
        "1）连续氢化建设项目管理支持：\n"
        "项目已推进至 HAZOP 完成阶段。2026年持续协调中英各方，保障设计、采购与验证工作按计划推进。"
    ),
    5: (
        "2）HPLC和冻干机建设项目管理支持：\n"
        "可行性研究已完成。2026年下半年持续协调工程设备部与英国站点，推进下阶段设计及长周期设备相关决策。"
    ),
    6: (
        "3）902贴建项目管理支持：\n"
        "扩建可行性研究已完成（2026年5月）。2026年下半年持续协调推进概念设计及中外团队关键方案确认。"
    ),
}


def main():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb["李涛自评"]
    wrap = Alignment(wrap_text=True, vertical="top")

    for row, text in COMPLETION.items():
        cell = ws.cell(row=row, column=15)
        cell.value = text
        cell.alignment = wrap

    for row, text in ANNUAL_TARGET_UPDATE.items():
        cell = ws.cell(row=row, column=7)
        cell.value = text
        cell.alignment = wrap

    wb.save(XLSX)
    print(f"Updated {XLSX}")


if __name__ == "__main__":
    main()
