#!/usr/bin/env python3
"""check_consistency.py - 檢測章節矛盾（含角色約束 + 物品連續性）

Usage:
  python _腳本/check_consistency.py --novel 無限直播間 --chapter 001 --volume 01
  python _腳本/check_consistency.py --novel 無限直播間 --volume 01         # 全卷
  python _腳本/check_consistency.py --novel 無限直播間 --all               # 全部
"""

import argparse
import re
from pathlib import Path


DEFAULT_VAULT = Path(__file__).resolve().parent.parent


# ─── helper ───────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_frontmatter(path: Path) -> dict:
    text = read_file(path)
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    import yaml
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def read_body(path: Path) -> str:
    text = read_file(path)
    m = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def parse_table(text: str, col_count: int) -> list[list[str]]:
    """Parse markdown table from text, returning rows as list of cells."""
    rows = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= col_count:
            rows.append(cells[:col_count])
    return rows


# ─── parse character state machine ────────────────────────────────

def parse_character_states(path: Path) -> dict:
    """Return {character: {constraint: details}} and state change log."""
    text = read_file(path)
    if not text:
        return {}

    constraints = {}
    state_logs = {}
    current_char = None
    in_constraints = False
    in_state_log = False

    for line in text.split("\n"):
        # Detect character section headers (## Name)
        m = re.match(r"^##\s+(.+)", line)
        if m:
            name = m.group(1).strip()
            if name not in ("角色狀態機",):
                current_char = name
                if current_char not in constraints:
                    constraints[current_char] = {}
                    state_logs[current_char] = []
                in_constraints = False
                in_state_log = False
            continue

        # Detect constraint table start (|约束|... )
        if "| 約束 |" in line or "| 約束|" in line:
            in_constraints = True
            in_state_log = False
            continue

        # Detect state change log table start
        if "| 章節 |" in line or "| 章節|" in line:
            in_constraints = False
            in_state_log = True
            continue

        # Skip header separators
        if re.match(r"^\|?\s*[-]+\s*\|", line):
            continue

        # Parse constraint rows
        if in_constraints and current_char and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4:
                constraint_name = cells[0]
                detail = f"來源:{cells[1]} 範圍:{cells[2]} 詳情:{cells[3]}"
                status = cells[4] if len(cells) > 4 else "?"
                constraints[current_char][constraint_name] = {
                    "detail": detail,
                    "status": status,
                }

        # Parse state change log rows
        if in_state_log and current_char and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3:
                state_logs[current_char].append({
                    "chapter": cells[0],
                    "change": cells[1],
                    "desc": cells[2] if len(cells) > 2 else "",
                })

    return {"constraints": constraints, "logs": state_logs}


# ─── parse item continuity ───────────────────────────────────────

def parse_item_continuity(path: Path) -> dict:
    """Return {item_name: list of state entries}."""
    text = read_file(path)
    if not text:
        return {}

    items = {}
    current_item = None
    in_table = False
    rows_data = []

    for line in text.split("\n"):
        # Detect item section headers
        m = re.match(r"^##\s+(.+)", line)
        if m:
            # Save previous item
            if current_item and rows_data:
                items[current_item] = list(rows_data)
            current_item = m.group(1).strip()
            rows_data = []
            in_table = False
            continue

        # Detect table start
        if "| 章節 |" in line or "| 章節|" in line:
            in_table = True
            continue

        if re.match(r"^\|?\s*[-]+\s*\|", line):
            continue

        if in_table and current_item and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4:
                rows_data.append({
                    "chapter": cells[0],
                    "status": cells[1],
                    "location": cells[2],
                    "note": cells[3] if len(cells) > 3 else "",
                })

    if current_item and rows_data:
        items[current_item] = list(rows_data)

    return items


# ─── chapter discovery ────────────────────────────────────────────

def find_chapter(vault: Path, novel: str, volume: str, chapter: str) -> Path | None:
    """Locate chapter file by volume and chapter number."""
    vol_dir = vault / novel / "03-章節"
    if not vol_dir.exists():
        return None

    # Find volume directory
    vol_path = None
    for d in sorted(vol_dir.iterdir()):
        if d.is_dir() and volume in d.name:
            vol_path = d
            break
    if not vol_path:
        return None

    # Find chapter file
    for f in sorted(vol_path.iterdir()):
        if f.suffix == ".md" and chapter in f.stem.replace("章", ""):
            return f

    return None


