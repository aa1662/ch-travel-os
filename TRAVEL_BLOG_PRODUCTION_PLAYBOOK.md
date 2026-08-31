# CH Travel Blog Production Playbook

> 本文件是 CH Travel OS 跨旅程、跨模型的文章製作流程 SSoT。
> 它規範「怎麼把素材做成一篇可發布作品」；文風依 `EDITORIAL_STYLE_GUIDE.md`，品牌與內容邊界依 `TRAVEL_PORTAL_ROADMAP.md`。

## 1. 目標與完成定義

一篇文章只有同時符合下列條件才算完成：

- 作者確認事實、人物、語氣、故事重心與公開邊界。
- 文章先是一篇能獨立閱讀的旅行作品，再提供造訪當時的實戰資訊。
- 圖片有明確敘事功能；正文、IG 卡片與燈箱不機械重複。
- Source、公開頁、圖片 manifest、內部連結與 canonical 一致。
- 桌面、手機、燈箱與全站 validator 均通過。

人工 UAT 判斷內容是否成立；工具負責證明技術契約成立。不得把 hash、manifest、死鏈或輸出一致性轉嫁給作者檢查。

## 2. 文件與資料責任

| 項目 | 唯一責任來源 |
| --- | --- |
| 品牌定位、內容型態、Journey／Place 邊界 | `TRAVEL_PORTAL_ROADMAP.md` |
| CH Voice、去 AI 味、隱私與內容 UAT | `EDITORIAL_STYLE_GUIDE.md` |
| 製作步驟、交接、驗收與停止條件 | 本 Playbook |
| 旅程文章清單、URL、日期與導覽關係 | `trips/<journey>/blog-migration.json` |
| 核准後文章正文 | `trips/<journey>/sources/blog/` |
| 原始照片與 Takeout | `masters/` 或作者指定私人來源；不進 Git |
| 公開頁與 WebP | `docs/`；只能由核准來源與管線生成 |

母稿、照片 audit、prompt 與 preview 是製作證據，不得反向覆蓋已核准的 source。

## 3. 角色分工

### 作者

- 提供口述記憶、人物關係、真實評價與公開授權。
- 決定文章命題、哪些照片一定要用／不要用，以及最後內容與呈現是否過關。
- 若每個主要景點缺少適合版面的橫式照片，由流程主動向作者確認或索取。

### 主編 Agent

- 理解全部來源，找出真正故事，不用景點百科取代作者經驗。
- 主持必要的 grillme、完成母稿、比較既有頁、整合正文與圖片。
- 保護 SSoT、執行 build／validator／瀏覽器驗收，整理待作者判斷的少量問題。

### 批次分析 Agent

- 適合處理大量照片的 metadata、時間排序、視覺分類、近似重複與初步候選清單。
- 輸出的 `confidence` 只代表視覺分類信心，不代表地點、人物、事件或故事事實已查證。
- 不得自行決定公開、刪除原圖、發明照片情境或把全部候選直接發布。

### 自動化工具

- 負責 hash、WebP、manifest、HTML build、連結、anchor、metadata 與媒體安全檢查。
- 不能取代內容判斷或人工視覺 UAT。

## 4. Stage 0：啟動與素材邊界

開始寫作前先確認本篇可取得哪些素材：

- 作者完整口述或經 HITL 修訂的母資料。
- 行前規劃網站、時間表、地圖與票券紀錄。
- Instagram／Blogger／舊遊記。
- 原始照片、IG 圖片與既有公開 derivatives。
- 既有文章、preview 或過去 AI 草稿。
- 作者指定的 hero、必用圖、禁用圖與人物公開界線。

同時定義：

- Journey、Place／Route 主題及文章的 canonical URL。
- 文章是一個 Place、一條 Route，或確實需要拆成多篇。
- 哪些資料只是參考，哪些是可引用證據。
- 有沒有主要景點缺橫式照片。缺少時先詢問作者，不用低品質或不相干照片硬撐版面。

若素材不足以支持獨立命題，停止寫作，改做資料盤點或向作者提問。

