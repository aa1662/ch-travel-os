# 📊 User Story & Implementation Plan: CH x Travel GA4 數據串接與 MyDashboard 整合

> **文件狀態**：規劃完成，供 `MyDashboard` 討論串接續執行<br>
> **目標系統**：`MyDashboard` (CH Private Butler, `http://localhost:3000`)<br>
> **關聯專案**：`ch-travel-os` ([chxtravel.com](https://chxtravel.com/))<br>
> **GA4 Property**：`494941251`（帳號 `12830114`，代碼 `G-T54CXJ3E73`）

---

## 1. 前因後果與背景 (Background & Problem Statement)

### 1.1 背景現況
- 《CH x Travel 2.0》（[chxtravel.com](https://chxtravel.com/)）是作者 CH 的個人旅程圖文誌，目前已發布 2026 德國自駕、2026 關西盛夏漫遊、2024 澳洲與 2023 東京出差散步等多條 Journey，全站已正式部署於 Cloudflare Pages 全球 CDN。
- 網站前端（`core/js/app.js`）已埋設 Google Analytics 4（GA4 代碼：`G-T54CXJ3E73`，對應後台資源 ID：`494941251`）。

### 1.2 核心痛點
- **GA4 官方後台 UI 體驗極差**：
  1. 介面充斥電商轉換、購物漏斗、LTV、獲利等與個人遊記完全無關的雜訊指標。
  2. 預設報表層級深且繁瑣，若想知道「讀者看了哪篇文章？讀了多久？有沒有滑到文末？」，需要頻繁切換探索報表（Explorations），載入遲緩且反直覺。
  3. 作者不想、也不需要花時間去登入 GA4 官方後台瀏覽臃腫的圖表。

### 1.3 決策與目標
- **徹底拋棄 GA4 官方網頁端**。
- 透過 **Google Analytics Data API (v1beta)** 直接拉取乾淨的原始統計數據。
- 將數據管道直接整合進作者日常使用的單一工作台 —— **MyDashboard (CH Private Butler)**。
- 由 MyDashboard 呈現專為「深度遊記、高畫質相簿與個人寫作」量身打造的專屬閱讀數據卡片。

---

## 2. 使用者故事 (User Story)

```gherkin
Feature: CH x Travel 讀者閱讀數據自動整合至 MyDashboard

  As a 旅程圖文誌《CH x Travel》的創作者與生活管理者
  I want 在自己的 MyDashboard（深度旅遊模組或 DBX 數據中心）一鍵或定時自動同步 chxtravel.com 的 GA4 數據
  So that 我完全不需要打開繁瑣的 GA4 官方後台，就能直接掌握遊記篇章熱度、讀者完讀率、大圖點擊與來源場景，作為未來文章策展、篇幅調整與排版設計的依據。
```

---

## 3. 專為圖文誌設計的 5 大核心分析維度 (Editorial Dimensions)

不同於電商或一般產品，個人遊記關注的是**共鳴、沉浸與視覺體驗**，以下是為此定義的 5 大數據指標：

| 維度名稱 | 核心業務問題 | GA4 指標 (Metrics) | GA4 維度 (Dimensions) |
| :--- | :--- | :--- | :--- |
| **1. 篇章熱度排行 (Content Resonance)** | 哪篇文章最受歡迎？是東京散步、德國自駕還是關西古寺？ | `screenPageViews`<br>`activeUsers`<br>`sessions` | `pagePath`<br>`pageTitle` |
| **2. 閱讀深度與完讀率 (Reading Depth)** | 讀者是真的有讀完，還是秒跳出？開頭是否太長導致流失？ | `userEngagementDuration`<br>`averageSessionDuration`<br>`scrolledUsers` (90% 捲動) | `pagePath` |
| **3. 視覺與元件互動 (Interactions)** | 讀者會點開 GLightbox 看高畫質 WebP 大圖嗎？出差隨拍影片有被播放嗎？ | `eventCount`<br>(自訂事件：`gallery_open`, `video_play`, `share_click`) | `eventName`<br>`pagePath` |
| **4. 讀者來源途徑 (Traffic Sources)** | 流量主要是 Instagram、朋友私聊、搜尋引擎還是直接輸入？ | `sessions`<br>`activeUsers` | `sessionSourceMedium`<br>`pageReferrer` |
| **5. 閱讀裝置環境 (Context & Devices)** | 讀者多用手機還是桌機看？（決定文章優先做手機單欄或桌機多欄） | `sessions`<br>`activeUsers` | `deviceCategory`<br>`operatingSystem`<br>`country` |

---

## 4. MyDashboard 端實作架構規劃 (Technical Architecture)

### 4.1 認證機制 (Authentication)
1. **Google Cloud Service Account (服務帳號)**：
   - 在 Google Cloud Console 啟用 `Google Analytics Data API`。
   - 建立專屬服務帳號（例：`ch-dashboard-reader@ch-travel-os.iam.gserviceaccount.com`），下載 JSON 金鑰檔。
   - 將金鑰存放在 `MyDashboard/data/credentials/ga4-service-account.json`（已加入 `.gitignore`）。
2. **GA4 權限設定**：
   - 進入 GA4 資源 `494941251` ➔ **資源存取管理** ➔ 新增該服務帳號 Email，指派 **「檢視者 (Viewer)」** 權限。

### 4.2 後端同步腳本 (Data Pipeline)
在 `MyDashboard` 新增專用腳本與 API 路由：
- **同步腳本**：`MyDashboard/scripts/fetch_ch_travel_analytics.py`（或使用 Node.js `@google-analytics/data` 套件）。
- **呼叫範例**：
  ```python
  from google.analytics.data_v1beta import BetaAnalyticsDataClient
  from google.analytics.data_v1beta.types import (
      DateRange, Dimension, Metric, RunReportRequest
  )

  # 查詢近 30 天遊記熱門篇章
  request = RunReportRequest(
      property=f"properties/494941251",
      dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
      metrics=[
          Metric(name="screenPageViews"),
          Metric(name="activeUsers"),
          Metric(name="userEngagementDuration")
      ],
      date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
  )
  ```
- **本機快取與持久化**：
  - 將拉取回來的彙整數據存於 `MyDashboard/data/ch_travel_analytics.sqlite` 或 `ch_travel_analytics.json`。
  - 避免前端每次刷新都打 GA4 API，提升反應速度且不超出配額限制。
- **後端端點 (Express API in `server.js`)**：
  - `GET /api/travel/analytics/summary`：近 30 天總覽、裝置佔比、流量來源。
  - `GET /api/travel/analytics/articles`：所有篇章之訪問量、平均停留時長與完讀估計。
  - `POST /api/travel/analytics/sync`：強制立即從 GA4 抓取最新數據。

### 4.3 前端介面呈現 (UI / Frontend in MyDashboard)
融入 MyDashboard 的雙風格主題（macOS 毛玻璃 / Notion 工作台），於 **Travel (深度旅遊)** 模組新增「**📖 圖文誌數據 (Blog Pulse)**」卡片群：
1. **頂部 KPI 摘要卡 (Bento Cards)**：
   - 近 30 天訪客總數 (Unique Visitors)
   - 總頁面瀏覽量 (Pageviews)
   - 平均閱讀沉浸時長 (Avg. Engagement Time)
   - 燈箱大圖放大總次數 (Photo Interactions)
2. **熱門遊記排行榜 (Top Story Leaderboard)**：
   - 依文章列出：縮圖、文章標題、瀏覽數、平均停留時間、手機比例。
3. **裝置佔比與讀者來源 (Context Breakdown)**：
   - 手機 vs 桌機佔比（簡潔雙色條狀進度條）。
   - 來源分佈（Instagram / Direct / Google Search 佔比圓餅或清單）。

---

## 5. 實作驗收條件 (Definition of Done)

- [ ] **GCP 與 GA4 授權**：服務帳號已取得 Property `494941251` 檢視權限，金鑰安全存放。
- [ ] **資料清洗**：排除 `localhost` 本機測試流量、剔除無效的 `404` 或未定義路由。
- [ ] **一鍵同步功能**：在 MyDashboard 能透過介面按鈕或背景工作執行同步，並正確更新本地 SQLite / JSON。
- [ ] **介面零負擔**：開啟 MyDashboard 時能在 3 秒內看到整理好的 5 大維度，完全不必再前往 GA4 官方網站。

---

## 6. 給 MyDashboard 討論串的執行建議步驟

當您切換到 `MyDashboard` 專案時，可以直接將此文件提供給對應的 AI 討論串，執行步驟如下：
1. **Step 1**：在 MyDashboard 安裝依賴（Node.js 端安裝 `@google-analytics/data`，或 Python 端安裝 `google-analytics-data`）。
2. **Step 2**：配置 Service Account 金鑰與 GA4 Property ID `494941251`。
3. **Step 3**：實作 `fetch_analytics` 服務與 SQLite 快取表。
4. **Step 4**：在 `server.js` 掛載 `/api/travel/analytics` 路由。
5. **Step 5**：在前端 Travel 模組加入「CH x Travel 讀者洞察」Bento 卡片與樣式適配。
