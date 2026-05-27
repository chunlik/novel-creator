#!/usr/bin/env python3
"""validate_chapter_logic.py - 章節邏輯防呆檢查

Usage:
  python _腳本/validate_chapter_logic.py --novel infinite_livestream --volume 2 --chapter 9
  python _腳本/validate_chapter_logic.py --novel infinite_livestream --file 無限直播間/03-章節/02-記憶放映廳/009-休息舱.md

本工具偏向防呆，不取代人工審校。它檢查最容易造成長篇 bug 的文字線索：
- 積分 / 評價 / 道具持有錯誤
- pending_canon 未落地就直接使用
- 場景錯用
- 規則跨副本誤用
- 照片過早打開
"""

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from 小說設定 import resolve_novel_folder

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


ISSUE_LEVELS = ("ERROR", "WARN", "INFO")


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


def add_issue(issues: list[tuple[str, str]], level: str, message: str):
    if level not in ISSUE_LEVELS:
        level = "WARN"
    issues.append((level, message))


def check_frontmatter(path: Path, fm: dict[str, Any], body: str, issues: list[tuple[str, str]]):
    required = ["type", "novel_id", "novel", "title", "chapter_no", "volume", "volume_title", "status"]
    for field in required:
        if field not in fm or fm[field] in (None, "", []):
            add_issue(issues, "ERROR", f"frontmatter 缺少必要欄位：{field}")
    if fm.get("type") != "chapter":
        add_issue(issues, "ERROR", f"frontmatter type 應為 chapter，目前是：{fm.get('type')}")

    if fm.get("volume") == 2 and int(fm.get("chapter_no", 0) or 0) >= 9:
        if "記憶放映廳" not in str(fm.get("volume_title", "")):
            add_issue(issues, "WARN", "卷2章節的 volume_title 建議為：記憶放映廳")


def check_system_state(body: str, issues: list[tuple[str, str]]):
    # Current canonical points after volume 1.
    if re.search(r"積分\s*(?:餘額|余额|是|：|:)\s*47|47\s*積分|47\s*积分", body):
        add_issue(issues, "ERROR", "積分疑似寫成舊值 47；目前卷1結算後積分應為 18。")

    if re.search(r"評價\s*(?:是|：|:)\s*B(?!-)|B級通關|F級通關", body):
        add_issue(issues, "WARN", "評價疑似不是 B-；卷1正式結算為 B-。")

    owned_tool_patterns = [
        ("一次性手电筒", r"(?:掏出|拿出|打开|举起|使用|点亮).{0,12}一次性手电筒|一次性手电筒.{0,12}(?:在他手里|握在|亮起|点亮)"),
        ("空白工牌", r"(?:掏出|拿出|佩戴|使用).{0,12}空白工牌|空白工牌.{0,12}(?:在他手里|挂在|别在)"),
        ("三十秒录音带", r"(?:掏出|拿出|播放|使用).{0,12}三十秒录音带|三十秒录音带.{0,12}(?:播放|转动|在他手里)"),
    ]
    for item, pattern in owned_tool_patterns:
        if re.search(pattern, body):
            if not re.search(r"购买|購買|扣除|花费|花費|兑换|兌換|商城", body):
                add_issue(issues, "ERROR", f"{item} 是 unlocked_not_owned；章節中若使用，必須先購買或系統發放。")

    if re.search(r"直播(?:图标|圖標|标志|標誌).{0,8}(?:熄灭|熄滅|关闭|關閉|消失)", body):
        if not re.search(r"系统提示|系統提示|提示|倒计时|倒計時|结算|結算", body):
            add_issue(issues, "WARN", "直播圖標若關閉/消失，需有系統或場景明確提示。")


def check_pending_canon(body: str, issues: list[tuple[str, str]]):
    # 3-meter / associated entity should be landed, not assumed.
    uses_3m = re.search(r"3\s*米|三\s*米|关联实体|關聯實體|强制拉扯|強制拉扯|距离限制|距離限制", body)
    lands_3m = re.search(r"系统提示|系統提示|提示：|终端|終端|登记|登記|绑定|綁定|關聯實體|关联实体|拉扯|距離限制|距离限制", body)
    if uses_3m and not lands_3m:
        add_issue(issues, "ERROR", "許小小 3 米 / 關聯實體屬 pending_canon；使用前必須在正文落地。")

    uses_black_line = re.search(r"黑线|黑線|手背.*黑|指节.*黑|指節.*黑", body)
    lands_black_line = re.search(r"第一次|才发现|才發現|看见|看見|浮现|浮現|显出|顯出|休息舱.*光|放映.*光", body)
    if uses_black_line and not lands_black_line:
        add_issue(issues, "WARN", "手背黑線屬 pending_canon；若出現，建議寫成首次明確發現/落地。")

    uses_second_note = re.search(r"第二张.*陈述|第二張.*陳述|大厅笔记本|大廳筆記本", body)
    if uses_second_note:
        add_issue(issues, "WARN", "第二張陳述紙條 / 大廳筆記本屬 pending_canon；若使用，需在本章正式建立來源。")


