# 外部腳本擴充介面

本目錄預留給未來的外部腳本整合。

## 檔案格式標準

所有 Obsidian 筆記使用以下標準：
- **編碼**: UTF-8
- **格式**: Markdown + YAML frontmatter
- **分隔**: frontmatter 以 `---` 包覆，位於檔案開頭

## 讀取介面

外部腳本應可：
1. 解析 YAML frontmatter（使用 js-yaml / PyYAML）
2. 讀取 Markdown 正文
3. 依 `type` 欄位過濾筆記類型

## 寫入介面

外部腳本應生成符合標準 frontmatter 的 `.md` 檔案：
- 必須包含 `type` 和 `novel` 欄位
- 章節檔案存入 `{novel}/03-章節/`
- 設定檔案存入 `{novel}/01-設定工坊/`

## 查詢介面

使用 Dataview 的 JSON 匯出功能（Obsidian 社群外掛）：
- `Dataview: Export all files as JSON` 指令
- 或讀取 `.obsidian/` 配置直接解析 vault

## 預留整合場景

| 場景 | 輸入 | 輸出 |
|------|------|------|
| AI 章節生成 | 前 N 章 frontmatter + 大綱 | 新章節 .md |
| 向量檢索 | vault 全部 .md | 語義搜尋結果 |
| 自動審校 | 單一章節 .md | 矛盾報告 |
| 角色狀態分析 | 全部角色 .md | 發展軌跡圖 |
