#!/usr/bin/env python3
"""Fill 李涛绩效.xlsx completion status from Sandwich project work."""

from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment

XLSX = Path("/workspace/李涛绩效.xlsx")

# Column O = 15 完成情况（面向未参与项目的领导：进展 + 背景 + 个人作用，简洁表述）
COMPLETION = {
    4: (
        "项目整体：连续氢化建设已完成 HAZOP，正推进后续设计与实施准备。\n"
        "本人作用：在中英多方之间做好信息传递与会议组织，跟进关键节点，保障沟通顺畅、问题及时闭环。"
    ),
    5: (
        "项目背景：英国三明治站点在既有厂房内改造，新增制备色谱和冻干能力，是近期投产类重点项目。\n"
        "整体进展：上半年已完成可行性研究，投资与建设节奏框架基本明确，具备进入下一阶段条件。\n"
        "本人作用：作为英国与国内、工程设备部之间的协调接口，组织多轮沟通，整理决策汇报材料，"
        "推动方案与需求对齐，并协调国内经验支持英国侧方案完善（含高活实验室等相关配套）。"
    ),
    6: (
        "项目背景：902 厂房东侧贴建/扩建，用于扩大英国站点反应与生产规模，属中长期产能建设。\n"
        "整体进展：上半年已完成可行性研究（结论可行），投资与总控计划已初步明确，正推进概念设计。\n"
        "本人作用：参与英国设计方讲解与纪要整理，向内通报进展与关键假设，协助编制管理层汇报材料，"
        "跟进中外团队需共同确认的方案与决策事项，促进信息对称、推进节奏可控。"
    ),
    7: (
        "按安排参与 Sandwich 站点预算相关支持与机器学习小组协调工作，保障例行任务按时完成。"
    ),
    8: (
        "按部门安排配合电算化等生产管理重点工作，完成交办支持任务。"
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
