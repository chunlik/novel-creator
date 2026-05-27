# 外部腳本擴充介面

本目錄提供 Python 腳本輔助 AI 寫作流程。

## 檔案格式標準

所有 Obsidian 筆記使用以下標準：
- **編碼**: UTF-8
- **格式**: Markdown + YAML frontmatter
- **分隔**: frontmatter 以 `---` 包覆，位於檔案開頭
- **必填欄位**: `type`, `novel_id`, `novel`

## 小說識別

### novel_id 系統

`novel_id` 是穩定唯一 key，所有 script 查找路徑時使用。

| novel_id | folder | display title |
|----------|--------|---------------|
| `infinite_livestream` | `無限直播間` | `无限直播间` |

**已支援的 alias（全可互換）：**
- `--novel infinite_livestream`
- `--novel 无限直播间`
- `--novel 無限直播間`

內部會統一 map 到 folder `無限直播間`。

### 讀取介面

外部腳本應可：
1. 解析 YAML frontmatter（使用 js-yaml / PyYAML）
2. 讀取 Markdown 正文
3. 依 `type` 欄位過濾筆記類型

### 寫入介面

外部腳本應生成符合標準 frontmatter 的 `.md` 檔案：
- 必須包含 `type`, `novel_id`, `novel` 欄位
- 章節檔案存入 `{novel_folder}/03-章節/{volume_dir}/{chapter_no}-{title}.md`
- 卷大綱存入 `{novel_folder}/02-大綱/卷/`
- AI 上下文存入 `{novel_folder}/05-AI上下文/`
- 狀態追蹤檔案存入 `{novel_folder}/04-狀態追蹤/`

### 查詢介面

使用 Dataview 的 JSON 匯出功能（Obsidian 社群外掛）：
- `Dataview: Export all files as JSON` 指令
- 或讀取 `.obsidian/` 配置直接解析 vault

## AI 寫作流程

### 生成一章的標準流程

1. **準備**：讀取 `當前寫作包.md` + `下一章指令.md`
2. **生成**：AI 寫出章節 `.md`，遵循 `禁止事項.md` + `風格規則.md`
3. **自檢**：檢查主語控制、因果鏈、空間一致性、簡體中文
4. **定稿**：
   ```bash
   python _腳本/update_state.py --novel infinite_livestream --volume {V} --chapter {N} --summary "..." --timeline "..."
   python _腳本/check_consistency.py --novel infinite_livestream --volume {V} --chapter {N}
   ```
5. **手動更新**：`角色狀態機.md`、`物品連續性.md`、`伏筆管理.md`

### 完成一卷的封卷流程

完成一卷後不要直接寫下一卷，先封卷：

```bash
python _腳本/check_consistency.py --novel infinite_livestream --volume {V}
python _腳本/close_volume.py --novel infinite_livestream --volume {V} --title "卷名"
```

`close_volume.py` 會產生：

```text
{novel_folder}/02-大綱/卷/{V}-{卷名}_卷總結.md
```

封卷後必須人工補完：
- 一句話總結
- 本卷核心變化
- 本卷完成事項
- 已回收伏筆
- 仍需承接的活躍伏筆
- 角色封卷狀態
- 物品封卷狀態
- 下一卷承接事項

### 啟動新卷的流程

```bash
python _腳本/start_volume.py --novel infinite_livestream --volume {NEXT_V} --title "新卷名" --first-chapter {FIRST_CHAPTER}
```

`start_volume.py` 會建立：

```text
{novel_folder}/03-章節/{NEXT_V}-{新卷名}/
{novel_folder}/02-大綱/卷/{NEXT_V}-{新卷名}.md
{novel_folder}/05-AI上下文/卷{NEXT_V}-{新卷名}_啟動包.md
{novel_folder}/05-AI上下文/下一章指令.md
```

新卷啟動後，先人工補完卷大綱與啟動包，再產生 AI 上下文：

```bash
python _腳本/compile_context.py --novel infinite_livestream --chapter {FIRST_CHAPTER} --vector-query "新卷名 前卷承接 伏筆"
```

## 可用腳本

### update_state.py
更新全局摘要、時間線，並提醒手動更新伏筆與狀態檔。

### check_consistency.py
角色約束檢查、物品連續性檢查、伏筆回收檢查、frontmatter 完整性檢查。

### vector_search.py
跨章節語義檢索（基於 sentence-transformers）。
支援 `--rebuild` 強制重建索引，也會用 chunk hash 偵測內容變更。

### compile_context.py
彙整寫作上下文給 AI agent，含全局摘要、角色狀態、伏筆管理、前章回顧與可選語義檢索。

### close_volume.py
封卷工具。掃描指定卷章節，產生卷總結草稿，協助清點完成事項、伏筆與承接項目。

### start_volume.py
開卷工具。建立新卷章節資料夾、卷大綱、AI 啟動包，並更新下一章指令。

## 共用範本

| 範本 | 用途 |
|------|------|
| `_共用範本/章節範本.md` | 新章節 frontmatter 與寫作檢查表 |
| `_共用範本/卷總結範本.md` | 手動建立卷總結 |
| `_共用範本/新卷啟動包範本.md` | 手動建立新卷 AI 啟動包 |
| `_共用範本/伏筆範本.md` | 單一伏筆條目 |
| `_共用範本/設定條目範本.md` | 世界觀 / 規則 / 設定條目 |

## 預留整合場景

| 場景 | 輸入 | 輸出 |
|------|------|------|
| AI 章節生成 | 當前寫作包 + 風格規則 | 新章節 .md |
| 向量檢索 | vault 全部 .md | 語義搜尋結果 |
| 自動審校 | 單一章節 .md | 矛盾報告 |
| 封卷整理 | 已完成卷章節 + 狀態檔 | 卷總結草稿 |
| 新卷啟動 | 前卷總結 + 新卷設定 | 卷大綱 + AI 啟動包 |
