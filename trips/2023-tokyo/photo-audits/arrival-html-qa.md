# 第一篇 HTML 本機驗證

日期：2026-09-27。尚未 commit／push／發布，作者版面 UAT 待進行。

## 範圍

- 五則 IG，28 張保留照片；Hero 與正文相機圖各一張，共 30 個唯一圖集項目。
- 第一篇 source／migration config／公開 derivatives／HTML；共用 CSS 新增僅套用 `.photo-essay` 的樣式。
- Builder 新增 `article_series_href` 可省略旅程首頁連結；既有旅程預設值不變，兩個 focused regression 通過。
- 未改動第二篇、全球首頁或另一討論串的 About Me 內容。

## 已執行

- 圖片管線初次：30 張；第二次：Cache Hit 30、新生成 0。
- 圖片逐檔 hash、最大長邊 1600、禁止原始 JPG 公開、EXIF/XMP/ICC 移除：通過。
- 首次全旅程 build 與後續單篇 rebuild：HTML SHA256 完全一致。
- `python -m unittest tools.tests.test_navigation_contract`：5 tests 通過。
- `python tools/validate_images.py`：3842 圖片、52 HTML、3 JS；零失效連結與資產問題。
- `git diff --check`：通過，僅 Git 既有 LF/CRLF 提示。
- 真實 HTTP 預覽：`http://127.0.0.1:8765/2023-tokyo/blog/tokyo-arrival-meiji-jingu.html`。
- Playwright 桌機 1440×1000、手機 390×844：各為四欄與兩欄；無水平溢出，30 張圖全數載入。
- 30 個照片入口逐一點開及關閉，全部命中對應 WebP 版本；registry 30 個唯一 URL。
- 圖集按鈕、桌機下一張及 Escape 關閉：通過。手機由既有 GLightbox 觸控介面處理，沒有可點擊的桌機下一張箭頭；本次未模擬實體觸控滑動。
- 第一篇 A3 無 caption；公司名稱照片未進入 master 工作集、公開目錄、HTML 或 registry；永久排除規則已加入。
- 親自檢視桌機與手機全頁截图：`.playwright-mcp/tokyo-desktop.png`、`tokyo-mobile.png`；手機上方截圖 `tokyo-mobile-top.png`。截圖為本機忽略檔，非公開資產。全頁截圖拍攝後僅移除重複圖集按鈕，再重建驗證。

## 已知限制與人工驗收

- JavaScript console 無 error；既有 GLightbox 開啟時有一則 aria-hidden 焦點警告，未影響本次點圖／換圖／關閉。此為共用燈箱可及性待改善項，未擴大本次修改到互動引擎。
- 本輪製作中修正：空的直式圖集入口與重複圖集按鈕；尚未進行本版人工 UAT（0 次）。
- 仍未接通：東京旅程首頁、第二篇 HTML、上下篇導覽與正式發布。頁面目前不暴露這些未完成連結。
- 接下來作者只需看閱讀節奏、照片選擇與呈現，不需自行核對 hash 或指令輸出。


## 作者第一輪版面回饋後驗證

- 參考澳洲版模改開場、導言卡、字體、三欄 IG、手機 dock 與 compact 導覽；作者指定五張照片自公開資產移除，私人檔保留。
- 25 張全部命中圖片快取；刪除照片無公開衍生檔或 HTML 引用，排除規則持續生效。
- 桌機 1440：三欄；手機 390：兩欄，均無橫向溢出；字體與全部圖片載入成功。
- 25 個照片入口實際逐一點開、核對 URL、關閉成功；手機 dock 圖集開啟成功。
- 全站 validator：3843 圖片、80 HTML、4 JS，通過；導航 regression 5 tests 通過；重建 HTML hash 一致；diff check 通過。
- 桌機與手機全頁視覺檢查：`.playwright-mcp/tokyo-v2-desktop.png`、`tokyo-v2-mobile.png`。Console 無 error，既有 GLightbox aria-hidden 警告仍在。
- 人工 UAT 1 輪 changes requested 已集中修正；新版呈現待作者確認，未 commit 或發布。

## 澳洲實頁逐項對齊

- 依作者指定的 `http://127.0.0.1:5500/docs/2024-australia/blog/sydney-harbour-and-gulls.html` 實際渲染結果重新比對，不再只參考版模。
- 桌機兩頁 Hero 均為 920px 卡片、897px 的 16:9 上方大圖、米色背景、22px 圓角，以及下方標籤／大標／導言／資料列；東京標題同為 Noto Sans TC 41.6px。高度差只來自文字量。
- 修正共用 CSS 快取版本，避免瀏覽器繼續載入前一版左右分欄樣式。
- 手機 390px 驗證：Hero 335px、圖片 312×176px、IG 兩欄、無水平溢出、無破圖。
- 導覽 regression 5 tests、全站 validator（3843 圖片、80 HTML、4 JS）與 `git diff --check` 通過。

## IG 雙欄、Hover 與 Footer

- 五組 IG 收斂為 4／8／2／2／4 張，桌機與手機均為兩欄；圖片 `sizes` 同步調整為桌機 460px。
- 三張版面 UAT 移除圖已加入可重建排除清單、manifest／registry／公開衍生圖同步清理；私人原檔保留。
- 桌機 hover 實測由 `none` 變為 `scale(1.025)` 並降低亮度；鍵盤 focus 有可見外框。
- 深色 footer 已補回品牌、系列名稱、全球旅程、照片與回頂部入口；手機額外保留 dock 空間。
- 桌機兩欄各 457px、手機兩欄各 156.5px；22 個照片入口逐一點開核對成功，無破圖或橫向溢出。
- 圖片管線第二次 22 張全數 cache hit；全站 validator 更新為 3831 圖片、80 HTML、4 JS，通過。
