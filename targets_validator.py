#!/usr/bin/env python3
"""
targets_validator.py — 校验研报是否完整覆盖 targets.json 中的所有标的

用法:
  python targets_validator.py <report.md> [--targets <targets.json>]

功能:
  1. 从 targets.json 提取所有有效标的（name 和 code 均非空的条目）
  2. 在研报 markdown 中逐一搜索每个标的的名称或代码
  3. 输出: 遗漏标的列表、多余标的列表、覆盖率统计

退出码:
  0 — 全部覆盖，无遗漏无多余
  1 — 存在遗漏或多余标的
"""

import json
import re
import sys
from pathlib import Path


def load_targets(targets_path: str) -> list[dict]:
    with open(targets_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    sections = [
        ("a_shares", ["index_major", "sse_stocks", "sse_etf", "szse_stocks", "szse_etf"]),
        ("hk_shares", ["index_major", "hkex_stocks", "hkex_etf"]),
        ("us_shares", ["index_major", "stocks", "adr", "etf"]),
    ]

    for market, categories in sections:
        market_data = data.get(market, {})
        for category in categories:
            for item in market_data.get(category, []):
                name = item.get("name", "").strip()
                code = item.get("code", "").strip()
                if name and code:
                    entries.append({
                        "name": name,
                        "code": code,
                        "market": market,
                        "category": category,
                    })

    return entries


def check_target_in_report(target: dict, report_text: str) -> bool:
    name = target["name"]
    code = target["code"]

    code_variants = [code]
    if code.endswith(".HK"):
        code_variants.append(code.replace(".HK", ""))
    if code.endswith(".SH") or code.endswith(".SZ"):
        code_variants.append(code.replace(".SH", "").replace(".SZ", ""))

    for variant in code_variants:
        if re.search(re.escape(variant), report_text):
            return True

    if re.search(re.escape(name), report_text):
        return True

    return False


def extract_report_targets(report_text: str, all_targets: list[dict]) -> list[dict]:
    found = []
    for target in all_targets:
        if check_target_in_report(target, report_text):
            found.append(target)
    return found


def validate(report_path: str, targets_path: str) -> bool:
    targets = load_targets(targets_path)
    report_text = Path(report_path).read_text(encoding="utf-8")

    missing = []
    for target in targets:
        if not check_target_in_report(target, report_text):
            missing.append(target)

    found = [t for t in targets if t not in missing]

    print(f"{'='*60}")
    print(f"targets.json 校验报告")
    print(f"{'='*60}")
    print(f"研报文件: {report_path}")
    print(f"标的配置: {targets_path}")
    print(f"")
    print(f"targets.json 有效标的总数: {len(targets)}")
    print(f"研报已覆盖标的数: {len(found)}")
    print(f"遗漏标的数: {len(missing)}")
    print(f"覆盖率: {len(found)/len(targets)*100:.1f}%")
    print(f"")

    if missing:
        print(f"❌ 遗漏标的 ({len(missing)}):")
        print(f"{'-'*60}")
        for t in missing:
            print(f"  [{t['market']}/{t['category']}] {t['name']} ({t['code']})")
        print()

    if not missing:
        print(f"✅ 所有标的均已覆盖，无遗漏！")

    print(f"{'='*60}")

    return len(missing) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python targets_validator.py <report.md> [--targets <targets.json>]")
        sys.exit(1)

    report_file = sys.argv[1]
    targets_file = "targets.json"

    if "--targets" in sys.argv:
        idx = sys.argv.index("--targets")
        if idx + 1 < len(sys.argv):
            targets_file = sys.argv[idx + 1]

    ok = validate(report_file, targets_file)
    sys.exit(0 if ok else 1)