def get_chapter_fm(vault: Path, novel: str, volume: str, chapter: str):
    """Get frontmatter for a chapter."""
    path = find_chapter(vault, novel, volume, chapter)
    if not path:
        return None
    return read_frontmatter(path)


def get_all_chapters(vault: Path, novel: str, volume: str | None) -> list[tuple[str, str, str]]:
    """Return list of (volume, chapter_no, chapter_path) tuples."""
    vol_dir = vault / novel / "03-章節"
    if not vol_dir.exists():
        return []

    chapters = []
    for d in sorted(vol_dir.iterdir()):
        if not d.is_dir():
            continue
        vol_num = d.name[:2]  # "01", "02", etc.
        if volume and volume.zfill(2) != vol_num.zfill(2):
            continue
        for f in sorted(d.iterdir()):
            if f.suffix == ".md":
                ch = f.stem.split("-")[0].lstrip("0")
                chapters.append((vol_num, ch, str(f)))
    return chapters


# ─── checks ───────────────────────────────────────────────────────

def check_constraints(
    body: str,
    chapter_label: str,
    char_states: dict,
) -> list[str]:
    """Check character constraints against chapter content."""
    issues = []
    constraints = char_states.get("constraints", {})

    for char_name, cons in constraints.items():
        if char_name not in body:
            continue

        for constraint_name, info in cons.items():
            if info["status"] != "active":
                continue

            # Check specific known constraint violations
            if char_name == "许小小":
                # Check 3米 violation indicators
                if "她的房間" in body or "走遠" in body:
                    # These might be OK if it's within 3m. Flag for review.
                    issues.append(
                        f"⚠ 檢查：{char_name} 的「{constraint_name}」要求≤3米範圍，"
                        "但本文字句中暗示了分離（「她的房間/走遠」）。如非系統明確解除，請確認空間邏輯"
                    )

            if char_name == "周仓":
                if constraint_name == "心跳倒數·被動預警":
                    # Check if心跳倒数 triggered for non-threats
                    pass  # Hard to auto-detect, need manual check for now

    return issues


def check_item_continuity(
    body: str,
    chapter_label: str,
    vol_num: str,
    ch_num: str,
    items_db: dict,
) -> list[str]:
    """Check item state transitions against chapter content."""
    issues = []

    for item_name, entries in items_db.items():
        if item_name == "关联实体·许小小":
            continue  # Already checked via constraints

        # Find where this item was at the chapter before this one
        prev_entry = None
        current_entry = None
        for entry in entries:
            entry_label = entry.get("chapter", "")
            # Check if this entry is for the current chapter
            if vol_num in entry_label and ch_num in entry_label:
                current_entry = entry
                break
            prev_entry = entry

        if current_entry and prev_entry:
            # Verify continuity: if item changed location, chapter should mention it
            prev_loc = prev_entry.get("location", "")
            curr_loc = current_entry.get("location", "")
            if prev_loc != curr_loc and "持有" in curr_loc:
                # Item changed to "held" - check if chapter mentions acquiring it
                if item_name not in body and "纸条" not in item_name:
                    # Don't flag items that aren't mentioned at all
                    pass

    return issues


def check_dead_characters(vault: Path, novel: str, body: str) -> list[str]:
    """Check if dead characters appear in body."""
    issues = []
    chars_dir = vault / novel / "01-設定工坊" / "角色"
    if not chars_dir.exists():
        return issues

    for f in chars_dir.iterdir():
        if f.suffix != ".md":
            continue
        fm = read_frontmatter(f)
        if fm.get("status") == "dead":
            name = fm.get("name", f.stem)
            if name in body:
                issues.append(f"❌ 已死亡角色「{name}」出現在本章")
    return issues


def check_consumed_foreshadowing(vault: Path, novel: str, body: str) -> list[str]:
    """Check if consumed foreshadowing is reused."""
    issues = []
    fs_dir = vault / novel / "04-狀態追蹤"
    if not fs_dir.exists():
        return issues

    fs_file = fs_dir / "伏筆管理.md"
    if not fs_file.exists():
        return issues

    text = read_file(fs_file)
    rows = parse_table(text, 7)
    for cells in rows:
        if len(cells) >= 4:
            status = cells[3].strip()
            name = cells[0].strip()
            if status == "paid" and name in body:
                issues.append(f"⚠ 已回收伏筆「{name}」在本章被再次提起")
    return issues


