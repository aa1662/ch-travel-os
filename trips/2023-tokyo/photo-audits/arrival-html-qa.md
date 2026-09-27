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
