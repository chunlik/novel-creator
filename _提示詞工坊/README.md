---
type: prompt_workshop_index
updated: 2026-05-28
---

# 提示詞工坊

> 這裡存放固定 prompt 模板，讓 AI 寫作流程標準化。  
> 目的不是讓 prompt 變長，而是讓每次生成、重寫、修 bug、加爽點都有一致流程。

---

## 模板清單

| 模板 | 用途 | 使用時機 |
|------|------|----------|
| `章節生成.md` | 生成新章節 | 寫新章節第一次初稿 |
| `章節重寫.md` | 根據報告局部重寫 | 初稿已生成，需修 bug / 加強品質 |
| `爽點加強.md` | 放大規則流爽點 | 解法成立但讀起來不夠爽 |
| `邏輯修復.md` | 修補硬邏輯問題 | 讀者會覺得牽強 / 不合理 |
| `伏筆回收.md` | 設計自然回收 | 卷結、章末反轉、通關解法 |

---

## 建議工作流

### 1. 生成新章節

```bash
python _腳本/compile_context.py --novel infinite_livestream --chapter 9 --vector-query "記憶放映廳 陳述 照片 觀眾席 票根"
```

然後貼上：

```text
_提示詞工坊/章節生成.md
```

### 2. 初稿完成後檢查

```bash
python _腳本/validate_chapter_logic.py --novel infinite_livestream --volume 2 --chapter 9 --write-report
python _腳本/evaluate_story_quality.py --novel infinite_livestream --volume 2 --chapter 9 --write-report
```

### 3. 生成重寫任務

```bash
python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode rewrite --write
```

或按問題類型選模板：

```bash
python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode logic --write
python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode payoff --write
python _腳本/build_revision_task.py --novel infinite_livestream --volume 2 --chapter 9 --mode foreshadowing --write
```

### 4. 把輸出貼給 AI

輸出檔案：

```text
06-審校/重寫任務.md
```

貼給 AI 後，要求它只輸出修訂章節或替換段落。

---

## 模板選擇規則

| 問題 | 用哪個模板 |
|------|------------|
| 新章節還沒寫 | 章節生成 |
| 報告有 ERROR | 邏輯修復 |
| 章節可讀但不爽 | 爽點加強 |
| 伏筆回收牽強 | 伏筆回收 |
| 初稿整體偏平 | 章節重寫 |
| 有作者解釋 / 出戲句 | 章節重寫或邏輯修復 |

---

## 原則

- 模板不能取代狀態庫；每次仍要先讀 `compile_context.py`。
- 模板不能改變已確認事實；如需改事實，要先更新正文，再同步 database。
- 重寫應優先局部修補，不要每次推倒整章。
- 好小說不是只靠設定，還要鉤子、危機、選擇、代價、情感問題。
