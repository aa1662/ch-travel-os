# 2024 Australia｜發布前技術品質稽核

- 稽核日期：2026-09-25
- 稽核範圍：Day 01–02、Day 03–04、Day 05 Journey Interlude、Day 06、Day 07、Day 08
- 排除範圍：文章內容、文風、敘事事實與 caption 文案正確性
- 稽核對象：`trips/2024-australia/sources/`、`trips/2024-australia/blog-migration.json`、`docs/2024-australia/`、共用公開資產與本機實際渲染結果

## 發布判定

**技術面可發布（Go）。**

現有構建、圖片安全、連結、SEO metadata、桌機／手機渲染皆通過。原先阻擋發布的 Git release set 已用精確 allowlist 收斂：

1. Day 03 正式頁已納入發布範圍。
2. Day 03、Day 05、Day 08 共 16 個新增 WebP derivatives 已納入發布範圍。
3. Source、migration config、manifest、builder、validator 與公開輸出已成套納入。

Day 07 的 Lightbox SSoT 問題已修正並通過實際點擊驗證；澳洲篇燈箱也已依作者決策統一不顯示標題。Day 01–02 與 Day 03–04 的 heading level 已修正，且不改變文字或視覺樣式。

## Findings

### 已修正｜Day 07 IG 圖片改用唯一 Lightbox registry

**證據**

- Source 從 [`puffing-billy-and-fairy-penguins.html`](../sources/blog/puffing-billy-and-fairy-penguins.html) 第 378 行開始，IG 圖片使用 `class="glightbox" data-gallery="ig-post-*"`；同類寫法共 36 個。
- Published output 從 `docs/2024-australia/blog/puffing-billy-and-fairy-penguins.html` 第 494 行開始仍保留這 36 個直接註冊項目。
- 同一頁底部 registry 另有 89 個 slide，且上述 IG 圖片已經包含在 registry 中。
- 實際瀏覽器操作：頁尾「瀏覽完整圖集」正常開啟 58 張橫式 registry slide；點第一張 IG 縮圖則另開只有 6 張的 `ig-post-15` 圖集。相同影像因此存在兩套 Lightbox 入口與分組。

**調整結果**

- 36 個 IG anchor 已改為 `gallery-opener`，正文照片、位置、尺寸、焦點與顯示順序均未改動。
- Published output 的 registry 外 `a.glightbox` 已歸零；89 個 registry slide 無重複 ID，47 個 opener 全部命中既有 slide。
- 實際從 IG 縮圖點入後，會開啟對應的完整橫式 registry（58 張），不再建立 6 張的第二套 `ig-post-*` 小圖集。
- `tools/validate_images.py` 已新增 registry 外直接註冊 `a.glightbox` 的阻擋規則。

**驗證結果**

- 完整 build 成功。
- 全站 validator 100% 通過。
- Browser smoke test 確認點擊 IG 縮圖後顯示正確圖片、完整圖集張數正確，燈箱內沒有非空標題或描述。

### 已修正｜17 個發布必要檔案納入 release set

**證據**

目前 `git ls-files --others --exclude-standard` 顯示以下正式發布資產尚未追蹤：

- `docs/2024-australia/blog/sydney-skyline-and-lazy-zoo.html`
- `docs/2024-australia/images/day-03-04/`：2 張照片、共 8 個 WebP derivatives
- `docs/2024-australia/images/day-05/`：1 張照片、共 4 個 WebP derivatives
- `docs/2024-australia/images/day-08/20241103_165437-*`：共 4 個 WebP derivatives

Day 03 output 已由 Journey Index 連結；Day 03、Day 05、Day 08 derivatives 也已進入目前的 `image-manifest.json`。本機 validator 能通過，是因為這些 untracked 檔案存在於 working tree；Git-based deployment 不會自動帶上未追蹤檔案。

**處理結果**

- 以精確 allowlist 納入 Day 03 正式頁與 16 個必要 WebP，沒有使用 `git add .`。
- C2C 設定、測試草稿、未採用 manuscript 與其他非發布檔案均排除。
- Staged 清單與 manifest 對照後再次執行全站 validator。

### 作者決策｜澳洲篇燈箱統一不顯示 title

原先將 Day 03–04 的空 title 列為 metadata 完整性問題；作者已確認燈箱不需要顯示標題，因此此項不再視為 finding。

- `blog-migration.json` 已設定 `show_gallery_titles: false`，作用範圍限於 2024 Australia。
- Builder 在此設定下不輸出 `data-title`；原有 migration 描述資料仍可保留，不影響正文 caption 或 `alt`。
- Validator 會依旅程設定阻擋 registry 再次輸出 `data-title`。
- 五篇文章共 338 個 registry slide 均不輸出 title，瀏覽器實測沒有非空燈箱標題或描述。

