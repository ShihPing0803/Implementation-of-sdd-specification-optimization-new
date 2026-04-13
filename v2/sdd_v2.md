# CashTrack CLI - SDD v2.0

## 1. 專案概覽（Project Overview）

- 程式名稱：CashTrack 記帳系統
- 版本：v2.0
- 一句話描述：一個可記錄個人收入與支出的記帳工具
- 目標使用者：想快速記錄日常收支的個人使用者
- 核心價值：提供簡單的記帳方式

---

## 2. CLI 介面規格（Interface Specification）

### 指令列表

| 指令     | 參數        | 說明     | 範例      |
| ------------ | ----- | --------------------- | --------------- |
| `add`    | `[--type income\|expense] --name TEXT --amount FLOAT [--note TEXT] [--category TEXT]` | 新增一筆記錄（name 與 amount 為必填），type 缺少時會進入到互動選擇 | `python main.py add --type expense --name "lunch" --amount 120 --category food --note "noodles"` |
| `list` | `--type income\|expense\|all [--category TEXT] [--startAt DATE] [--endAt DATE] [--sortBy amount\|created_at] [--order asc\|desc]`（type 預設 `all`，排序預設 `created_at desc`） | 列出記錄，支援分類篩選、日期範圍篩選與排序 | `python main.py list --type expense --category food --sortBy amount --order desc` |
| `update` | （無 CLI 參數，互動式更新）  | 透過互動方式更新記錄  | `python main.py update`   |
| `delete` | `--id INT`  | 刪除指定 ID 的記錄  | `python main.py delete --id 1`    |
| `summary` | `--type income\|expense\|all`（type 預設 `all`） | 依 category 彙總收入與支出，未分類資料歸為 Uncategorized | `python main.py summary --type expense` |
| `import` | `--file FILE_PATH` | 匯入 CSV 檔案（支援收入與支出紀錄） | `python main.py import --file example.csv` |

### CSV 匯入說明
- 第一列為表頭，依序為 type、name、amount、category、note
- 必填和選填欄位 
  - 必填：type, name, amount
  - 選填：category, note
  - category 空值時預設 uncategorized
- 匯入支援 utf-8-sig、utf-8、cp950，若都失敗，顯示 unsupported encoding 錯誤
- 錯誤處理策略: 匯入資料時若有例外狀況 (如: 資料不符合格式等等)，將採取部分匯入，亦即跳過不符合格式的資料。選擇部分匯入原因為，若資料量較大，只因一筆資料的例外狀況，而選擇全部不匯入，將會降低匯入效率，使用者須將問題資料找出後，才能匯入資料，這會降低使用者體驗，因此採用部分匯入的方式。
- 考量到 created_at 最初設定為系統建立這筆資料的時間，因此若使用者採取匯入 csv 的方式，日期一樣統一由系統建立 
- CSV 範例可參考 example.csv

### 指令執行後的輸出
- `add` / `update` / `delete` 指令執行後：
  - 顯示對應操作訊息（例如 `Added record.`）
  - 顯示目前所有記錄的表格
  - Total Income
  - Total Expense
  - Balance
- `list` 指令執行後：
  - 顯示符合篩選條件的記錄表格（若未指定任何篩選條件，則顯示全部）
  - Total Income、Total Expense、Balance 均反映篩選後的資料，而非全部資料的總計
  - 若指定 `--category` 但該分類不存在，顯示錯誤提示並退出，不顯示空表格
  - 若指定日期範圍但區間內無資料，顯示錯誤提示並退出

  範例：執行 `list --type expense --category food` 後：
  - 表格只顯示 category 為 food 的支出記錄
  - Total Income 顯示 0.00（因為篩選只含 expense）
  - Total Expense 與 Balance 只計算篩選結果內的金額

- `summary` 指令執行後
  - 使用仿長條圖的方式顯示各類別的 total income、total expense 和筆數，此方式能增加可讀性，使用者在閱讀時也能較快看出哪個類別花費較多
  - 顯示整體的 Total Income、Total Expense 與 Balance

- `import` 指令執行後
  - 顯示成功成功 X 筆、跳過 Y 筆
  - 若檔案無法讀取呈現錯誤訊息

---

## 3. 資料模型（Data Model）

### Record

