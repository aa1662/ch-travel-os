# 讀者點讚與私密留言交接

## 最新任務：文章回饋總覽（2026-10-25）

狀態：`LOCAL_READY_FOR_UAT`。作者要求補上後台每篇點讚統計；本輪本機完成，不 commit、push 或部署。

- `core/author-feedback.html`：新增可收合的緊湊文章總覽表，顯示文章、有效讚數、留言、未讀；依旅程篩選，依讚數／留言／未讀降冪或名稱排序，穩定名稱與 ID tie-break；含零回饋文章。
- 沿用既有受保護 `/api/author/summary` 與 likes_count，無新 API、DB schema 或資料 migration，不提供個人身分／點讚事件流水帳。
- 上方總覽依自己的旅程選擇統計，不受下方留言關鍵字／處理狀態篩選影響。按文章進入全部該篇留言，清除舊搜尋／未讀／狀態限制，並保護未儲存筆記。
- API 資料未完成／失敗時隱藏統計表並提示重試，不把錯誤當成 0；遞增 request ID 防舊 summary 覆蓋新資料，登出清除資料。標記已讀後重載 summary，刷新取得最新點讚。
- `tools/tests/inbox_preview_server.py`：只為隔離 synthetic DB 加入德國 7、日本 3 筆 likes；保留原 65 則合成留言。
- `tools/tests/test_server_feedback_routes.py`：增加真實 HTTP regression，驗證跨篇計數、重試不多算、取消讚、零回饋、未授權 401 及已讀更新不改 likes／留言總數。
- 26 項 Python tests OK；git diff --check 通過；全站 validator（3983 圖片、83 HTML、5 JS）通過，正式文章與資產本輪不重建。
- 真實瀏覽器（8091）：總計 10 讚／65 留言；旅程日本顯示 3 讚／25 留言；文章名稱排序與讚數排序正確；點文章載入該篇 all 狀態留言；標記已讀後未讀 25→24 即時同步；草稿切換提示、留在此頁及放棄後切換均正常；停止服務後顯示載入失敗不顯示假零，重啟再刷新恢復。
- 桌機與 390×844 手機畫面通過；只有合成資料截圖，位於 output/article-feedback-overview/desktop.png、mobile.png。未對真實私人留言截圖。
- 日常 DB likes/messages 全欄位 fingerprint 與本輪起始相同；8080 作者頁 HTTP200／no-store，從磁碟即時讀取新版 HTML，不需修改後端 process。管理頁不在 docs/。
- 本機入口 http://127.0.0.1:8080/core/author-feedback.html。新版作者 UAT 尚未執行，集中修正 1 輪；既有收件匣前輪 UAT 已完成。Cloudflare 互動 backend 仍未接通。

---

## 歷史任務：全站文章本機擴充（2026-10-24）

狀態：`LOCAL_READY_FOR_UAT`（2026-10-25）。本機擴充與 Astra review／整合驗證完成。作者已確認收件匣 UAT 完成，授權 GPT-6.1 實作、Astra 整合與 review；本輪只做本機，不 commit、push、deploy 或 publish。

### 本輪完成與 Astra review

- GPT-6.1 已完成主要實作，最後遇額度限制；作者明確要求繼續，由 Astra 完成修正、獨立驗證與交接。不是僅依子代理口頭回報驗收。
- 五個 `trips/<journey>/blog-migration.json` 的 entries 開啟 feedback；與 baseline 比較，除該欄位外設定完全一致。31 篇公開文章輸出各只有一組正確 article ID 的互動區。
- `tools/feedback_eligibility.py`：共用 strict boolean、非 draft、合法穩定 ID 與 canonical public blog output 契約；`tools/feedback_service.py` 與 `tools/build_trip_html.py` 共用。輸出實際存在於 rollout 驗證確認，避免初次 build 須先有衍生檔的循環依賴。
- `core/js/app.js` 與 `docs/core/js/app.js`：確認資格及服務後才啟用、驗證回應 article ID、10 秒 timeout、5xx／斷線停用並可重試，失敗保留輸入與 submission ID。400／429 保持原有錯誤提示。
- Builder：預設 disabled 按鈕與重試入口，啟用文章 CSS／JS 使用 `20261024-feedback` cache version。指定 --entry 構建，未重建 Journey hub。related teaser 空行整理僅為避免產生 trailing whitespace。
- 新增 `tools/tests/test_feedback_rollout.py`、`test_feedback_client.cjs`；更新既有 service fixture 與 `inbox_preview_server.py` 的明確 dest，以符合共同資格。
- Review 集中修正：① AU reading_units／entries 同 ID 誤放開關，已改為 entries 並驗證 config 其餘相同；② 瀏覽器舊 JS cache 導致永久 disabled，已加版本號且實際重載確認；③ 移除為保持空白而讀取既有 docs header 的實作，維持 source/config → docs 的單向構建。允許 HTML 純空白與資源 query 差異，不為此引入衍生資料依賴。

