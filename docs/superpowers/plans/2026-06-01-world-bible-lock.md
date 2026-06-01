# World Bible Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `無限直播間+` World Bible into a pre-drafting lock state without writing novel chapters.

**Architecture:** Use one Part-level control document as source of coordination, then add six supporting documents for truth reveal, power system, organization history, character function, long-form foreshadowing, and dungeon design. Any new canon setting must first be presented to the user as candidate options and approved before being written into the Bible.

**Tech Stack:** Markdown, YAML frontmatter, Obsidian wiki links, PowerShell native file inspection, git.

---

## Canon Approval Gate

Before writing any new setting into `無限直播間+`, perform this gate:

```text
候選設定審核：
- 設定名稱：
- 放入檔案：
- 解決問題：
- 影響角色：
- 影響組織：
- 影響系統規則：
- 可能衝突：
- A/B/C 選項：
- 推薦：
```

Only after user approval may the setting be added to World Bible files.

This gate does not block creating empty structure, tables, or non-canon planning scaffolds. It blocks new lore, named characters, organization events, ability rules, and Part-level story facts.

## File Structure

- Create `無限直播間+/07-篇章大綱/全書結構鎖定表.md`
  - Responsibility: Part01-Part05 total structure, Part function, truth reveal, organization/ability hooks.
- Create `無限直播間+/07-篇章大綱/系統真相分層揭露表.md`
  - Responsibility: who knows what at each Part; prevent early reveal.
- Create `無限直播間+/05-系統規則/能力與權限系統.md`
  - Responsibility: unified power system across主播、觀眾、未登記者、組織、系統.
- Create `無限直播間+/04-組織勢力/組織事件年表.md`
  - Responsibility: organization history, mistakes, crimes, splits, representatives.
- Create `無限直播間+/03-角色資料庫/角色功能矩陣.md`
  - Responsibility: role coverage, character function, missing role slots.
- Create `無限直播間+/16-作者控制台/長線伏筆總表.md`
  - Responsibility: cross-Part foreshadowing control.
- Create `無限直播間+/06-副本資料庫/副本設計規格.md`
  - Responsibility: dungeon design schema and Part01/Part02 application hooks.
- Modify only after approval: `無限直播間+/00-總覽/篇章總索引.md`
  - Responsibility: update Part03/Part04 if user-approved structure exists.
- Modify only after approval: `無限直播間+/00-總覽/角色總索引.md`
  - Responsibility: add approved new character categories or named characters.
- Modify only after approval: `無限直播間+/00-總覽/組織總索引.md`
  - Responsibility: add approved representatives/events.
- Modify only after approval: `無限直播間+/16-作者控制台/已定案設定總表.md`
  - Responsibility: register approved files and status.

---

### Task 1: Create Structural Skeletons

**Files:**
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\全書結構鎖定表.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\系統真相分層揭露表.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\能力與權限系統.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\組織事件年表.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\角色功能矩陣.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\長線伏筆總表.md`
- Create: `C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\副本設計規格.md`

- [ ] **Step 1: Prepare canonical frontmatter**

Use this frontmatter pattern for each new file, changing `type`, `tags`, and `related` per file:

```markdown
---
type: 規劃
status: 草案
level: Level-B
tags:
  - 規劃
  - 草案
  - Level-B
related:
  - 已定案設定總表
updated: 2026-06-01
---
```

- [ ] **Step 2: Create files with tables only**

Create only headings, instructions, and empty or existing-setting-backed tables. Do not add new named lore.

Expected result: seven files exist and contain no new canon beyond currently approved material.

- [ ] **Step 3: Check files exist**

Run:

```powershell
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\全書結構鎖定表.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\系統真相分層揭露表.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\能力與權限系統.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\組織事件年表.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\角色功能矩陣.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\長線伏筆總表.md'
Test-Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\副本設計規格.md'
```

Expected: seven `True` lines.

- [ ] **Step 4: Commit skeletons**

```powershell
git add -- '無限直播間+/07-篇章大綱/全書結構鎖定表.md' '無限直播間+/07-篇章大綱/系統真相分層揭露表.md' '無限直播間+/05-系統規則/能力與權限系統.md' '無限直播間+/04-組織勢力/組織事件年表.md' '無限直播間+/03-角色資料庫/角色功能矩陣.md' '無限直播間+/16-作者控制台/長線伏筆總表.md' '無限直播間+/06-副本資料庫/副本設計規格.md'
git commit -m '新增世界觀鎖定規劃骨架'
```

---

### Task 2: Draft Candidate Part Structure for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\篇章總索引.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part01-初入直播篇.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part02-修復倫理篇.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part05-未登記主播篇.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\全書結構鎖定表.md`