## 5. Stage 1：照片盤點

### 5.1 先 audit，後搬移與發布

先以唯讀方式盤點原始照片及 Takeout，再決定 master 歸屬、正文候選與燈箱候選。大量照片可交由批次分析 Agent 初篩，主編仍須複核所有入選圖。

建議 audit 欄位：

```text
source_path, filename, captured_at, width, height, orientation,
sha256, visual_group, likely_place, narrative_role,
quality_notes, duplicate_of, privacy_notes, confidence,
recommended_use, owner_decision
```

`recommended_use` 可為 `hero`、`body`、`ig-card`、`photo-note`、`gallery`、`archive`、`reject`。`owner_decision` 一旦有值，優先於模型建議。

### 5.2 選圖標準與來源優先序 (Curatorial Standards)

選圖必須同時服務**正文故事推進**與**燈箱時間線體驗**，嚴格遵守以下體系：

1. **來源優先序 (SSoT Hierarchy)**：
   - **第一優先**：作者手動建立的精選資料庫（如 `*精選` 目錄或人工指定清單），代表作者第一手審美與核心回憶。
   - **第二優先**：正文敘事所需的大景補強（如 16:9 橫幅 Hero、章節轉換滿版大圖、清晨壓軸大景）。
   - **第三優先**：跨季或跨次造訪的對比視角（如初夏綠意 vs 深秋紅葉、打鐵花 vs 無人機秀）。
2. **四大選圖判斷標準 (4 Curatorial Criteria)**：
   - 🎯 **敘事責任 (Narrative Responsibility)**：每張入選圖必須在正文或燈箱中承擔具體的「事實證據」，拒絕無敘事增量的純風景。
   - 🔍 **去重與淘汰連拍 (Deduplication)**：同一角度連拍只留 1 張對焦最銳利、曝光動態範圍最好的代表；淘汰晃動、過暗、浮水印與近似圖。
   - 📐 **構圖與版位適配 (Layout Fitness)**：橫圖（16:9）專供滿版 Hero 與 Wide Photo；直圖（3:4 / 9:16）專供 1:1 等高 Story-Split 與 4 格 IG Post Card。
   - 🛡️ **隱私與肖像安全 (Privacy Protection)**：優先選用建築、地景、步道與光影氣氛，避免路人正面特寫與私人同行者過度暴露。
3. **燈箱嚴格時間排序 (Chronological Ordering)**：
   - 燈箱圖庫（`landscape` 與 `portrait` 分組）必須嚴格依照照片拍攝時間戳記（`YYYYMMDD_HHMMSS`）由早至晚升冪排序，讓讀者滑動燈箱時能完整體會真實的時間軸與光影流轉。

### 5.3 原圖與 derivatives 發布邊界

- **嚴禁全量轉檔**：不為未入選或「也許以後會用」的照片製作公開 derivatives。
- **精選原圖進 masters**：僅將經過 5.2 節核准的精選原圖移入 `masters/<journey>/<day-or-place>/`。
- **公開 WebP 隔離**：`docs/` 只保存 image pipeline 產生的 WebP（480w, 960w, 1200w, 1600w），徹底移除 EXIF、GPS 與相機原圖。

## 6. Stage 2：盲寫母稿

母稿的目的，是先忠實整理作者完整記憶，不受舊 HTML、IG 卡片數量或現有版面綁架。

1. 完整讀完口述，不先摘要成短文。
2. 校正可由行程、照片時間或既有來源確認的地名與時間，但保留作者語氣。
3. 標記矛盾、缺口、推測與待確認事項；不可用順暢文字掩蓋。
4. 依事件順序整理出完整母稿，保留笑點、抱怨、臨時決定、同行互動與實際取捨。
5. 另列「可進 Bento 的實用資訊」，不讓攻略打斷故事。

母稿應保存於 `trips/<journey>/manuscripts/`。它是寫作證據，不是公開頁，也不得整批覆蓋其他文章的母稿。

### 6.1 新文章硬關卡

新文章或重大改寫必須先完成並取得作者確認：

