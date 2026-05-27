#!/usr/bin/env python3
"""story_anatomy.py - 分析已寫章節的結構健康度

Usage:
  python _腳本/story_anatomy.py --novel 無限直播間
"""

import argparse
import re
from pathlib import Path


DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def read_body(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def analyze(vault: Path, novel: str):
    chapters_dir = vault / novel / "03-章節"
    if not chapters_dir.exists():
        print("尚無章節")
        return

    chapter_files = []
    outline_files = []
    for f in sorted(chapters_dir.iterdir()):
        if f.is_dir():
            for sub in sorted(f.iterdir()):
                if sub.suffix == ".md":
                    if "_大綱" not in sub.stem:
                        chapter_files.append(sub)
                    else:
                        outline_files.append(sub)
        elif f.suffix == ".md":
            if "_大綱" not in f.stem:
                chapter_files.append(f)
            else:
                outline_files.append(f)

    print(f"\n📊 結構分析: {novel}")
    print(f"   已寫章節: {len(chapter_files)}")
    print(f"   已有大綱: {len(outline_files)}")

    print(f"\n📝 字數統計:")
    total = 0
    for f in chapter_files:
        body = read_body(f)
        wc = len(body)
        total += wc
        print(f"   {f.stem}: {wc} 字")
    print(f"   總字數: {total}")

    tc_path = vault / novel / "02-大綱" / "張力曲線.md"
    if tc_path.exists():
        tc_text = tc_path.read_text(encoding="utf-8")
        tc_lines = tc_text.split("\n")
        print(f"\n📈 張力曲線對照:")
        for f in chapter_files:
            m = re.search(r"(\d+)", f.stem)
            if m:
                ch = m.group(1)
                for line in tc_lines:
                    if line.startswith(f"| {ch} |"):
                        real_wc = len(read_body(f))
                        print(f"   第{ch}章 | 規劃: {line.strip()} | 實寫字數: {real_wc}")

    fs_dir = vault / novel / "04-狀態追蹤"
    active = 0
    paid = 0
    if fs_dir.exists():
        for f in fs_dir.iterdir():
            if f.suffix != ".md":
                continue
            text = f.read_text(encoding="utf-8")
            if "status: active" in text:
                active += 1
            elif "status: paid" in text:
                paid += 1
    print(f"\n🔍 伏筆統計:")
    print(f"   活躍中: {active}")
    print(f"   已回收: {paid}")


def main():
    parser = argparse.ArgumentParser(description="分析已寫章節結構健康度")
    parser.add_argument("--novel", required=True)
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = parser.parse_args()

    vault = Path(args.vault)
    analyze(vault, args.novel)


if __name__ == "__main__":
    main()