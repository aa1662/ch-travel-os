# 澳洲遊記新篇範型（給 Gemini）

2026-10-17 更新：只供後續新篇組版參考，不回改已完成澳洲文章。先讀根目錄 `AGENTS.md`、`EDITORIAL_STYLE_GUIDE.md`、`TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md` 與本篇 plan 最新決策。`blog-source.template.html` 是元件骨架，不是固定寫法、模組數或 IG 欄數；在口述與選圖討論完成後才按需要使用，不從 `docs/` 反向起稿。

## 開工順序

1. **看圖與口述**：由作者集中候選照片的資料夾看圖，邊聽故事邊一起選圖，不先全量轉縮圖。只有需要時才作私人低解析預覽。
2. **討論寫法**：潤飾前先 grillme，確認本篇型態、分篇、語氣與呈現。IG 欄數、點開原圖／調色版及 caption 逐篇決定，記入 plan，不硬套澳洲或其他篇配置。IG 原文與新正文分清楚，保留作者核准的適度藝術加工。
3. **確認後轉檔**：母稿及最終選圖確認後，僅為入選圖製作公開 WebP；先核對 pipeline 輸入範圍，不能只用 `--pilot-day` 假定已排除未選圖。直接討論的選圖引用本篇 plan／mapping；若使用 Editor，才建立必要 `status: draft` scaffold、準備 `masters/` 工作副本，並用 `photo-selections` 保存。現有 Editor 不等於任意資料夾匯入器，不為開始口述而先建 source/config。
4. **工程**：定案後補齊 source、`blog-migration.json`、`og_*` 與 `gallery_groups`，移除完成篇的 draft 標記。模板佔位符不進公開 build；gallery 只收核准圖片版本、唯一註冊且順序可追溯。正文圖若不入燈箱則不掛 opener，不暴露未生成頁面的入口。
5. **版面**：沿用共用元件，依本篇決策組合 Hero、正文、IG、照片札記、gallery 與可選 Bento。檢查照片焦點、圖文平衡、字體、header/footer 與手機互動，不以固定段數或欄數代替驗收。
6. **驗證**：執行單篇 builder、validator、diff check 與桌機／手機視覺檢查。小修不重跑新篇流程；核准文字與選圖不被 gallery 或 caption 修正連帶改動。原圖不公開、不進 Git；commit、push、deploy 依當次授權執行。

## 完成前自檢

- 本篇母稿、最終選圖及呈現決策已確認；未入選候選未轉為公開資產。
- 最終清單／mapping（使用 Editor 時含 `photo-selections/<entry-id>.json`）已對應正文與 migration config；不假造 Editor 已儲存。
- 文章沒有未替換佔位符；caption、alt、畫面與段落相符。作者選定的原圖／IG 版本及燈箱行為正確。
- Source、config、manifest、docs 一致；自動與視覺驗證通過後才交作者集中 UAT。新流程不修改任何已完成文章。
