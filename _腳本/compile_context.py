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


def get_story_quality_rubric(vault: Path) -> str:
    return read_system_doc(vault, "story_quality_rubric.md", "（尚無小說品質規準）")


def get_foreshadowing_table(vault: Path, novel: str) -> str:
    path = vault / novel / "04-狀態追蹤" / "伏筆管理.md"
    body = read_body(path)
    if not body:
        foreshadow_dir = vault / novel / "04-狀態追蹤"
        lines = []
        if foreshadow_dir.exists():
            for f in sorted(foreshadow_dir.iterdir()):
                if f.suffix == ".md":
                    fm = read_frontmatter(f)
                    if fm.get("type") == "foreshadowing" and fm.get("status") == "active":
                        title = fm.get("title", f.stem)
                        imp = fm.get("importance", "?")
                        target = fm.get("target_chapter", "?")
                        lines.append(f"- [{imp}] {title} (預計回收: 第{target}章)")
        return "\n".join(lines) if lines else "（無活躍伏筆）"
    return body


def get_recent_chapters(vault: Path, novel: str, chapter: int, count: int = 3) -> str:
    paths = get_chapter_paths(vault, novel)
    relevant = [p for p in paths if _chapter_number(p) < chapter]
    relevant = relevant[-count:]
    parts = []
    for p in relevant:
        num = _chapter_number(p)
        body = read_body(p)
        summary = body[:1000] if len(body) > 1000 else body
        parts.append(f"=== 第{num}章 ===\n{summary}")
    return "\n\n".join(parts) if parts else "（無前章）"


def _chapter_number(path: Path) -> int:
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else 0


def get_arc_info(vault: Path, novel: str, volume: int = None) -> str:
    if volume is None:
        return ""
    arcs_dir = vault / novel / "02-大綱"
    if not arcs_dir.exists():
        return ""
    vol_prefix = f"{volume:02d}"
    for f in sorted(arcs_dir.iterdir()):
        if f.suffix == ".md" and f.stem.startswith(vol_prefix):
            return read_body(f)
    return ""


def get_story_bible(vault: Path, novel: str) -> str:
    path = vault / novel / "02-大綱" / "故事聖經.md"
    return read_body(path) or ""


def get_tension_curve(vault: Path, novel: str, chapter: int) -> str:
    path = vault / novel / "02-大綱" / "張力曲線.md"
    body = read_body(path)
    if not body:
        return ""
    lines = body.split("\n")
    for line in lines:
        if line.startswith(f"| {chapter} |"):
            return line.strip()
    return ""


def vector_search(vault: Path, novel: str, query: str, k: int = 5) -> str:
    import subprocess
    script = vault / "_腳本" / "vector_search.py"
    if not script.exists():
        return ""
    try:
        result = subprocess.run(
            ["python", str(script), "--novel", novel, "--query", query, "--k", str(k)],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def build_context(vault: Path, novel: str, chapter: int, vector_query: str = None) -> str:
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

    parts.append("\n=== 伏筆管理 ===")
    parts.append(get_foreshadowing_table(vault, novel))

    parts.append("\n=== 小說品質規準 ===")
    parts.append(get_story_quality_rubric(vault))

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
        vs = vector_search(vault, novel, vector_query)
        parts.append(vs if vs else "（無結果）")

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