### 已修正｜Day 01–02 與 Day 03–04 的 Bento heading level

**證據**

- Day 01–02 source 第 1401 行為 Bento 區塊 `h2`，其四張卡片在第 1407、1421、1435、1449 行直接使用 `h4`。
- Day 03–04 source 第 619 行為 Bento 區塊 `h2`，卡片在第 622、628 行直接使用 `h4`。
- 其餘頁面沒有偵測到 heading level jump。

**處理結果**

- 六個 Bento 卡片標題已由 `h4` 改為 `h3`。
- 文字、inline style 與視覺呈現均維持原狀；文件階層改為 `h2 → h3`。

### 已修正｜Validator 補上唯一 registry 契約

`python tools/validate_images.py` 現在會阻擋 `.gallery-registry` 外的可見 `a.glightbox`，避免正文、Hero 或 IG 縮圖再次直接註冊 slide。

Gallery title 依旅程設定為可選欄位；2024 Australia 已明確選擇不顯示，不應加入「title 不得為空」的檢查。

## 通過項目

### SSoT 與構建一致性

- 在隔離的 scratch build root 執行完整 `build_trip_html.py`，成功構建五篇 blog 與 Journey Hub，零 builder error。
- 六個 rebuilt output 與目前 `docs/2024-australia/` 對應檔案 SHA-256 完全一致。
- 代表目前正式輸出可由 source、migration config 與 manifest 確定性重建，沒有只存在 `docs/` 的手改內容。
- `core/css/style.css`、`core/js/app.js`、`core/js/main.js`、GLightbox CSS／JS 與 `docs/core/` 公開副本 hash 全數一致。

### 圖片、連結與 metadata

- `python tools/validate_images.py`：掃描 3,716 個公開圖片、50 份 HTML、3 份 JS，零錯誤。
- 公開圖片全部為 WebP，尺寸、檔案大小、可解碼性、EXIF／GPS 清除與 manifest 對應通過。
- 六個頁面所有 `<img>` 皆有非空 alt、width、height；沒有公開 JPG／PNG 原圖引用。
- 無重複 HTML id、無寫死「N 張現場實拍」badge、無缺失 opener target。
- 五篇文章的 canonical、`og:url`、description 與 migration contract 一致；Journey Hub 的 canonical 與 `og:url` 彼此一致。
- 全站內部連結、anchor 與本地資產零 404。

### Gallery registry

- 五篇 blog 的 registry slide 順序與 `blog-migration.json` 完全一致。
- Registry 本身無重複 `data-gallery-image`。
- Day 01–02、Day 03–04、Day 06、Day 07、Day 08 的正文／IG 圖片全部使用 opener 映射，沒有可見 GLightbox 直接註冊。
- 澳洲五篇文章的 registry 均不輸出 `data-title`，符合作者指定的無標題燈箱設計。
- 五篇文章的「瀏覽完整圖集」皆能實際開啟 GLightbox；按 Escape 可正常關閉。

### 實際瀏覽器 smoke test

測試尺寸：桌機 1440×900、手機 390×844。

六個 URL 在兩種 viewport 下均符合：

- HTTP 200。
- `overflowX = 0`，沒有整頁水平溢位。
- H1 與 main landmark 存在。
- console error 為 0，無 page error。
- 頁面載入圖片數與靜態 HTML audit 一致。

## 發布回歸紀錄

1. 已修正 Day 01–02、Day 03–04 的 Bento heading level。
2. 已執行完整 build：

   ```powershell
   python tools/build_trip_html.py --trip 2024-australia --dest 2024-australia
   ```

3. 已執行：

   ```powershell
   python tools/validate_images.py
   git diff --check
   ```

4. 已完成六頁桌機／手機 smoke test，並特別驗證 Day 07：
   - 可見區域 `a.glightbox` 為 0。
   - 36 個 IG opener 都命中唯一 registry item。
   - 從 IG 縮圖進入後使用的是 registry 對應圖集，沒有第二套 `ig-post-*` slide group。
5. 已建立 selective staged allowlist，納入 17 個必要 output／WebP，並排除 C2C、草稿與暫存檔。

## 結論

整體工程狀態可發布：確定性構建、資產安全、SEO metadata、連結、桌機／手機渲染、共用資產同步、heading hierarchy 與 Lightbox SSoT 都已通過；正式 output 與新增 WebP 也已納入同一 release set。
