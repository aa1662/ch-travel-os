# 🤖 CH Travel OS 2.0 — AI 協作規範與多旅程架構準則 (AGENTS.md)

本文件定義 AI Agent 在維護與擴充「CH Travel OS 2.0 全球旅程圖文誌與自動化發布系統」時必須嚴格遵守的架構規範。

---

## 0. C2C 觸發詞

- 當使用者訊息以 `c2c:` 開頭時，啟用 `.agents/c2c-blog-workflow.md` 定義的 Codex with ChatGPT 協作流程。
- `c2c:` 後方文字視為本次任務目標；若沒有內容，先詢問要處理的任務。
- ChatGPT 負責分析、規劃與 Review；Codex 負責讀寫檔案、執行命令、測試與 Git。
- `c2c:` 不包含 `commit`、`push`、`deploy` 或 `publish` 授權；這些操作仍須依當次明確範圍另行確認。
- 未使用 `c2c:` 時，不應自行啟動 C2C，除非使用者以其他文字明確要求使用 Codex with ChatGPT。

---

## 1. 核心定位與架構邊界 (SSoT)

1. **引擎與內容完全解耦 (Separation of Engine & Content)**：
   - `core/`：全站共用唯一大腦（CSS、JS、GLightbox、HTML 模板、視覺化編輯器）。
   - `trips/`：純旅程數據與文案（By Folder 獨立管理，不放冗餘樣式）。
   - `masters/`：原始相機照片與 Takeout 來源庫（**絕不公開、不進 Git**）。
   - `docs/`：靜態發布輸出目錄（公開圖片只含核准 WebP derivatives；核准影片依既有媒體契約處理，零構建依賴）。部署依 `CLOUDFLARE_PAGES_DEPLOYMENT.md`。
2. **圖片發布安全規範 (依據 web-image-publishing-playbook.md)**：
   - 公開輸出尺寸上限：480w, 960w, 1200w, 燈箱上限 1600w。
   - 預設格式 WebP (q84)，輸出時徹底移除 EXIF/GPS/裝置 metadata。
   - 禁止在 `docs/` 存放相機原圖或直接將原圖外洩至公開網址。

---

## 2. 圖文遊記呈現元件

Instagram 卡片 (`.ig-post-card`)、旅人散文 (`.story-split`)、單張／對照圖、燈箱與實戰 Bento (`.bento-grid`) 都是可選呈現元件，不是每篇必須套用的固定三層模板。元件選擇必須服務文章命題與照片證據；同一 Journey 維持導覽、Bento、圖集入口與整體視覺語言一致。

### 新遊記流程（2026-10-17 起）

- 先讀專案 skill：`.agents/skills/ch-travel-blog-workflow/SKILL.md`。全域 `ch-travel-blog` 或其他模型入口只作導引；本專案的製作流程以此 skill 引用的現行 Playbook 為準，不套用舊入口中的固定流程。
- 作者先將候選照片集中在一個私人資料夾；AI 看圖協助作者口述、同步選圖，先以必要的 grillme 討論分篇、寫法與呈現，再整理潤飾母稿。
- IG 欄數、圖片版本、caption 與版型每篇討論，不設全站固定值，也不強制套用黃金範本。
- 最終選圖確認後，才為入選圖製作公開縮圖與其他必要尺寸；私人看圖預覽不等於公開轉檔。
- 本次流程改版只適用後續新篇與另行指定的修改。已完成文章、圖片、config 與公開頁不因規則更新而重建或回改。

---

## 3. 內容發展與編輯規範 (SSoT)

在擴充新旅程（如 2024 Australia、2019 Italy、香港重返等）時，必須嚴格遵守專案根目錄下的：
- [TRAVEL_PORTAL_ROADMAP.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/TRAVEL_PORTAL_ROADMAP.md)：定義品牌定位、4 大內容型態（旅程專刊、重返現場、在路上、城市切片）、里程碑與 Place 內容模型。
- [EDITORIAL_STYLE_GUIDE.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/EDITORIAL_STYLE_GUIDE.md)：定義 CH Voice Profile 寫作語氣、來源優先序、人工記憶訪談與內容 UAT 契約。
- [TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md)：定義集中候選照片、看圖口述與同步選圖、Grillme、母稿確認、入選圖轉檔、構建與驗收流程。
- 嚴格遵守「小步閉環 (Milestones)」與「Config 驅動構建 (`blog-migration.json` / `timeline-migration.json`)」。
- 尚未生成的頁面禁止在前端暴露 404 連結。
- 涉及文章、資產、設定或程式變更時，必須通過 `python tools/validate_images.py` 與相應範圍驗證。純流程文件改版檢查文件一致性與變更範圍，不為此重建既有文章。