- [ ] **Step 1: Extract existing Part facts**

Use PowerShell:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\篇章總索引.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part01-初入直播篇.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part02-修復倫理篇.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\Part05-未登記主播篇.md'
```

- [ ] **Step 2: Present candidate Part03/Part04 options**

Ask user to choose before writing:

```text
候選設定審核：Part03/Part04 功能

A. 觀眾側政治 → 主播競爭
- Part03：觀眾側、打賞、商城情報污染、高權重觀眾初露面
- Part04：競爭主播、存續者試探、組織代表登場
- 優點：自然接到 Part05 未登記主播
- 風險：需要新增觀眾側代表與競爭主播

B. 組織追查 → 觀眾側政治
- Part03：第零修復科殘留、存續者分裂、沈未線延伸
- Part04：觀眾側與商城情報污染
- 優點：組織故事更早扎根
- 風險：可能過早變重

C. 副本連鎖 → 組織/觀眾雙線
- Part03：多副本連鎖，逐步露出商城與觀眾污染
- Part04：組織代表與競爭主播同時登場
- 優點：讀者仍有副本快感
- 風險：Part04 負載高

推薦：A
```

- [ ] **Step 3: Write only approved Part structure**

After user selects option, update `全書結構鎖定表.md` with only approved content.

- [ ] **Step 4: Commit approved Part structure**

```powershell
git add -- '無限直播間+/07-篇章大綱/全書結構鎖定表.md'
git commit -m '補全全書篇章結構鎖定表'
```

---

### Task 3: Draft Candidate Power System for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\主播本質.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\積分系統.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\商城情報與權限.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\高權重觀眾.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\01-世界觀\未登記者.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\能力與權限系統.md`

- [ ] **Step 1: Extract existing ability facts**

Run:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\主播本質.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\積分系統.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\商城情報與權限.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\05-系統規則\高權重觀眾.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\01-世界觀\未登記者.md'
```

- [ ] **Step 2: Present candidate power taxonomy**

Ask user to approve:

```text
候選設定審核：能力與權限系統

推薦架構：權限層級，不是戰鬥力階級

五類：
1. 主播權限：通關、查閱、購買、有限操作
2. 觀眾權限：觀看、打賞、索引、模仿、權重干涉
3. 未登記能力：規避定位、偽裝彈幕、時間錨點、短暫附著 UI
4. 組織技術：補錄、隔離、檔案保存、人格穩定、錯誤修復
5. 系統權限：校正、抹消、結算、重新登記、代理校正

核心限制：
- 能力不能直接救命或復活
- 能力不能無代價改寫存在
- 升級 = 接觸更深記錄層，代價也更高
- 周倉終局力量 = 被觀測 + 未登記 + 存續人格重疊
```

- [ ] **Step 3: Write approved power system**

After approval, write the taxonomy, table, limits, costs, reveal Part, related files.

- [ ] **Step 4: Commit power system**

```powershell
git add -- '無限直播間+/05-系統規則/能力與權限系統.md'
git commit -m '建立能力與權限系統'
```

---

### Task 4: Draft Candidate Organization History for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\第零修復科.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\存續者.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\人格保留派.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\保守存續派.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\激進改寫派.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\關停派.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\組織事件年表.md`

- [ ] **Step 1: Read organization files**

Run:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\第零修復科.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\存續者.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\人格保留派.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\保守存續派.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\激進改寫派.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\04-組織勢力\關停派.md'
```

- [ ] **Step 2: Present candidate organization event chain**

Ask user to approve before writing:

```text
候選設定審核：第零修復科 → 存續者事件鏈

