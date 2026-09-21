# 🇦🇺 2024 Australia 澳洲雙城圖文誌 · 權威執行計畫 (plan_gemini.md)

> **旅程時間**：2024-10-27 ～ 2024-11-03（雪梨 Sydney ＋ 墨爾本 Melbourne）  
> **核心定位**：比照 `2026-Germany` 現代圖文遊記標準（雜誌風 Hero ＋ 圖文交錯 Story-Split ＋ 原生 IG 卡片 ＋ 實戰 Bento 攻略盒 ＋ GLightbox 沉浸式燈箱）。  
> **工作母稿**：`trips/2024-australia/manuscripts/`（6 篇已完成修訂之喜劇母稿，笑點開在自己身上，手足真實互助互動，無不雅負面用語）。  
> **更新確認**：融合 Codex 審查共識與作者最新口述決策（46 樓會議室保留、琴酒研究保留、精確日期定錨）。  
> **更新日期**：2026-09-20  

---

## 一、 旅程時間軸定錨 (Canonical Chronology SSoT)

經作者最新核對與確認，全站時間軸精準鎖定如下：

| 旅程日 | 日期 | 城市 / 區域 | 核心行程與主題 | 文章歸屬 |
| :--- | :--- | :--- | :--- | :--- |
| **Day 1** | 2024-10-27 (Sun) | 雪梨 Sydney | 抵達雪梨、QVB 古鐘、歌劇院白天與夜景、環形碼頭 | **Vol. 01** (`sydney-harbour-and-gulls.html`) |
| **Day 2** | 2024-10-28 (Mon) | 雪梨 Sydney | 達令港水族館、魚市場海鮮盛宴、海德公園披薩皮海鷗空中劫案、BigBus | **Vol. 01** (`sydney-harbour-and-gulls.html`) |
| **Day 3** | 2024-10-29 (Tue) | 雪梨 Sydney | 46 樓會議室高空俯瞰歌劇院、美味袋鼠排、麥覺理夫人石椅夜騎 Lime 電輔車 | **Vol. 02** (`sydney-skyline-and-lazy-zoo.html`) |
| **Day 4** | 2024-10-30 (Wed) | 雪梨 Sydney | 雪梨野生動物園 (Wild Life Sydney Zoo) 全員極致躺平昏睡、市區漫步 | **Vol. 02** (`sydney-skyline-and-lazy-zoo.html`) |
| **Day 5** | 2024-10-31 (Thu) | 雪梨 ➔ 墨爾本 | 跨城大移動：4,000 元機票完勝夜車、入住郊區 Novotel 嗑熱牛肉麵、免費電車全車不刷卡文化衝擊 | **Index 特刊** (`index.html` 核心轉場專題) |
| **Day 6** | 2024-11-01 (Fri) | 亞拉河谷 Yarra Valley | 聽妹妹的話成行酒莊微醺、琴酒擠眉弄眼自嘲、午後撥雲見日遇見封神大草原 | **Vol. 03** (`yarra-valley-wine-and-grassland.html`) |
| **Day 7** | **2024-11-02 (Sat)** | 丹頓農 ➔ 菲利普島 | 彩虹木屋、普芬比利蒸汽火車腿懸空炭煙洗禮、Maru 袋鼠、夜戰海邊冷風看神仙小企鵝歸巢 | **Vol. 04** (`puffing-billy-and-fairy-penguins.html`) |
| **Day 8** | **2024-11-03 (Sun)** | 墨爾本 ➔ 疏芬山 ➔ 返台 | 拒絕在市區當刷卡奴隸！自力救濟搭週末特惠 V/Line 火車、警長鳴槍、關帝廟、地底礦坑、90 歲神秘老奶奶蒸發、木造保齡球館 ➔ 夜班機返台 | **Vol. 05** (`sovereign-hill-gold-rush.html`) |

---

## 二、 核心內容與隱私決策確認 (Editorial & Privacy Boundaries)