| 欄位         | 型別  | 說明                                   | 必填            |
| ------------ | ----- | -------------------------------------- | --------------- |
| `id`         | int   | 唯一識別碼，自動遞增                   | ✅              |
| `type`       | str   | 收入或支出，值為 `income` 或 `expense` | ✅              |
| `name`       | str   | 項目名稱                               | ✅              |
| `amount`     | float | 金額，必須大於 0                       | ✅              |
| `category`   | str   | 分類，例如 food、transport、salary     |                 |
| `note`       | str   | 備註說明                               |                 |
| `created_at` | str   | 建立時間（ISO 格式）                   | ✅ (由系統建立) |

### json 儲存格式

```json
[
  {
    "id": 1,
    "type": "expense",
    "name": "name",
    "amount": 1000.0,
    "category": "test",
    "note": "note",
    "created_at": "2026-03-18 10:35:06"
  }
]
```

## 4. 模組架構（Module Design）

```mermaid
graph TD
    A[main.py / CLI Entry] --> B[commands.py / Parser]
    A --> C[service.py / Business Logic]
    A --> D[storage.py / Data Access]
    A --> F[display.py / UI]
    
    C --> D
    D --> E[(data/records.json)]
    
    %% Error Handling 
    A -.-> G[error.py]
    C -.-> G
    D -.-> G
```

### 核心功能流程圖 (匯入 CSV 功能)

```mermaid
sequenceDiagram
    participant User
    participant CLI as main.py
    participant Service as service.py
    participant Storage as storage.py

    User->>CLI: python main.py import --file data.csv

    CLI->>Service: import_records(file_path)
    Service->>Storage: load_records("all")
    Storage-->>Service: existing records

    Service->>Service: 嘗試開啟 CSV（utf-8-sig / utf-8 / cp950）
    alt 檔案不存在
        Service-->>CLI: raise StorageError("File not found.")
        CLI-->>User: [ERROR] StorageError: File not found.
    else 編碼均失敗
        Service-->>CLI: raise BusinessError("unsupported encoding")
        CLI-->>User: [ERROR] BusinessError: Failed to read file
    end

    Service->>Service: 檢查 CSV header 是否含 type, name, amount
    alt header 缺少必要欄位
        Service-->>CLI: raise BusinessError("Invalid CSV header")
        CLI-->>User: [ERROR] BusinessError: Invalid CSV header.
    end

    loop 逐列處理每一筆 row
        Service->>Service: validate_record_input(name, type, amount)
        alt 資料合法
            Service->>Service: 建立 new_record，append 至 records
            Note right of Service: success_count += 1
        else 格式錯誤 / 驗證失敗
            Note right of Service: skipped_count += 1（跳過此列）
        end
    end

    Service->>Storage: save_records(records)
    Storage-->>Service: 寫入成功
    Service-->>CLI: "成功 X 筆、跳過 Y 筆"
    CLI-->>User: 成功 X 筆、跳過 Y 筆
```

**簡要說明**

- `main.py`：CLI 入口與參數解析
- `commands.py`: 指令設計，subparser 總共有六個指令，分別是 add、update、list、delete、summary 和 import
- `service.py`：負責核心功能，包含 CRUD 該如何實作
- `storage.py`: 和資料有關的 function，包含載入和儲存資料
- `data/records.json`: 資料儲存位置，當作暫時資料庫使用
- `display.py`: 繪製表格顯示結果給使用者查看

## 5. 錯誤處理規格（Error Handling）

### 錯誤分類

- Usage Error（使用方式錯誤）：CLI 指令使用不正確，例如缺少必填參數或參數格式錯誤。
- Validation Error（資料驗證錯誤）：輸入資料不符合欄位規則，例如不支援的 type 或金額小於等於 0。
- Business Error（業務邏輯錯誤）：輸入格式正確，但操作目標不符合業務邏輯，例如找不到指定的記錄（ID 不存在）。
- Storage Error（資料存取錯誤）：資料讀寫過程發生錯誤，例如 JSON 檔案損毀、檔案無法讀取或寫入、權限不足等。
- System Error（系統錯誤）：未預期的執行時錯誤，不屬於上述分類，例如程式錯誤或未知例外。

### Exit Code