推薦事件骨架：
1. 第零修復科成立：處理存在層錯誤與抹消撤回
2. 第一次錯誤：把「修復」誤當「還原原始本體」
3. 關鍵發現：世界可同時存在兩個正確答案
4. 最大罪行：為證明/控制此發現，犧牲後生人格或樣本
5. 分裂：人格保留派、保守存續派、激進改寫派、關停派成形
6. 存續者成立：不是革命軍，是不肯被刪掉的人

需你決定：
A. 第一次錯誤偏技術事故
B. 第一次錯誤偏倫理選擇
C. 第一次錯誤偏高層命令

推薦：B
```

- [ ] **Step 3: Write approved organization timeline**

Only write approved event chain. Keep `系統起源` and `歸零事件完整版` frozen.

- [ ] **Step 4: Commit organization timeline**

```powershell
git add -- '無限直播間+/04-組織勢力/組織事件年表.md'
git commit -m '建立組織事件年表'
```

---

### Task 5: Draft Candidate Character Matrix for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\角色總索引.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\周倉.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\許小小.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\沈未.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\小眠.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\陳述.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\角色功能矩陣.md`

- [ ] **Step 1: Read existing character files**

Run:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\角色總索引.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\周倉.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\許小小.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\沈未.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\小眠.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\03-角色資料庫\陳述.md'
```

- [ ] **Step 2: Present role slot proposal**

Ask user to approve categories before adding named characters:

```text
候選設定審核：角色補足方向

先不新增名字，只新增角色槽位：
1. 副本短期角色：測試規則、承受代價、製造鏡像選擇
2. 觀眾側代表：讓觀眾池具象化
3. 組織代表：每派至少一個具名角色
4. 競爭主播：展示其他通關策略
5. 灰色盟友：提供資源但保留利用意圖

命名階段另行討論。

推薦：先建槽位，不急著命名。
```

- [ ] **Step 3: Write approved matrix**

Write existing characters plus approved unnamed role slots. Mark unnamed slots as `待命名`, not canon names.

- [ ] **Step 4: Commit character matrix**

```powershell
git add -- '無限直播間+/03-角色資料庫/角色功能矩陣.md'
git commit -m '建立角色功能矩陣'
```

---

### Task 6: Draft Candidate Truth and Foreshadowing Controls for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\核心問題總表.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\伏筆追蹤.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\07-篇章大綱\系統真相分層揭露表.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\長線伏筆總表.md`

- [ ] **Step 1: Read existing questions and foreshadowing**

Run:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\核心問題總表.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\伏筆追蹤.md'
```

- [ ] **Step 2: Present reveal-layer proposal**

Ask user to approve:

```text
候選設定審核：系統真相分層

推薦揭露節奏：
Part01：直播間像遊戲，但規則有縫隙
Part02：修復不等於拯救，系統會把人當物處理
Part03：觀眾不是背景，觀測本身會改變判定
Part04：組織不是答案，各派都只掌握一部分真相
Part05：周倉被刪除後返回，證明系統記錄不是存在唯一來源

保留：
- 系統起源完整版
- 歸零事件完整版
- 0號樣本完整身份
- 林█自我刪除型真相
- X 與許小小終局答案
```

- [ ] **Step 3: Write approved reveal and foreshadowing tables**

Write only approved reveal layers and cross-Part foreshadowing. Mark frozen topics as `凍結，不揭露核心答案`.

- [ ] **Step 4: Commit truth and foreshadowing controls**

```powershell
git add -- '無限直播間+/07-篇章大綱/系統真相分層揭露表.md' '無限直播間+/16-作者控制台/長線伏筆總表.md'
git commit -m '建立真相分層與長線伏筆控制'
```

---

### Task 7: Draft Dungeon Design Spec for Approval

**Files:**
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\紅雨衣便利店.md`
- Read: `C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\失物檔案館.md`
- Later modify after approval: `C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\副本設計規格.md`

- [ ] **Step 1: Read existing dungeon files**

Run:

```powershell
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\紅雨衣便利店.md'
Get-Content -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+\06-副本資料庫\失物檔案館.md'
```

- [ ] **Step 2: Present dungeon schema**

