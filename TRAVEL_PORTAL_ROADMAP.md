# CH Travel OS 內容與入口網站 Roadmap

> 本文件定義未來內容產品的方向、里程碑與驗收條件。
> 原始 Takeout 貼文與媒體數量必須經由審計腳本重新 audit，不得直接以舊統計作為 SSoT。

## 1. 品牌定位

CH Travel OS 的品牌核心是個人旅行誌，不是即時旅遊資料庫：

> 以重返、移動與家人同行為線索，記錄同一個旅人在不同人生階段重新看見地方的方式。

內容採雙層策略：

- **品牌層（B）**：個人經驗、重返、人物關係、移動過程與旅行後留下的感受。
- **搜尋層（A）**：造訪當時親自使用過的交通、停車、路線、票價與營業資訊，作為讀者找到故事的入口。

若兩者衝突，以品牌層為優先。不得為了增加篇數或搜尋流量，自動把每一日、每則 IG 或每個景點擴寫成文章。

## 2. Source of Truth 與責任

| 資料 | SSoT | Owner | 公開規則 |
| --- | --- | --- | --- |
| 原始照片、Instagram 與 Blogger Takeout | 私人來源庫／`masters/` | 使用者 | 絕不直接發布、不進 Git |
| 旅程邊界、Place、文章命題與公開狀態 | 未來的 `journey-catalog` | 使用者確認、工具維護 | 只發布 `approved` 內容 |
| 口述記憶 | 每次 Journey／Place 訪談稿 | 使用者 | 僅作寫作來源，不預設全文公開 |
| 文章來源 | `trips/` | 使用者內容決策、AI 協作整理 | 通過內容與隱私 UAT 後構建 |
| 共用呈現與構建行為 | `core/`、`tools/` | 專案工具鏈 | 不承載單一旅程內容 |
| 公開衍生物 | `docs/` | Builder | 只含核准文字與公開衍生資產 |

AI 不擁有記憶、公開狀態或文章觀點。AI 可以整理與擬稿，但不得自行把推測升格為事實。

## 3. 內容模型

```text
Journey（一次完整旅程）
└── Place（一篇可獨立閱讀與搜尋的地方作品）
    ├── City（城市）
    ├── Town（小鎮／村落）
    ├── Landscape（自然地景／區域）
    └── Route（自駕／單車／鐵道／健行路線）
```

原則：

- 城市是最常見的 Place，但不是硬性限制。
- Day 是 Journey 的時間脈絡，不是深度文章的強制邊界。
- 一個 Place 可以跨越多日；同一天也可以包含多個 Place。
- 現有 Day Blog 若已完整承載一個 Place，優先重編，不新增重複文章。
- 一個公開主題只保留一個 canonical URL；舊 URL 若遷移，只作轉址或相容入口。

## 3.1 URL 策略：先採 Day + Place Hybrid，不過度設計

目前 2026 Germany 仍是一本完整旅程專刊，因此已完成的正式文章優先維持在 Journey 連載脈絡內，不急著另建純 Place URL。

短期規則：

- 若文章本質仍是某一天的旅程章節，但主題已明確收斂到城市、地點或季節，URL 採 hybrid slug：
  - `docs/germany/blog/day-02-hallstatt-winter.html`
  - `docs/germany/blog/day-13-neuschwanstein-winter.html`
- Hybrid URL 兼顧兩件事：保留 Day 順序，也讓 slug 帶有可搜尋的 Place 關鍵字。
- 原本 `day-xx-blog.html` 若已公開，不立即刪除；是否改名、保留相容頁或更新內部連結，需逐篇 UAT 後決定。
- 不為了 SEO 另外複製一篇內容相近的純 Place 文章，避免 duplicate content 與維護分裂。

長期規則：

- 只有當一篇文章已超出單一旅程日記，成為跨年份、跨旅程或 evergreen 的地方專題時，才建立純 Place URL：
  - `docs/germany/hallstatt-winter-return.html`
  - `docs/germany/neuschwanstein-return.html`
- 純 Place URL 必須有自己的命題、結構與 canonical，不只是 Day 文章換檔名。
- Day URL 可作為 Journey 章節入口；Place URL 則作為搜尋與長期收藏入口。

成本與效益判斷：

- Hybrid URL 是目前最低成本方案：不拆內容模型、不破壞 Journey 導覽，也提升 URL 可讀性與搜尋語意。
- 純 Place URL 成本較高：需要重編開頭、canonical、內部連結與去重策略，等 Pilot UAT 確認後再採用。

## 4. 編輯與探索架構

首頁先讓讀者認識故事，再提供地方與行程入口：