1. **46 樓會議室場景（作者確認保留）**：
   - 保留「46 樓會議室」的高空神級視野與壯麗視角作為標題與特色（展現由高而下的宏大氣場），公司具體名稱維持去識別化為「澳洲會員所 / 澳洲辦公室」。
2. **琴酒品味與研究（作者確認保留）**：
   - 保留對琴酒歷史工藝的生動探索，以及現場品嚐時面部神經抽筋的幽默自嘲。
3. **亞拉河谷手足真實互動（已修正完畢）**：
   - 已全面修正 `manuscripts/comedy_day06.md`，徹底剔除「手足背刺」與「淘金好土」等腦補假衝突，回歸妹妹提議去酒莊放鬆、作者欣然相伴的真實旅伴默契；笑點集中在自己努力裝高雅破功與遇見大草原的意外驚喜。
4. **同事照片嚴格排除**：
   - 審計確認：Post #6 中之 `17896643601090107.jpg`（三位主管陽台合影）100% 標記 `EXCLUDED_COLLEAGUE` 排除，其餘 7 張純景觀與餐點照片合規收錄。

---

## 三、 圖片與燈箱底層架構契約 (Image & Lightbox Architecture)

1. **IG 貼文圖片「全數收錄」**：
   - 22 則 IG 貼文的所有靜態照片完整於 `.ig-post-card` 展示（排除影片與同事照）。
2. **照片「重覆使用與原圖映射」**：
   - 內文 (`.story-split`) 可重覆引用 IG 照片，並優先調用 `Mobile Devices` 的高解析度相機原檔生成之 WebP。
3. **每篇獨立 Hero**：
   - 每篇頂部必備視覺衝擊 Hero 封面，且該照片可在內文中再次出現。
4. **GLightbox「橫直分組、唯一 Slide、時間升冪」**：
   - **橫式 (Landscape) 與 直式 (Portrait) 視界分組**，各組依拍攝時間升冪排序。
   - 同一張照片無論在 Hero、內文或 IG 出現幾次，底層 GLightbox 只有**唯一一個 Slide 節點**，點開後線性瀏覽，絕不重複。

---

## 四、 篇章規劃與檔案目錄責任

### 1. 篇章結構（5 大核心專刊 ＋ Index 轉場特刊）
- **Vol. 01 (Day 1-2)**: `sources/blog/sydney-harbour-and-gulls.html`
- **Vol. 02 (Day 3-4)**: `sources/blog/sydney-skyline-and-lazy-zoo.html`
- **Index 特刊 (Day 5)**: `sources/index.html` 內嵌雙城轉場專題
- **Vol. 03 (Day 6)**: `sources/blog/yarra-valley-wine-and-grassland.html`
- **Vol. 04 (Day 7)**: `sources/blog/puffing-billy-and-fairy-penguins.html`
- **Vol. 05 (Day 8)**: `sources/blog/sovereign-hill-gold-rush.html`

### 2. 規範目錄結構
```text
trips/2024-australia/
├── plan_gemini.md                  # 唯一權威執行計畫 (SSoT)
├── manuscripts/                    # 6 篇正式喜劇工作母稿 (已全數移入)
│   ├── comedy_day01_02.md
│   ├── comedy_day03_04.md
│   ├── comedy_day05.md
│   ├── comedy_day06.md             # 已修正手足互動
│   ├── comedy_day07.md
│   └── comedy_day08.md
├── intake/                         # 原始口述與素材索引
│   ├── INTAKE_CONTEXT.md
│   ├── Oral_逐字稿.md
│   └── ORAL_MEMORIES_*.md
├── research/                       # 資產審計證據
│   └── media-audit.csv             # 188 個媒體項目的審計與排除清單
├── sources/                        # 正式發布原始碼 (待建立)
│   ├── index.html                  # 旅程首頁 (含 Day 05 轉場專題)
│   └── blog/                       # 5 篇圖文遊記正式 HTML
└── blog-migration.json             # 導覽與 URL 映射配置
```

---

## 五、 開工實施里程碑

