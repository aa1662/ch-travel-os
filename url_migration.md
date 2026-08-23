# CH Travel OS 2.0 - Journey Namespace and URL Migration Plan

## 目的

目前 docs/germany/ 同時代表「Germany 地區」與「2026 Germany 這趟 Journey」，未來新增 2027 或 2028 Germany 時，index、day-XX、blog 與 images 都會撞名。

目前 GitHub 版本只供作者試看，尚未正式對外發布，因此一次完成乾淨遷移，不保留舊 URL、不建立 redirect。

本次包含兩個連續動作：

1. Journey namespace：germany -> 2026-germany。
2. Blog filename：16 篇改成 Place/Theme slug；Day 只保留在 Timeline 與 Journey metadata。

不得只做其中一半，也不得擴大成通用 routing framework。

## 遷移後公開結構

~~~text
docs/
├── index.html
├── core/
├── germany/
│   └── index.html                 # Germany Country Hub，只列歷年 Journey
└── 2026-germany/
    ├── index.html                 # 2026 Germany Journey Hub
    ├── day-01.html ... day-15.html
    ├── blog/
    │   └── 16 篇 Place/Theme URL Blog
    ├── images/
    └── image-manifest.json
~~~

未來新增旅程：

~~~text
docs/2027-germany/
docs/2028-germany/
~~~

Germany Country Hub 不擁有 Day、Blog、Images 或文章正文，只負責連到不同年份的 Journey Hub。

## 最終 Blog URL Mapping

下表是唯一命名依據。Gemini 不得自行改寫 slug。

| ID | 現有檔名 | 新檔名 |
| --- | --- | --- |
| Day 01 | day-01-blog.html | salzburg-to-hallstatt.html |
| Day 02 | day-02-blog.html | hallstatt-winter.html |
| Day 03 | day-03-blog.html | ingolstadt-wuerzburg.html |
| Day 04 | day-04-blog.html | bamberg-old-town.html |
| Day 05 | day-05-blog.html | nuremberg-kaiserburg.html |
| Day 06 | day-06-blog.html | rothenburg-winter.html |
| Day 07 | day-07-blog.html | wuerzburg-residenz.html |
| Day 08 | day-08-blog.html | heidelberg-castle.html |
| Day 09 | day-09-blog.html | hanau-frankfurt.html |
| Day 10 上 | day-10-speyer-blog.html | speyer-cathedral.html |
| Day 10 下 | day-10-colmar-blog.html | colmar-little-venice.html |
| Day 11 | day-11-blog.html | eguisheim-basel.html |
| Day 12 | day-12-blog.html | garmisch-das-graseck.html |
| Day 13 | day-13-blog.html | neuschwanstein-winter.html |
| Day 14 | day-14-blog.html | partnachklamm-ice.html |
| Day 15 | day-15-blog.html | munich-departure.html |

新的完整 URL 範例：

~~~text
https://aa1662.github.io/ch-travel-os/2026-germany/blog/hallstatt-winter.html
https://aa1662.github.io/ch-travel-os/2026-germany/day-02.html
~~~

## 不變項目

- trips/2026-germany/ 的 Journey source 根目錄不改名。
- Blog entry id、圖片 day folder 與 Timeline day filename 不變。
- 不改寫、刪節或潤飾文章正文。
- 不建立舊 URL redirect、相容頁或 duplicate article。
- 不搬移 masters/，不重新命名圖片。
- 不重做 Germany Journey Hub 的版面。
- Germany Country Hub 只做最小歷年入口，不做新的行銷首頁。
- 不 commit、不 push、不 deploy。

## Source of Truth

| 資料 | Source of truth |
| --- | --- |
| Journey identity | trips/2026-germany/ |
| Published destination | migration config 的 dest = 2026-germany |
| Blog URL、canonical 與導航 | trips/2026-germany/blog-migration.json |
| Timeline URL 與 Blog link | trips/2026-germany/timeline-migration.json |
| 文章正文 | trips/2026-germany/sources/blog/ |
| Timeline 正文 | trips/2026-germany/sources/timeline/ |
| Journey 精選故事資料 | docs/2026-germany/index.html 的 window.__JOURNEY_STORIES__ |
| 公開圖片 contract | docs/2026-germany/image-manifest.json |
| 公開衍生輸出 | docs/2026-germany/ |

Builder、editor server 與 validator 必須讀取 config 的 dest，不得再由 trip slug 最後一段推算成 germany。

目前 Journey Hub 本身是手工維護的 published page，因此精選故事資料暫由該頁擁有；core/js/app.js 只保留共用抽選行為，不再承載 2026 Journey 內容。

## 執行步驟

### 1. Preflight