```text
本期主題作品
→ 重返現場
→ 在路上的故事
→ 最近完成的 Place
→ 依地方探索
→ 完整 Journey 與時間表
```

建議主導覽：

- **故事**：編輯精選、重返、人物與心得。
- **地方**：城市、小鎮、地景與路線。
- **旅程**：完整 Journey Hub、日期與時間表。
- **關於**：作者、記錄動機與內容方法。

國家、年份、季節與旅行方式是篩選條件，不是互斥的第一層分類。世界地圖可以作探索工具，但不作首頁主角。

## 5. Canonical User Journeys

### Journey A：從故事進站

1. 讀者從首頁看見一篇重返故事。
2. 進入 Place 文章，先讀個人經驗與照片敘事。
3. 在文末取得造訪當時的實戰筆記。
4. 前往同一 Journey 或同一主題的下一篇。

### Journey B：從搜尋進站

1. 讀者以地名、季節、停車或路線找到 Place。
2. 頁面以清楚的 SEO title 回答搜尋意圖。
3. 可見 H1 與正文仍維持作品感，不退化為關鍵字文章。
4. 讀者可回到 Journey Hub 取得完整行程。

### Journey C：探索完整旅程

1. 讀者從 Journey Hub 查看日期、路線與 Place。
2. 時間表保持完整；深度文章只連到已發布內容。
3. 讀者可依時間順序或 Place 自由閱讀，所有入口指向同一 canonical 文章。

## 6. 文章契約

- 使用「文學 H1＋描述副標＋SEO title＋穩定 canonical URL」。
- IG 卡片、長篇散文、Before／After、照片短句、地圖、圖集與實戰筆記都是可選呈現方式，不是每篇必填模板。
- 實用資訊只描述造訪當時的第一手紀錄，例如「2026 年 2 月造訪時」。
- 不承諾最新票價、即時營業時間或完整攻略，也不建立外部定期查核責任。
- AI 寫作必須遵守 `EDITORIAL_STYLE_GUIDE.md`。
- 人物、家庭與工作資訊必須通過逐篇隱私 UAT。

## 7. 五個里程碑

### Milestone 1：可信內容底帳

**目的**：先確定實際擁有的內容，再決定能寫什麼。

工作：

- 以 canonical Takeout export 建立貼文與媒體 evidence inventory。
- 分開統計貼文、圖片、影片與其他媒體。
- 區分發布日期、旅遊日期與照片拍攝日期。
- 將自動事件群集標記為候選，不直接視為確認旅程。
- 建立 `confidence`、`privacy_status` 與來源追溯欄位。

驗收：

- 每則來源與每個媒體都有唯一識別及來源路徑。
- 無 `posts.json`／`posts_1.json`／archived posts 重複計數。
- 新加坡與台南、東京與返台內容等事件邊界完成拆分。
- 舊 Blueprint 的數量不再被工具或 Roadmap 引用為既定事實。

### Milestone 2：Journey Catalog 與 Editorial Contract

**目的**：把 archive 轉為可編輯、可核准的內容目錄。

工作：

- 建立 Journey、Place、主題、來源與公開狀態模型。
- 從 Blogger legacy 旅遊文章萃取成熟版 CH Voice Profile。
- 建立 Journey 一次口述＋Place 寫作前短口述流程。
- 為每個候選 Place 定義一句核心命題，不先決定篇數。

驗收：

- 每個候選內容都有明確 Place 類型與所屬 Journey。
- 每篇都能說明「為什麼只有 CH 能寫這篇」。
- 沒有口述或來源支持的內在感受不得進入可發布初稿。
- 文章數量由故事命題決定，不由 IG 數量決定。

### Milestone 3：哈修塔特 Place 化 Pilot

**目的**：驗證新模型，不新增重複內容。

範圍：

- 以現有 `day-02-blog.html` 為唯一哈修塔特文章基礎。
- 對照 2014 Blogger、2026 Instagram、照片與現有文章。
- 先做 Keep／Rewrite／Remove audit，再進行口述訪談。
- 重編偏 AI 味段落，精選 IG 現場原聲，保留有效圖資與實戰筆記。
- 初期保留現有 URL；是否遷移到 Place URL 留待 Pilot UAT 後決定。
- 不改動 Day 02 時間表的完整行程功能。

驗收：

- 公開內容只有一份哈修塔特正文，無 SEO duplicate。
- 使用者確認「像我寫的」，且沒有被發明的記憶或對話。
- 家庭與人物內容通過隱私 UAT。
- 搜尋讀者仍能取得造訪當時的停車與旅行筆記。
- 圖片、內部連結、canonical 與全站 validator 通過。

