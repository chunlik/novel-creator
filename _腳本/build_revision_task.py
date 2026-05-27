#!/usr/bin/env python3
"""build_revision_task.py - 生成可貼給 AI 的章節重寫任務

Usage:
  python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode rewrite
  python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode logic --write

mode:
  rewrite       使用 _提示詞工坊/章節重寫.md
  logic         使用 _提示詞工坊/邏輯修復.md
  payoff        使用 _提示詞工坊/爽點加強.md
  foreshadowing 使用 _提示詞工坊/伏筆回收.md
"""

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from 小說設定 import resolve_novel_folder

DEFAULT_VAULT = Path(__file__).resolve().parent.parent

TEMPLATE_MAP = {
    "rewrite": "章節重寫.md",
    "logic": "邏輯修復.md",
    "payoff": "爽點加強.md",
    "foreshadowing": "伏筆回收.md",
}


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


def _chapter_number(path: Path) -> str:
    m = re.search(r"(\d+)", path.stem)
    return str(int(m.group(1))) if m else "0"


def find_chapter(vault: Path, novel_folder: str, volume: str, chapter: str) -> Path | None:
    chapters_dir = vault / novel_folder / "03-章節"
    if not chapters_dir.exists():
        return None
    target_chapter = str(int(chapter))
    target_volume = str(int(volume))
    for path in sorted(chapters_dir.rglob("*.md")):
        if path.name.startswith(".") or "Deleted" in path.parts or "_大綱" in path.stem:
            continue
        fm = read_frontmatter(path)
        vol = str(fm.get("volume") or "")
        ch = str(fm.get("chapter_no") or _chapter_number(path))
        try:
            vol = str(int(vol))
            ch = str(int(ch))
        except ValueError:
            pass
        if vol == target_volume and ch == target_chapter:
            return path
    return None


def build_task(vault: Path, novel_folder: str, chapter_path: Path, mode: str) -> str:
    template_name = TEMPLATE_MAP[mode]
    template_path = vault / "_提示詞工坊" / template_name
    logic_report = vault / novel_folder / "06-審校" / "章節邏輯驗證.md"
    quality_report = vault / novel_folder / "06-審校" / "章節品質評估.md"
    context_pack = vault / novel_folder / "05-AI上下文" / "當前寫作包.md"

    chapter_text = read_file(chapter_path) or "（章節檔案不存在或為空）"
    template_text = read_body(template_path) or "（模板不存在或為空）"
    logic_text = read_file(logic_report) or "（尚無章節邏輯驗證報告，建議先執行 validate_chapter_logic.py）"
    quality_text = read_file(quality_report) or "（尚無章節品質評估報告，建議先執行 evaluate_story_quality.py）"
    context_text = read_file(context_pack) or "（尚無當前寫作包）"

    return f"""# 重寫任務

- 模式：`{mode}`
- 模板：`{template_name}`
- 章節：`{chapter_path}`

---

## 當前寫作包

```markdown
{context_text}
```

---

## 原章節全文

```markdown
{chapter_text}
```

---

## 邏輯驗證報告

```markdown
{logic_text}
```

---

## 品質評估報告

```markdown
{quality_text}
```

---

## 使用模板

```markdown
{template_text}
```
"""


def main():
    parser = argparse.ArgumentParser(description="生成可貼給 AI 的章節重寫任務")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--volume", required=True, help="卷號")
    parser.add_argument("--chapter", required=True, help="章號")
    parser.add_argument("--mode", choices=sorted(TEMPLATE_MAP.keys()), default="rewrite")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--write", action="store_true", help="寫入 06-審校/重寫任務.md")
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    chapter_path = find_chapter(vault, novel_folder, args.volume, args.chapter)
    if chapter_path is None:
        parser.error("找不到章節檔案")

    task = build_task(vault, novel_folder, chapter_path, args.mode)
    print(task)

    if args.write:
        out = vault / novel_folder / "06-審校" / "重寫任務.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(task, encoding="utf-8")
        print(f"已寫入：{out}")


if __name__ == "__main__":
    main()