1. 文章級母稿。
2. 照片 audit 與公開／排除邊界。
3. 正文選圖、IG 原貼文與 gallery 的呈現計畫。
4. 必要的 Grillme 與 factual／voice／privacy HITL。

以上尚未通過時，主編 Agent 不得建立或修改正式 `sources/blog/`、migration config、公開 derivatives 或 `docs/`。作者明確要求平行 preview 時例外，但 preview 必須留在 editorial workflow 目錄，不得冒充正式構建成果。

## 7. Stage 3：Grillme 與內容 HITL

只針對母稿仍影響故事的問題提問，優先問：

- 這篇真正想留下的是哪一件事？
- 哪個瞬間最像「只有作者能寫」？
- 同行者在故事中的關係與反應是否正確？
- 哪個評價是親身感受，哪個只是行前查到？
- 有沒有照片看不出的臨時決定、失誤、笑點或遺憾？
- 哪些人物、價格、對話或照片不適合公開？

可用逐題選項降低負擔，但答案必須回寫母稿。停止條件是故事主線、事實與公開界線已清楚；不要為了「訪談完整」無限追問。

## 8. Stage 4：與既有文章比對

有既有文章時，不直接覆蓋，也不因母稿較新就假設它全面更好。逐項比較：

| 面向 | 判斷問題 |
| --- | --- |
| 記憶完整度 | 哪一版保留了更多真實事件與因果？ |
| 敘事主線 | 開頭、轉折與收束是否服務同一命題？ |
| CH Voice | 是否像作者，而不是標準旅遊文或 AI 散文？ |
| 節奏密度 | 是否拖、重複，或把重要事件壓縮掉？ |
| 圖文關係 | 照片是否放在對應事件旁，而非只做裝飾？ |
| 實用價值 | Bento 是否保留親測 tips、避雷與當時規劃？ |
| UI／技術 | 既有版面、IG、gallery、navigation 有何值得保留？ |

每個差異只能歸入：`保留既有`、`採用母稿`、`融合重寫`、`刪除`、`交作者決定`。先形成決策，再修改 SSoT。

## 9. Stage 5：正式文章與呈現

### 9.1 全站雙黃金標準範本 (Dual Gold Standards)

所有新篇章的視覺結構與節奏，必須嚴格對齊以下兩大已驗收的最高標準範本：

1. **路線健行／多景點長篇範本**：[`docs/2026-osaka/blog/kurama-kifune-hike.html`](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/docs/2026-osaka/blog/kurama-kifune-hike.html)
   - *適用場景*：有多個途經點、翻山越嶺、時間線性推進、包含交通轉乘與行前功課對比的長篇作品。
   - *節奏公式*：`Hero (16:9 大景)` ➔ `開篇 Narrative Card (破題與同行背景)` ➔ `Story-Split (圖文並茂起點)` ➔ `Wide Photo (滿版轉換空間)` ➔ `IG 4-Photo Grid (沿途連拍細節)` ➔ `Reverse Split (特色框景/回望)` ➔ `Closing Wide Photo (壓軸大景)` ➔ `Summary Card` ➔ `4~6 格實戰 Bento`。
2. **單點精華／散文短篇範本**：[`docs/2025-2026-beijing/blog/mutianyu-great-wall.html`](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/docs/2025-2026-beijing/blog/mutianyu-great-wall.html)
   - *適用場景*：停留 1～2 小時、包車／單一景點、著重現場氛圍、臨場趣味互動與單一核心命題的精煉作品。
   - *節奏公式*：`Hero (16:9 氣勢破題)` ➔ `開篇 Narrative Card (出發背景與起因)` ➔ `Story-Split (1:1 圖文等高，聚焦核心笑點/起點石階)` ➔ `Wide Photo (山脊延伸巨龍)` ➔ `IG 4-Photo Grid (步道、石階與文化遺產標誌)` ➔ `雙向交錯 Split (纜車上下 & 敵樓拱窗框景)` ➔ `Closing Wide Photo (夕陽暮色金光)` ➔ `Summary Card (作者核心評價)` ➔ `4 格乾淨實戰 Bento`。