def check_scene_logic(fm: dict[str, Any], body: str, issues: list[tuple[str, str]]):
    volume = int(fm.get("volume", 0) or 0)
    chapter = int(fm.get("chapter_no", 0) or 0)

    if volume >= 2 and chapter >= 9:
        # Real world is absent.
        real_world_patterns = r"回到家|家门|家門|卧室|臥室|街道|出租车|計程車|上班|公司|便利店外的街|正常世界|现实世界|現實世界"
        if re.search(real_world_patterns, body):
            add_issue(issues, "ERROR", "本作目前設定『無回家，只有過渡空間』；卷2不可無交代回到現實世界。")

        # Convenience store mechanisms should not be directly active in volume 2.
        if re.search(r"关东煮|關東煮|便利店收银机|便利店收銀機|后门.*三点|後門.*三點", body):
            if not re.search(r"回放|放映|记忆|記憶|画面|畫面|银幕|銀幕|归档|歸檔", body):
                add_issue(issues, "WARN", "便利店專屬機制出現在卷2時，應透過回放/記憶/歸檔呈現。")

        if re.search(r"黑水", body):
            if not re.search(r"回放|放映|记忆|記憶|画面|畫面|银幕|銀幕|归档|歸檔|照片|字幕", body):
                add_issue(issues, "WARN", "黑水是卷1機制；卷2若出現，需透過回放/記憶/歸檔或重新建立機制。")

        if re.search(r"记忆放映厅|記憶放映廳|放映厅|放映廳", body):
            has_rule = re.search(r"规则|規則|票根|座位|观众席|觀眾席|字幕|放映", body)
            if not has_rule:
                add_issue(issues, "WARN", "記憶放映廳首次出現時，應建立至少一個可見機制或規則。")


def check_locked_content(body: str, issues: list[tuple[str, str]]):
    if re.search(r"打开.{0,12}照片|打開.{0,12}照片|照片.{0,12}(?:完全展开|完全展開|全部内容|全部內容|看清)", body):
        if not re.search(r"没能|沒能|不能|不要|阻止|弹回|彈回|警告|现在不要打开|現在不要打開", body):
            add_issue(issues, "ERROR", "孕婦照片目前 active_locked；不可在第9章完整打開並揭露。")

    if re.search(r"陈述(?:就是|是).{0,20}(?:店长|店長|死了|死人|观众|觀眾|系统|系統)", body):
        add_issue(issues, "WARN", "陳述身份不可太早直接揭露；建議保留為線索而非定論。")


def check_text_style(body: str, issues: list[tuple[str, str]]):
    if "「" in body or "」" in body:
        add_issue(issues, "WARN", "章節正文應使用大陸式雙引號 `""`，不要使用台灣式引號「」。")

    # Very rough Traditional Chinese detector for common chars in body.
    trad_hits = re.findall(r"[體臺門後裏裡這個為與無現實關聯顯示記憶規則狀態]", body)
    if len(trad_hits) > 25:
        add_issue(issues, "WARN", "章節正文可能混入較多繁體字；小說正文規範是簡體中文。")


def validate(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    fm = read_frontmatter(path)
    body = read_body(path)

    if not path.exists():
        add_issue(issues, "ERROR", f"章節檔案不存在：{path}")
        return issues

    check_frontmatter(path, fm, body, issues)
    check_system_state(body, issues)
    check_pending_canon(body, issues)
    check_scene_logic(fm, body, issues)
    check_locked_content(body, issues)
    check_text_style(body, issues)

    if not issues:
        add_issue(issues, "INFO", "未發現常見邏輯防呆問題；仍需人工審校。")
    return issues


def format_report(path: Path, issues: list[tuple[str, str]]) -> str:
    lines = [
        f"# 章節邏輯驗證報告",
        "",
        f"- 檔案：`{path}`",
        "",
        "## 結果",
        "",
    ]
    for level, message in issues:
        icon = {"ERROR": "❌", "WARN": "⚠", "INFO": "ℹ"}.get(level, "-")
        lines.append(f"- {icon} **{level}**：{message}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="章節邏輯防呆檢查")
    parser.add_argument("--novel", help="小說 ID 或名稱")
    parser.add_argument("--volume", help="卷號")
    parser.add_argument("--chapter", help="章號")
    parser.add_argument("--file", help="直接指定章節檔案")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--write-report", action="store_true", help="寫入 06-審校/章節邏輯驗證.md")
    args = parser.parse_args()

    vault = Path(args.vault)

    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = vault / path
        novel_folder = path.parts[0] if path.parts else ""
    else:
        if not args.novel or not args.volume or not args.chapter:
            parser.error("請指定 --file，或同時指定 --novel --volume --chapter")
        novel_folder = resolve_novel_folder(args.novel)
        path = find_chapter(vault, novel_folder, args.volume, args.chapter)
        if path is None:
            path = vault / novel_folder / "03-章節" / f"{int(args.volume):02d}" / f"{int(args.chapter):03d}.md"

    issues = validate(path)
    report = format_report(path, issues)
    print(report)

    if args.write_report and args.novel:
        novel_folder = resolve_novel_folder(args.novel)
        out = vault / novel_folder / "06-審校" / "章節邏輯驗證.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"報告已寫入：{out}")


if __name__ == "__main__":
    main()
