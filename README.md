[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5PhkpLhw)
# HW2-Implementation-of-SDD-Specification-Optimization
### 1. 專案簡介
- v1.0 的功能描述與設計動機
    v1.0 的功能為基本 CRUD，也就是使用者能操作基本的新增、讀取、更新和刪除記帳資料，第一版選擇設計這幾個功能原因為，滿足使用者在記帳時的基本使用
- 從 v1.0 到 v2.0 的演化摘要
    v2.0 根據使用者需求新增了 summary 和 import 兩個功能，這兩個功能分別為各類別收支統計與使用者若有多筆資料能夠使用匯入方式記。另外，在原先 list (讀取記帳資料) 中新增除 type (income、expense 和 all) 外的篩選原則，也就是使用者能根據類別、日期等等篩選想看到的資料，也能自定義想要的排序方式。  

### 2. v1.0 設計決策（Design Decisions）
- 將資料存取和邏輯拆分開來，總共拆成六個檔案，會拆分開來而不是所有寫在 `main.py` 中的原因為，盡量確保未來在擴充時能夠改動太多前一版的 code
- 將核心邏輯（service.py）與資料存取（storage.py）分開，是為了讓未來替換底層儲存方式（例如從 JSON 換成 SQLite）時，只需修改 storage.py，不需動到 service.py 的邏輯
- 資料模型中包含 `created_at`欄位，在 v1.0 中沒有實際作用，但考量到未來可能有根據日期過濾或排序需求，因此在資料模型中加入了新增這筆帳的日期
- CLI 設計採用 argparse 並使用 subcommand 模式將不同功能（add、list、update、delete）設計為子指令，使每個功能的參數清楚分離，避免參數混用，提升可讀性與可維護性
- 雖然 v1.0 沒有按 category 篩選的功能，但考量到記帳工具的常見需求（分類統計、依類別查詢），設計時就將 category 作為選填欄位納入資料模型。這讓 v2.0 的 summary 與 list --category 功能無需修改資料結構，直接在舊資料上運作。
- 刻意將錯誤分成三層，而非統一用一個 Exception，是為了讓未來新增功能時能清楚定位錯誤來源。v2.0 新增 import 與 summary 時，直接沿用現有錯誤類型，不需新增任何錯誤類別
- `generate_id()` 以 max(id) + 1 而非 len + 1，選擇用現有最大 ID 加一，而非用資料筆數加一，是為了避免刪除資料後 ID 重複的問題。這個設計在 v2.0 的 import 批量新增時同樣適用，不需要額外處理 ID 衝突


### 3. v2.0 實作說明

- 說明你如何閱讀並理解 Agent 產生的 v2.0 需求
閱讀需求列表中使用者所希望增加的功能或需求，有一兩個較無法確定意思的，再到驗收標準中確認，確認 v2 滿足所有使用者需求
- 說明你如何將 v2.0 需求映射到 SDD
將需求拆解為三大功能模組，並對應到 SDD：
    - list 強化（既有功能擴充）
        - PRD 要求支援 category、日期範圍篩選與排序
        - 對應到 SDD：
            1. CLI list 新增參數（--category, --startAt, --endAt, --sortBy, --order）
            2. storage 層負責篩選與排序邏輯
            3. display 層負責呈現結果與 totals

    - summary（新功能）
        - PRD 要求依 category 分組統計收入、支出與筆數
        - 對應到 SDD：
            1. 新增 summary 指令
            2. service 層新增 summary_record() 負責分組統計邏輯
            3. display 層新增 print_summary() 負責數字搭配長條圖呈現結果

    - import（新功能）
        - PRD 要求支援 CSV 批量匯入
        - 對應到 SDD：
            1. 新增 import 指令與 --file 參數
            2. service 層負責 CSV parsing、資料驗證與錯誤處理策略
            3. storage 層負責寫入資料