Ask user to approve:

```text
候選設定審核：副本設計規格

推薦每副本固定欄位：
- 表面規則
- 真規則
- 核心衝突
- 情感功能
- 世界觀功能
- 能力/權限揭露
- 新資訊
- 代價
- 主要角色
- 組織痕跡
- 伏筆
- 卷末鉤子
- 不可揭露內容

推薦原則：
- 每個副本只主打一種恐怖或倫理壓力
- 副本是真相切片，不是普通關卡
- Part01/Part02 先細化，其餘只留功能位
```

- [ ] **Step 3: Write approved dungeon spec**

Write schema and apply it to existing `紅雨衣便利店` and `失物檔案館` only at function level. Do not invent chapter events.

- [ ] **Step 4: Commit dungeon spec**

```powershell
git add -- '無限直播間+/06-副本資料庫/副本設計規格.md'
git commit -m '建立副本設計規格'
```

---

### Task 8: Update Indexes After User-Approved Content Exists

**Files:**
- Modify: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\篇章總索引.md`
- Modify: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\角色總索引.md`
- Modify: `C:\Users\user\novel-creator\novel-creator\無限直播間+\00-總覽\組織總索引.md`
- Modify: `C:\Users\user\novel-creator\novel-creator\無限直播間+\16-作者控制台\已定案設定總表.md`

- [ ] **Step 1: Confirm approvals**

Verify each update maps to a previously approved content block from Tasks 2-7.

- [ ] **Step 2: Update indexes only with approved content**

Update indexes to point to the seven new files and any approved Part/role/organization changes.

- [ ] **Step 3: Search for forbidden placeholder leakage**

Run:

```powershell
Get-ChildItem -Path 'C:\Users\user\novel-creator\novel-creator\無限直播間+' -Recurse -File |
  Select-String -Pattern 'TODO|TBD|UNKNOWN|待命名但已定案|凍結但已揭露' |
  Select-Object Path,LineNumber,Line
```

Expected: no `TODO` or `TBD`; `UNKNOWN` only if backed by explicit missing source; `待命名` only in draft role slots.

- [ ] **Step 4: Commit index updates**

```powershell
git add -- '無限直播間+/00-總覽/篇章總索引.md' '無限直播間+/00-總覽/角色總索引.md' '無限直播間+/00-總覽/組織總索引.md' '無限直播間+/16-作者控制台/已定案設定總表.md'
git commit -m '更新世界觀鎖定索引'
```

---

### Task 9: Final Consistency Review

**Files:**
- Read: all files created or modified in Tasks 1-8

- [ ] **Step 1: Run git diff review**

```powershell
git diff HEAD~8..HEAD --stat
git diff HEAD~8..HEAD -- '無限直播間+'
```

Expected: only planned World Bible files changed.

- [ ] **Step 2: Check no forbidden canon change slipped in**

Manually verify:

- `林█` remains frozen.
- `0號樣本` remains frozen.
- `X` remains frozen.
- `系統起源` remains frozen.
- `歸零事件完整版` remains frozen.
- No chapter正文 added.
- No power system becomes裝備商城.
- No organization becomes pure good/evil.

- [ ] **Step 3: Final commit if review fixes were needed**

If review changes were made:

```powershell
git add -- '無限直播間+'
git commit -m '修正世界觀鎖定一致性'
```

If no changes were needed, skip commit.

## Self-Review

Spec coverage:

- Whole story structure: Tasks 1-2.
- System truth reveal: Task 6.
- Long foreshadowing: Task 6.
- Character long lines and role shortage: Task 5.
- Organization detail story: Task 4.
- Power system: Task 3.
- Dungeon design spec: Task 7.
- Index and status integration: Task 8.
- Final consistency: Task 9.
- User approval before new settings: Canon Approval Gate plus Tasks 2-7 approval steps.

Placeholder scan:

- No `TBD`, `TODO`, or undefined implementation placeholders are required for execution.
- `待命名` is intentionally allowed only for role slots before user approves names.

Scope check:

- The plan covers one coherent workstream: pre-drafting World Bible lock.
- The work is split into independently reviewable tasks with commits after each stage.
