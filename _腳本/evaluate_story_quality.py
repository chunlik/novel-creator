#!/usr/bin/env python3
"""evaluate_story_quality.py - 章節小說品質評估器

Usage:
  python _腳本/evaluate_story_quality.py --novel infinite_livestream --volume 2 --chapter 9
  python _腳本/evaluate_story_quality.py --file 無限直播間/03-章節/02-記憶放映廳/009-休息舱.md --write-report

本工具不是 LLM 評審，而是 heuristic preflight：
- 用可觀察文本線索檢查章節是否具備好小說的 10 個要素。
- 產出「修補建議」與「可貼給 AI 的重寫提示」。
- 搭配 validate_chapter_logic.py 使用：一個查 bug，一個查可讀性 / 爽感。
"""

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from 小說設定 import resolve_novel_folder

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


QUALITY_ITEMS = [
    ("Q1", "一句話鉤子", [r"\?|？", r"为什么|為什麼|怎么|怎麼|是谁|是誰|哪里|哪裡|不对|不對|不能|不要", r"倒计时|倒計時|最后|最後|下一次"]),
    ("Q2", "明確危機", [r"倒计时|倒計時|警告|危险|危險|死|污染|黑水|威胁|威脅|不能|不要|追|逼近"]),
    ("Q3", "有矛盾的主角", [r"没有否认|沒有否認|不想|害怕|犹豫|猶豫|代价|代價|耳鸣|耳鳴|颤抖|顫抖|冷静|冷靜"]),
    ("Q4", "清楚短期目標", [r"必须|必須|需要|要在|剩余|剩餘|目标|目標|交易|确认|確認|提交|打开|打開|找到"]),
    ("Q5", "長期主線謎團", [r"陈述|陳述|F-0217|照片|店长|店長|直播|观众|觀眾|他们|他們|系统|系統|编号|編號"]),
    ("Q6", "世界觀規則可運作", [r"规则|規則|系统|系統|交易|状态|狀態|买方|買方|工牌|积分|積分|倒计时|倒計時|权限|權限"]),
    ("Q7", "配角有功能與立場", [r"许小小|許小小|店长|店長|陈述|陳述|孕妇|孕婦|影子|红雨衣|紅雨衣|弹幕|彈幕"]),
    ("Q8", "高潮有選擇與代價", [r"选择|選擇|确认|確認|提交|按下|代价|代價|扣减|扣減|留下|失去|完成|交易完成"]),
    ("Q9", "真相分層揭露", [r"原来|原來|不是.*而是|才明白|明白了|第一次确定|第一次確定|这不是|這不是|真正"]),
    ("Q10", "主題深度", [r"相信|不相信|名字|身份|记忆|記憶|活下来|活下來|人|不是人|自己|他们|他們|代价|代價"]),
]


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


def score_item(body: str, patterns: list[str]) -> tuple[int, list[str]]:
    hits = []
    for pattern in patterns:
        found = re.findall(pattern, body)
        if found:
            hits.append(pattern)
    count = len(hits)
    if count == 0:
        return 0, hits
    if count == 1:
        return 1, hits
    if count == 2:
        return 2, hits
    return 3, hits


def detect_author_explanation(body: str) -> list[str]:
    flags = []
    bad_patterns = [
        r"第\s*[一二三四五六七八九十0-9]+\s*章",
        r"前一半|后一半|後一半",
        r"读者|讀者|作者|伏笔|伏筆",
        r"这代表|這代表|这里说明|這裡說明",
    ]
    for pattern in bad_patterns:
        if re.search(pattern, body):
            flags.append(pattern)
    return flags


def detect_hook_strength(body: str) -> str:
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return "無正文"
    opening = "\n".join(paragraphs[:3])
    ending = "\n".join(paragraphs[-5:])
    open_hook = bool(re.search(r"\?|？|不对|不對|警告|倒计时|倒計時|出现|出現|没有|沒有", opening))
    end_hook = bool(re.search(r"\?|？|下一|倒计时|倒計時|亮着|不能|不要|是谁|是誰|消失|打开|打開", ending))
    if open_hook and end_hook:
        return "章首與章末都有鉤子"
    if end_hook:
        return "章末鉤子較強"
    if open_hook:
        return "章首鉤子較強，章末可加強"
    return "鉤子偏弱"


