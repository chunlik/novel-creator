#!/usr/bin/env python3
"""update_state.py - 章節定稿後更新所有狀態檔案

Usage:
  python _腳本/update_state.py --novel 無限直播間 --chapter 3 --summary "周倉進入第七病棟" --timeline "第七病棟第一天"
"""

import argparse
import yaml
import re
from datetime import datetime
from pathlib import Path

from 小說設定 import resolve_novel_folder, get_novel_meta

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def read_frontmatter(path: Path):
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
    return {}


def read_body(path: Path):
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def write_frontmatter(path: Path, frontmatter: dict, body: str):
    fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{fm_text}\n---\n\n{body}\n"
    path.write_text(content, encoding="utf-8")


def update_global_summary(vault: Path, novel: str, chapter_no: int, volume: int, summary: str):
    path = vault / novel / "04-狀態追蹤" / "全局摘要.md"
    body = read_body(path)
    entry = f"\n## 卷{volume}·第{chapter_no}章\n{summary}\n"
    body += entry
    fm = {**get_novel_meta(novel), "type": "global_summary", "updated": str(datetime.now())}
    write_frontmatter(path, fm, body)
    print(f"  ✓ 全局摘要已更新（卷{volume}·第{chapter_no}章）")


def update_timeline(vault: Path, novel: str, chapter_no: int, volume: int, timeline_entry: str):
    path = vault / novel / "04-狀態追蹤" / "時間線.md"
    body = read_body(path)
    entry = f"\n| 卷{volume}·第{chapter_no}章 | {timeline_entry} |\n"
    body += entry
    fm = {**get_novel_meta(novel), "type": "timeline", "updated": str(datetime.now())}
    write_frontmatter(path, fm, body)
    print(f"  ✓ 時間線已更新（卷{volume}·第{chapter_no}章）")


def main():
    parser = argparse.ArgumentParser(description="章節定稿後更新所有狀態檔案")
    parser.add_argument("--novel", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--volume", type=int, default=1, help="卷號")
    parser.add_argument("--summary", default="", help="本章事件摘要")
    parser.add_argument("--timeline", default="", help="時間線標記")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    print(f"更新狀態: {novel_folder} 卷{args.volume}·第{args.chapter}章")

    if args.summary:
        update_global_summary(vault, novel_folder, args.chapter, args.volume, args.summary)
    update_foreshadowing(vault, novel_folder, args.chapter, args.volume)
    if args.timeline:
        update_timeline(vault, novel_folder, args.chapter, args.volume, args.timeline)

    print()
    print("⚠  別忘了手動更新以下檔案：")
    print("    1. 04-狀態追蹤/角色狀態機.md — 新增角色狀態變化")
    print("    2. 04-狀態追蹤/物品連續性.md — 更新物品位置/狀態")
    print()
    print("    完成後執行檢查：")
    print("    python _腳本/check_consistency.py --novel", novel_folder, "--volume", f"{args.volume:02d}")
    print()

    print("狀態更新完成。")


if __name__ == "__main__":
    main()
