# CH x Travel 雲端回饋

獨立 Worker + D1，文章由既有 Pages 靜態站提供。同來源 `/api/feedback/*` 提供匿名點讚與私密收件；不公開點讚總數、留言、作者筆記或管理頁。

## 資料與存取

- `trips/*/blog-migration.json` 是文章資格／ID／標題唯一來源。執行 `python tools/build_feedback_catalog.py` 更新生成的 `articles.json`；不得手改 catalog。
- D1 是正式站回饋唯一來源；本機 SQLite 是獨立測試資料，不複製／合併／回灌。
- `/internal/author/*` 必須有 Worker `ADMIN_SECRET`。作者只在本機管理頁登入，由 server 驗證本機 session 後代理雲端請求；secret 不傳入瀏覽器、不進 Git。
- 私人 `.local_data/cloud_feedback.json` 包含 `url`（Worker HTTPS endpoint）、`admin_secret`。`CH_FEEDBACK_CLOUD_CONFIG` 可指定隔離設定。首次設定或輪替透過 Wrangler secret stdin，不把值放在命令列或文件。
- `RATE_SECRET` 用於每日雜湊來源 IP 的限流 key；不保存原始 IP、user-agent，也不記錄留言 body。匿名 client ID 留在讀者瀏覽器；清除瀏覽器資料會失去本人按讚狀態，不宣稱能識別實際人數。
- 留言暱稱選填 40 字、內容 1000 字；僅作者看到，沒有 Email 通知、公開回覆或讀者身分驗證。作者筆記是私人的處理紀錄。

## 驗證與發布

1. 產生 catalog、跑 Python 與 client tests、全站 validator、diff check。
2. `wrangler d1 migrations apply DB --local --config workers/reader-feedback/wrangler.jsonc`；於 `.dev.vars` 使用隔離隨機 secret（Git 忽略）。
3. `wrangler dev --config workers/reader-feedback/wrangler.jsonc --ip 127.0.0.1 --port 8093`。
4. `python tools/tests/cloud_feedback_http_check.py --config <ignored-test-config.json>`，config 含 localhost `url` 與測試 `admin_secret`。此腳本拒絕正式 URL，會寫入合成留言，只能用隔離 D1。
5. 授權後新資料庫套用 remote migration、設定 Worker secrets、從精確 commit 的乾淨 worktree 執行 `wrangler deploy --config workers/reader-feedback/wrangler.jsonc`。既有 DB 不可重建；新增 migration 應先 review。
6. 核對部署版本、兩個正式網域同來源 API、公開作者 API 401、本機 cloud 收件匣、重送冪等與 409，回報實際端到端結果。不得只看 CLI 成功。

## 維護與回復

API 全部 no-store，無寬鬆 CORS；公開 POST 限兩個正式 Origin。client 與每日雜湊來源 IP 雙重分鐘限流，過期計數可清理。SQL 參數化，筆記更新以 version CAS 防覆寫。

故障時撤除本 Worker 的 `/api/feedback/*` routes 或回到相容版本；文章會在 API 不可用時隱藏互動。保留 D1，不刪庫、不拿本機資料覆蓋；既有同來源靜態文章不受影響。備份／資料保留／進階防垃圾訊息可另行規劃，不以本版本的限流宣稱完整防機器人。