### 最終驗證（以本節取代中途報告）

- `python -m unittest discover -s tools/tests`：23 tests OK。測試啟動環境 DB／secret 使用隔離路徑，未對日常資料寫入測試。
- `node --test tools/tests/test_feedback_client.cjs`：6 tests OK，含錯誤 article ID、timeout、503、重試保留稿件及避免重複送出。
- 真實隔離 HTTP 對全部 31 篇執行 status、like／重試、message／重試，得到 31 筆而非 62 筆留言；未授權管理 401、未知文章拒絕及持久化通過。
- Astra 獨立內容比對：31 篇正確且唯一的回饋區；扣除 feedback、CSS／JS query 與 HTML 空白後內容相同；其他公開檔案 hash 全部不變。再 build 全部 31 篇，輸出逐檔 byte-identical。
- `python tools/validate_images.py`：3983 圖片、83 HTML、4 JS，通過。`git diff --check` 通過（既有 LF/CRLF 警告不影響結果）。
- 瀏覽器實際操作（8092 隔離 DB）：東京篇點讚；送留言時注入 HTTP503，輸入保留且按鈕停用；服務恢復後重試成功；作者收件匣只有一則且文章歸屬正確；筆記儲存，實際重啟 server 後留言與筆記仍存在。
- 桌機表單與 390×844 iframe 真實窄 viewport 檢查通過，表單、送出及底部 dock 可用；不是實體手機驗收。畫面僅合成資料。
- 日常 8080 已重啟，新 process PID 8616（僅當次證據），31 篇 status 與作者入口唯讀 HTTP200。正式 likes/messages 全欄位 fingerprint 與本輪起始相同；不輸出私人原文。
- 證據：`output/reader-feedback-rollout-review/` 的 content-check.json、python-tests.log、validator.log、final-build.log、idempotence.log、mobile.png、inbox-after-restart.png。子代理原中途證據在 `output/reader-feedback-rollout/`，若與此處不同以最終驗證為準。憑證／DB 均忽略且不可提交。
- 本輪作者人工 UAT 0 次；前輪收件匣 UAT 已由作者確認完成。Astra review 修正集中完成 1 輪；未要求作者反覆技術驗收。
- 本機入口：任一上述文章及 `http://127.0.0.1:8080/core/author-feedback.html`。8092 隔離測試服務於驗證完停止，日常 8080 留供作者驗收。
- 尚未 commit、push 或部署；Cloudflare API／儲存／production 作者認證仍未接通。沒有新增公開留言、寄信或回覆功能。

### 範圍與責任

- 31 篇既有文章：2023-tokyo 2、2024-australia 5、2025-2026-beijing 4、2026-germany 16、2026-osaka 4。Hanau 已啟用，新增 30 篇。
- 不包含首頁、Journey hub、About、plan、草稿、2026-Tokyo intake；不修改正文與照片。既有 GA4 文件等 unrelated dirty changes 保留。
- Config 是文章 ID、metadata 與啟用資格唯一來源；SQLite 是點讚、留言及作者處理狀態唯一來源。不得更換既有 ID、重建 DB 或變更 schema。
- 前後端採一致 eligibility；服務未成功確認可用前禁用互動，失敗可重試且保留輸入。無 JS 時也不能顯示可送出的假入口。
- GPT-6.1 修改實作、config、指定文章輸出與 focused tests；Astra 檢查增量變更、更新本文件及 Roadmap、執行整合驗證。
- 精確以文章 --entry build；先保存 baseline，排除 feedback 區塊後核對既有內容，避免 full Journey build 改動 hub。