### 9.2 排版與敘事四大禁令 (Anti-Patterns)

- 🚫 **嚴禁同一事實跳針重複（No Repetitive Looping）**：同一個核心事件（如 VIP 快速通關隨到隨上、纜車上下）在開篇破題後，後續段落**必須推進到新的視角與體驗**（如石階攀爬體感、敵樓避風框景、夕陽光線、與其他長城難易度對比）。嚴禁在正文、各區塊小標、照片札記與 Bento 之間機械式跳針重複同一句事實。
- 🚫 **嚴禁文字大幅高於照片（Text/Image Height Balance）**：在 `.story-split` 圖文交錯模組中，文字段落必須精簡（控制在 2～3 段內），與旁邊的直式照片高度維持 **1:1 視覺對齊**。若有較長的背景或出發起因，應**先以全幅 `.blog-narrative-card` 破題**，再進入左右圖文 Split，嚴禁出現 6～7 段長文壓過短照片造成單側大片留白。
- 🚫 **嚴禁正文與圖集重複註冊 GLightbox（Gallery Opener Standard）**：正文中的所有圖片（Hero、Wide Photo、Story-Split、IG 卡片縮圖）一律使用 `<a class="gallery-opener" data-gallery-open="<image_stem>">` 作為入口觸發器，嚴禁在正文內標籤直接掛載 `class="glightbox"` 與 `data-gallery`。整個頁面的燈箱幻燈片**唯一由底部的 `<div class="gallery-registry">` SSoT 管理**。此規範可杜絕同一照片重複出現在燈箱中，並確保燈箱幻燈片嚴格沿時間軸由早至晚單向推進，徹底避免白天與黑夜來回穿插倒退的混亂體感。
- 🚫 **嚴禁脫離 SSoT 在 `docs/` 手寫非編譯檔案**：所有正式頁面必須保持 SSoT（`trips/<journey>/sources/blog/*.html`）與 migration config 同步，並透過 `python tools/build_trip_html.py` 原子編譯至 `docs/`，確保 `core/editor.html` 視覺化編輯器、`validate_images.py` 與發布系統 100% 同步。

### 9.3 核心呈現準則

- 先完成故事，再加入 Bento；Bento 原則上是 bottom navigation 上方最後一個內容 section。
- IG 卡片、story split、單張滿版、雙圖、portrait feature、對照圖與 gallery 都是可選元件。
- 不要求每篇出現相同數量的 IG 卡片或相同版型；同一 Journey 的導覽、Bento 規格、圖集入口與整體視覺語言必須一致。
- 批評「元件使用過量」不等於禁用作者已核准的呈現形式。重做時必須逐一判斷元件是否有敘事功能，不得用全部刪除取代編輯判斷。
- 照片順序可依敘事重排；gallery 本身仍按拍攝時間排序。
- 直式敘事照片優先保留完整構圖，可以使用 `object-fit: contain`；但容器比例、尺寸與周邊版面必須配合照片，不得留下大片無敘事作用的空白邊。固定版位確實需要滿框時可使用 `cover`，並以桌機／手機 UAT 確認人物與主體焦點未被切掉。
- 行前規劃有獨立網站時，在 Bento 提供清楚入口；文章只摘錄與實際經驗最相關的內容，不複製整站，也不加入多餘免責聲明。
- 網路推薦可保留為「當時行前口袋名單」，不得寫成作者吃過、用過或背書的第一手推薦。
- 實用資訊以造訪年份或月份自然標示，不承諾即時更新。

### 9.4 旅途照片札記（Travel Photo Notes）

「旅途照片札記」是借用 IG 卡片閱讀節奏的圖文模組，用來承接未進入正文主線、但仍有獨立故事或資訊價值的核准照片。它不是 Instagram 原貼文，也不是把剩餘照片全部可視化的替代 gallery。

