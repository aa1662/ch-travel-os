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

---

## 2. Cloudflare Dashboard 建立步驟

1. 登入 Cloudflare Dashboard ➔ 進入 **Compute (Workers & Pages)** ➔ **Pages**。
2. 點擊 **Connect to Git**（或透過 Direct Upload / Wrangler）。
3. 選擇 GitHub Repository：`aa1662/ch-travel-os`。
4. 設定 **Build settings**：
   - **Framework preset**：`None`
   - **Build command**：*(空)*
   - **Build output directory**：`docs`
5. 點擊 **Save and Deploy** 即可於 15 秒內完成全球 CDN 部署。

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