### 驗收與停止條件

1. 每篇只有一組回饋區、ID 正確，既有正文／照片／導覽保持一致；未納入頁面不新增入口。
2. 隔離真實 HTTP 服務驗證跨系列點讚、取消、私密留言、作者篩選與持久化；不灌入日常 DB。
3. 手機／桌機及服務失效檢查，相關回歸、全站 validator 與 diff check；服務程式更新後重啟日常 8080 並做唯讀健康檢查。
4. 若資格不一致、資料歸屬錯誤、內容意外改動或私人資料外洩，停止 rollout，修正後再驗證；回復僅針對本輪精確變更，不能清空或回灌舊 DB。

雲端 adapter、production 認證及公開網站收件尚未接通；本機完成不等於 Cloudflare 可收件。

---

## 歷史任務：作者收件匣改版（2026-10-24）

狀態：`READY_FOR_REVIEW`。起始 HEAD `01ec37f5b717a95a3b62e3fbf06dcbfdf747312a`。本機收件匣實作與整合驗證完成，等待獨立 Codex review 與作者新版 UAT；尚未 commit、push 或部署。

### 本輪實作結果（2026-10-24）

- `core/author-feedback.html`：改為緊湊收件匣，桌機雙欄、手機列表／詳情切換；狀態、文章、旅程、未讀與搜尋組合篩選；後端分頁；筆記儲存、離開前儲存／放棄／留在此頁、複製問題 fallback、版本衝突核對及草稿保留。
- `tools/feedback_service.py`：schema 1 增量欄位 status／author_note／version；一致性備份；穩定排序分頁及共同條件計數；版本檢查更新；SQLite 連線明確關閉。首次建立憑證改為隨機值，讀取失敗不回退固定密碼；現有作者憑證未更動，不能把本機方案視為 production 認證。
- `tools/server.py`：增加受保護 update-message API、查詢參數；作者路由限 loopback、可信 Host／Origin；私人 API 不輸出查詢日誌；作者 HTML no-store。加入 CH_FEEDBACK_DB／SECRET／TRIPS 環境變數，供隔離資料驗證。
- `tools/tests/test_feedback_inbox.py`：新增 65 則跨兩旅程合成留言之分頁、篩選、計數、非法欄位、未授權、衝突、重啟持久化及舊 schema 重跑測試。
- `tools/tests/test_feedback_service.py`、`test_server_feedback_routes.py`：測試改用隔離 DB 自己生成的憑證；增加真實 HTTP 更新、409 衝突、401 未授權、Host 拒絕與查詢驗證，各 case 使用乾淨的 disposable DB。
- `tools/tests/inbox_preview_server.py`：僅供本機視覺驗收的合成資料 server，監聽 8091、資料在受忽略 `.local_data/inbox-preview/`，不改正式文章資格。
- `tools/tests/run_live_e2e_verification.py`：移除硬編碼舊憑證及預設連到日常 8080；必須明確提供 disposable test URL、標記與測試憑證才允許執行。該舊腳本本輪未執行，避免污染作者資料。
- `TRAVEL_PORTAL_ROADMAP.md` 與本交接：更新完成狀態與證據。其餘第一階段既有 dirty changes、GA4 文件與 Tokyo intake 未修改；本輪沒有重新 build 公開文章或同步公開 assets。

### 驗證證據與重現