~~~powershell
git status --short --branch
rg -n "docs/germany|/germany/|\"dest\": \"germany\"|dest_slug=\"germany\"" core docs trips tools
rg -n "day-(?:0[1-9]|1[1-5])-blog\.html|day-10-(?:speyer|colmar)-blog\.html" core docs trips tools
~~~

記錄原始命中與 working tree。不得 stage、revert、覆蓋或清除無關變更。

### 2. 搬移 Journey 發布目錄

~~~powershell
git mv docs/germany docs/2026-germany
~~~

搬移後 relative depth 不變：

- Blog 到 core 仍為 ../../core/。
- Timeline 與 Journey Hub 到 core 仍為 ../core/。
- Blog 到 images 仍為 ../images/。

不得複製後留下舊 Journey 內容。

### 3. 更新 Journey destination contract

同步更新：

- blog-migration.json
  - dest -> 2026-germany
  - 所有 output -> docs/2026-germany/blog/...
  - 所有 og_url -> /2026-germany/blog/...
  - 所有 og_image -> /2026-germany/images/...
- timeline-migration.json
  - dest -> 2026-germany
  - 所有 output -> docs/2026-germany/day-XX.html
  - 所有 og_url -> /2026-germany/day-XX.html
  - 所有 og_image -> /2026-germany/images/...
- docs/2026-germany/image-manifest.json
  - top-level dest -> 2026-germany
  - 所有 derivative publicPath：germany/images/ -> 2026-germany/images/

先更新 manifest path，再執行 image pipeline，避免 cache hit 把舊 publicPath 留在新 manifest。

### 4. 更新工具的 dest ownership

只做支援多 Journey 所需的最小修改：

- build_trip_html.py
  - 不再預設 germany。
  - 未傳 dest 時讀取 blog-migration.json 的 dest。
  - main entry 只指定 trip 2026-germany，或明確使用 config dest。
- build_timeline_html.py
  - 同樣讀取 timeline-migration.json 的 dest。
  - 移除註解與 legacy replacement 中硬編碼的 docs/germany。
- server.py
  - 不得再使用 trip_slug.split("-")[-1] 推算 dest。
  - list-images、save、restore、preview publish 都從該 Journey config 取得 dest。
- validate_images.py
  - 移除 docs/germany 與 germany/blog 的硬編碼。
  - 從 manifest 或 migration config 辨識 2026-germany。
  - 從每個 Journey Hub 的 window.__JOURNEY_STORIES__ 驗證故事 URL 與圖片。
- core/js/app.js
  - 將 16 筆 ALL_STORIES 內容移出 core。
  - 改為讀取 window.__JOURNEY_STORIES__；若頁面沒有 featured-grid，不要求故事資料。
- docs/2026-germany/index.html
  - 在載入 core/js/app.js 前宣告 window.__JOURNEY_STORIES__。
  - 內容沿用現有 16 筆資料，只更新 Journey path 與 Place/Theme filename。

不要為此新增 router、database、redirect module 或 framework。

### 5. 執行 16 組 Blog rename

依「最終 Blog URL Mapping」，在下列兩個目錄逐一使用 git mv：

~~~text
trips/2026-germany/sources/blog/
docs/2026-germany/blog/
~~~

要求：

- 每個舊檔只對應一個新檔。
- 改名前確認舊檔存在、新檔不存在。
- source 與 published 目錄最後各有 16 篇。
- 舊檔不保留。

### 6. 全專案 exact replace

依 mapping 精確替換所有舊 Blog filename，並將公開 Journey base 從 germany/ 改成 2026-germany/。

至少涵蓋：

