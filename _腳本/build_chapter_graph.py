#!/usr/bin/env python3
"""build_chapter_graph.py - 產生章節關係圖資料

Usage:
  python _腳本/build_chapter_graph.py --novel infinite_livestream --volume 1
  python _腳本/build_chapter_graph.py --novel infinite_livestream --all --write

輸出 Mermaid graph，幫助 AI / 作者看清：
- 章節之間的順序
- 每章使用角色
- 每章種下 / 回收伏筆
- 章節與物品 / 狀態變化的關聯

靈感：MuMuAINovel 的思維鏈 / 章節關係圖譜能力。
"""

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from 小說設定 import resolve_novel_folder, get_novel_meta

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff") if path.exists() else ""


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = read_file(path)
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _chapter_number(path: Path, fm: dict[str, Any]) -> int:
    if fm.get("chapter_no") not in (None, ""):
        try:
            return int(fm["chapter_no"])
        except (TypeError, ValueError):
            pass
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else 0


def _volume_number(path: Path, chapters_dir: Path, fm: dict[str, Any]) -> int:
    if fm.get("volume") not in (None, ""):
        try:
            return int(fm["volume"])
        except (TypeError, ValueError):
            pass
    try:
        rel = path.relative_to(chapters_dir)
    except ValueError:
        return 0
    first = rel.parts[0] if rel.parts else ""
    m = re.search(r"(\d+)", first)
    return int(m.group(1)) if m else 0


def get_chapters(vault: Path, novel_folder: str, volume: int | None = None):
    chapters_dir = vault / novel_folder / "03-章節"
    if not chapters_dir.exists():
        return []
    chapters = []
    for path in sorted(chapters_dir.rglob("*.md")):
        if path.name.startswith(".") or "Deleted" in path.parts or "_大綱" in path.stem:
            continue
        fm = read_frontmatter(path)
        if fm.get("type") and fm.get("type") != "chapter":
            continue
        vol = _volume_number(path, chapters_dir, fm)
        if volume is not None and vol != volume:
            continue
        chapters.append((path, fm))
    return sorted(chapters, key=lambda item: (_volume_number(item[0], chapters_dir, item[1]), _chapter_number(item[0], item[1])))


def node_id(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff]+", "_", str(text))
    return text.strip("_") or "node"


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [v.strip() for v in re.split(r"[,，、]", value) if v.strip()]
    return [str(value)]


def build_mermaid(chapters: list[tuple[Path, dict[str, Any]]], title: str) -> str:
    lines = [
        "```mermaid",
        "graph TD",
        f"  ROOT[\"{title}\"]",
    ]

    prev_chapter_id = None
    for path, fm in chapters:
        ch_no = fm.get("chapter_no") or _chapter_number(path, fm)
        ch_title = fm.get("title") or path.stem
        ch_id = f"CH{int(ch_no):03d}"
        label = f"Ch{ch_no}｜{ch_title}"
        lines.append(f"  {ch_id}[\"{label}\"]")
        lines.append(f"  ROOT --> {ch_id}")
        if prev_chapter_id:
            lines.append(f"  {prev_chapter_id} --> {ch_id}")
        prev_chapter_id = ch_id

        for char in as_list(fm.get("characters_used")):
            cid = "CHAR_" + node_id(char)
            lines.append(f"  {cid}((\"{char}\"))")
            lines.append(f"  {cid} --> {ch_id}")

        for fp in as_list(fm.get("foreshadowing_planted")):
            fid = "FP_" + node_id(fp)
            lines.append(f"  {ch_id} -- 種下 --> {fid}[\"{fp}\"]")

        for fp in as_list(fm.get("foreshadowing_paid")):
            fid = "FP_" + node_id(fp)
            lines.append(f"  {ch_id} -- 回收 --> {fid}[\"{fp}\"]")

    lines.append("```")
    return "\n".join(lines)


def build_markdown(chapters: list[tuple[Path, dict[str, Any]]], novel_meta: dict[str, Any], title: str) -> str:
    lines = [
        "# 章節關係圖",
        "",
        f"> 來源：{title}",
        "> 本圖由 `_腳本/build_chapter_graph.py` 依章節 frontmatter 生成。",
        "",
        build_mermaid(chapters, title),
        "",
        "## 章節索引",
        "",
        "| 章節 | 標題 | 角色 | 種下伏筆 | 回收伏筆 |",
        "|------|------|------|----------|----------|",
    ]
    for path, fm in chapters:
        ch_no = fm.get("chapter_no") or _chapter_number(path, fm)
        title_text = fm.get("title") or path.stem
        chars = "、".join(as_list(fm.get("characters_used")))
        planted = "、".join(as_list(fm.get("foreshadowing_planted")))
        paid = "、".join(as_list(fm.get("foreshadowing_paid")))
        lines.append(f"| Ch{ch_no} | {title_text} | {chars} | {planted} | {paid} |")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="產生章節關係圖")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--volume", type=int, help="只產生指定卷")
    parser.add_argument("--all", action="store_true", help="產生全部章節")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--write", action="store_true", help="寫入 06-審校/章節關係圖.md")
    args = parser.parse_args()

    if not args.all and args.volume is None:
        parser.error("請指定 --volume N 或 --all")

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    meta = get_novel_meta(args.novel)
    volume = None if args.all else args.volume
    label = "all volumes" if args.all else f"volume {args.volume}"
    chapters = get_chapters(vault, novel_folder, volume)
    if not chapters:
        parser.error("找不到章節")

    md = build_markdown(chapters, meta, label)
    print(md)

    if args.write:
        out = vault / novel_folder / "06-審校" / "章節關係圖.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"已寫入：{out}")


if __name__ == "__main__":
    main()