- `python -m unittest discover -s tools/tests`：20 tests，OK。曾發現 Windows DB handle 未關閉及 HTTP 測試共享資料污染，已修正後完整重跑通過。
- `python tools/validate_images.py`：3983 圖片、83 HTML、4 JS，通過；`git diff --check` 通過，僅既有 LF/CRLF 提示。
- 私人一致性備份：`.local_data/inbox-migration-audit/before.db`；副本 `trial.db` migration 重跑兩次通過。日常 DB 升級後，兩則留言及兩筆 likes 的所有既有欄位與備份逐列相同；schema=1。備份與測試憑證不得公開或加入 Git。
- 8080 已重啟至本輪程式，僅監聽 127.0.0.1；`/core/author-feedback.html` HTTP 200。
- 真實瀏覽器使用 8091 合成資料完成：65 則／4 頁、第二頁、關鍵字縮至單則、筆記未儲存離開提示、保存、處理中、完成、重新開啟、服務重啟後筆記保留。另以 HTTP 模擬第二頁籤更新，瀏覽器收到 409、保留草稿、顯示最新筆記並核對後可再次儲存。
- 桌機 1365×900 與手機 390×844 實際畫面通過，DOM 未水平溢出。合成資料截圖：`output/inbox-desktop.jpg`、`output/inbox-mobile.jpg`。作者真實留言不寫入截圖證據。
- Reviewer 重現：啟動 `python tools/tests/inbox_preview_server.py`，開啟 `http://127.0.0.1:8091/core/author-feedback.html`；僅合成資料用登入值見該腳本。依上述步驟操作；服務可重啟且保留測試筆記。不要執行舊 E2E 腳本對日常資料寫入。
- 作者日常入口：`http://127.0.0.1:8080/core/author-feedback.html`，沿用目前本機憑證。原有留言保留已讀值，處理狀態初始化待處理。
- 新版人工 UAT 0 次、changes requested 0 輪；第一階段作者曾確認基本可用。GPT 6.1 frontend 子代理遭額度中斷，主 agent 已接手檢查與完成整合；不得視為獨立 review 已通過。

### 尚未接通及 reviewer 重點

- 本次只有私人筆記，沒有對讀者寄送回覆、公開問答、Email 或 Cloudflare adapter。
- 本機既有憑證保留相容性；雲端上線仍需另做身分驗證及安全 review。
- 衝突恢復目前依文章分頁找出原留言，未提供獨立單則 GET；大量留言時可另優化，不影響一般分頁查詢。
- 新留言進來可能讓 offset 分頁位移，重新整理取得最新結果；不是固定快照。
- 不得直接還原舊 DB 而覆蓋本輪以後的新留言。先停寫、保存目前一致性備份，再依 L2 計畫回復相容程式。

### 本輪 L2 資料升級計畫

- SSoT：私人 SQLite 擁有留言、點讚、已讀、處理狀態與筆記；Journey config 擁有文章 metadata。起始 dirty tree 包含整套第一階段試作、Roadmap、GA4 規劃及 Tokyo intake，均保留。
- 影響：feedback service、作者 HTTP 路由、作者管理頁及相關測試。前台公開文章及公開資產不重建。
- 不變條件：既有 ID、原文、暱稱、去重值、已讀及所有 likes 欄位逐列一致；新欄位預設 pending、空筆記、version=0；schema 升至 1。
- 方法：以 SQLite backup API 保存一致性私人備份；先在副本 dry-run 並重跑，驗證不變條件，再讓本機服務套用增量交易 migration。新舊程式均可讀既有欄位。
- 衝突：作者更新使用 version compare-and-swap；衝突回 409，前端保留未儲存文字。
- 停止：任何資料不一致、migration 失敗或未知較新 schema 都停止。回復先停止寫入、保存目前一致性備份，再回復相容程式；不可直接用舊備份覆蓋新留言。
- before/after：全量取回改為後端每頁 20 筆；只有已讀改為已讀與三種處理狀態獨立；單則儲存、重啟與跨頁篩選須真實驗證。

產品規格唯一來源：`TRAVEL_PORTAL_ROADMAP.md` 第 10.6 節。實作結果直接更新本段，保留後方歷史紀錄，不另建交接文件。原報告的內嵌認證資訊已移除，後續交接不得記錄任何可用憑證。