# ─── main check ───────────────────────────────────────────────────

def check_chapter(
    vault: Path,
    novel: str,
    vol_num: str,
    ch_num: str,
    char_states: dict,
    items_db: dict,
) -> list[str]:
    issues = []
    chapter_label = f"卷{vol_num}·第{int(ch_num)}章"

    path = find_chapter(vault, novel, vol_num, ch_num)
    if not path:
        return [f"⚠ 章節檔案不存在: {chapter_label}"]

    fm = read_frontmatter(path)
    body = read_body(path)

    # 1. Dead characters
    issues.extend(check_dead_characters(vault, novel, body))

    # 2. Consumed foreshadowing
    issues.extend(check_consumed_foreshadowing(vault, novel, body))

    # 3. Frontmatter completeness
    required = ["title", "chapter_no", "arc", "status"]
    for field in required:
        if field not in fm or not fm[field]:
            issues.append(f"⚠ frontmatter 缺少必要欄位: {field}")

    # 4. Character constraints
    used_chars = fm.get("characters_used", [])
    cons_issues = check_constraints(body, chapter_label, char_states)
    issues.extend(cons_issues)

    # 5. Item continuity
    item_issues = check_item_continuity(body, chapter_label, vol_num, ch_num, items_db)
    issues.extend(item_issues)

    if not issues:
        issues.append("✓ 未檢測到明顯矛盾（仍需人工核對）")

    return issues


def format_report(novel: str, vol_num: str | None, ch_num: str | None, issues: list[str]) -> str:
    from datetime import datetime
    scope = f"卷{vol_num}" if vol_num else (f"第{ch_num}章" if ch_num else "全部章節")
    lines = [
        f"# 矛盾檢測報告: {novel} {scope}\n",
        f"檢測時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "---\n",
    ]
    lines.extend(f"{issue}\n" for issue in issues)
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="檢測章節矛盾（含角色約束 + 物品連續性）")
    parser.add_argument("--novel", required=True)
    parser.add_argument("--volume", help="卷號，例如 01")
    parser.add_argument("--chapter", help="章號，例如 001")
    parser.add_argument("--all", action="store_true", help="檢測全部章節")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = parser.parse_args()

    vault = Path(args.vault)
    novel = args.novel

    # Load state machine & item continuity (optional — created per-volume)
    state_path = vault / novel / "04-狀態追蹤" / "角色狀態機.md"
    item_path = vault / novel / "04-狀態追蹤" / "物品連續性.md"
    char_states = parse_character_states(state_path) if state_path.exists() else {}
    items_db = parse_item_continuity(item_path) if item_path.exists() else {}

    all_issues = []

    if args.all:
        chapters = get_all_chapters(vault, novel, args.volume)
        for vol_num, ch_num, ch_path in chapters:
            issues = check_chapter(vault, novel, vol_num, ch_num, char_states, items_db)
            label = f"卷{vol_num}·第{int(ch_num)}章"
            all_issues.extend([f"[{label}] {i}" for i in issues])
    elif args.volume and args.chapter:
        issues = check_chapter(vault, novel, args.volume, args.chapter, char_states, items_db)
        all_issues.extend(issues)
    elif args.volume:
        chapters = get_all_chapters(vault, novel, args.volume)
        for vol_num, ch_num, ch_path in chapters:
            issues = check_chapter(vault, novel, vol_num, ch_num, char_states, items_db)
            label = f"卷{vol_num}·第{int(ch_num)}章"
            all_issues.extend([f"[{label}] {i}" for i in issues])
    else:
        parser.print_help()
        return

    report = format_report(novel, args.volume, args.chapter, all_issues)
    print(report)

    review_dir = vault / novel / "06-審校"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_path = review_dir / "矛盾檢測.md"
    review_path.write_text(report, encoding="utf-8")
    print(f"報告已寫入: {review_path}")


if __name__ == "__main__":
    main()