**停止條件**：若使用者認為 Voice、Place 邊界或故事／資訊比例仍不對，不進行全量轉型，先修正模型與 Pilot。

### Milestone 4：第一波內容轉型

**目的**：先打磨 2026 Germany，驗證 Hallstatt 方法可延伸，但不複製成制式模板。

#### A. 完整平行改寫

依序處理：

1. **Day 13 新天鵝堡**：整合 2001 Blogger 舊文與 2026 父女重返，核心是「當年以為照片是假的，二十五年後帶 Belle 走進城堡」。先校正只有作者與 Belle 同行的敘事視角。
2. **Day 15 返程後記**：改寫為父女學測後旅行的總結，移除「全家同行」誤述與空泛的圓滿／回甘句型。
3. **Day 12 Das Graseck**：以「這麼貴、這麼麻煩，值不值得住一晚」為第一手命題，保留花錢觀、纜車飯店與烏來雲仙樂園插曲。
4. **Day 01 薩爾斯堡**：收斂為「莫札特的家，我為什麼來了三次」，避免取車與交通資訊淹沒城市主線。
5. **Day 08 海德堡**：先以口述確認真正留下的記憶，再決定是否從景點總覽改為「原本為古堡而來，最後記住了什麼」。

以上均先做純文字與 `noindex` 平行預覽，不直接取代現有 Day URL。

#### B. 結構整理與去 AI 味

- **Day 09 哈瑙＋法蘭克福**：先處理兩個城市的主次或拆分邊界。
- **Day 10 科爾馬**：減少泛用童話形容，補回人潮、停車、實際感受與是否名符其實。
- **Day 11 巴塞爾＋埃吉桑姆**：釐清兩個 Place 是否應各自成篇。
- **Day 06 羅騰堡**：先瘦身；只有口述找到獨有事件時才升級為完整改寫。

#### C. 輕量校正

- Day 03、04、05、07、Day 10 史派爾與 Day 14 暫以事實、語氣及實用資訊校正為主，不強迫加入深情主線。

驗收：

- 每篇處理強度都有明確證據，不把所有 Day 頁改成同一種文章。
- Day 13、15 的父女同行關係與人物事實正確。
- 首頁主推的是編輯精選，不是所有已生成頁面的機械列表。
- Journey Hub、Place、時間表三者能互相導覽且不重複承載正文。
- 所有公開內容完成 Voice、事實與隱私 UAT。

Germany 完成後，再評估香港重返、澳洲、台灣分段環島、義大利或金門；這些是後續內容 backlog，不與本 Milestone 並行。

### Milestone 5：Portal 收斂與正式發布

**目的**：讓 B 真正主導產品，A 提供穩定搜尋入口。

工作：

- 將首頁調整為故事優先的探索順序。
- 建立地方與旅程入口、必要篩選及站內搜尋。
- 補齊 canonical、metadata、OG、結構化導覽與 sitemap 契約。
- 地圖只在對敘事或路線有幫助時使用。
- 依現有圖片管線與 validator 完成全站回歸。

驗收：

- 三條 canonical user journey 均能從入口走到真實內容與下一步。
- 未發布內容沒有可點擊的 404 入口。
- 公開目錄沒有原始照片、影片、GPS／EXIF 或未核准人物內容。
- 本機瀏覽器 UAT 與 `python tools/validate_images.py` 100% 通過。
- Commit、push 與 GitHub Pages 發布各自取得當下範圍的明確授權。

## 8. 非目標

在前述里程碑完成前，不優先投入：

- 為每則 IG 或每一天建立一篇文章。
- 建立另一份重複的 Place 正文。
- 宣稱「最新」「最完整」或維護即時票價與營業資訊。
- 以世界地圖、國家數、里程儀表板取代內容主張。
- 為尚未核准的文章建立前端入口。
- 因框架流行而重寫現有 zero-build 架構。
- 在內容底帳完成前承諾固定文章總數。

## 9. 下一個可執行步驟

1. 以 `trips/2026-germany/prompts/day-13-neuschwanstein-gemini.md` 交由 Gemini audit Day 13。
2. 回答 Gemini 僅針對證據缺口提出的短訪談問題，優先使用口說稿。
3. Gemini 交付純文字稿後，由 Codex 做 factual、voice、privacy 與重複內容 review。
4. 草稿通過後才建立 Day 13 `noindex` 平行預覽，不覆寫正式 Day 13。
5. 完成 Day 13 UAT，再依 Milestone 4 順序處理 Day 15、12、01、08。
