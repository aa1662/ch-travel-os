# Dashboard 私人素材接收

此工具僅接收，不啟動 AI、不 build、不發布。先讀現行 `TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md` 與 `EDITORIAL_STYLE_GUIDE.md`。

1. 在本專案執行 `python tools/dashboard_intake.py ITEM_ID`，會接收最高已交接版本，輸出該快照位置。
2. 讀取快照完整 item（選圖順序／備註、回憶與照片關聯、寫法及不公開註記）。照片 sourcePath 只讀，publicApproved=false，不代表作者核准公開。
3. `--stage questions --question "待作者回答的問題"` 記錄必要提問；不要從照片編造記憶。
4. 經討論寫母稿至 `.local_data/dashboard-intake/ITEM_ID/manuscript-vN.md`，保留舊稿。執行 `python tools/dashboard_intake.py ITEM_ID --revision N --stage draft --manuscript .local_data/dashboard-intake/ITEM_ID/manuscript-vN.md` 更新狀態。
5. 新版本先接收、比較，保留舊母稿與核准正文；實際整合後使用 `--stage integrated --revision N --manuscript .local_data/dashboard-intake/ITEM_ID/manuscript-vN.md`。Dashboard 重新整理即可閱讀同一份文字。

參數不提供正文覆寫或公開轉檔功能。分篇可重複 `--manuscript`。母稿需保留在此私人目錄，正式編排仍使用既有流程與獨立授權。

母稿引用相對於專案根目錄，也可直接指向 `trips/<journey>/manuscripts/*.md`，不複製既有母稿。


## 原始口述與整理稿（2026-10-26）

`item.igSource.caption` 是原IG來源，不是新口述；`item.memories` 是作者原始口述SSoT，photoIds為多圖分組。`item.acceptedDraft.text` 是作者明確接受的AI整理稿，不能取代原文，依據 `inputRevision`。快照頂層 `acceptedDraftStale=true` 表示口述已補充、接受稿尚未涵蓋新內容；保留舊稿並重新整合，不把它當最新版母稿。照片全組帶入仍是候選，不等於想用或公開核准。正式母稿與核准正文維持既有SSoT。
