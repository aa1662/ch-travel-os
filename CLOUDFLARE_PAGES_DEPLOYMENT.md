# ☁️ CH Travel OS 2.0 — Cloudflare Pages 部署指引 (CLOUDFLARE_PAGES_DEPLOYMENT.md)

本文件定義 CH Travel OS 2.0 部署至 Cloudflare Pages 的標準配置。

---

## 1. 部署基本資訊

- **Cloudflare Pages Project**：`ch-travel`
- **Pages Preview Domain**：`https://ch-travel.pages.dev/`
- **正式 Canonical Domain**：`https://chxtravel.com/`
- **架構模式**：純靜態 WebP 衍生物輸出（Zero-Build / Zero-Runtime）
- **發布目錄 (Build Output Directory)**：`docs`
- **構建命令 (Build Command)**：*(留空 / None)*
- **根目錄 (Root Directory)**：*(預設 `/`)*
- **Node.js / Python Runtime**：無須設定（零構建依賴）

### 讀者回饋的獨立雲端服務（2026-10-25）

靜態網站仍使用上述 Pages Direct Upload。31 篇開放回饋的文章另由 `workers/reader-feedback/` 提供 API，Worker `ch-travel-feedback` 綁定同名 D1；靜態 Pages upload 不會部署 Worker。

- 正式網域與 www 的 `/api/feedback/*` 交由 Worker；canonical `/internal/author/*` 另需 Worker secret，不公開作者資料。
- 作者管理頁仍只在本機 `http://127.0.0.1:8080/core/author-feedback.html`，登入後預設「雲端」，可切回獨立本機資料。管理 HTML、SQLite、secret 與東京私人規劃不進發布目錄。
- Worker、D1 migration、catalog 更新與故障回復見 `workers/reader-feedback/README.md`。從目標 commit 的乾淨 worktree 發布 Worker，再核對 live API 與本機 protected bridge；不能只核對 Pages deployment。

---

## 2. 部署方式

Cloudflare Pages 專案 `ch-travel` 目前採用 **Direct Upload (Wrangler)** 模式（Git Provider: No）。

發布前核實實際模式；本文件既有記錄為 Direct Upload，因此 Git push 是 GitHub 保存，不應假設會自動發布或空等 Git integration。已授權發布時，從明確目標 commit 建立乾淨 export／detached worktree，僅上傳該版本的 `docs/`，不可直接部署含無關 dirty changes 的工作目錄。若實際模式已變更，先釐清並更新指引。

以下指令在**已驗證的乾淨 export／worktree 根目錄**執行，且需當次發布授權：
```bash
npx --yes wrangler pages deploy docs --project-name=ch-travel --branch=master
```
> 完成後核對 deployment 與目標版本、live HTTP 200 及本次內容 fingerprint；指令返回成功不代替 live 驗證。不得因文件更新而實際部署。


---

## 3. 自訂網域 (Custom Domain) 綁定

1. 進入該 Pages 專案的 **Custom domains** 分頁。
2. 點擊 **Set up a custom domain**。
3. 輸入正式網域：`chxtravel.com`。
4. 另新增 `www.chxtravel.com` 作為同一個 Pages 專案的 custom domain。
5. 若 Cloudflare 未自動建立 DNS record，於 `chxtravel.com` zone 新增：
   - `CNAME` / `@` / `ch-travel.pages.dev` / Proxied
   - `CNAME` / `www` / `ch-travel.pages.dev` / Proxied
6. 等待 Cloudflare 完成 HTTP validation 與 SSL 憑證核發後，確認 `https://chxtravel.com/` 可正常開啟。

---

## 4. HTTP Headers 與快取策略

本專案已在 `docs/_headers` 配置標準快取規則：
- `/*.webp`：`Cache-Control: public, max-age=31536000, immutable`（WebP 圖片一年長效快取）
- `/*.html`：`Cache-Control: public, max-age=0, must-revalidate`（HTML 即時更新）
- `/core/*`：`Cache-Control: public, max-age=86400`（共用樣式與腳本 24 小時快取）