### 給 GPT 6.1 的執行 Prompt

```text
請在 C:\Data\charlotte-ai-os-dev\ch-travel-os 接手讀者回饋管理頁改版。
讀取 AGENTS.md、TRAVEL_PORTAL_ROADMAP.md 第 10 節，特別是 10.6，
以及本交接文件。先檢查 git status -sb、HEAD 與目前實作。

目標：把 core/author-feedback.html 改為可管理多則留言的收件匣，
完成搜尋、旅程／文章篩選、後端分頁、獨立已讀／處理狀態、
私有作者筆記、複製問題及正確文章入口。產品細節遵照 10.6，
不要自行省略真實持久化、作者權限或未儲存內容保護。

先記錄現有 dirty changes，既有試作是本輪基礎，不可 checkout、
reset、stash 或覆寫其他人的工作。需要修改同一檔案時只增量調整。
不要只改畫面；前後端狀態、查詢計數與權限必須一致。

這次涉及 SQLite schema 擴充，先按 L2 記錄 invariants、migration、
相容性、停止條件及回復方式於本文件。先做私人一致性備份，
在副本驗證 migration 可重跑且資料無損，再整合本機服務。
沿用文章與留言 ID，不能清空資料庫，也不能將已讀視為已完成。

以隔離測試資料驗證大量留言及跨文章篩選；真實作者資料不得
輸出到 log、測試報告、公開 docs/、Git 或外部 AI。
不要沿用報告中的測試憑證；審查目前管理存取邊界。
遇權限漏洞先記錄並處理必要的本機保護，不宣稱 production 安全已完成。

本輪不做公開問答、寄信、Email 收集、回覆查詢、自動 AI、
全站啟用或 Cloudflare 資源。不要 commit、push、deploy 或 publish。
不修改旅遊正文、照片；不將管理頁放入 docs/。

完成 10.6 的三個交付步驟及端到端驗收，修改服務後驗證實際
運行的 process／port；跑相關測試、全站 validator、git diff --check。
不要把 mock、HTTP 測試或舊報告當作手機／桌機視覺驗證。

在本文件更新 READY_FOR_REVIEW 或 BLOCKED、起始 HEAD、
本輪精確修改範圍、migration 證據、測試結果、本機入口、限制，
以及讓 Codex 可重現的流程。證據沿用 output/ 慣例，僅用合成資料。
不要另建根目錄 plan 或 handoff，也不要自行啟動 C2C。
最後交由 Codex review 實際 diff 與運行結果，再由作者驗收使用體驗。
```

---

## 歷史紀錄：第 1 階段單篇本機試作

- **狀態**：`READY_FOR_REVIEW`
- **記錄日期**：2026-10-24
- **需求來源**：`TRAVEL_PORTAL_ROADMAP.md` 第 10 節（唯一需求規劃）
- **架構準則**：遵守 `AGENTS.md`、`CLOUDFLARE_PAGES_DEPLOYMENT.md` 與全域規則

---

## 1. 任務範圍與執行邊界

- **本次試作範圍**：僅在 `/2026-germany/blog/hanau-frankfurt.html` 啟用讀者回饋。
- **核心實作成果**：
  1. **免登入點讚**：支援點讚與取消，點讚狀態以後端確認為準，公開頁不顯示讚數，無裝置指紋。
  2. **獨立私密留言**：留言入口獨立於點讚（不必先按讚）；暱稱選填（最多 40 字）、不收 Email、不提供附件、內容 1–1000 字（拒絕純空白）。
  3. **明確隱私提示**：介面清楚提示「留言只給 CH 看，不會公開」；送出後顯示「已收到，謝謝你」，不承諾回覆。
  4. **本機持久化儲存**：使用本機 SQLite 資料庫，伺服器重啟後資料與狀態完全保留。
  5. **受保護的作者管理入口**：作者透過專屬管理入口登入後查看文章讚數、私密留言及標記已讀；一般訪客與公開 JS 無法存取私密留言或管理 API。
  6. **失敗保留輸入**：網路或伺服器錯誤時，讀者輸入內容完整保留於當頁，後端成功才清空並顯示成功卡片。
