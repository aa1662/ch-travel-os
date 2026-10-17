# CH Travel Blog Production Playbook

> 本文件是 CH Travel OS 跨旅程、跨模型的文章製作流程 SSoT。
> 它規範「怎麼把素材做成一篇可發布作品」；文風依 `EDITORIAL_STYLE_GUIDE.md`，品牌與內容邊界依 `TRAVEL_PORTAL_ROADMAP.md`。

> 流程版本：2026-10-17。適用後續新遊記；已完成文章維持原樣，除非作者另行指定修改。歷史 plan、案例與舊 prompt 不得覆蓋本流程及本篇最新確認。

新篇主線：**集中候選照片 → 看圖口述、同步選圖 → Grillme 討論寫法與呈現 → 潤飾並確認母稿／選圖 → 僅入選圖轉檔 → 排版與驗收 → 依授權發布**。口述、選圖與寫法討論可以來回進行，不要求先跑完獨立 audit 或先建立 HTML。

## 1. 目標與完成定義

一篇文章只有同時符合下列條件才算完成：

- 作者確認事實、人物、語氣、故事重心與公開邊界。
- 文章可以是照片小品、故事遊記或實用行程筆記；先在開篇討論中確認目的，不強迫每篇具備重大轉折、感悟或 Bento。
- 圖片可服務故事、觀察或單純的攝影欣賞；正文、IG 卡片與燈箱不機械堆疊。
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
| 候選照片與原始素材 | 作者指定的單一私人資料夾／`masters/`；不進 Git，候選不等於入選 |
| 本篇最新內容與呈現決策 | `trips/<journey>/plan.md` 置頂摘要；作者最新確認優先，歷史段落只作追溯 |
| 公開頁與 WebP | `docs/`；只能由核准來源與管線生成 |

母稿、照片 audit、prompt 與 preview 是製作證據，不得反向覆蓋已核准的 source。

`plan.md` 只記本篇所需決策：篇界與寫法、來源資料夾、必用／排除與最終選圖、正文／IG／燈箱用途、IG 欄數及點開版本、caption、目前狀態與下一步。未決欄位標待討論，不預填永久預設。工具已有 `photo-selections` 或 mapping 時引用其決策，不重抄另一份清單。

## 3. 角色分工

### 作者

- 提供口述記憶、人物關係、真實評價與公開授權。
- 決定文章命題、哪些照片一定要用／不要用，以及最後內容與呈現是否過關。
- 在看圖與口述中確認缺少的畫面；先依現有照片討論呈現，只有確實需要補圖時才詢問，不為固定版型要求每個景點都交橫圖。

### 主編 Agent

- 理解全部來源，找出真正故事，不用景點百科取代作者經驗。
- 看圖協助作者回憶與選圖；在潤飾前主持必要的 grillme，討論寫法、分篇、語氣與呈現，然後完成母稿與圖文整合。
- 保護 SSoT、執行 build／validator／瀏覽器驗收，整理待作者判斷的少量問題。

### 批次分析 Agent

- 適合處理大量照片的 metadata、時間排序、視覺分類、近似重複與初步候選清單。
- 輸出的 `confidence` 只代表視覺分類信心，不代表地點、人物、事件或故事事實已查證。
- 不得自行決定公開、刪除原圖、發明照片情境或把全部候選直接發布。

### 自動化工具

- 負責 hash、WebP、manifest、HTML build、連結、anchor、metadata 與媒體安全檢查。
- 不能取代內容判斷或人工視覺 UAT。

## 4. Stage 0：啟動與素材邊界

作者先將本次候選照片集中在一個私人資料夾。AI 確認該資料夾與相關口述，再按需要查 IG、舊文或行前資料，不為開始說故事而全量掃描其他來源。

開始時確認可取得哪些素材：

- 作者完整口述或經 HITL 修訂的母資料。
- 行前規劃網站、時間表、地圖與票券紀錄。
- Instagram／Blogger／舊遊記。
- 原始照片、IG 圖片與既有公開 derivatives。
- 既有文章、preview 或過去 AI 草稿。
- 作者指定的 hero、必用圖、禁用圖與人物公開界線。

同時定義：

- Journey 與暫定篇章範圍；分篇與 URL 可在看圖、口述及 grillme 後定案，不作為開始取材的前提。
- 哪些資料只是參考，哪些是可引用證據。
- 現有照片有哪些值得欣賞或說故事的畫面；先依素材討論版面，再決定是否需要補圖。

