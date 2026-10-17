# 2023 東京旅程首頁 HTML QA

## 來源與輸出

- Source：`trips/2023-tokyo/sources/index.html`
- Output：`docs/2023-tokyo/index.html`
- Hero master：`masters/2023-tokyo/index/20231114_135023.jpg`
- Hero 公開資產：`docs/2023-tokyo/images/index/20231114_135023-*.webp`

## 首頁契約

- 首頁是旅程封面與兩篇文章入口，不另寫成第三篇遊記。
- Hero 使用皇居外苑、護城河與城市天際線的橫式俯瞰照。
- 內容順序：Hero → 旅程背景與摘要 → 兩篇入口卡 → 三日動線 → 收束與 footer。
- 文章卡桌機雙欄、手機單欄；只連結已完成的兩篇文章。
- 兩篇文章的系列標題與頂部導覽均已接回旅程首頁。

## 驗證

- `python tools/build_trip_html.py --trip 2023-tokyo`：首頁與兩篇文章共 3 頁原子構建成功。
- `python tools/validate_images.py`：全站 82 份 HTML、3983 個公開圖片、4 份 JS 全數通過，零死鏈。
- 行動版實際瀏覽：Hero、CTA、內容卡、三日動線、mobile dock 與 footer 正常，無可見水平溢出。
- 排除照 `18002494235179485.webp`：公開引用 0、公開 derivatives 0。
- 首頁 footer 已連至 About CH、全球旅程與 Instagram，不再顯示內部製作來源說明。
- 兩篇文章的系列標題、麵包屑、正文結尾與 mobile dock 均提供東京旅程首頁入口；第一篇另提供下一篇，第二篇另提供上一篇。
