# Codex with ChatGPT 網誌協作流程

## 定位

本 workspace 僅用於 `CH Travel OS` 旅遊網誌。ChatGPT 負責需求理解、文章企劃、資料研究、內容結構、編輯建議與實際 diff review；Codex 負責讀寫檔案、處理圖片、執行 build/validator、修正錯誤與 Git 操作。

ChatGPT 經由 C2C 只能唯讀存取本 workspace。`masters/`、Takeout、暫存、備份及工具狀態由 `.c2cignore` 封鎖。

## 執行與發布界線

- C2C bridge 只供 ChatGPT 唯讀讀取、規劃與 Review，不是部署或發布工具。
- ChatGPT 不執行 shell、寫檔、Git、build、push、deploy 或 Cloudflare Pages 操作。
- Codex負責本機修改、驗證與 Git；即使 ChatGPT 的 PLAN 建議發布，Codex也不得把該建議視為發布授權。
- `commit`、`push`、Cloudflare Pages `deploy` 與正式發布必須依當前明確範圍分別取得使用者授權。
- C2C 使用的 `cloudflared` 固定網址只服務唯讀 bridge，不得取代、修改或部署正式網誌 `chxtravel.com`。

## 適合使用的情境

- 規劃新旅程專刊或系列架構。
- 根據現有文章、研究與照片 manifest 設計網誌敘事。
- Review Codex 實際修改的 HTML、文稿、設定與 Git diff。
- 分析 validator、build 或瀏覽器驗證結果，提出下一輪修正計畫。

不使用 C2C 讀取原始相機照片、私人 Takeout、帳號資訊、憑證或其他 Charlotte AI OS 專案。

## 建議叫用方式

```text
c2c: 規劃這篇旅遊網誌，先讀取 CH Travel OS 的相關規格與現有內容，提出可驗收的 PLAN；由 Codex 執行後，再由 ChatGPT review 實際 git diff 與驗證結果。
```

文章製作仍須遵守根目錄 `AGENTS.md`、`EDITORIAL_STYLE_GUIDE.md` 與 `TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md`。內容、照片選擇、隱私與公開判斷由使用者進行人工 UAT；檔案、hash、build、dead link 與 asset 驗證由 Codex 自動完成。

## 首次驗證

連線完成後，先要求 ChatGPT 使用 `Codex with ChatGPT · CH Travel OS` connector 讀取 `tests/c2c-test.md`，並回覆：

1. 標題
2. `purpose`
3. `version`

三項完全相符後，才進行低風險 Markdown diff review。第一輪不修改網誌文章、不處理圖片、不發布。