照片小品不必先有深刻命題。只有缺少會改變事實、人物或公開決定的資料時才針對缺口提問，不用華麗文字補造記憶。

## 5. Stage 1：看圖口述與同步選圖

### 5.1 從作者資料夾開始

AI 先看候選照片，以場景或時間分組，引導作者講故事並同步標記想用、不用或待決的照片。可直接開原圖，或按討論需要建立私人低解析預覽／contact sheet；不要求先為整個資料夾製作縮圖，也不啟動公開 image pipeline。

保留足夠辨識照片與作者選擇的簡短記錄即可。大量素材或來源映射複雜時，再擴充 audit 欄位：

```text
source_path, filename, captured_at, width, height, orientation,
sha256, visual_group, likely_place, narrative_role,
quality_notes, duplicate_of, privacy_notes, confidence,
recommended_use, owner_decision
```

`recommended_use` 可為 `hero`、`body`、`ig-card`、`photo-note`、`gallery`、`archive`、`reject`。`owner_decision` 一旦有值，優先於模型建議。

### 5.2 選圖標準與來源優先序 (Curatorial Standards)

選圖由作者與主編在口述過程中一起決定；候選資料夾不是公開 allowlist，也不因模型評分而自動刪圖。

1. **來源優先序 (SSoT Hierarchy)**：
   - **第一優先**：作者手動建立的精選資料庫（如 `*精選` 目錄或人工指定清單），代表作者第一手審美與核心回憶。
   - **第二優先**：正文敘事所需的大景補強（如 16:9 橫幅 Hero、章節轉換滿版大圖、清晨壓軸大景）。
   - **第三優先**：跨季或跨次造訪的對比視角（如初夏綠意 vs 深秋紅葉、打鐵花 vs 無人機秀）。
2. **四大選圖判斷標準 (4 Curatorial Criteria)**：
   - 🎯 **觀看與故事價值**：照片可以推進事件、補充觀察，也可以因作者喜歡的構圖或景色而入選，不要求每張都有情節。
   - 🔍 **去重與連拍**：主編提出代表圖建議；是否保留不同角度或版本由作者決定，不為湊網格擅自刪圖。
   - 📐 **構圖與版位適配**：依本篇照片與寫法討論橫直圖、尺寸、裁切及版位，不將照片強塞進固定模板。
   - 🛡️ **隱私與肖像安全 (Privacy Protection)**：優先選用建築、地景、步道與光影氣氛，避免路人正面特寫與私人同行者過度暴露。
3. **燈箱嚴格時間排序 (Chronological Ordering)**：
   - 燈箱依可確認的拍攝順序排列並維持橫直分組；無時間戳時保留可追溯的來源順序與不確定性，不拿發布日冒充拍攝日。

### 5.3 原圖與 derivatives 發布邊界

- **嚴禁全量轉檔**：不為未入選或「也許以後會用」的照片製作公開 derivatives。
- **私人候選與公開輸出分離**：候選可留在作者資料夾；工具需要時才在 `masters/<journey>/<day-or-place>/` 準備私人工作副本。不因盤點或未入選就搬移、刪除原圖。
- **定案後轉檔**：母稿、呈現方向及最終選圖確認後，只為確定用於正文、IG 卡、Hero 或燈箱的照片製作公開縮圖與必要尺寸；不能只因照片位於資料夾就整批轉檔。
- **公開 WebP 隔離**：`docs/` 只保存 image pipeline 產生的 WebP（480w, 960w, 1200w, 1600w），徹底移除 EXIF、GPS 與相機原圖。

## 6. Stage 2：Grillme 討論寫法，再潤飾母稿

邊看圖、邊聽作者口述、邊選圖；在正式潤飾前，以第 7 節的必要問題討論怎麼寫。作者已清楚指定的部分直接沿用，不重問。母稿不受舊 HTML 或固定模組數綁架，也不必等照片全選完才開始整理。

1. 完整讀完口述，不先摘要成短文。
2. 校正可由行程、照片時間或既有來源確認的地名與時間，但保留作者語氣。
3. 標記矛盾、缺口、推測與待確認事項；不可用順暢文字掩蓋。
4. 依本篇已討論的寫法整理母稿，保留笑點、抱怨、臨時決定、同行互動與實際取捨；照片小品可用短段觀察串聯，不強迫寫長篇。
5. 有需要才整理實用資訊，不為填滿 Bento 加內容。

母稿應保存於 `trips/<journey>/manuscripts/`。它是寫作證據，不是公開頁，也不得整批覆蓋其他文章的母稿。

