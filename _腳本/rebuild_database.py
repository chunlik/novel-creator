#!/usr/bin/env python3
"""rebuild_database.py - 從正式章節重建核心狀態資料庫

Usage:
  python _腳本/rebuild_database.py --novel infinite_livestream --volume 1
  python _腳本/rebuild_database.py --novel infinite_livestream --all --overwrite

本腳本重建：
- 04-狀態追蹤/全局摘要.md
- 04-狀態追蹤/時間線.md
- 06-審校/database_rebuild_report.md

注意：角色狀態機、物品連續性、伏筆管理仍需要 AI agent 根據正文判斷更新，
因為這三者包含推理與敘事判斷，不應由簡單 frontmatter 完全自動覆蓋。
"""

import argparse
import re
from datetime import datetime
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


def read_body(path: Path) -> str:
    text = read_file(path)
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def write_frontmatter(path: Path, frontmatter: dict[str, Any], body: str, overwrite: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        print(f"已存在，略過：{path}")
        return
    fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    path.write_text(f"---\n{fm_text}\n---\n\n{body}\n", encoding="utf-8")


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


def get_chapters(vault: Path, novel_folder: str, volume: int | None = None) -> list[tuple[Path, dict[str, Any], str]]:
    chapters_dir = vault / novel_folder / "03-章節"
    if not chapters_dir.exists():
        return []

    chapters: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(chapters_dir.rglob("*.md")):
        if path.name.startswith(".") or "Deleted" in path.parts or "_大綱" in path.stem:
            continue
        fm = read_frontmatter(path)
        if fm.get("type") and fm.get("type") != "chapter":
            continue
        vol = _volume_number(path, chapters_dir, fm)
        if volume is not None and vol != volume:
            continue
        body = read_body(path)
        chapters.append((path, fm, body))

    return sorted(chapters, key=lambda item: (_volume_number(item[0], chapters_dir, item[1]), _chapter_number(item[0], item[1])))


def summarize_body(body: str, max_chars: int = 280) -> str:
    """Return a conservative extractive summary seed, not a creative summary."""
    text = re.sub(r"\n+", " ", body).strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "……"


def build_global_summary(chapters: list[tuple[Path, dict[str, Any], str]], source_label: str) -> str:
    lines = [
        "# 全局摘要",
        "",
        f"> 本檔由 `rebuild_database.py` 根據正式章節重建。來源：`{source_label}`。",
        "> 自動摘要採保守抽取式摘要；需要文學判斷的卷總結請以 `02-大綱/卷/*_卷總結.md` 為準。",
        "",
    ]

    current_volume = None
    for path, fm, body in chapters:
        volume = fm.get("volume") or "?"
        if volume != current_volume:
            current_volume = volume
            volume_title = fm.get("volume_title", "未命名卷")
            lines.extend([f"## 卷{volume}：{volume_title}", ""])

        chapter_no = fm.get("chapter_no") or _chapter_number(path, fm)
        title = fm.get("title") or path.stem
        scene = fm.get("scene", "")
        timeline = fm.get("timeline", "")
        planted = fm.get("foreshadowing_planted", []) or []
        paid = fm.get("foreshadowing_paid", []) or []

        lines.append(f"### 卷{volume}·第{chapter_no}章｜{title}")
        meta_parts = []
        if timeline:
            meta_parts.append(f"時間：{timeline}")
        if scene:
            meta_parts.append(f"場景：{scene}")
        if meta_parts:
            lines.append("- " + "；".join(meta_parts))
        lines.append(f"- 摘要種子：{summarize_body(body)}")
        if planted:
            lines.append("- 種下伏筆：" + "、".join(map(str, planted)))
        if paid:
            lines.append("- 回收伏筆：" + "、".join(map(str, paid)))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_timeline(chapters: list[tuple[Path, dict[str, Any], str]], source_label: str) -> str:
    lines = [
        "# 時間線",
        "",
        f"> 本檔由 `rebuild_database.py` 根據正式章節 frontmatter 重建。來源：`{source_label}`。",
        "",
        "| 章節 | 時間 | 場景 | 主要角色 | 種下伏筆 | 回收伏筆 |",
        "|------|------|------|----------|----------|----------|",
    ]
    for path, fm, body in chapters:
        volume = fm.get("volume") or "?"
        chapter_no = fm.get("chapter_no") or _chapter_number(path, fm)
        title = fm.get("title") or path.stem
        timeline = fm.get("timeline", "")
        scene = fm.get("scene", "")
        chars = "、".join(map(str, fm.get("characters_used", []) or []))
        planted = "、".join(map(str, fm.get("foreshadowing_planted", []) or []))
        paid = "、".join(map(str, fm.get("foreshadowing_paid", []) or []))
        lines.append(f"| 卷{volume}·第{chapter_no}章：{title} | {timeline} | {scene} | {chars} | {planted} | {paid} |")
    lines.append("")
    return "\n".join(lines)


def build_report(chapters: list[tuple[Path, dict[str, Any], str]], source_label: str) -> str:
    required = ["type", "novel_id", "novel", "title", "chapter_no", "volume", "volume_title", "status"]
    lines = [
        "# Database Rebuild Report",
        "",
        f"- Rebuilt at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Source: `{source_label}`",
        f"- Chapters scanned: {len(chapters)}",
        "",
        "## Frontmatter Issues",
        "",
    ]

    issues = []
    for path, fm, body in chapters:
        missing = [field for field in required if field not in fm or fm[field] in (None, "", [])]
        if missing:
            issues.append(f"- `{path}` missing: {', '.join(missing)}")
        if fm.get("type") != "chapter":
            issues.append(f"- `{path}` type is `{fm.get('type')}`, expected `chapter`")

    if issues:
        lines.extend(issues)
    else:
        lines.append("- No required frontmatter issues found.")

    lines.extend([
        "",
        "## Manual / AI Review Required",
        "",
        "- `角色狀態機.md` must be reviewed by AI/human when a chapter changes character constraints.",
        "- `物品連續性.md` must be reviewed by AI/human when a chapter moves, consumes, or creates key items.",
        "- `伏筆管理.md` must be reviewed by AI/human when a chapter plants or pays off foreshadowing.",
        "- Any `pending_canon` item must be landed in正文 before other files treat it as fact.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="從正式章節重建核心狀態資料庫")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--volume", type=int, help="只重建指定卷")
    parser.add_argument("--all", action="store_true", help="重建所有卷")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--overwrite", action="store_true", help="覆蓋既有全局摘要和時間線")
    args = parser.parse_args()

    if not args.all and args.volume is None:
        parser.error("請指定 --volume N 或 --all")

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    meta = get_novel_meta(args.novel)
    volume = None if args.all else args.volume
    source_label = "all volumes" if args.all else f"volume {args.volume}"

    chapters = get_chapters(vault, novel_folder, volume)
    if not chapters:
        print("找不到章節。")
        return

    state_dir = vault / novel_folder / "04-狀態追蹤"
    review_dir = vault / novel_folder / "06-審校"

    common_fm = {
        **meta,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "rebuild_database.py",
    }

    write_frontmatter(
        state_dir / "全局摘要.md",
        {**common_fm, "type": "global_summary", "status": "rebuilt"},
        build_global_summary(chapters, source_label),
        overwrite=args.overwrite,
    )
    write_frontmatter(
        state_dir / "時間線.md",
        {**common_fm, "type": "timeline", "status": "rebuilt"},
        build_timeline(chapters, source_label),
        overwrite=args.overwrite,
    )
    write_frontmatter(
        review_dir / "database_rebuild_report.md",
        {**common_fm, "type": "database_rebuild_report"},
        build_report(chapters, source_label),
        overwrite=True,
    )

    print(f"已重建核心資料庫：{novel_folder} / {source_label}")
    print(f"章節數：{len(chapters)}")
    print("已更新：04-狀態追蹤/全局摘要.md")
    print("已更新：04-狀態追蹤/時間線.md")
    print("已更新：06-審校/database_rebuild_report.md")
    print("注意：角色、物品、伏筆資料庫仍需依 AGENTS.md 由 AI agent 補判斷型內容。")


if __name__ == "__main__":
    main()
