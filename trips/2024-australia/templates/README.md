# 澳洲遊記新篇範型（給 Gemini）

新篇先讀根目錄 `AGENTS.md`、`EDITORIAL_STYLE_GUIDE.md`、`TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md`，再讀本篇口述、IG 原文、照片 audit、`plan.md` 與 `photo-selections/<entry-id>.json`。以 `blog-source.template.html` 複製成 `sources/blog/<slug>.html`，替換所有 `{{...}}` 佔位符；不要從已發布的 `docs/` 頁面反向起稿。參照已驗收的同 Journey 文章確認視覺節奏，但不要複製其事件、笑點或多餘的 inline CSS。

## 開工順序

1. **內容**：先寫出文章命題、事件順序、正文／IG 原文／讀者筆記的界線。IG 貼文只用 Takeout 原文；作者未確認的記憶和照片內容不得補成事實。適度喜劇加工可保留在語氣與無傷大雅對話，笑點優先落在作者自己身上。
2. **建立可選圖的文章草稿**：先依 `blog-source.template.html` 建立 source，並在 `blog-migration.json` 登錄唯一 `id/title/source/output/image_folder`，並設 `"status": "draft"`。這讓 editor 能選到新篇。模板中的圖片佔位符此時不能進行 build，也不要把新篇加進公開導覽；待照片定案後才補齊 source、config，移除 `status: draft` 並建立公開頁面。
3. **選圖**：作者在本機 editor 的「選圖與燈箱」先標記 `body` 與 `gallery`。`status=draft` 時，只能使用本機低解析預覽，不得把 master 路徑、預覽 API 或未轉檔照片寫入 HTML。作者按「確認選圖並統一轉 WebP」後，清單為 `finalized`；只引用其已產生的公開 WebP。`body` 是正文候選，仍須逐張對準段落；`gallery` 是燈箱入選，仍須按拍攝時間與橫直分組。兩欄可同時為 true，燈箱只註冊一次。已有 IG 歷史貼文如需完整呈現，仍以本篇已核准的 IG 清單和隱私規則為準。
4. **工程**：替換 source 中所有佔位符，在 `blog-migration.json` 補齊 `og_*` 與 `gallery_groups`。`gallery_groups` 只含作者選入燈箱且核准的照片；每個 `image_id` 全頁唯一，橫直分組各自依拍攝時間升冪。正文、Hero、IG 縮圖只用 `.gallery-opener[data-gallery-open]` 指向 registry；若作者選為正文但不進燈箱，用沒有 opener 的圖片呈現。不得讓未產生頁面出現 404 導覽連結。
5. **版面**：橫圖使用 `.fullwidth-landscape-wrap` 滿寬，彼此間至少隔一至兩段有內容推進的正文；直圖使用 `.story-split`，框內填滿且 `object-position` 對準主體，必要時調整容器比例。IG 縮圖桌機四欄、手機兩欄；badge 只寫日期與「IG 發布紀錄」，不寫死張數。Bento、IG 卡、照片札記皆按故事需要取捨，不套固定篇數或段數。
6. **驗證**：執行 `python tools/build_trip_html.py --trip 2024-australia --dest 2024-australia --entry <entry-id>`、`python tools/validate_images.py`、`git diff --check`，再做桌機及手機視覺檢查，逐張核對圖說與像素畫面。`masters/` 永不進 `docs/` 或 Git。暫時腳本只放 `scratch/<task>/`，完成後清理；可重用工具放 `tools/`。不要自行 commit、push、deploy。

## 完成前自檢

- 文章沒有 `{{...}}` 佔位符、虛構場景、錯誤時間或 AI 套話。
- `photo-selections/<entry-id>.json` 的 `body`／`gallery` 決策已逐一對應到正文與 migration config；未入選照片沒有被公開。
- 每張照片的 caption、alt、畫面和段落相符；Hero、正文、IG 可重用同一影像，但 Lightbox registry 不重複。
- Source、config、manifest、docs 的連結一致，所有驗證通過後才交作者 UAT。
