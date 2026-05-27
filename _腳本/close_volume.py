#!/usr/bin/env python3
"""close_volume.py - 完成一卷後產生卷總結草稿

Usage:
  python _腳本/close_volume.py --novel infinite_livestream --volume 1 --title 夜班便利店
  python _腳本/close_volume.py --novel 無限直播間 --volume 1 --title 夜班便利店 --overwrite
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

import yaml

from 小說設定 import resolve_novel_folder, get_novel_meta

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff") if path.exists() else ""


def read_frontmatter(path: Path) -> dict:
    text = read_file(path)
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def read_body(path: Path) -> str:
    text = read_file(path)
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def write_frontmatter(path: Path, frontmatter: dict, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    path.write_text(f"---\n{fm_text}\n---\n\n{body}\n", encoding="utf-8")


def _chapter_number(path: Path, fm: dict | None = None) -> int:
    fm = fm or {}
    if fm.get("chapter_no") not in (None, ""):
        try:
            return int(fm["chapter_no"])
        except (TypeError, ValueError):
            pass
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else 0


def _volume_number(path: Path, chapters_dir: Path, fm: dict | None = None) -> int:
    fm = fm or {}
    if fm.get("volume") not in (None, ""):
        try:
            return int(fm["volume"])
        except (TypeError, ValueError):
            pass
    try:
        rel = path.relative_to(chapters_dir)
    except ValueError:
        return 0
    first_part = rel.parts[0] if rel.parts else ""
    m = re.search(r"(\d+)", first_part)
    return int(m.group(1)) if m else 0


def get_volume_chapters(vault: Path, novel_folder: str, volume: int) -> list[tuple[Path, dict]]:
    chapters_dir = vault / novel_folder / "03-章節"
    if not chapters_dir.exists():
        return []

    chapters = []
    for path in sorted(chapters_dir.rglob("*.md")):
        if path.name.startswith(".") or "_大綱" in path.stem:
            continue
        fm = read_frontmatter(path)
        if _volume_number(path, chapters_dir, fm) == volume:
            chapters.append((path, fm))

    return sorted(chapters, key=lambda item: _chapter_number(item[0], item[1]))


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def chapter_table(chapters: list[tuple[Path, dict]]) -> str:
    lines = [
        "| 章節 | 標題 | 狀態 | 字數 | 時間線 | 主要角色 |",
        "|------|------|------|------|--------|----------|",
    ]
    for path, fm in chapters:
        chapter_no = fm.get("chapter_no") or _chapter_number(path, fm)
        title = fm.get("title") or path.stem
        status = fm.get("status", "?")
        word_count = fm.get("word_count", "")
        timeline = fm.get("timeline", "")
        chars = "、".join(str(x) for x in _as_list(fm.get("characters_used")))
        lines.append(f"| {chapter_no} | {title} | {status} | {word_count} | {timeline} | {chars} |")
    return "\n".join(lines)


def parse_foreshadowing(vault: Path, novel_folder: str) -> tuple[list[str], list[str]]:
    path = vault / novel_folder / "04-狀態追蹤" / "伏筆管理.md"
    text = read_body(path)
    active = []
    paid = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "伏笔" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        name, importance, purpose, status = cells[:4]
        item = f"- [{importance}] {name} — {purpose}"
        if status == "active":
            active.append(item)
        elif status == "paid":
            paid.append(item)
    return active, paid


def build_volume_summary(vault: Path, novel_folder: str, volume: int, title: str) -> str:
    chapters = get_volume_chapters(vault, novel_folder, volume)
    active, paid = parse_foreshadowing(vault, novel_folder)

    chapter_section = chapter_table(chapters) if chapters else "（未找到本卷章節，請確認 volume/frontmatter 或資料夾命名。）"
    active_section = "\n".join(active) if active else "（目前無 active 伏筆，請人工確認。）"
    paid_section = "\n".join(paid) if paid else "（目前無 paid 伏筆，請人工確認。）"

    return f"""# 卷{volume}：{title}｜卷總結

> 本檔由 `close_volume.py` 產生，請人工補完「卷核心」、「完成事項」、「下一卷承接」等判斷型內容。

## 封卷資訊

- **封卷時間：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **卷號：** {volume}
- **卷名：** {title}
- **章節數：** {len(chapters)}

## 一句話總結

TODO：用一句話說清楚本卷完成了什麼。

## 本卷核心變化

- TODO：主角理解世界的方式有什麼改變？
- TODO：角色關係有什麼不可逆變化？
- TODO：系統/副本規則揭露了什麼新層次？

## 章節清單

{chapter_section}

## 本卷完成事項

- TODO：完成的副本任務 / 通關條件
- TODO：已回收的主要衝突
- TODO：已確認的世界規則

## 已回收伏筆

{paid_section}

## 仍需承接的活躍伏筆

{active_section}

## 角色封卷狀態

請同步檢查：`04-狀態追蹤/角色狀態機.md`

- TODO：周仓目前狀態 / 代價 / 能力限制
- TODO：主要配角當前狀態
- TODO：本卷離場角色與是否可再出場

## 物品封卷狀態

請同步檢查：`04-狀態追蹤/物品連續性.md`

- TODO：主角持有物
- TODO：已消耗物
- TODO：留在副本 / 過渡空間 / 系統托管的物品

## 下一卷承接事項

- TODO：下一卷第一章必須承接的身體狀態
- TODO：下一卷第一章必須承接的物品狀態
- TODO：下一卷要推進但不能立刻揭露的伏筆

## 封卷檢查清單

- [ ] 已跑 `check_consistency.py --volume {volume}`
- [ ] 已更新 `全局摘要.md`
- [ ] 已更新 `時間線.md`
- [ ] 已更新 `角色狀態機.md`
- [ ] 已更新 `物品連續性.md`
- [ ] 已更新 `伏筆管理.md`
- [ ] 已建立下一卷啟動包
"""


def main():
    parser = argparse.ArgumentParser(description="完成一卷後產生卷總結草稿")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--volume", type=int, required=True, help="要封卷的卷號")
    parser.add_argument("--title", required=True, help="卷名，例如 夜班便利店")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--overwrite", action="store_true", help="覆蓋既有卷總結")
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    meta = get_novel_meta(args.novel)

    out_path = vault / novel_folder / "02-大綱" / "卷" / f"{args.volume:02d}-{args.title}_卷總結.md"
    if out_path.exists() and not args.overwrite:
        print(f"卷總結已存在，未覆蓋：{out_path}")
        print("如需重建，請加 --overwrite")
        return

    frontmatter = {
        **meta,
        "type": "volume_summary",
        "volume": args.volume,
        "volume_title": args.title,
        "status": "sealed_draft",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    body = build_volume_summary(vault, novel_folder, args.volume, args.title)
    write_frontmatter(out_path, frontmatter, body)
    print(f"卷總結已建立：{out_path}")


if __name__ == "__main__":
    main()