def evaluate(path: Path) -> dict[str, Any]:
    body = read_body(path)
    fm = read_frontmatter(path)
    results = []
    total = 0
    for code, name, patterns in QUALITY_ITEMS:
        score, hits = score_item(body, patterns)
        total += score
        results.append({"code": code, "name": name, "score": score, "hits": hits})

    flags = detect_author_explanation(body)
    hook = detect_hook_strength(body)

    suggestions = []
    low_items = [r for r in results if r["score"] <= 1]
    for item in low_items:
        suggestions.append(f"加強 {item['code']}「{item['name']}」：目前只有 {item['score']} 分。")
    if flags:
        suggestions.append("正文疑似有作者解釋 / 章節視角語句，建議改為角色觀察或系統提示。")
    if "偏弱" in hook:
        suggestions.append("章首或章末鉤子偏弱，建議補一個具體問題、危機或反常畫面。")

    verdict = "需要大修" if total <= 12 else "可讀但偏平" if total <= 18 else "合格，有追讀力" if total <= 24 else "強章，建議保留骨架"
    return {"path": path, "frontmatter": fm, "results": results, "total": total, "verdict": verdict, "flags": flags, "hook": hook, "suggestions": suggestions}


def build_rewrite_prompt(report: dict[str, Any]) -> str:
    low = [r for r in report["results"] if r["score"] <= 1]
    low_text = "、".join(f"{r['code']} {r['name']}" for r in low) or "無明顯低分項"
    suggestions = "\n".join(f"- {s}" for s in report["suggestions"]) or "- 保留骨架，只做微調。"
    return f"""請根據以下品質報告局部重寫章節，不要推翻已成立的劇情骨架。

低分項：{low_text}
章節鉤子狀態：{report['hook']}
總分：{report['total']}/30（{report['verdict']}）

修補建議：
{suggestions}

重寫要求：
1. 不改變已確認的劇情事實、積分、物品位置、角色狀態。
2. 把作者解釋改成角色觀察、行動、系統提示或對話。
3. 至少加強一個明確危機或章末鉤子。
4. 若有爽點，後面補一個代價或陰影。
5. 輸出修訂後的完整章節 Markdown。
"""


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "# 章節品質評估報告",
        "",
        f"- 檔案：`{report['path']}`",
        f"- 總分：**{report['total']} / 30**",
        f"- 判定：**{report['verdict']}**",
        f"- 鉤子：{report['hook']}",
        "",
        "## 10 項評分",
        "",
        "| 項目 | 分數 | 命中線索 |",
        "|------|------|----------|",
    ]
    for r in report["results"]:
        hit_text = "、".join(r["hits"][:3]) if r["hits"] else "—"
        lines.append(f"| {r['code']} {r['name']} | {r['score']} / 3 | `{hit_text}` |")
    lines.extend(["", "## 風險旗標", ""])
    if report["flags"]:
        for flag in report["flags"]:
            lines.append(f"- 可能有作者解釋 / 出戲語句：`{flag}`")
    else:
        lines.append("- 未發現明顯作者視角語句。")
    lines.extend(["", "## 修補建議", ""])
    if report["suggestions"]:
        lines.extend(f"- {s}" for s in report["suggestions"])
    else:
        lines.append("- 暫無重大修補建議。")
    lines.extend(["", "## 可貼給 AI 的重寫提示", "", "```text", build_rewrite_prompt(report).strip(), "```", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="章節小說品質評估")
    parser.add_argument("--novel", help="小說 ID 或名稱")
    parser.add_argument("--volume", help="卷號")
    parser.add_argument("--chapter", help="章號")
    parser.add_argument("--file", help="直接指定章節檔案")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--write-report", action="store_true", help="寫入 06-審校/章節品質評估.md")
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = None
    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = vault / path
    else:
        if not args.novel or not args.volume or not args.chapter:
            parser.error("請指定 --file，或同時指定 --novel --volume --chapter")
        novel_folder = resolve_novel_folder(args.novel)
        path = find_chapter(vault, novel_folder, args.volume, args.chapter)
        if path is None:
            parser.error("找不到章節檔案")

    report = evaluate(path)
    text = format_report(report)
    print(text)

    if args.write_report:
        if novel_folder is None:
            if args.novel:
                novel_folder = resolve_novel_folder(args.novel)
            else:
                # best effort: infer from path after vault
                try:
                    novel_folder = path.relative_to(vault).parts[0]
                except Exception:
                    parser.error("使用 --write-report 時請提供 --novel，或使用 vault 內相對路徑")
        out = vault / novel_folder / "06-審校" / "章節品質評估.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"報告已寫入：{out}")


if __name__ == "__main__":
    main()
