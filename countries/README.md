# Country Hub 管理方式

`countries/` 是國家層首頁的維護入口，位於全球首頁與各年份 Journey 之間。

## 資料夾契約

每個國家使用相同結構：

```text
countries/<country-id>/
├── country.json
└── sources/
    └── index.html
```

- `country.json`：國家 ID、source、公開 output、canonical URL，以及已完成 Journey 清單。
- `sources/index.html`：可維護的 Country Hub source of truth。
- `docs/<country-id>/index.html`：建構產物，不作為人工編輯入口。

只有已完成且實際存在的 Journey 可以寫入 `journeys`。設定中的 Journey 連結與封面必須同時出現在 source，且目標必須存在於 `docs/`；建構器會阻止尚未完成或超出公開目錄的路徑。

## 建構與檢查

```powershell
python tools/build_country_html.py --country japan
python tools/build_country_html.py --country japan --check
python tools/build_country_html.py --all
python tools/build_country_html.py --all --check
```

新增或修改 Country Hub 後，還必須執行：

```powershell
python tools/validate_images.py
```

Country Hub 與全球首頁、Journey 首頁、文章頁之間應形成以下導覽層級：

```text
全球旅程 → 國家首頁 → 年份 Journey → 單篇文章
```

Country Hub 不取代 Journey 首頁。國家首頁負責跨年份整理；Journey 首頁仍負責該次旅行的文章目錄與行程脈絡。