- 列點說明每一個**非顯而易見的實作選擇**（例如：為何選此遷移策略、快取機制如何設計）
    - category 若使用者未填寫分類，原本使用 "-" 表示，但考量到在 list 篩選查詢時，使用者不易聯想 "-" 代表未分類，因此呈現給使用者的列表將 "-" 修改為 "uncategorized"，使用者在查詢時也能直接使用 "uncategorized" 查詢。需特別注意的是，在修改過程並沒有動到原本的資料，雖然現在資料量較小，但若模擬大量資料實作，修改資料庫我覺得不是一個好的策略
    - summary 摘要統計呈現時使用長條圖 + 數據呈現，選擇使用長條圖的原因為，此功能通常會用來看每個月在個類別的支出多寡，若是只使用文字和數字，則較不好比較，使用者體驗也較差，因此選擇以長條圖和數字表示
    - update 使用互動式選擇而非 argparse 原因為，考量更新流程較複雜，須調整參數較多，使用者可能會無法記住指令或參數可選選項有哪些，因此採用互動式的方式更新
    - import 若有資料不符合格式，採用部分跳過部分匯入的原則，因為若有大量資料須匯入，但因一筆資料的失敗而不匯入所有資料，並請使用者找出有問題的資料進行修正，對於使用者而言，需要花費很多時間體驗較差。

### 4. 向下相容性實作細節

本專案在遵循不對 v1.0 進行 breaking change 的情況下開發 v2.0:

1. CLI 介面保持向下相容
   - 原有指令（add / list / update / delete）皆未移除或改名
   - 僅新增 optional 參數（例如 list 的篩選條件），不影響原有使用方式

2. 資料格式保持向下相容
   - v1.0 使用 "-" 表示未分類資料
   - v2.0 為提升可讀性，於 display 層統一轉換為 "uncategorized"
   - 但內部資料仍保留 "-"，避免修改既有資料造成不相容

3. 查詢行為向下相容
   - 使用者可使用 "uncategorized" 查詢未分類資料
   - 系統在查詢時會將 "uncategorized" 正規化為 "-"
   - 確保新舊資料可被一致處理

4. import 採部分匯入策略
   - 即使部分資料錯誤，其餘合法資料仍會被寫入
   - 避免因單筆錯誤影響整體匯入流程

本專案未使用額外 Adapter Pattern，而是透過資料正規化（normalize）策略實現向下相容。

### 5. 架構演化比較

| 面向 | v1.0 | v2.0 | 說明 |
|---|---|---|---|
| 儲存層 | JSON 檔案 | JSON 檔案（不變） | v1.0 設計時已預留擴充空間，v2.0 需求未要求換 DB，故維持不變 |
| CLI Library | argparse + subcommand | argparse + subcommand（不變） | subcommand 模式天然支援新增指令而不影響舊指令 |
| 模組數量 | 5 個模組 | 5 個模組（不變） | v2.0 三個新功能均能對應到既有模組分工，無需新增模組 |
| 指令數量 | 4 個（add/list/update/delete） | 6 個（新增 summary/import） | 純新增，無修改或移除 |
| load_records() | 僅支援 type 篩選 | 新增 category、日期、sortBy、order 參數 | 函式介面設計時預留了擴充位置 |
| 錯誤處理 | 三層錯誤類型 | 三層錯誤類型（不變） | v2.0 新功能直接沿用，未新增任何 Exception 類別 |
| 資料模型 | 含 category、created_at | 完全相同（不變） | v1.0 已預見分類與日期篩選的需求，提前納入 |

架構幾乎未變動，並非缺乏思考，而是 v1.0 設計時已充分考量延伸方向，v2.0 的三個新需求（list 強化、summary、import）能直接在既有架構上擴充。

### 6. 環境需求與執行方式

```bash
# v1.0
cd v1/
pip install -r requirements.txt
python main.py --help

# v2.0
cd v2/
pip install -r requirements.txt
python main.py --help
```

### 7. 已知限制與未來改進方向
**已知限制**
1. CLI 操作方式對於一般使用者而言並不直觀
2. `created_at` 若是用於自行輸入可行，但若是匯入的資料則會發生一天很多筆資料，但不一定是在那天消費的狀況
3. 資料存取採用 JSON，若是資料量大讀寫效率會下降
4. 資料存取時未加入 user，若是有多個使用者則所有資料會混一起
5. 缺乏自動化測試，目前僅透過手動測試驗證功能，無法確保未來修改不影響既有功能

**未來改進方向**
1. 由 CLI 改為介面操作
2. 將 created_at (系統紀錄時間) 與 transaction_date (實際消費時間) 拆分
3. 使用 MySQL 儲存資料
4. 加入 user 進到資料庫中，區分不同使用者記帳紀錄
5. 加入自動化測試，確保未來的修改不影響既有功能，且測試上也較省時