### 6.1 內容與選圖確認後才進入正式轉檔與排版

新文章或重大改寫必須先完成並取得作者確認：

1. 文章級母稿。
2. 照片 audit 與公開／排除邊界。
3. 正文選圖、IG 原貼文與 gallery 的呈現計畫。
4. 必要的 Grillme 與 factual／voice／privacy HITL。

以上確認前可以整理口述、候選圖與 plan，必要時可建立 `status: draft` 的本機 Editor scaffold；不產生公開 derivatives、不建置公開頁，也不覆蓋已完成文章。使用 Editor 的草稿不是口述或選圖的必要前置條件。作者要求平行 preview 時，只在私人製作目錄使用本機預覽，不冒充正式發布結果。

## 7. 寫作討論與內容 HITL（在口述／選圖期間進行）

主編在潤飾前主動提出必要的 grillme 問題與寫法建議，和作者決定：

- 本篇是照片小品、故事遊記、行程筆記，或只保存已定稿內容？要一篇還是拆篇？
- 想要輕鬆、幽默、觀察或較完整的故事節奏？哪些修辭可加工、哪些原句要保留？
- 本篇 IG 幾欄、正文圖大小、點開原圖或 IG 調色版、是否顯示 caption，以及用哪些元件？未決時先討論，不沿用其他篇當硬規則。

再依缺口詢問：

- 這篇真正想留下的是哪一件事？
- 哪個瞬間最像「只有作者能寫」？
- 同行者在故事中的關係與反應是否正確？
- 哪個評價是親身感受，哪個只是行前查到？
- 有沒有照片看不出的臨時決定、失誤、笑點或遺憾？
- 哪些人物、價格、對話或照片不適合公開？

可用簡短選項與推薦寫法降低負擔，答案回寫本篇母稿與 plan 最新摘要。當寫法、事實、選圖與公開界線足以開工就停止；後續作者主動調整可再更新，不為流程完整而無限訪談。已核准的幽默加工不反覆重審。

## 8. Stage 4：與既有文章比對

僅在作者明確要求修改某篇既有文章時使用本節。新流程改版不觸發任何已完成文章的比對、重寫或重建。需修改時，不因母稿較新就假設它全面更好，逐項比較：

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

### 9.1 按本篇討論選用案例與元件

在口述、選圖與 grillme 時決定寫法與版型。既有關西健行篇、北京散文篇、澳洲喜劇篇、東京照片小品，都只作視覺與節奏案例，不是固定公式。可參照一篇或組合既有元件，不照抄其段數、圖片數、IG 欄數或 Bento 數量。

共用導覽、字體與互動沿用 `core/`；本篇照片比例、圖文配置、IG 欄數與燈箱版本寫入 plan。沒有新素材時不為了填模板而擴寫。

### 9.2 排版、選圖與導覽六大禁令 (Anti-Patterns)

- 🚫 **嚴禁同一事實跳針重複（No Repetitive Looping）**：同一個核心事件（如 VIP 快速通關隨到隨上、纜車上下）在開篇破題後，後續段落**必須推進到新的視角與體驗**（如石階攀爬體感、敵樓避風框景、夕陽光線、與其他長城難易度對比）。嚴禁在正文、各區塊小標、照片札記與 Bento 之間機械式跳針重複同一句事實。
- 🚫 **避免圖文失衡**：依本篇內容與照片比例調整段落、容器與圖文位置，保持閱讀平衡。可換元件或拆段，不為了強制等高刪掉有價值的口述，也不為填空補造文字。
- 🚫 **不把候選庫全量塞入圖集**：Gallery 依本篇作者確認的範圍收錄；景點篇、小品或旅程生活片段可有不同邊界，不因同一天拍攝就全部加入，也不因照片是餐點或飯店就自動排除。
- 🚫 **不得用未定義的類別破壞導覽與版面**：沿用 `core/` 的導覽與網格元件；IG 欄數依本篇討論設定，確認桌面與手機正常，不以固定欄數代替版面驗收。
- 🚫 **正文與圖集不得重複註冊 GLightbox**：需要開啟燈箱的正文圖使用 `.gallery-opener[data-gallery-open]` 指向底部唯一 `.gallery-registry`，正文不直接註冊 `.glightbox`。作者選擇不入燈箱的可見照片不掛 opener；不能為統一 markup 改變選圖決策。
- 🚫 **嚴禁脫離 SSoT 在 `docs/` 手寫非編譯檔案**：所有正式頁面必須保持 SSoT（`trips/<journey>/sources/blog/*.html`）與 migration config 同步，並透過 `python tools/build_trip_html.py` 原子編譯至 `docs/`，確保 `core/editor.html` 視覺化編輯器、`validate_images.py` 與發布系統 100% 同步。

