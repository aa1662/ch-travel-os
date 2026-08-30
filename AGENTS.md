# 🤖 CH Travel OS 2.0 — AI 協作規範與多旅程架構準則 (AGENTS.md)

本文件定義 AI Agent 在維護與擴充「CH Travel OS 2.0 全球旅程圖文誌與自動化發布系統」時必須嚴格遵守的架構規範。

---

## 1. 核心定位與架構邊界 (SSoT)

1. **引擎與內容完全解耦 (Separation of Engine & Content)**：
   - `core/`：全站共用唯一大腦（CSS、JS、GLightbox、HTML 模板、視覺化編輯器）。
   - `trips/`：純旅程數據與文案（By Folder 獨立管理，不放冗餘樣式）。
   - `masters/`：原始相機照片與 Takeout 來源庫（**絕不公開、不進 Git**）。
   - `docs/`：GitHub Pages 發布目錄（**只包含 WebP 公開 derivatives，零構建依賴**）。
2. **圖片發布安全規範 (依據 web-image-publishing-playbook.md)**：
   - 公開輸出尺寸上限：480w, 960w, 1200w, 燈箱上限 1600w。
   - 預設格式 WebP (q84)，輸出時徹底移除 EXIF/GPS/裝置 metadata。
   - 禁止在 `docs/` 存放相機原圖或直接將原圖外洩至公開網址。

---

## 2. 圖文遊記呈現元件

Instagram 卡片 (`.ig-post-card`)、旅人散文 (`.story-split`)、單張／對照圖、燈箱與實戰 Bento (`.bento-grid`) 都是可選呈現元件，不是每篇必須套用的固定三層模板。元件選擇必須服務文章命題與照片證據；同一 Journey 維持導覽、Bento、圖集入口與整體視覺語言一致。

---

## 3. 內容發展與編輯規範 (SSoT)

在擴充新旅程（如 2024 Australia、2019 Italy、香港重返等）時，必須嚴格遵守專案根目錄下的：
- [TRAVEL_PORTAL_ROADMAP.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/TRAVEL_PORTAL_ROADMAP.md)：定義品牌定位、4 大內容型態（旅程專刊、重返現場、在路上、城市切片）、里程碑與 Place 內容模型。
- [EDITORIAL_STYLE_GUIDE.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/EDITORIAL_STYLE_GUIDE.md)：定義 CH Voice Profile 寫作語氣、來源優先序、人工記憶訪談與內容 UAT 契約。
- [TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md](file:///c:/Data/charlotte-ai-os-dev/ch-travel-os/TRAVEL_BLOG_PRODUCTION_PLAYBOOK.md)：定義素材盤點、盲寫母稿、Grillme、既有頁融合、選圖、構建與雙向 UAT 的跨系列製作流程。
- 嚴格遵守「小步閉環 (Milestones)」與「Config 驅動構建 (`blog-migration.json` / `timeline-migration.json`)」。
- 尚未生成的頁面禁止在前端暴露 404 連結。
- 每次變更必須 100% 通過 `python tools/validate_images.py` 全站死鏈與資產稽核。