| Code | 代表意思                                       |
| ---- | ---------------------------------------------- |
| 0    | Success                                        |
| 1    | Validation / Business / Storage / System error |
| 2    | Usage error                                    |

### 錯誤情境

| 情境                                          | 錯誤分類         | 預期行為                                                                   | 退出碼 |
| --------------------------------------------- | ---------------- | -------------------------------------------------------------------------- | ------ |
| CLI 缺少必要參數                              | Usage Error      | 顯示使用方式並退出                                                         | 2      |
| add / update 的 type 非 `income` 或 `expense` | Validation Error | 顯示錯誤訊息；若為互動模式則重新輸入，否則退出                             | 1      |
| list 的 type 非 `income`、`expense` 或 `all`  | Usage Error | 顯示使用方式並退出                                                         | 2      |
| 單項記錄金額小於或等於 0                      | Validation Error | 顯示錯誤訊息 `[ERROR] ValidationError: Amount must be greater than 0. Keeping original value.` 並退出或保留原值（update 互動模式） | 1      |
| 找不到 ID                                     | Business Error   | 跳出 `[ERROR] BusinessError: Record with ID [ID] not found.` 並退出                              | 1      |
| JSON 檔案讀取失敗（檔案無法開啟）        | Storage Error | 顯示 `[ERROR] StorageError: Failed to load records file: {e}` 並退出  | 1         |
| JSON 檔案格式錯誤（JSON parse 失敗） | Storage Error | 顯示 `[ERROR] StorageError: Failed to parse records file: {e}` 並退出 | 1         |
| JSON 檔案寫入失敗                | Storage Error | 顯示 `[ERROR] StorageError: Failed to save records file: {e}` 並退出  | 1         |
| 非預期 runtime error                          | System Error     | 顯示通用錯誤訊息並退出                                                     | 1      |
| 無任何紀錄可更新 | Business Error | 顯示 `[ERROR] BusinessError: No records available.` 並退出 | 1 |
| `list --startAt/--endAt` 日期格式錯誤	| Validation Error	| 顯示日期格式錯誤訊息並退出 	| 1 |
| `list --category` 指定不存在的分類	| Business Error	| 顯示查無該分類記錄並退出	| 1 |
| summary 時沒有任何可統計資料	| Business Error	| 顯示無資料可統計並退出	 | 1 |
| import --file 指定不存在檔案	| Storage Error	| 顯示檔案不存在並退出	 | 1 |
| import 的 CSV header 缺少必要欄位	| Business Error	| 顯示 header 不符合規定並退出	| 1 |
| `import` 檔案編碼不支援或無法讀取 | Business Error | 顯示讀取失敗訊息並退出 | 1   |

## 6. 測試案例（Test Cases）

**Add**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 新增收入 | `python main.py add --type income --name Salary --amount 5000 --category Job --note August` | 顯示 `Added: [id] Salary`，資料成功寫入並出現在列表中 | stdout 含 `Added:` 且退出碼為 0 |
| 新增支出 | `python main.py add --type expense --name Lunch --amount 120 --category Food --note Bento` | 顯示 `Added: [id] Lunch`，資料成功新增並出現在列表中 | stdout 含 `Added:` 且退出碼為 0 |
| 不提供 category 與 note | `python main.py add --type expense --name Coffee --amount 60` | category 為 `uncategorized`，note 為空字串 | stdout 表格中該筆 category 欄為 `uncategorized`，note 欄為空，退出碼為 0 |
| 互動選擇 type | `python main.py add --name Bonus --amount 1000` | 系統要求選擇 type，完成後新增資料，且資料於列表中呈現 | stdout 含 `Added:` 且退出碼為 0 |
| 互動選擇 type（type 選擇不在列表中的項目） | `python main.py add --name Bonus --amount 1000` | 系統要求重新選擇 type，直到選擇到列表中任一選項 | stdout 含錯誤提示並重新要求輸入，最終成功新增後退出碼為 0 |
| amount 為負數 | `python main.py add --type expense --name Refund --amount -50` | 顯示 `[ERROR] ValidationError: Amount must be greater than 0.` | stdout 含 `ValidationError` 且退出碼為 1 |
| amount 非數字 | `python main.py add --type expense --name Tea --amount abc` | argparse 報錯並中止程式 | stderr 含 `invalid float value` 且退出碼為 2 |