### 9.3 核心呈現準則

- 先完成故事，再加入 Bento；Bento 原則上是 bottom navigation 上方最後一個內容 section。
- IG 卡片、story split、單張滿版、雙圖、portrait feature、對照圖與 gallery 都是可選元件。
- 不要求每篇出現相同數量的 IG 卡片或相同版型；同一 Journey 的導覽、Bento 規格、圖集入口與整體視覺語言必須一致。
- 批評「元件使用過量」不等於禁用作者已核准的呈現形式。重做時必須逐一判斷元件是否有敘事功能，不得用全部刪除取代編輯判斷。
- 照片順序可依敘事重排；gallery 本身仍按拍攝時間排序。
- IG 欄數與桌面／手機配置每篇討論，不設永久預設，也不為湊欄數擅自刪圖。依入選照片、構圖與本篇呈現設定 `cover`、焦點或相符比例的容器。
- IG 卡片 badge 只標示發布日期與「IG 發布紀錄」，不得寫死「N 張現場實拍」；公開照片可能因隱私、授權、去重或編輯決策調整，固定數字會立刻失真。
- 直式敘事照片優先保留完整構圖，可以使用 `object-fit: contain`；但容器比例、尺寸與周邊版面必須配合照片，不得留下大片無敘事作用的空白邊。固定版位確實需要滿框時可使用 `cover`，並以桌機／手機 UAT 確認人物與主體焦點未被切掉。
- 正文直式照片放入固定比例卡片時必須填滿可視框；依主體位置明確設定 `object-position` 為上、中或下焦點，不得以 `contain` 留下大片空白邊。只有完整構圖本身不可裁切時，才改用與照片比例相符的容器。
- 正文橫圖通常適合滿寬呈現；也可依本篇討論採雙圖或其他已有元件。圖文間距與節奏以實際閱讀驗收，不固定每兩圖之間的段落數。
- 作者指定的照片若只是在標示場景或內容，而版位需要橫式照片，必須回到原始照片庫搜尋同場景或時間相鄰的橫式原圖，再以照片內容逐張確認；不得直接把直式圖塞進橫式框、硬裁成橫幅，或只依檔名與既有 caption 猜測內容。替換後同步修正 alt、gallery title、mapping caption 與 Lightbox registry。
- 雙圖或拼圖依本篇確認的呈現選用，手機配置一併討論與驗收；不得為套模板裁掉作者要保留的主體。
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

- 依本篇入選素材建立 `IG 匯出圖 -> 相機原圖（若有） -> 正文／IG 卡用途 -> Lightbox slide` 映射；取材期間可先標記候選，不為開始講故事而全量匹配 IG 與原圖。
- Hero、正文大圖依需要選相機原圖；IG 卡及點開後採原圖或 IG 調色版，由本篇討論決定，不為畫質自動替換作者的版本選擇。
- IG 卡若原貼文有明顯裁切、調色或版面意圖，使用 IG 匯出圖重現當時貼文；若差異不具意義，直接以原圖配合卡片裁切，避免重複資產。
- 點擊入口依本篇確認的版本映射到 Lightbox；同一影像版本只註冊一次。作者刻意保留的不同裁切／調色版本不機械合併，完全相同影像仍去重。
- 只有 IG 匯出圖、找不到相機原圖時，可以 IG 圖作為公開來源，但不得拿低解析 IG 圖充當 Hero 或大型 Lightbox。
- IG carousel 可因人物隱私移除個別照片；caption 必須維持原文，不以 AI 補寫成「原始貼文」。若另寫補充文字，應清楚區分為文章正文或旅途照片札記。
- 被作者排除的照片不得進公開 derivatives、可見卡片或隱藏 gallery registry；私人候選原檔保留，不因排除公開就自動刪除或搬移。
- IG 匯出圖若需要公開，同樣必須經 image pipeline 轉為 WebP 並清除 metadata；不得直接複製 Takeout 檔案到 `docs/`。

先更新 `trips/<journey>/sources/blog/` 與 migration config，再由 builder 產生 `docs/`。不得把 `docs/` 當唯一 source 手工維護。

### 9.6 可選工具：本機 Editor 選圖