- **Milestone 1：媒體審計與排查**（✅ 已完成，`media-audit.csv` 產出，鎖定同事照片排除）。
- **Milestone 2：Vol. 03 亞拉河谷 (Day 6) 構建與發布**（✅ 已完成，大草原 Hero、微醺琴酒、實戰 Bento、100% 合規）。
- **Milestone 3：Vol. 04 普芬比利與小企鵝 (Day 7) 構建與發布**（✅ 已完成，雙腳懸空蒸汽火車、企鵝歸巢夜戰、100% 合規）。
- **Milestone 4：Vol. 05 疏芬山淘金鎮 (Day 8) 構建與發布**（✅ 已完成，神祕老奶奶、警長鳴槍、木造保齡球、17 張精選 Caption 重寫、圖集客觀中性降級）。
- **Milestone 5：雪梨篇全面展開 (Vol. 01 Day 1-2 & Vol. 02 Day 3-4)**（🚀 下一階段推進重點）。
- **Milestone 6：旅程總首頁 (Index 特刊 Day 5 雙城轉場) 整合與全站收官**。

---

## 六、 製作復盤與借鏡手冊（Day 08 經驗沉澱與後續篇章 SOP）

經 Day 08 深入打磨與人機協作實測，沉澱出以下 5 大核心經驗與後續篇章標準工作流（SOP）：

### 1. 核心教訓與痛點復盤
1. **關鍵高光照片優先錨定**：寫稿與排版前必須先掃描 raw camera 與 IG 素材庫，確認「人設與情節高光」（如老奶奶背影、特殊道具）有對應的照片證據，避免文章寫完才發現漏圖。
2. **Hero 首圖焦點守護**：直幅原圖強裁橫版時，不得直接更換照片，應優先透過 `style="object-position: center YY%;"` 調整重心，保全天空與地面人群。
3. **換圖與 Caption 必須原子化**：在線上視覺編輯器更換照片時，`src`、`alt` 與 `blog-migration.json` 的 `title` 必須同步更新，嚴禁殘留舊版描述。
4. **拒絕「時間區間暴力打標」**：EXIF 具備時鐘與 GPS，但「沒有眼睛」。嚴禁將某個特定情節（如「警長鳴槍」）批次覆蓋到整個時段的所有隨手拍照片上。
5. **嚴守人機協作邊界**：作者在編輯器定稿的正文段落（幽默感、自嘲、吐槽、生活哲學、冷知識）由作者掌控，AI 不擅自做學術化刪修或稀釋語氣。

### 2. 後續篇章「兩層式圖片標籤架構」
- **精選層（正文 15~20 張 Story Photos）**：
  - 規格：具備強烈敘事性、包含時間戳、呼應段落情節。
  - 流程：AI 必須呼叫 Vision 視覺審查主體與細節，產出對照表經確認後寫入。
- **全量層（大圖集 50~100 張 Gallery Photos）**：
  - 規格：**客觀中性降級（Objective Neutral Fallback）**。
  - 公式：`[宏觀地點／景區名稱] + 現場實境隨影 · [MM/DD HH:MM]`
  - 範例：`巴拉瑞特百年車站古典街景隨影 · 11/03 11:08`、`疏芬山淘金鎮十九世紀實境隨影 · 11/03 11:37`。
  - 效益：無論點開碎石路面、牆角或天空，都 100% 成立且自然，絕無破綻。

### 3. 下一篇章啟動 SOP
1. **素材盤點先行**：展開 Takeout 與 IG，標出該日 5~8 個不可替代的高光畫面。
2. **母稿結構與 Bento 定稿**：梳理 4~5 個 Acts 結構，規劃實戰 Bento 提示卡片。
3. **雙層 Caption 設計**：正文精選專屬打標，圖集客觀中性打標。
4. **構建與線上預覽**：原子編譯、調整 Hero 焦點，交由作者在線上編輯器進行第一手驗收與潤飾。
5. **全站合規驗證**：100% 通過 `validate_images.py` 零 404 死鏈。