- blog-migration.json 的 source、output、og_url、prev_link、next_link。
- timeline-migration.json 的 blog_link。
- sources/blog/*.html 的 canonical、og:url、navbar、prev/next、mobile dock。
- sources/timeline/*.html 內硬編碼的 blog/day-XX 連結。
- docs/2026-germany/index.html 的 window.__JOURNEY_STORIES__ 16 個 URL 與圖片。
- core/js/app.js 只改成消費 Journey-owned stories，不保留 2026 專屬內容。
- docs/index.html 的 Journey Hub、精選 Blog 與圖片路徑。
- docs/2026-germany/index.html 的 Blog 入口。
- previews/、prompts/ 中的 source path 與公開 URL。
- 其他由 rg 找到的精確引用。

Gemini review 特別指出的三項必查：

1. ALL_STORIES：16 筆內容移到 Journey Hub 的 window.__JOURNEY_STORIES__，url 全部換成 Place/Theme filename；core 只保留抽選行為，build 後確認 docs/core/js/app.js 同步。
2. Timeline sources：不可只改 timeline-migration.json，sources/timeline/*.html 的硬編碼連結也要清掉。
3. Validator：必須同時驗證 href、canonical、og:image、Journey-owned stories 圖片與新 Journey root。

只修改 path、URL 與必要工具參數，不順手調整文案、CSS、圖片或互動。

### 7. 建立最小 Germany Country Hub

在 docs/germany/index.html 建立讀者視角的最小目錄頁：

- 標題為 Germany／德國旅程。
- 只列出「2026 德南冬季自駕」並連到 ../2026-germany/index.html。
- 可使用一張既有公開 WebP 作 Journey cover。
- 不複製 2026 Journey Hub 的行程、Blog 卡片或正文。
- 不新增行銷式 Hero、施工詞彙或未來空卡片。

docs/index.html：

- Germany 地區入口連到 germany/index.html。
- 2026 Journey 與精選文章入口直接連到 2026-germany/。
- 圖片路徑改成 2026-germany/images/。

### 8. Build

~~~powershell
python -m py_compile tools\build_trip_html.py tools\build_timeline_html.py tools\image_pipeline.py tools\server.py tools\validate_images.py
python tools\image_pipeline.py --trip 2026-germany --dest 2026-germany
python tools\build_timeline_html.py
python tools\build_trip_html.py
~~~

圖片 pipeline 預期：

- master 數量不變。
- moved derivatives 100% cache hit。
- manifest top-level dest 與所有 publicPath 都是 2026-germany。
- 不生成 docs/germany/images/。

若 image pipeline 因 dest contract 重新生成全部圖片，先停止並回報，不要繼續大量寫入。

### 9. Validate

~~~powershell
python tools\validate_images.py
git diff --check
rg -n "docs/germany/(?:blog|images|day-)|/germany/(?:blog|images|day-)|\"dest\": \"germany\"" core docs trips tools
rg -n "day-(?:0[1-9]|1[1-5])-blog\.html|day-10-(?:speyer|colmar)-blog\.html" core docs trips tools
git status --short
git diff --stat
~~~

允許的 germany/ 引用只有 Germany Country Hub 路徑。所有 Journey Blog、Timeline 與 Image 引用必須使用 2026-germany/。

## Smoke Test

啟動或重啟既有本機 server 後驗證：

1. /germany/ 是 Country Hub，只列 2026 Journey。
2. /2026-germany/ 是原本完整 Journey Hub。
3. 16 個新 Blog URL 全部 HTTP 200。
4. 15 個 Timeline URL 全部 HTTP 200。
5. 每頁 canonical、og:url、og:image 都使用 /2026-germany/。
6. 16 篇 prev/next 導航完整閉環。
7. Blog 與 Timeline 雙向連結正常，Day 10 上下篇皆可抵達。
8. docs/index.html、Germany Hub、Journey Hub 的入口都正確。
9. window.__JOURNEY_STORIES__ 16 篇 URL 與圖片全部正常；core 不含 2026 專屬故事資料。
10. 圖片、Lightbox、mobile dock 與 editor list-images 正常。
11. Build、save 或 restore 不會重新建立 docs/germany/blog、images 或 day-XX。
12. 舊 Journey URL 與舊 Blog filename 不再是正式頁；本次不保留 redirect。

## 驗收標準

- docs/2026-germany/ 完整承載 2026 Journey。
- docs/germany/ 只含 Country Hub，不含 blog、images、manifest 或 day-XX。
- source 與 published Blog 各有 16 個新檔名。
- 舊 Blog filename 零殘留。
- config、builder、server、validator 對 dest 的理解一致。
- 圖片 pipeline 100% cache hit，manifest paths 全部正確。
- Blog、Timeline、首頁、Country Hub、Journey Hub 與 Journey-owned stories 無死鏈。
- core/js/app.js 不再擁有 2026 Journey 內容，未來 2027/2028 Journey 可提供自己的故事陣列。
- validate_images.py 100% 通過，git diff --check 通過。
- 文章正文、圖片內容與 UI 行為沒有非必要改動。
- 沒有 commit、push 或 deploy。

若工具重新產生 docs/germany Journey 內容、圖片全量重轉、validator 必須關閉檢查才能通過，或出現大量非預期差異，立即停止並交回 Codex review。

## Gemini 回報

完成後回報：

1. Journey directory move 與 16 組 rename 清單。
2. config、builder、server、validator 的 dest 修改摘要。
3. 舊 Journey path 與舊 Blog filename 零殘留證據。
4. Image pipeline cache hit 與 manifest contract 結果。
5. Build、validator、git diff --check 結果。
6. 12 項 smoke test 結果。
7. git status --short 與 diff stat。
8. 是否有 blocker；若無，寫「無已知 blocker，待 Codex review」。

不得自行 commit、push 或 deploy。