- 預設直接由作者集中資料夾看圖、口述與選圖，不先建立 source/config。若作者選擇使用現有 Editor，才建立必要的 template source 與 `status: draft` entry；builder 略過草稿，不加入公開導覽。
- 編輯器「選圖與燈箱」從 `masters/<journey>/<day>/` 讀取本機照片，只回傳低解析、去 metadata 的預覽；不送出相機原檔，也不把 master 路徑寫入 source 或 `docs/`。
- 作者分別標記「正文候選」與「燈箱收錄」，可同時標記；保存為 `trips/<journey>/photo-selections/<entry-id>.json` 的 `draft`。保存草稿不產生新的公開 derivatives，也不修改文章。
- 作者確認整篇選圖後，在 Editor 明確執行「確認選圖並統一轉 WebP」，僅為入選照片產生安全 derivatives，清單狀態改為 `finalized`。轉檔前先核對原圖 hash 與排除清單；原圖變更時回到草稿重新確認。
- 使用 Editor 時以 `finalized` 清單作選圖決策；直接看圖討論時以本篇 plan 引用的作者最終清單／mapping 為準，不假造 Editor 已儲存。工具讀取 `masters/`，不宣稱已支援任意資料夾直接匯入；只有需要時才準備私人工作副本。實際版位、caption、IG 映射與 `gallery_groups` 在定案後補入 source/config，再由 builder 驗證。既有頁面與 WebP 不因新草稿而刪除或重建。

## 10. Stage 6：圖片管線與 Build

先核對最終選圖與 image pipeline 實際輸入範圍。僅讓本次入選圖進入公開轉檔輸入；`--pilot-day` 只限制日期，不等於選圖 allowlist，不可對含未入選候選的資料夾直接執行後宣稱只處理入選圖。

選圖定案並限定輸入後的建議順序：

```powershell
python tools/image_pipeline.py --trip <journey> --dest <dest> [--pilot-day <day>]
python tools/build_trip_html.py --trip <journey> --dest <dest> [--entry <entry-id>]
python tools/validate_images.py
```

必要契約：

- Manifest 頂層至少保存 `pipeline_version`、`quality`、`profiles`、`trip`、`dest` 與完整圖片 entries。
- Cache hit 必須同時符合來源 hash 與 pipeline contract；不能只看輸出檔存在。
- `--pilot-day` 只更新該日 entries，必須保留其他日已存在且契約相容的 entries。
- 若現有 manifest contract 不相容，pilot 必須失敗並要求完整 rebuild，不得靜默覆寫全 manifest。
- Builder 採記憶體緩衝與原子寫入；source missing、mapping miss 或構建錯誤時，不得留下部分發布結果。
- 單篇來源或單篇 config 內容調整使用 `--entry`，只寫入指定文章；不得連帶重建其他文章、Journey Hub 或同步公開 core 資產。
- 共用 CSS／JS、導覽規則、圖片契約、Journey Hub 或 builder 本身變更時，省略 `--entry` 執行全 Journey build。
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
- 可重複使用的 Python 工具一律放在專案 `tools/`，不得散落在 Journey 根目錄或 `research/`。一次性轉換腳本優先使用 inline command；確實需要落地時只能放在 `scratch/<task>/`，完成驗證後連同 `__pycache__` 一併刪除。`research/` 只保存可追溯的 audit、mapping、config evidence 與研究資料，不保存已完成任務的臨時產生器。
- Instagram 原文曾使用第三方或官方攝影圖時，文章可以如實說明，但該圖不得進入本站公開頁、燈箱、`masters/` 或 derivatives；僅保留作者自己的現場照片。
- 移除或 archive 過渡檔前先確認沒有 config、builder、navigation 或文件引用。
- Commit、push、deploy 分別取得授權；selective stage，不混入其他 working-tree 變更。

### 12.1 Editor 單篇發布 Fast Path

本流程適用於作者已完成 HITL、由本機 editor 儲存的單篇 blog 或 timeline 內容修訂。目標是在一般情況下 2～4 分鐘內完成 build、驗證、selective commit、push 與 production 確認，不重新啟動完整文章製作流程。

適用條件：

- 只修改一篇既有 source，且對應單一既有公開輸出。
- 不涉及 migration config、canonical URL、圖片 manifest、公開 derivatives、共用 CSS／JS、builder、validator 或 Journey Hub。
- editor 任務已明確授權本次 selective commit、push 與 Cloudflare production 發布。

執行順序：