---

**List**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 列出全部資料 | `python main.py list --type all` | 顯示所有 records 與 totals，和總支出與總收入 | stdout 含表格與 `Total Income`、`Total Expense`、`Balance`，退出碼為 0 |
| 只列收入 | `python main.py list --type income` | 僅顯示 type 為 income 的資料，總支出顯示為 0 | stdout 不含 expense 記錄，含 `Total Expense: 0.00`，退出碼為 0 |
| 只列支出 | `python main.py list --type expense` | 僅顯示 type 為 expense 的資料，總收入顯示為 0 | stdout 不含 income 記錄，含 `Total Income: 0.00`，退出碼為 0 |
| type 不在列表內 | `python main.py list --type 123` | argparse 報錯並中止程式 | stderr 含 `invalid choice` 且退出碼為 2 |

---

**Update**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| ID 非數字或按 enter | `python main.py update` → 輸入 abc | 顯示 `[ERROR] ValidationError: Invalid ID. Please enter a number.`，不更新資料 | stdout 含 `ValidationError` 且退出碼為 1，資料無變動 |
| ID 不存在 | `python main.py update` → 輸入不存在 ID | 顯示 `[ERROR] BusinessError: Record with ID 999 not found.` | stdout 含 `BusinessError` 且退出碼為 1，資料無變動 |
| 更新 name | `python main.py update` → 輸入 ID → 輸入新 name | 顯示 `Updated: [id] [新的 name]` | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 name 已更新 |
| name 按 enter | `python main.py update` → 輸入 ID → name 按 enter | 保持原本的 name | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 name 不變 |
| 更新 type | `python main.py update` → 輸入 ID → 輸入 income/expense | type 成功更新並顯示 `Updated: [id] [該 id 紀錄名稱]` | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 type 已更新 |
| type 輸入錯誤後重輸 | `python main.py update` → type 輸入錯誤值再輸入正確值 | 顯示 `[ERROR] ValidationError: Type must be 'income' or 'expense'...` 並重新要求輸入 | stdout 含 `ValidationError` 提示後繼續互動，最終退出碼為 0 |
| type 直接 Enter | `python main.py update` → 輸入 ID → type 按 Enter | 保持原本 type | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 type 不變 |
| 更新 amount | `python main.py update` → 輸入數值 | amount 更新成功，顯示 `Updated: [id] [該 id 紀錄名稱]` | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 amount 已更新 |
| amount 為負數 | `python main.py update` → 輸入 -10 | 顯示 `[ERROR] ValidationError: Amount must be greater than 0. Keeping original value.` | stdout 含 `ValidationError` 且退出碼為 0，該筆 amount 保持原值 |
| amount 非數字 | `python main.py update` → 輸入 abc | 顯示 `[ERROR] ValidationError: Invalid amount format. Keeping original value.` | stdout 含 `ValidationError` 且退出碼為 0，該筆 amount 保持原值 |
| amount 直接 Enter | `python main.py update` → 輸入 ID → amount 按 Enter | 保持原本 amount | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 amount 不變 |
| 更新 category | `python main.py update` → 輸入 ID → 輸入新 category | 顯示 `Updated: [id] [name]` | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 category 已更新 |
| category 按 enter | `python main.py update` → 輸入 ID → category 按 enter | 保持原本的 category | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 category 不變 |
| 更新 note | `python main.py update` → 輸入 ID → 輸入新 note | 顯示 `Updated: [id] [name]` | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 note 已更新 |
| note 按 enter | `python main.py update` → 輸入 ID → note 按 enter | 保持原本的 note | stdout 含 `Updated:` 且退出碼為 0，列表中該筆 note 不變 |
| 無任何紀錄可更新 | `python main.py update`（無資料時） | 顯示 `[ERROR] BusinessError: No records available.` | stdout 含 `BusinessError` 且退出碼為 1 |

---

**Delete**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 成功刪除 | `python main.py delete --id 3` | 顯示 `Deleted: [3] salary`，資料被移除並印出更新後列表 | stdout 含 `Deleted:` 且退出碼為 0，列表中該筆記錄不再存在 |
| 刪除不存在 ID | `python main.py delete --id 999` | 顯示 `[ERROR] BusinessError: Record with ID 999 not found.` | stdout 含 `BusinessError` 且退出碼為 1，資料無變動 |

