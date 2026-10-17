# 日本 Country Hub QA

更新日期：2026-09-28

## 範圍

- 建立日本統一入口 `docs/japan/index.html`。
- 收錄已完成的 `2023 東京出差散步` 與 `2026 關西盛夏漫遊`。
- 全球首頁的日本主導覽、Hero CTA、旅程卡與手機 Dock 統一指向日本入口。
- 東京與大阪 Journey 首頁、文章頁補上日本層級導覽。
- 德國既有頁面不在本次搬移範圍。

## Source of truth

- 設定：`countries/japan/country.json`
- 維護來源：`countries/japan/sources/index.html`
- 公開輸出：`docs/japan/index.html`
- 建構器：`tools/build_country_html.py`

## 自動驗證

- `python tools/build_site_html.py --check`：通過。
- `python tools/build_country_html.py --all --check`：通過。
- `python tools/validate_images.py`：通過；83 份 HTML、4 份 JS、3,983 張公開圖片，沒有死鏈或圖片契約違規。

## 瀏覽器驗收

- 日本首頁 Hero、雙 Journey 卡、典藏入口與手機 Dock 可正常顯示。
- 全球首頁可進入日本首頁。
- 日本首頁可分別進入東京與關西 Journey。
- 東京與關西文章麵包屑可回到日本首頁。
- 手機版 Hero 與導覽沒有遮擋主要內容。

## 尚未執行

- 未 commit、push、deploy 或 publish。
