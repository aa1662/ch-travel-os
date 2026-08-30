# 🗺️ CH Travel OS × Snaplog 統一門戶整合策略與決策紀錄 (Portal Integration Strategy)

> **建立日期**：2026 年 8 月 30 日  
> **文件定位**：記錄 CH Travel OS 與 Snaplog（Blogger 數位典藏）之整合管理決策、生命週期演進規範與託管發布策略，作為下一階段實施與長期維護的 SSoT 依據。

---

## 一、 背景與原始資產現況 (Assets Inventory)

| 站點與資產 | 目前技術與託管 | 內容角色與特徵 | 面臨之整合課題 |
| :--- | :--- | :--- | :--- |
| **1. Blogger 原始網誌**<br>ch-photodiary.blogspot.tw | Google Blogger (2001–2015) | 二十年家庭旅行、孩子成長與早期自由行（英國、義大利、京阪神等）之不可替代歷史起點。 | 版型老舊、缺乏現代排版、未做高畫質 WebP 最佳化與隱私過濾。 |
| **2. Snaplog 數位典藏**<br>snaplog-c77.pages.dev | Astro (SSG) + MDX<br>Cloudflare Pages | 將 20+ 個歷史系列整理為高質感的「旅行影像檔案庫」，具備嚴格圖片衍生管線與隱私篩選。 | 與新寫的旅程分屬不同網址，親友閱讀時需切換站點。 |
| **3. CH Travel OS 2.0**<br>a1662.github.io/ch-travel-os | 純靜態 HTML + Core 引擎<br>GitHub Pages | 2024+ 現代旅程（2026 德國、2026 大阪等），深度融合口述記憶、IG 原聲、Before/After 重返現場、燈箱與 Bento 實戰資訊之「雜誌級專刊」。 | 目前託管於 GitHub Pages，長遠來看圖文資產體積較大。 |

---

## 二、 作者核心需求與邊界約束 (Core Intent & Constraints)

1. **核心定位**：以**「私藏記錄」**與**「分享給少數好友」**為主，重視排版美感、極致讀取速度與純粹的閱讀心流。
2. **整合願景**：
   - **短期**：將分散的歷史典藏與現代旅程收攏至**單一統一門戶**，親友只需記住一個專屬網址。
   - **長期**：以 CH Travel OS 的現代深度專刊標準，逐步將過去 Cloudflare 上的歷史遊記進行深度改寫與升級。
3. **商業與廣告邊界**：
   - 保留未來若讀者反應良好時，掛載輕量廣告（如 Google AdSense）的彈性。
   - **硬性紅線**：必須是不起眼的靜態橫幅，**絕對不影響閱讀、零彈窗（No Pop-up）、零懸浮貼底、零穿頁廣告**。

---

## 三、 Grillme 關鍵決策歷程 (Decision Log)

`mermaid
flowchart TD
    Q1[1. 內容整合架構] -->|決策：選項 A| A1[單一統一門戶 Unified Portal]
    Q2[2. 集中託管平台] -->|決策：選項 A| A2[統一託管於 Cloudflare Pages<br>綁定自訂網域]
    Q3[3. URL 與改寫策略] -->|決策：選項 A| A3[旅程軸原址升級 In-Place Upgrade<br>/year-trip/ 覆蓋無痛升級]
    Q4[4. 廣告放置原則] -->|決策：選項 A| A4[Zero Clutter 模式<br>僅 Bento/文末單一橫幅，正文 0 廣告]

    A1 --> TargetArchitecture[統一現代旅行入口網站]
    A2 --> TargetArchitecture
    A3 --> TargetArchitecture
    A4 --> TargetArchitecture
`

### 決策 1：內容定位 ➔ 單一統一門戶 (Unified Portal)
- **拍板決策**：首頁建立統一品牌門戶，整合「現代深度專刊（2024+）」與「歷年足跡典藏（2001–2015）」。
- **決策理由**：解決網址分散問題，親友一站即可閱讀所有年代的旅程；未來若申請廣告，只需審核單一自訂網域。

### 決策 2：託管平台 ➔ Cloudflare Pages（綁定自訂網域）
- **拍板決策**：全面統一託管於 Cloudflare Pages。
- **決策理由**：
  1. 亞太 Edge CDN 速度快、頻寬無上限壓力。
  2. 解除 GitHub Pages 單一 Repo 1GB 與每月 100GB 頻寬限制。
  3. Google AdSense 審核強制要求頂級自訂網域（如 	ravel.yourdomain.com），Cloudflare 綁定與 DNS 管理最友善。

### 決策 3：改寫管理 ➔ 旅程軸原址升級 (In-Place Upgrade)
- **拍板決策**：全站統一採旅程路徑（如 /<year>-<trip>/）。
- **決策理由**：
  - 舊旅程初期先以 Snaplog 典藏版提供閱讀。
  - 一旦進行口述訪談與照片審計升級為「CH Travel OS 深度專刊」後，直接原址覆蓋，網址與外連永遠不中斷。

### 決策 4：廣告規範 ➔ Zero Clutter 文末單一橫幅模式
- **拍板決策**：正文 0 廣告，僅在文末收束區／Bento 攻略下方放置固定不起眼橫幅。
- **決策理由**：
  - 關閉 AdSense 自動廣告（Auto Ads）、彈窗（Pop-up）、穿頁（Vignette）與手機貼底（Anchor）。
  - 保留純粹的文學閱讀質感，絕不在散文與照片對照之間插入突兀廣告。

---

## 四、 長期「現代專刊」漸進改寫標準流程 (Modernization SOP)

`	ext
┌───────────────────────────────────────────────────────────┐
│                    歷史遊記改寫五步驟                       │
├───────────────────────────────────────────────────────────┤
│ 1. 素材取樣 (Audit)  │ 唯讀解析 Blogger 原文 + Takeout/原相機照片   │
│ 2. 口述訪談 (HITL)   │ 5 分鐘短訪談（重返動機、最深畫面、笑點、自嘲）│
│ 3. 盲寫母稿 (Voice)  │ 依 CH Voice 整理真實故事，不受舊版面限制     │
│ 4. 專刊構建 (Build)  │ 生成 Place 專刊（Before/After 對比 + Bento）│
│ 5. 原址升級 (Deploy) │ 放入該旅程目錄，無縫升級為現代深度專刊      │
└───────────────────────────────────────────────────────────┘
`

---

## 五、 下一階段執行里程碑 (Actionable Roadmap)

### Milestone 1：統一託管與自訂網域建立
- [ ] 決定並購買／設定一個乾淨好記的自訂網域（例如在 Cloudflare 託管）。
- [ ] 設定 Cloudflare Pages 專案，將打包後的現代靜態站點（HTML + WebP 資產）自動化部署。
- [ ] 首頁 Header 建立統一導覽切換（精選專刊 vs 歷年足跡庫）。

### Milestone 2：好友分享與體驗驗收
- [ ] 提供統一網址供好友試讀。
- [ ] 驗證手機與桌面端之排版質感、全螢幕燈箱流暢度與載入效能。

### Milestone 3：歷史篇章改寫與廣告預留
- [ ] 挑選 Pilot 舊旅程（如 2014 奧地利哈修塔特或 2004 英國）率先改寫升級。
- [ ] 待內容篇數穩定後提交 Google AdSense 自訂網域審核。
- [ ] 於 core/ 模板之 Bento 下方預留非侵入式廣告容器標籤。
