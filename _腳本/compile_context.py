#!/usr/bin/env python3
"""compile_context.py - 彙整寫作上下文給 AI agent

Usage:
  python _腳本/compile_context.py --novel 無限直播間 --chapter 3
  python _腳本/compile_context.py --novel 無限直播間 --chapter 3 --vector-query "規則陷阱"
"""

import argparse
import yaml
import re
from pathlib import Path

from 小說設定 import resolve_novel_folder

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def read_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
    return {}


def read_body(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def read_state_doc(vault: Path, novel: str, filename: str, fallback: str = "（尚未定義）") -> str:
    path = vault / novel / "04-狀態追蹤" / filename
    return read_body(path) or fallback


def read_system_doc(vault: Path, filename: str, fallback: str = "（尚未定義）") -> str:
    path = vault / "_系統" / filename
    return read_body(path) or fallback


def get_chapter_paths(vault: Path, novel: str) -> list[Path]:
    """Return all chapter markdown files, including nested volume/subfolders."""
    chapters_dir = vault / novel / "03-章節"
    if not chapters_dir.exists():
        return []

    return sorted(
        f for f in chapters_dir.rglob("*.md")
        if "_大綱" not in f.stem and not f.name.startswith(".") and "Deleted" not in f.parts
    )


def get_global_summary(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "全局摘要.md", "（尚無摘要）")


def get_timeline(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "時間線.md", "（尚無時間線）")


def get_system_state(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "系統狀態.md", "（尚無系統狀態）")


def get_character_state(vault: Path, novel: str) -> str:
    path = vault / novel / "04-狀態追蹤" / "角色狀態機.md"
    body = read_body(path)
    if not body:
        chars_dir = vault / novel / "01-設定工坊" / "角色"
        lines = []
        if chars_dir.exists():
            for f in sorted(chars_dir.iterdir()):
                if f.suffix == ".md":
                    fm = read_frontmatter(f)
                    name = fm.get("name", f.stem)
                    status = fm.get("status", "unknown")
                    ability = fm.get("ability", "")
                    lines.append(f"- {name} | {status} | {ability}")
        return "\n".join(lines) if lines else "（尚無角色）"
    return body


def get_item_continuity(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "物品連續性.md", "（尚無物品連續性）")


def get_rule_continuity(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "規則連續性.md", "（尚無規則連續性）")


def get_scene_mechanics(vault: Path, novel: str) -> str:
    return read_state_doc(vault, novel, "場景機制.md", "（尚無場景機制）")


def get_story_quality_rubric(vault: Path, novel: str) -> str:
    path = vault / novel / "06-知識庫" / "story_quality_rubric.md"
    return read_body(path) or "（尚無小說品質規準）"


def get_story_bible(vault: Path, novel: str) -> str:
    path = vault / novel / "02-大綱" / "故事聖經.md"
    return read_body(path) or ""


def get_tension_curve(vault: Path, novel: str, chapter: int) -> str:
    import glob
    vol_dirs = sorted(Path(vault / novel / "02-大綱" / "卷").iterdir())
    for vd in reversed(vol_dirs):
        tc = vd / "04-張力曲線.md"
        if tc.exists():
            return read_body(tc) or ""
    return ""


def get_recent_chapters(vault: Path, novel: str, chapter: int, n: int = 3) -> str:
    paths = get_chapter_paths(vault, novel)
    recent = [p for p in paths if extract_chapter_no(p) and extract_chapter_no(p) < chapter][-n:]
    lines = []
    for p in recent:
        fm = read_frontmatter(p)
        no = fm.get("chapter_no", p.stem)
        title = fm.get("title", p.stem)
        lines.append(f"- 第{no}章 {title}")
    return "\n".join(lines) if lines else "（無前章）"


def extract_chapter_no(path: Path) -> int | None:
    fm = read_frontmatter(path)
    return fm.get("chapter_no")


def build_context(vault: Path, novel: str, chapter: int, vector_query: str | None = None) -> str:
    parts = []

    parts.append("=== 全局摘要 ===")
    parts.append(get_global_summary(vault, novel))

    parts.append("\n=== 時間線 ===")
    parts.append(get_timeline(vault, novel))

    parts.append("\n=== 系統狀態 ===")
    parts.append(get_system_state(vault, novel))

    parts.append("\n=== 角色狀態 ===")
    parts.append(get_character_state(vault, novel))

    parts.append("\n=== 物品連續性 ===")
    parts.append(get_item_continuity(vault, novel))

    parts.append("\n=== 規則連續性 ===")
    parts.append(get_rule_continuity(vault, novel))

    parts.append("\n=== 場景機制 ===")
    parts.append(get_scene_mechanics(vault, novel))

    parts.append("\n=== 品質規準 ===")
    parts.append(get_story_quality_rubric(vault, novel))

    parts.append("\n=== 故事聖經 ===")
    bible = get_story_bible(vault, novel)
    parts.append(bible if bible else "（尚未定義）")

    parts.append("\n=== 張力規劃 ===")
    tc = get_tension_curve(vault, novel, chapter)
    parts.append(tc if tc else "（尚未定義）")

    parts.append("\n=== 前章回顧 ===")
    parts.append(get_recent_chapters(vault, novel, chapter))

    if vector_query:
        parts.append("\n=== 語義檢索結果 ===")
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "vector_search.py"),
             "--novel", novel, "--query", vector_query, "--k", "5"],
            capture_output=True, text=True, cwd=Path(__file__).parent
        )
        vs = result.stdout.strip() or "（無結果）"
        parts.append(vs)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="彙整寫作上下文給 AI agent")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--chapter", type=int, required=True, help="即將寫的章節編號")
    parser.add_argument("--vector-query", help="選擇性語義檢索查詢")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT), help="Obsidian vault 根目錄")
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    context = build_context(vault, novel_folder, args.chapter, args.vector_query)
    print(context)


if __name__ == "__main__":
    main()