1. 讀取 `AGENTS.md` 並執行 `git status -sb`，記錄但不碰任務外 dirty changes。
2. 對該篇執行 builder 的 `--entry <entry-id>`；禁止為單篇文字修改重建整個 Journey。
3. 執行 `python tools/validate_images.py` 與 `git diff --check`。
4. 只 stage 本次 source 與其公開輸出；用 `git diff --cached --name-status` 確認 staged scope 後 commit、push。
5. 依 `CLOUDFLARE_PAGES_DEPLOYMENT.md` 核實部署模式並查最新一筆 production；只回傳 `Source`、`Deployment` 與狀態，已是目標內容時不重複部署。
6. Direct Upload 模式下，Git push 只作 GitHub 保存，不等待不存在的 Git 自動部署。從已授權的目標 commit 建立乾淨 export 或 detached worktree，依部署指引上傳該版本 `docs/`；不直接上傳含無關 dirty changes 的工作目錄。
7. 只有實際確認為 Git integration 時才等待自動部署，每 20～30 秒查一次、最多 60～90 秒；超時先確認原因與既有發布授權，不改服務設定、不擅自擴大部署範圍。
8. 核對 deployment、目標 commit／乾淨 export、live HTTP 200 與 1～2 個本次內容 fingerprint，完成後清理本次臨時 export。文件規定不是當次遠端成功的證據。

下列任一情況必須退出 Fast Path，改走完整 build 與相應驗收：

- 同時修改多篇文章、Journey Hub、navigation 或 migration config。
- 新增、刪除或替換圖片，或變更 manifest／pipeline contract。
- 修改共用 CSS／JS、builder、validator 或發布設定。
- Source 與 output 無法由單一 entry 確定性重建，或 validator／live fingerprint 驗證失敗。

工具輸出應保持精簡：validator 保留結果摘要，Cloudflare 只保留最新 deployment，Git 只列 staged scope、commit 與最終 status。不得把完整 deployment history 或大段未變更 HTML 帶回對話。

## 13. 一頁 SOP Checklist

```text
[ ] 確認作者本次集中候選照片的私人資料夾
[ ] 看圖、聽口述並同步標記想用／不用／待決，不先全量轉檔
[ ] 潤飾前 grillme 討論寫法、分篇、語氣、版型及 IG 欄數
[ ] 在 plan 置頂目前有效決策，不從舊篇硬套設定
[ ] 母稿與最終選圖通過內容／語氣／公開確認
[ ] 只在使用 Editor 時準備必要 draft scaffold，不把它當開始取材的前提
[ ] 核對最終清單與 pipeline 輸入，只為入選圖製作公開縮圖及必要尺寸
[ ] 按本篇決策完成 source/config；IG 原文、照片版本與燈箱映射正確
[ ] 共用導覽、字體、footer 與互動完整；版面平衡、無不合理裁切
[ ] 正文、圖說與實際畫面相符；燈箱唯一註冊、順序可追溯
[ ] 跑對應範圍的 builder、validator、diff check 及桌面／手機視覺檢查
[ ] 單篇修改未寫其他文章；caption／燈箱修正未改壞核准正文及選圖
[ ] 作者集中驗收內容與呈現；系統自行完成技術驗證
[ ] 只在有相應授權時 commit、push、部署並確認 live 結果
[ ] 本次流程改版未回改已完成文章、圖片或公開頁
```

## 14. 流程演進

只有下列情況才修改本 Playbook：

- 新 Journey 的實際 dry-run 顯示流程缺口。
- 同一類錯誤重複發生，且可用明確契約預防。
- 工具鏈或 SSoT 架構改變。
- 作者明確確認往後的工作流程變更。

單篇文章的特殊選圖、笑點或版型，不升格為全域硬規則。每次流程調整應記錄原因，並確認沒有與 Style Guide 或 Roadmap 重複定義。

2026-10-17：依作者確認改為「集中照片、看圖口述同步選圖、潤飾前 grillme 討論、定案後轉檔」，取消固定 IG 欄數與強制黃金範本；Editor scaffold 改為可選。改版不回改任何已完成文章。

本次文件驗證：專案 skill 的兩欄 YAML metadata、4 個本地引用、現行規則一致性與 `git diff --check` 通過；185 個既有 HTML、config、共用程式等檔案的 SHA-256 與改版前一致。未執行圖片轉檔、文章 build 或部署。`skill-creator` 的 Python validator 因現有環境缺少 PyYAML 未能完成，已用 PowerShell 驗證此 skill 實際使用的簡單 metadata 與引用；下一篇的新流程實作與作者 UAT 尚未發生。