- **邊界把關**：
  - 不建立任何雲端資源、不連正式資料庫。
  - 不 commit、不 push、不 deploy、不 publish。
  - 本機資料庫與密鑰均受 `.gitignore` 隔離，絕不進 Git 或公開發布目錄 `docs/`。

---

## 2. 版本狀態與檔案修改清單

### 2.1 開始時 Git 狀態
- **HEAD Commit**：`01ec37f` (`docs: refine photo-led travel writing workflow`)
- **既有 Dirty Changes**（任務開始前即存在，本次作業完全未更動正文）：
  - `M TRAVEL_PORTAL_ROADMAP.md`
  - `?? GA4_DASHBOARD_INTEGRATION_PLAN.md`
  - `?? trips/2026-Tokyo/`

### 2.2 本次實際新增與修改檔案清單

| 檔案路徑 | 類型 | 說明與修改區段 |
| --- | --- | --- |
| `tools/feedback_service.py` | 新增 | 後端回饋服務模組：SQLite 持久化、文章白名單、點讚/留言冪等防重試、基礎限流、作者 Passcode 驗證與 Session Token 管理。 |
| `tools/tests/test_feedback_service.py` | 新增 | `FeedbackService` 單元測試（白名單、點讚冪等、留言驗證、防重複收件、作者認證、重啟持久化、XSS 安全）。 |
| `tools/tests/test_server_feedback_routes.py` | 新增 | 本機 HTTP API 整合測試（點讚、留言、401 攔截、密碼登入、已讀標記）。 |
| `tools/tests/run_live_e2e_verification.py` | 新增 | 本機端到端 15 項真實場景自動化驗證腳本，輸出至 `output/reader_feedback_e2e.log`。 |
| `core/author-feedback.html` | 新增 | 本機專用受保護作者管理入口（純前端，密碼登入、總覽統計、留言列表安全純文字渲染、已讀標記）。 |
| `trips/2026-germany/blog-migration.json` | 修改 | 於 `day-09` (`hanau-frankfurt`) 加入 `"feedback": true` 白名單標記（第 130 行）。 |
| `tools/build_trip_html.py` | 修改 | 加入 `render_reader_feedback()` 渲染函式（第 429 行）；在構建文章時若 `feedback: true`，自動注入於正文後與導覽按鈕前（第 768 行）。 |
| `tools/server.py` | 修改 | 引入 `FeedbackService`（第 51 行）；新增作者入口路由、讀者狀態 API、作者總覽/留言 GET 路由（第 106–160 行）；新增點讚、留言、登入、標記已讀 POST 路由（第 497–590 行）；新增 `extract_bearer_token` 輔助方法（第 909 行）。 |
| `tools/validate_images.py` | 修改 | 新增發布目錄防呆檢查：禁止 `docs/core/author-feedback.html` 進入發布目錄（第 129 行）。 |
| `.gitignore` | 修改 | 加入 `.local_data/` 儲存目錄及 `docs/core/author-feedback.html` 防護（第 17、28 行）。 |
| `core/css/style.css` | 修改 | 於檔案末尾新增 `.reader-feedback-section` 核心卡片、按鈕、輸入框與微動畫樣式（第 2342–2649 行）。 |
| `core/js/app.js` | 修改 | 於 DOMContentLoaded 加入 `initReaderFeedback()` 呼叫（第 42 行）；於檔案末尾實作讀者點讚狀態查詢、按鈕切換、留言展開與非同步送出防重試引擎（第 333–573 行）。 |
| `docs/2026-germany/blog/hanau-frankfurt.html` | 編譯產物 | 由 `build_trip_html.py` 自動編譯產出之公開 HTML，僅注入讀者回饋區塊，未修改文章正文與照片。 |
| `docs/core/css/style.css` | 構建同步 | 由 `sync_public_core_assets()` 同步。 |
| `docs/core/js/app.js` | 構建同步 | 由 `sync_public_core_assets()` 同步。 |

---