- 卡片標示「旅途照片札記」，不得冒充「Instagram 原始貼文」；只有確實來自 Instagram 的 caption 才能使用後者。
- 每則通常使用 1～4 張照片，搭配一段真實現場補充、人物互動、短故事、親測 tip、避雷或景點背景。
- 只在照片能帶出正文沒有說完的內容時使用；沒有新增敘事或資訊價值的照片留在 Lightbox，不為消化庫存硬寫文字。
- 札記可以放在對應正文段落旁，或集中置於故事收束後、gallery 入口前；不得插斷文章的主要轉折與結尾。
- 桌面預設單卡直向排列；可依內容採雙圖、拼圖或左圖右文。手機必須維持單卡閱讀，必要時改為照片在上、文字在下。
- 同一影像可以在札記中成為可見入口，但全頁只能註冊一個 Lightbox slide。札記 opener 必須映射到既有橫式或直式 gallery，不得建立重複 slide。
- 旅途照片札記不取代完整 gallery；gallery 仍依拍攝時間排序、橫直分組並維持精選邊界。
- 同一 Journey 應維持卡片標示、間距、圖集互動與手機行為一致，但不要求每篇都有札記或相同張數。

### 9.5 Instagram 原貼文與相機原圖雙軌契約

Instagram 原貼文是作者當時已完成的編輯作品；相機原圖則是正式圖文誌的畫質與完整構圖來源。兩者用途不同，不應強迫二選一。

- 建立 `IG 匯出圖 -> 相機原圖 -> 正文／IG 卡用途 -> Lightbox slide` 映射，再進入選圖與構建。
- Hero、正文大圖與 Lightbox 優先使用相機原圖，保留解析度與完整構圖。
- IG 卡若原貼文有明顯裁切、調色或版面意圖，使用 IG 匯出圖重現當時貼文；若差異不具意義，直接以原圖配合卡片裁切，避免重複資產。
- 點擊 IG 圖片時優先開啟對應的相機原圖 Lightbox；同一畫面全頁只能註冊一個 slide。
- 只有 IG 匯出圖、找不到相機原圖時，可以 IG 圖作為公開來源，但不得拿低解析 IG 圖充當 Hero 或大型 Lightbox。
- IG carousel 可因人物隱私移除個別照片；caption 必須維持原文，不以 AI 補寫成「原始貼文」。若另寫補充文字，應清楚區分為文章正文或旅途照片札記。
- 被作者排除的人物照不得進 masters、公開 derivatives、可見卡片或隱藏 gallery registry。
- IG 匯出圖若需要公開，同樣必須經 image pipeline 轉為 WebP 並清除 metadata；不得直接複製 Takeout 檔案到 `docs/`。

先更新 `trips/<journey>/sources/blog/` 與 migration config，再由 builder 產生 `docs/`。不得把 `docs/` 當唯一 source 手工維護。

## 10. Stage 6：圖片管線與 Build

建議順序：

```powershell
python tools/image_pipeline.py --trip <journey> --dest <dest> [--pilot-day <day>]
python tools/build_trip_html.py --trip <journey> --dest <dest>
python tools/validate_images.py
```

必要契約：

- Manifest 頂層至少保存 `pipeline_version`、`quality`、`profiles`、`trip`、`dest` 與完整圖片 entries。
- Cache hit 必須同時符合來源 hash 與 pipeline contract；不能只看輸出檔存在。
- `--pilot-day` 只更新該日 entries，必須保留其他日已存在且契約相容的 entries。
- 若現有 manifest contract 不相容，pilot 必須失敗並要求完整 rebuild，不得靜默覆寫全 manifest。
- Builder 採記憶體緩衝與原子寫入；source missing、mapping miss 或構建錯誤時，不得留下部分發布結果。
- `core/` 與 `docs/core/` 的同步由構建流程負責，不依賴人工複製。

## 11. Stage 7：自動驗收與瀏覽器 UAT

### 系統驗收

- image pipeline 第二次執行達預期 cache hit。
- manifest 保留非 pilot 日 entries。
- builder 成功且 source／published URL 一致。
- `python tools/validate_images.py` 以 0 error 結束。
- 無死鏈、缺失 anchor、原始媒體、GPS／EXIF、缺圖或 JS 故事資料破圖。
- `git diff --check` 無新增格式錯誤。

