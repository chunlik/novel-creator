#!/usr/bin/env python3
"""start_volume.py - 建立新卷資料夾、卷大綱與 AI 啟動包

Usage:
  python _腳本/start_volume.py --novel infinite_livestream --volume 2 --title 記憶放映廳 --first-chapter 9
  python _腳本/start_volume.py --novel 無限直播間 --volume 2 --title 記憶放映廳 --first-chapter 9 --overwrite
"""

import argparse
from datetime import datetime
from pathlib import Path

import yaml

from 小說設定 import resolve_novel_folder, get_novel_meta

DEFAULT_VAULT = Path(__file__).resolve().parent.parent


def write_frontmatter(path: Path, frontmatter: dict, body: str, overwrite: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        print(f"已存在，略過：{path}")
        return False
    fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    path.write_text(f"---\n{fm_text}\n---\n\n{body}\n", encoding="utf-8")
    print(f"已建立：{path}")
    return True


def build_volume_outline(volume: int, title: str, first_chapter: int) -> str:
    return f"""# 卷{volume}：{title}

## 卷定位

TODO：這一卷在全書中的功能是什麼？例如：規則恐怖 → 身份恐怖 / 記憶恐怖 / 系統恐怖。

## 一句話鉤子

TODO：用一句話說清楚本卷核心懸念。

## 開場狀態

- TODO：主角身體狀態
- TODO：主角持有物
- TODO：同行角色 / 關聯實體狀態
- TODO：上一卷留下的直接危機

## 本卷主要推進伏筆

- TODO：伏筆 1
- TODO：伏筆 2
- TODO：伏筆 3

## 本卷不能揭露太早的內容

- TODO：不能在前 1/3 直接解釋的世界觀
- TODO：不能讓角色直接說明的真相

## 卷結構規劃

| 章節 | 功能 | 事件 | 線索 | 章末鉤子 |
|------|------|------|------|----------|
| Ch{first_chapter} | 開場 / 轉場 | TODO | TODO | TODO |
| Ch{first_chapter + 1} | 規則建立 | TODO | TODO | TODO |
| Ch{first_chapter + 2} | 第一次測試 | TODO | TODO | TODO |
| Ch{first_chapter + 3} | 中段反轉 | TODO | TODO | TODO |
| Ch{first_chapter + 4} | 危機升級 | TODO | TODO | TODO |
| Ch{first_chapter + 5} | 結算 / 轉場 | TODO | TODO | TODO |

## 本卷通關條件 / 表面任務

TODO：副本表面要求主角做什麼？

## 本卷真正陷阱

TODO：表面任務背後真正危險是什麼？

## 本卷結尾目標

- TODO：主角知道了什麼？
- TODO：主角失去了什麼？
- TODO：下一卷必須承接什麼？
"""


def build_startup_pack(volume: int, title: str, first_chapter: int, previous_volume: int | None) -> str:
    prev_line = f"請先閱讀 `02-大綱/卷/{previous_volume:02d}-*_卷總結.md`。" if previous_volume else "若有前卷，請先閱讀前卷卷總結。"
    return f"""# 卷{volume}：{title}｜AI 啟動包

> 本檔由 `start_volume.py` 產生。寫本卷第一章前，請先人工補完 TODO。

## 前置閱讀

- {prev_line}
- `04-狀態追蹤/全局摘要.md`
- `04-狀態追蹤/角色狀態機.md`
- `04-狀態追蹤/物品連續性.md`
- `04-狀態追蹤/伏筆管理.md`
- `05-AI上下文/禁止事項.md`
- `05-AI上下文/風格規則.md`

## 本卷第一章

- **章號：** {first_chapter}
- **卷號：** {volume}
- **卷名：** {title}
- **建議保存位置：** `03-章節/{volume:02d}-{title}/{first_chapter:03d}-章名.md`

## 第一章開場狀態

- TODO：場景在哪裡？
- TODO：主角醒來 / 進入 / 被傳送的第一個可見細節是什麼？
- TODO：同行角色是否在場？距離、位置、狀態如何？
- TODO：主角身上的代價如何表現？

## 第一章必須承接

- TODO：前卷最後一個畫面
- TODO：前卷未解決的身體狀態
- TODO：前卷未解決的物品狀態
- TODO：前卷留下的主線疑問

## 第一章要建立的新規則

- TODO：新副本第一條可見規則
- TODO：這條規則表面保護什麼？實際上可能害什麼？

## 第一章要種 / 推進的伏筆

- TODO：伏筆 1
- TODO：伏筆 2
- TODO：伏筆 3

## 第一章禁止事項

- 不要直接解釋上一卷所有伏筆。
- 不要讓角色用對話說明系統本質。
- 不要把主角的能力寫成主動技能。
- 不要讓副本規則一次講完。

## 可直接使用的生成指令

```bash
python _腳本/compile_context.py --novel infinite_livestream --chapter {first_chapter} --vector-query "{title} 前卷承接 伏筆"
```

把輸出貼給 AI 後，可追加：

```text
請根據以上上下文，寫卷{volume}第{first_chapter}章。遵守禁止事項、風格規則、角色狀態機、物品連續性與伏筆管理。輸出完整 Markdown 章節檔。
```
"""


def build_next_chapter_instruction(volume: int, title: str, first_chapter: int) -> str:
    return f"""# 下一章指令

## 格式要求

- YAML frontmatter 必填：`type: chapter`, `novel_id`, `novel`, `chapter_no`, `volume`, `volume_title`, `status: draft`, `word_count`, `scene`, `timeline`, `characters_used`, `foreshadowing_planted`, `foreshadowing_paid`
- 保存位置：`03-章節/{volume:02d}-{title}/{{chapter_no}}-{{title}}.md`

## 當前目標

- **卷號：** {volume}
- **卷名：** {title}
- **下一章：** 第 {first_chapter} 章

## 寫作規則

- 連續不超過 2 句以「他」開頭，平均每 4-5 句出現 1 次「他」
- 周倉（全名）和「他」交替使用
- 每個動作必須有所屬主語，不出現懸浮動作
- 引號格式使用 "" 雙引號（大陸規範）
- 異常不解釋（讓讀者自己推理）
- 細節代替心理描寫
- 簡體中文，不使用繁體字
- 所有被引用的規則/術語/設定必須在首次引用前已向讀者呈現

## 章節結構

- 60% 衝突推進 + 30% 線索推進 + 10% 選擇推進
- 每章結束至少改變一件事（位置/信息/關係/危機程度）
- 章末留有懸念或新疑問

## 定稿後流程

1. `python _腳本/update_state.py --novel infinite_livestream --volume {volume} --chapter {{N}} --summary "..." --timeline "..."`
2. 手動更新 `04-狀態追蹤/角色狀態機.md`
3. 手動更新 `04-狀態追蹤/物品連續性.md`
4. 手動更新 `04-狀態追蹤/伏筆管理.md`
5. `python _腳本/check_consistency.py --novel infinite_livestream --volume {volume} --chapter {{N}}`
"""


def main():
    parser = argparse.ArgumentParser(description="建立新卷資料夾、卷大綱與 AI 啟動包")
    parser.add_argument("--novel", required=True, help="小說 ID 或名稱")
    parser.add_argument("--volume", type=int, required=True, help="新卷卷號")
    parser.add_argument("--title", required=True, help="新卷卷名")
    parser.add_argument("--first-chapter", type=int, required=True, help="新卷第一章章號")
    parser.add_argument("--previous-volume", type=int, help="前一卷卷號，預設為 volume - 1")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--overwrite", action="store_true", help="覆蓋既有檔案")
    args = parser.parse_args()

    vault = Path(args.vault)
    novel_folder = resolve_novel_folder(args.novel)
    meta = get_novel_meta(args.novel)
    previous_volume = args.previous_volume if args.previous_volume is not None else args.volume - 1

    chapter_dir = vault / novel_folder / "03-章節" / f"{args.volume:02d}-{args.title}"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    print(f"章節資料夾已就緒：{chapter_dir}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    outline_path = vault / novel_folder / "02-大綱" / "卷" / f"{args.volume:02d}-{args.title}.md"
    write_frontmatter(
        outline_path,
        {
            **meta,
            "type": "volume_outline",
            "volume": args.volume,
            "volume_title": args.title,
            "status": "planning",
            "first_chapter": args.first_chapter,
            "created": now,
        },
        build_volume_outline(args.volume, args.title, args.first_chapter),
        overwrite=args.overwrite,
    )

    startup_path = vault / novel_folder / "05-AI上下文" / f"卷{args.volume}-{args.title}_啟動包.md"
    write_frontmatter(
        startup_path,
        {
            **meta,
            "type": "ai_context",
            "context_type": "volume_startup_pack",
            "volume": args.volume,
            "volume_title": args.title,
            "first_chapter": args.first_chapter,
            "last_updated": now,
        },
        build_startup_pack(args.volume, args.title, args.first_chapter, previous_volume),
        overwrite=args.overwrite,
    )

    next_instruction_path = vault / novel_folder / "05-AI上下文" / "下一章指令.md"
    write_frontmatter(
        next_instruction_path,
        {
            **meta,
            "type": "ai_context",
            "context_type": "next_chapter_instructions",
            "volume": args.volume,
            "volume_title": args.title,
            "next_chapter": args.first_chapter,
            "last_updated": now,
        },
        build_next_chapter_instruction(args.volume, args.title, args.first_chapter),
        overwrite=args.overwrite,
    )

    print("\n新卷啟動完成。下一步：")
    print(f"1. 人工補完：{outline_path}")
    print(f"2. 人工補完：{startup_path}")
    print(f"3. 產生上下文：python _腳本/compile_context.py --novel {args.novel} --chapter {args.first_chapter} --vector-query \"{args.title} 前卷承接 伏筆\"")


if __name__ == "__main__":
    main()
