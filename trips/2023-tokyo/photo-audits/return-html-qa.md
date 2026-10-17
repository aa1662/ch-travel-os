# 第二篇 HTML QA｜東京出差的空檔

## 來源與輸出

- Source：`trips/2023-tokyo/sources/blog/tokyo-imperial-palace-and-return.html`
- Output：`docs/2023-tokyo/blog/tokyo-imperial-palace-and-return.html`
- 來源 audit：`photo-audits/return-sources.json`
- 影片契約：`video-publish.json`

## 素材核對

- B1–B7：7 則 IG 原始貼文，原始 audit 共 36 張照片、1 段影片。作者 UAT 排除 `18002494235179485.webp` 後，gallery registry 保留 35 張照片。
- 正文原圖：Hero `20231115_125404.jpg`、二重橋直圖 `20231115_123659.jpg`。
- 所有照片经 WebP 管线处理，原图不进入 `docs/`。
- 影片公开衍生档：H.264、yuv420p、720×900、21.47 秒、无音轨、metadata stripped、fast-start。

## 页面契约

- 7 张 IG 卡片；桌面与手机均为两栏。
- 奇数张卡片保留最后一张，不为凑版删除。
- 影片在 B2 卡片内以原生 video 呈现，不进入 GLightbox。
- `autoplay muted loop playsinline controls`；共用 JS 在 canplay 时补触发 `play()`。
- Lightbox caption 隐藏；正文 figcaption 与 IG caption 保留。
- Footer、mobile dock、上一篇入口均存在。

## 自动与浏览器验证

- `python tools/build_trip_html.py --trip 2023-tokyo`：通过。
- `python tools/validate_images.py`：全站通过，零死链。
- Desktop 1440×1000：两栏为 457px + 457px；影片静音自动播放；36 个照片入口。
- Mobile 390×844：两栏为 156.5px + 156.5px；影片静音自动播放；无横向溢出。
- 影片 DOM 实测：`paused=false`、`muted=true`、`currentTime` 持续前进、`readyState=4`、无 media error。

- 版面 UAT：B2、B3 媒體區左右各保留約 25px 卡內留白；二重橋桌機為 412px 文字＋460px 照片，手機改為文字在上、照片在下，無水平溢出，正文不顯示圖說。
- 後續 UAT：B3 改回標準貼邊媒體網格，四張照片採正方形雙欄並逐張設定焦點；`18002494235179485.webp` 已從 registry、manifest 與公開 derivatives 移除，私人 master 與來源 audit 保留。