## 3. 架構設計與安全/隱私契約

1. **固定文章 ID (Stable Article ID)**：
   - 格式為 `<trip_slug>:<entry_id>`，本次為 `2026-germany:day-09`。
   - 綁定於旅程原始設定，不隨標題文字或靜態 URL 改動而變動。
2. **前後端共用資格與輸入限制 (Eligibility SSoT)**：
   - 僅 `blog-migration.json` 設定 `"feedback": true` 之文章才開放互動。
   - 後端 API 同樣驗證文章 ID，遇未知或未開放文章一律回傳 HTTP 400 (`未知或未開放回饋的文章`)。
   - 暱稱最多 40 字，留言限制 1–1000 字，純空白不得送出。
3. **資料 Owner 與本機持久化**：
   - 資料庫位置：`.local_data/reader_feedback.db`（SQLite，WAL 模式相容，本機伺服器重啟不遺失）。
   - 點讚表以 `(article_id, client_id)` 為 Primary Key，採用 `ON CONFLICT DO UPDATE` 達成設為喜歡與取消喜歡之冪等操作，重試不累加計數。
   - 留言表設定 `UNIQUE (article_id, client_submission_id)`，客戶端送出重試時不會產生重複紀錄。
4. **管理防護與隱私邊界**：
   - 訪客端 API 僅能查詢讀者本人的點讚狀態，公開 API 與網頁完全不洩漏讚數，亦不提供任何讀取他人留言之端點。
   - 本機作者入口受 Passcode 驗證保護（儲存於 `.local_data/author_secret.json`，交接文件不保存憑證值；保護實效待 code review）。
   - 登入後頒發 24 小時有效之亂數 Session Token；所有作者管理 API 均強制驗證 `Authorization: Bearer <token>`，未授權直接回傳 HTTP 401。
   - 留言內容在後端純文字儲存，前端管理介面一律使用 DOM `textContent` 安全呈現，杜絕 XSS。
   - 伺服器日誌與 GA4 不記錄讀者留言內文，亦不蒐集瀏覽器指紋。

---

## 4. 本機啟動與存取入口

### 4.1 伺服器啟動指令
在專案根目錄執行：
```powershell
python tools/server.py
```
（或透過專案既有之 `start_travel_os.bat` / `tools/launch.ps1` 啟動，服務常駐於 `http://127.0.0.1:8080/`）

### 4.2 本機存取網址
- **讀者文章入口（唯一啟用試作篇章）**：
  `http://127.0.0.1:8080/2026-germany/blog/hanau-frankfurt.html`
- **作者受保護管理入口**：
  `http://127.0.0.1:8080/core/author-feedback.html`
- **對照未啟用文章（驗證無回饋區塊、導覽正常）**：
  `http://127.0.0.1:8080/2026-germany/blog/heidelberg-castle.html`

---

## 5. 驗證記錄與測試結果

### 5.1 自動化測試結果
- **單元與整合測試集**：
  ```powershell
  python -m unittest discover -s tools/tests
  ```
  **結果**：`Ran 16 tests in 2.958s, OK`（包含全站既有測試與本次新增之 9 項單元測試、2 項 HTTP 路由測試）。
- **真實伺服器 15 項 E2E 流程驗證**：
  ```powershell
  python tools/tests/run_live_e2e_verification.py
  ```
  **結果**：15 項端到端場景 100% 通過，證據記錄於 `output/reader_feedback_e2e.log`。
  1. 初始點讚狀態確認（liked=False）
  2. 點讚成功（liked=True）
  3. 重試點讚（冪等確認，liked=True）
  4. 獨立留言送出成功（取得 message_id）
  5. 重試留言防重複收件確認（duplicate_prevented=True）
  6. 拒絕未知文章與純空白留言（回傳 HTTP 400）
  7. 未授權管理請求攔截（回傳 HTTP 401）
  8. 錯誤密碼攔截與正確密碼登入（取得 Bearer Token）
  9. 作者查看統計（讚數=1, 總留言=1, 未讀=1）
  10. 作者讀取留言（暱稱與內容安全呈現）
  11. 標記留言已讀成功
  12. 統計即時更新（未讀=0）
  13. 讀者取消點讚（liked=False）
  14. 統計即時更新（讚數=0）
  15. 未開放文章驗證（Heidelberg 文章無 feedback 區塊）
