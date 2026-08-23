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
| Journey 精選故事內容 | 各 Journey Hub 的 `window.__JOURNEY_STORIES__` | 使用者內容決策、Journey 維護流程 | 只引用該 Journey 已發布文章與公開圖片 |
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
- 一個公開主題只保留一個 canonical URL；正式公開後才對既有 URL 建立轉址責任，作者試看階段採 clean rename。

## 3.1 URL 策略：Journey-scoped Place/Theme URL

Journey path 負責識別一次完整旅程，Blog filename 只描述文章的 Place／Theme。Day 是 Journey 的時間脈絡，不是 Blog 的長期身份。

公開階層：

- Country Hub：`docs/germany/index.html`，只彙整歷年 Germany Journeys。
- Journey Hub：`docs/2026-germany/index.html`，承載單次旅程專刊與時間軸。
- Timeline：`docs/2026-germany/day-XX.html`，保留 Day filename。
- Blog：`docs/2026-germany/blog/<place-theme>.html`，filename 不含 `day-XX-`。

範例：

- `/2026-germany/blog/hallstatt-winter.html`
- `/2026-germany/blog/neuschwanstein-winter.html`
- `/2026-germany/day-02.html`

規則：

- Day 保留於 Blog entry id、Timeline filename、Journey 導覽順序、圖片 day folder 與頁面顯示標籤。
- 同一 Place 在不同 Journey 可有不同文章；Journey path 提供年份與旅程語境。
- 不為 SEO 複製內容相近的純 Place 文章，避免 duplicate content 與維護分裂。
- 目前站點尚未正式公開，本輪 URL migration 採 clean rename，不建立 redirect 或相容頁。
- 精選故事資料由各 Journey Hub 擁有；`core/js/app.js` 只負責隨機抽選、DOM render 與共用互動。

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

**狀態：已完成。** Day 02 已完成內容、Voice、隱私與實用資訊 UAT，並作為後續 Germany 文章精修基準。

**目的**：驗證新模型，不新增重複內容。

範圍：

- 以既有 Day 02 正文為唯一哈修塔特文章基礎。
- 對照 2014 Blogger、2026 Instagram、照片與現有文章。
- 先做 Keep／Rewrite／Remove audit，再進行口述訪談。
- 重編偏 AI 味段落，精選 IG 現場原聲，保留有效圖資與實戰筆記。
- Blog 將依全站 URL migration 改為 Journey-scoped `hallstatt-winter.html`。
- 不改動 Day 02 時間表的完整行程功能。

驗收：

- 公開內容只有一份哈修塔特正文，無 SEO duplicate。
- 使用者確認「像我寫的」，且沒有被發明的記憶或對話。
- 家庭與人物內容通過隱私 UAT。
- 搜尋讀者仍能取得造訪當時的停車與旅行筆記。
- 圖片、內部連結、canonical 與全站 validator 通過。

**停止條件**：若使用者認為 Voice、Place 邊界或故事／資訊比例仍不對，不進行全量轉型，先修正模型與 Pilot。

### Milestone 4：第一波內容轉型

**狀態：已完成。** 2026 Germany 共 16 篇文章已完成分級精修、內容 UAT 與公開衍生圖驗證。

**目的**：先打磨 2026 Germany，驗證 Hallstatt 方法可延伸，但不複製成制式模板。

#### A. 完整平行改寫

依序處理：

1. **Day 13 新天鵝堡**：整合 2001 Blogger 舊文與 2026 父女重返，核心是「當年以為照片是假的，二十五年後帶 Belle 走進城堡」。先校正只有作者與 Belle 同行的敘事視角。
2. **Day 15 返程後記**：改寫為父女學測後旅行的總結，移除「全家同行」誤述與空泛的圓滿／回甘句型。
3. **Day 12 Das Graseck**：以「這麼貴、這麼麻煩，值不值得住一晚」為第一手命題，保留花錢觀、纜車飯店與烏來雲仙樂園插曲。
4. **Day 01 薩爾斯堡**：收斂為「莫札特的家，我為什麼來了三次」，避免取車與交通資訊淹沒城市主線。
5. **Day 08 海德堡**：先以口述確認真正留下的記憶，再決定是否從景點總覽改為「原本為古堡而來，最後記住了什麼」。

以上內容已完成平行預覽、review 與正式 source 收斂；預覽檔保留為 editorial workflow artifacts。

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

1. 依 `url_migration.md` 執行 Journey Namespace and URL Migration。
2. 將 2026 Journey 從 `docs/germany/` 搬至 `docs/2026-germany/`，並建立最小 Germany Country Hub。
3. 將 16 篇 Blog clean rename 為 Journey-scoped Place／Theme URL。
4. 收斂 builder、editor server、validator 與 Journey stories ownership。
5. 完成圖片 cache、全站 validator 與本機瀏覽器 UAT 後，再獨立取得 commit／push 授權。