---

### v2.0 新增 / 修改功能測試

**List (v2.0 篩選與排序)**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 依分類篩選（存在） | `python main.py list --category food` | 僅顯示 category 為 food 的記錄，並更新總計金額 | stdout 僅含 food 記錄，且 Balance 反映篩選結果，退出碼為 0 |
| 依分類篩選（不存在） | `python main.py list --category game` | 顯示查無資料的提示`[ERROR] BusinessError: No records found for category 'game'.` | stdout 提示無資料，退出碼為 1 |
| 依日期範圍篩選 | `python main.py list --startAt 2026-03-01 --endAt 2026-03-31` | 僅顯示建立時間落於 3 月份的記錄 | stdout 僅含該區間記錄，退出碼為 0 |
| 日期格式輸入錯誤 | `python main.py list --startAt 2026/03/01` | 顯示 `[ERROR] ValidationError: Invalid date format. Please use YYYY-MM-DD.`| stderr 或 stdout 含錯誤提示，退出碼為 1 |
| 依金額降冪排序 | `python main.py list --sortBy amount --order desc` | 記錄依據金額由大到小排列 | stdout 表格內金額呈現遞減排序，退出碼為 0 |
| 組合條件篩選與排序 | `python main.py list --type expense --category food --sortBy amount --order desc` | 僅顯示 food 的支出，並依金額降冪排列 | stdout 符合所有篩選與排序條件，退出碼為 0 |

---

**Summary (v2.0 摘要統計)**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 顯示整體摘要 | `python main.py summary` | 顯示各 category 的收支總計、筆數，以及整體收入、支出總和與 Balance | stdout 含分類統計表與整體數據，退出碼為 0 |
| 依類型顯示摘要 | `python main.py summary --type expense` | 僅統計並顯示支出相關的 category | stdout 摘要表中不含 income 的數據，退出碼為 0 |
| 處理未分類記錄 | `python main.py summary`（存在無 category 資料時） | 無分類的記錄被歸類到 `Uncategorized` 群組中合併計算 | stdout 摘要表中出現 `Uncategorized` 項目且數據正確，退出碼為 0 |

---

**Import (v2.0 批量匯入)**

| 功能 | 輸入 | 預期結果 | 通過條件 |
|------|------|----------|----------|
| 成功匯入合法 CSV | `python main.py import --file example.csv` | 資料寫入系統，顯示 `成功 X 筆、跳過 Y 筆` | stdout 含成功訊息，後續執行 list 可見新資料，退出碼為 0 |
| 檔案不存在 | `python main.py import --file no_exist.csv` | 顯示 `[ERROR] StorageError: File not found.` | stdout 含錯誤提示，資料庫無變動，退出碼為 1 |
| 匯入含錯誤列的 CSV | `python main.py import --file mixed_data.csv`（內含 3 筆正確、2 筆格式錯誤） | 採取部分匯入策略：寫入 3 筆，並提示 `成功 3 筆、跳過 2 筆` | stdout 顯示成功與跳過筆數，後續 list 僅新增 3 筆，退出碼為 0 |

## 7. 向下相容性
### 保留的 v1.0 介面

| v1.0 指令 | v2.0 行為 | 是否相容 |
|---|---|---|
| `add` | 行為不變 | ✅ 完全相容 |
| `list --type` | 行為不變，新增篩選與排序參數 | ✅ 完全相容 |
| `update` | 行為不變 | ✅ 完全相容 |
| `delete --id` | 行為不變 | ✅ 完全相容 |

**設計策略**

- 所有 v1.0 CLI 參數名稱與行為完全保留
- v2.0 僅新增參數（如 list 的 order / sort）
- 考量到 v1.0 的舊資料可能沒有 category 欄位，系統會自動將空值或 "-" 歸類為 uncategorized，使用者在查詢特定分類列表時較易查詢。

### 破壞性變更（Breaking Changes）
v2.0 無 Breaking Changes。所有 v1.0 的指令與參數皆完全保留。

### 遷移策略（Migration Strategy）
v2.0 本次升級未更換底層資料庫，依然使用 JSON 儲存，且資料結構兼容，因此無須額外的資料遷移腳本。