- **發布安全性與圖片合規檢查**：
  ```powershell
  python tools/validate_images.py
  ```
  **結果**：共掃描 3983 個公開圖片、83 份 HTML、4 份 JS 文件，100% 通過，零 404 死鏈。
- **Git 格式與空白檢查**：
  ```powershell
  git diff --check
  ```
  **結果**：乾淨通過，零空白格式錯誤。

### 5.2 環境已知限制說明
- 在執行瀏覽器自動化子代理人（`browser_subagent`）時，系統底層 Playwright 自動下載依賴時遭遇 Microsoft Azure Edge CDN `404 Not Found` 網路限制，因此視覺自動錄影由本機真實 HTTP E2E 腳本（`tools/tests/run_live_e2e_verification.py`）完整替代驗證，所有請求均實際打在 `http://127.0.0.1:8080` 執行中的伺服器。

---

## 6. Reviewer 可重現之端到端驗證步驟

Reviewer 可依照下列步驟於本機完整重現：

1. **確認伺服器執行**：
   確認 `python tools/server.py` 於背景執行（監聽 `127.0.0.1:8080`）。
2. **讀者端測試**：
   - 開啟 `http://127.0.0.1:8080/2026-germany/blog/hanau-frankfurt.html`。
   - 捲動至文末 Bento 卡片下方，確認出現「喜歡這篇記錄嗎？」區塊。
   - 點擊「喜歡這篇」：按鈕轉為粉紅粉底「❤️ 謝謝你喜歡 (取消)」，下方顯示感謝文案。
   - 重新整理網頁：喜歡狀態依然維持（由 LocalStorage client_id + 後端狀態保持）。
   - 點擊「留幾句話給 CH」：表單展開。
   - 輸入暱稱與文字後點擊「送出私密留言」：按鈕顯示「傳送中...」，成功後顯示「💌 已收到，謝謝你！」。
   - 若刻意清空文字送出：顯示「請輸入想對 CH 說的留言內容」，輸入框保留文字不被重置。
   - 再次點擊喜歡按鈕：取消喜歡，按鈕回到預設狀態。
3. **作者端測試**：
   - 開啟 `http://127.0.0.1:8080/core/author-feedback.html`。
   - 出現密碼登入卡片，輸入錯誤密碼提示錯誤。
   - 使用目前本機作者憑證登入；不將憑證寫入報告或測試輸出。
   - 儀表板顯示 `2026-germany:day-09` 之讚數與留言統計。
   - 留言列表中可見剛剛送出的留言，點擊「✓ 標記為已讀」，標籤變為「已讀」，未讀計數歸零。
4. **對照組與安全檢查**：
   - 開啟 `http://127.0.0.1:8080/2026-germany/blog/heidelberg-castle.html`，文末無回饋區塊，上一篇/下一篇導覽正常。
   - 執行 `git status` 確認 `.local_data/` 未被 stage，且 `docs/` 下無作者管理頁面。

---

## 7. 尚未完成的 Production Adapter、登入與部署工作（後續里程碑規劃）

本試作為「第 1 階段：單篇本機試作」，依 Roadmap 規範，下列項目列入後續授權之第 2 階段工作：
1. **Cloudflare D1 / Workers 生產環境持久化 Adapter**：目前使用本機 SQLite，上線需轉換為 Cloudflare D1 儲存契約。
2. **Cloudflare Access / 生產身分驗證**：取代本機靜態 Passcode，接入生產級作者身分驗證。
3. **多篇推廣與 Config 批次驅動**：目前僅於 `2026-germany:day-09` 啟用，後續將依作者確認擴展至其他 Germany 篇章與其他 Journey。
4. **正式部署與 DNS 綁定**：未經當次發布授權，不執行 wrangler pages deploy 或 git push。