### 瀏覽器驗收

至少檢查桌面與手機：

- H1、首屏、段落密度、圖文順序與 Bento 位置。
- 文字不重疊、不溢出，直式照片不被不合理裁切。
- 橫式與直式 gallery 各自可開啟、張數正確、順序正確、無重複 slide。
- console 無 error，主要導覽與規劃網站連結可用。

### 作者 UAT

一次集中請作者判斷：

- 內容是否打動自己，且像自己會寫的文章。
- 事實、人物、笑點與評價是否正確。
- 圖片選擇、排列、裁切與整體呈現是否滿意。
- 實用資訊是否有價值，且沒有搶走故事。
- 是否可作為本 Journey 後續文章的一致基準。

技術問題先由系統集中修完再交回，不以多輪零碎 UAT 消耗作者。

## 12. 發布與清理

- HITL 通過後，將核准版本留在 source 並重新 build；不要只修 published HTML。
- Preview、prompt、audit 與 manuscript 依專案 editorial workflow 保存；臨時 screenshot、瀏覽器 scratch 與無用途中間檔不進 release commit。
- 移除或 archive 過渡檔前先確認沒有 config、builder、navigation 或文件引用。
- Commit、push、deploy 分別取得授權；selective stage，不混入其他 working-tree 變更。

## 13. 一頁 SOP Checklist

```text
[ ] 確認 Journey、Place／Route、canonical 與文章命題
[ ] 盤點口述、規劃站、IG／Blogger、原圖、既有頁
[ ] 向作者確認缺少的主要景點橫式照片
[ ] 建立照片 audit；主編複核 AI 分類與公開邊界
[ ] 完成盲寫母稿，不受舊版面限制
[ ] Grillme 補齊故事、事實、人物與隱私缺口
[ ] 母稿通過 factual／voice／privacy HITL
[ ] 母稿、照片 audit 與呈現計畫通過前，尚未建立正式 source／config／docs
[ ] 逐項比較既有頁，形成保留／採用／融合／刪除決策
[ ] 依文章型態嚴格對齊黃金範本（Osaka 健行型 或 Beijing 散文型）之視覺節奏
[ ] 檢查圖文 Split 文字高度是否與直式照片 1:1 等高，無文字欄過長失衡
[ ] 檢查正文、小標、照片札記與 Bento 無同一事實或笑點的跳針重複
[ ] 檢查正文圖片一律使用 gallery-opener，燈箱唯一由底部 registry 管理，零重複 slide 且按時間升冪排列
[ ] IG 原貼文已建立 IG 匯出圖／相機原圖／Lightbox 映射，並排除隱私與重複影像
[ ] 判斷非正文照片是否值得做旅途照片札記；沒有新增價值就只留 gallery
[ ] 更新 source、config、正文圖、IG／照片札記、gallery 與 Bento
[ ] 精選原圖進 masters；只產生入選公開 derivatives
[ ] 跑 pipeline、builder、validator 與 diff check
[ ] 確認 SSoT 手稿 (trips/.../sources/) 與 docs/ 完全同步，並在 editor.html 中可正常開啟
[ ] 驗證 pilot manifest 未丟失其他日 entries
[ ] 桌面／手機／gallery／console 瀏覽器驗收
[ ] 直式敘事照片沒有大片無意義空邊；使用 `contain` 或 `cover` 時均已確認構圖與主體
[ ] 作者完成內容與呈現 UAT
[ ] 清理臨時檔；commit、push、deploy 分開授權
```

## 14. 流程演進

只有下列情況才修改本 Playbook：

- 新 Journey 的實際 dry-run 顯示流程缺口。
- 同一類錯誤重複發生，且可用明確契約預防。
- 工具鏈或 SSoT 架構改變。

單篇文章的特殊選圖、笑點或版型，不升格為全域硬規則。每次流程調整應記錄原因，並確認沒有與 Style Guide 或 Roadmap 重複定義。
