/**
 * 2026 德國南部・冬季自駕與圖文遊記 - 核心互動引擎 (app.js)
 * 特色：德法雙語發音辭典、冬季藍調時刻預測、Bento 互動、燈箱整合與 Web Share
 */

document.addEventListener('DOMContentLoaded', () => {
  initReadingProgressBar();
  initAudioButtons();
  initShareButton();
  initTimelineCards();
  initGLightbox();
  initFeaturedRandomizer();
});

/* ==========================================================================
   1. 德語 / 法語發音與美食文化辭典 (German & French Pronunciation Engine)
   ========================================================================== */
const GERMAN_DICTIONARY = {
  // 經典美食
  "Forelle": { lang: "de-DE", zh: "湖區烤鱒魚", note: "奧地利湖區必吃鮮魚" },
  "Wiener Schnitzel": { lang: "de-DE", zh: "奧地利炸肉排", note: "薄切小牛肉或豬肉炸至金黃酥脆" },
  "Tafelspitz": { lang: "de-DE", zh: "皇家慢燉牛肉", note: "茜茜公主最愛的清燉牛肉佐辣根醬" },
  "Schweinshaxe": { lang: "de-DE", zh: "巴伐利亞脆皮烤豬腳", note: "外皮焦脆肉質多汁，搭配酸菜與馬鈴薯球" },
  "Rauchbier": { lang: "de-DE", zh: "班堡煙燻啤酒", note: "以山毛櫸木煙燻麥芽釀造的古老啤酒" },
  "Bocksbeutel": { lang: "de-DE", zh: "法蘭肯大肚瓶白葡萄酒", note: "符茲堡特有的扁圓大肚瓶葡萄酒" },
  "Flammkuchen": { lang: "fr-FR", zh: "亞爾薩斯火焰烤餅", note: "薄脆餅皮抹上法式酸奶油、洋蔥與培根" },
  "Kaiserschmarrn": { lang: "de-DE", zh: "皇家皇帝煎餅", note: "撒上糖霜與李子醬的奧地利蓬鬆撕塊鬆餅" },
  
  // 地名與景點
  "Hallstatt": { lang: "de-DE", zh: "哈修塔特", note: "世界遺產湖畔仙境" },
  "Salzburg": { lang: "de-DE", zh: "薩爾斯堡", note: "莫札特的故鄉與音樂之都" },
  "Würzburg": { lang: "de-DE", zh: "符茲堡", note: "羅曼蒂克大道的起點" },
  "Rothenburg ob der Tauber": { lang: "de-DE", zh: "陶伯河畔羅騰堡", note: "保存最完好的中世紀童話小鎮" },
  "Heidelberg": { lang: "de-DE", zh: "海德堡", note: "歌德遺落心靈的浪漫大學城" },
  "Colmar": { lang: "fr-FR", zh: "科爾馬", note: "霍爾的移動城堡原型小鎮" },
  "Eguisheim": { lang: "fr-FR", zh: "埃吉桑姆", note: "同心圓排列的法國最美童話村莊" },
  "Garmisch-Partenkirchen": { lang: "de-DE", zh: "加米許-帕滕基興", note: "阿爾卑斯雙子山城與楚格峰山腳" },
  "Neuschwanstein": { lang: "de-DE", zh: "新天鵝堡", note: "童話國王路德維希二世的浪漫城堡" },
  "Partnachklamm": { lang: "de-DE", zh: "帕特納赫峽谷", note: "冬季壯觀冰瀑峽谷" },
  "Zugspitze": { lang: "de-DE", zh: "楚格峰", note: "德國第一高峰 (2,962m)" }
};

function speakWord(term, explicitLang) {
  if (!('speechSynthesis' in window)) {
    showToast("⚠️ 您的瀏覽器暫不支援語音發音");
    return;
  }

  window.speechSynthesis.cancel(); // 停止先前的發音
  const info = GERMAN_DICTIONARY[term] || { lang: explicitLang || "de-DE" };
  const utterance = new SpeechSynthesisUtterance(term);
  utterance.lang = explicitLang || info.lang || "de-DE";
  utterance.rate = 0.85; // 稍微放慢速度以利聽清發音細節
  
  window.speechSynthesis.speak(utterance);
  
  if (info.zh) {
    showToast(`🔊 播放中: ${term} (${info.zh})`);
  }
}

function initAudioButtons() {
  document.querySelectorAll('[data-pronounce]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const term = btn.getAttribute('data-pronounce');
      const lang = btn.getAttribute('data-lang');
      speakWord(term, lang);
    });
  });
}

/* ==========================================================================
   2. 閱讀進度條 (Reading Progress Bar)
   ========================================================================== */
function initReadingProgressBar() {
  const progressBar = document.querySelector('.reading-progress');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + '%';
  });
}

/* ==========================================================================
   3. 原生分享與 Toast 提示 (Web Share & Toast API)
   ========================================================================== */
function showToast(message) {
  const existing = document.querySelector('.toast-msg');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2200);
}

function initShareButton() {
  const shareBtns = document.querySelectorAll('.btn-share');
  shareBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = window.location.href;
      const title = document.title;
      if (navigator.share) {
        try {
          await navigator.share({ title, url });
        } catch (err) {
          if (err.name !== 'AbortError') console.error('Share error:', err);
        }
      } else {
        try {
          await navigator.clipboard.writeText(url);
          showToast('🔗 已複製網址到剪貼簿！');
        } catch (err) {
          showToast('🔗 請直接複製網址分享！');
        }
      }
    });
  });
}

/* ==========================================================================
   4. 時間軸卡片快速導航 (Timeline Interaction)
   ========================================================================== */
function initTimelineCards() {
  document.querySelectorAll('.timeline-card[data-href]').forEach(card => {
    card.addEventListener('click', () => {
      const href = card.getAttribute('data-href');
      if (href) window.location.href = href;
    });
  });
}

/* ==========================================================================
   5. GLightbox 燈箱初始化與快速圖集觸發器
   ========================================================================== */
let globalLightboxInstance = null;

function initGLightbox() {
  if (typeof GLightbox !== 'undefined') {
    globalLightboxInstance = GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      zoomable: true
    });
  }

  // 綁定所有快速圖集瀏覽按鈕 (.btn-gallery-quick)
  document.querySelectorAll('.btn-gallery-quick').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openCurrentPageGallery();
    });
  });
}

function openCurrentPageGallery() {
  const firstLink = document.querySelector('.glightbox');
  if (firstLink) {
    firstLink.click();
  } else if (globalLightboxInstance) {
    globalLightboxInstance.open();
  }
}

// 支援所有天數的 inline onclick 呼叫 (如 openDay01Gallery, openDay03Gallery 等)
for (let i = 1; i <= 15; i++) {
  const pad = String(i).padStart(2, '0');
  window[`openDay${pad}Gallery`] = openCurrentPageGallery;
  window[`openDay${i}Gallery`] = openCurrentPageGallery;
}
window.openDayGallery = openCurrentPageGallery;

/* ==========================================================================
   6. 📸 精選遊記 16 篇隨機抽取與「🎲 換一批」引擎 (Featured Stories Randomizer)
   ========================================================================== */
const ALL_STORIES = [
  {
    day: "Day 01",
    country: "奧地利",
    place: "Salzburg",
    badgeType: "badge-alpine",
    theme: "🏛️ 音樂之都",
    themeType: "badge-wine",
    title: "薩爾斯堡莫札特故鄉 — 電梯直攻僧侶山俯瞰老城",
    quote: "「冬日的薩爾斯堡少了一分喧鬧，多了一分冷冽的古典韻味。踏入米拉貝爾花園，耳邊宛如響起《真善美》的樂章。」",
    img: "images/day-01/17869170573551215-desktop-1200w.webp",
    url: "blog/day-01-blog.html"
  },
  {
    day: "Day 02",
    country: "奧地利",
    place: "Hallstatt",
    badgeType: "badge-alpine",
    theme: "🏛️ 世界遺產",
    themeType: "badge-wine",
    title: "哈修塔特湖畔漫遊 — 夏與冬的十二年對照",
    quote: "「同一個地點，不同的季節與人生階段。十二年前是綠意盎然的盛夏，十二年後是白雪皚皚的清冷清晨。」",
    img: "images/day-02/18041867387724285-desktop-1200w.webp",
    url: "blog/day-02-blog.html"
  },
  {
    day: "Day 03",
    country: "德國",
    place: "Würzburg",
    badgeType: "badge-gold",
    theme: "🚗 古堡進駐",
    themeType: "badge-forest",
    title: "跨國挺進符茲堡 — 羅曼蒂克大道的北端起點",
    quote: "「告別奧地利雪白湖區，馳騁於德南平原。進駐符茲堡，為接下來的酒鄉與中世紀古城拉開序幕。」",
    img: "images/day-03/20260128_083704-desktop-1200w.webp",
    url: "blog/day-03-blog.html"
  },
  {
    day: "Day 04",
    country: "德國",
    place: "Bamberg",
    badgeType: "badge-gold",
    theme: "🍺 煙燻啤酒",
    themeType: "badge-wine",
    title: "小威尼斯班堡走讀 — 煙燻啤酒與水中市政廳",
    quote: "「這座未受二戰轟炸的中世紀古城，空氣中飄著山毛櫸木烘烤麥芽的獨特煙燻香氣，每一口啤酒都是六百年的歷史。」",
    img: "images/day-04/18066767258248200-desktop-1200w.webp",
    url: "blog/day-04-blog.html"
  },
  {
    day: "Day 05",
    country: "德國",
    place: "Nürnberg",
    badgeType: "badge-gold",
    theme: "🏰 玩具之都",
    themeType: "badge-forest",
    title: "紐倫堡皇帝堡走讀 — 聖誕之都的冬日紅磚風華",
    quote: "「登上皇帝堡城牆俯瞰整座紅色屋頂的帝國古都，在老城石板路上追尋杜勒與胡桃鉗的童話足跡。」",
    img: "images/day-05/18002102333848437-desktop-900w.webp",
    url: "blog/day-05-blog.html"
  },
  {
    day: "Day 06",
    country: "德國",
    place: "Rothenburg",
    badgeType: "badge-gold",
    theme: "🧸 童話小鎮",
    themeType: "badge-wine",
    title: "陶伯河畔羅騰堡 — 漫步中世紀時光膠囊",
    quote: "「走進普連萊小廣場，彩色桁架木屋在晨光下靜謐得如同童話插畫，彷彿時間在這裡整整停駐了五百年。」",
    img: "images/day-06/18078973727601770-desktop-900w.webp",
    url: "blog/day-06-blog.html"
  },
  {
    day: "Day 07",
    country: "德國",
    place: "Würzburg",
    badgeType: "badge-gold",
    theme: "🍷 藝術與酒",
    themeType: "badge-wine",
    title: "符茲堡主教宮與舊美茵橋白葡萄酒",
    quote: "「符茲堡是『藝術＋酒』的城市。白天看世界最大穹頂天頂畫，傍晚上橋喝一杯，冬天來，反而更剛好。」",
    img: "images/day-07/18075865346091014-desktop-901w.webp",
    url: "blog/day-07-blog.html"
  },
  {
    day: "Day 08",
    country: "德國",
    place: "Heidelberg",
    badgeType: "badge-wine",
    theme: "🏰 浪漫古城",
    themeType: "badge-forest",
    title: "我把心遺留在海德堡 — 城堡與老橋日落",
    quote: "「海德堡是『剛剛好的浪漫』。不浮誇、不壯闊，但走過老橋、看著城堡染上夕陽，會理解為什麼那麼多人把心留在這裡。」",
    img: "images/day-08/18065731982249055-desktop-1200w.webp",
    url: "blog/day-08-blog.html"
  },
  {
    day: "Day 09",
    country: "德國",
    place: "Hanau & Frankfurt",
    badgeType: "badge-gold",
    theme: "📖 格林童話",
    themeType: "badge-wine",
    title: "哈瑙童話起點 ✕ 法蘭克福采爾大道巡禮",
    quote: "「在格林兄弟銅像前尋找童話大道的源頭，走入法蘭克福現代都會的璀璨繁華，感受古典與當代的奇妙交織。」",
    img: "images/day-09/18058121042364450-desktop-900w.webp",
    url: "blog/day-09-blog.html"
  },
  {
    day: "Day 10 (上)",
    country: "德國",
    place: "Speyer",
    badgeType: "badge-gold",
    theme: "🏛️ 帝國大教堂",
    themeType: "badge-wine",
    title: "史派爾羅曼式大教堂 ✕ 跨國亞爾薩斯轉移",
    quote: "「站在千年紅色砂岩砌成的帝國教堂下，沉重的歷史感撲面而來，隨後跨越萊茵河，奔向法式彩色木屋的世界。」",
    img: "images/day-10/20260204_122442-desktop-676w.webp",
    url: "blog/day-10-speyer-blog.html"
  },
  {
    day: "Day 10 (下)",
    country: "法國",
    place: "Colmar",
    badgeType: "badge-wine",
    theme: "🏰 移動城堡",
    themeType: "badge-forest",
    title: "科爾馬小威尼斯 ✕ 走進霍爾的移動城堡",
    quote: "「運河倒映著粉藍、淡黃與酒紅色的木筋屋，彷彿下一秒霍爾與蘇菲就會從街角的屋頂輕盈飛過。」",
    img: "images/day-10/18082561442231943-desktop-1200w.webp",
    url: "blog/day-10-colmar-blog.html"
  },
  {
    day: "Day 11",
    country: "瑞士/法國",
    place: "Basel & Eguisheim",
    badgeType: "badge-alpine",
    theme: "🌐 三國交界",
    themeType: "badge-forest",
    title: "瑞士巴塞爾 BIS 朝聖 ✕ 埃吉桑姆最美童話村",
    quote: "「上午在巴塞爾萊茵河畔見證國際金融的心臟，下午走入法國最美同心圓花園小鎮埃吉桑姆，雙重感官的極致切換。」",
    img: "images/day-11/17986859564941938-desktop-1200w.webp",
    url: "blog/day-11-blog.html"
  },
  {
    day: "Day 12",
    country: "德國",
    place: "Garmisch",
    badgeType: "badge-alpine",
    theme: "♨️ 雪山溫泉",
    themeType: "badge-wine",
    title: "黑森林過渡 ✕ 加米許山莊溫泉 Das Graseck",
    quote: "「搭乘私人古老纜車直上懸崖峭壁，在零下的阿爾卑斯白雪群峰環抱下，浸入熱氣氤氳的無邊際高空溫泉。」",
    img: "images/day-12/20260206_180606-desktop-1200w.webp",
    url: "blog/day-12-blog.html"
  },
  {
    day: "Day 13",
    country: "德國",
    place: "Neuschwanstein",
    badgeType: "badge-alpine",
    theme: "❄️ 白雪童話",
    themeType: "badge-wine",
    title: "新天鵝堡雪景重遊 ✕ 跨越十二年的父女童話時光",
    quote: "「坐著傳統馬車踏著白雪緩緩上山，十二年前獨自遠眺的夢想城堡，如今牽著女兒的小手一同圓夢。」",
    img: "images/day-13/20260207_144110-desktop-1200w.webp",
    url: "blog/day-13-blog.html"
  },
  {
    day: "Day 14",
    country: "德國",
    place: "Partnachklamm",
    badgeType: "badge-alpine",
    theme: "🧊 天然冰宮",
    themeType: "badge-wine",
    title: "帕特納赫峽谷冬季冰瀑奇景 ✕ 天然冰宮探秘",
    quote: "「穿鑿於八十公尺高垂直岩壁間，凝視層層堆疊的幽藍冰瀑與冰簾，體驗大自然將時間徹底凍結的震撼奇景。」",
    img: "images/day-14/18038771039755485-desktop-900w.webp",
    url: "blog/day-14-blog.html"
  },
  {
    day: "Day 15",
    country: "德國",
    place: "Munich Airport",
    badgeType: "badge-wine",
    theme: "🎉 圓滿終章",
    themeType: "badge-gold",
    title: "慕尼黑機場滿載賦歸 ✕ 十五天德南冬旅自駕回甘",
    quote: "「陪伴我們 15 天、橫跨四國、奔馳兩千公里的白色 Audi A5 功成身退。在粉紫暮色與孩子燦爛的笑容中，圓滿回甘。」",
    img: "images/day-15/20260208_172729-desktop-675w.webp",
    url: "blog/day-15-blog.html"
  }
];

let lastPickedIndices = [];

function getRandomThreeStories() {
  const indices = ALL_STORIES.map((_, i) => i);
  // 排除上次抽取的，避免連莊
  const candidates = indices.filter(i => !lastPickedIndices.includes(i));
  const pool = candidates.length >= 3 ? candidates : indices;
  
  // 隨機打亂抽取 3 個
  const shuffled = [...pool].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 3);
  lastPickedIndices = selected;
  return selected.map(i => ALL_STORIES[i]);
}

function renderFeaturedStories(stories) {
  const container = document.querySelector('.featured-grid');
  if (!container) return;

  container.innerHTML = stories.map(s => `
    <article class="featured-card">
      <div class="featured-img-wrap">
        <img src="${s.img}" alt="${s.title}" loading="lazy">
        <span class="featured-tag-float">${s.day} · ${s.country}</span>
      </div>
      <div class="featured-body">
        <div>
          <div style="margin-bottom: 0.5rem;">
            <span class="badge ${s.badgeType}">📍 ${s.place}</span>
            <span class="badge ${s.themeType}">${s.theme}</span>
          </div>
          <h3 class="featured-title">${s.title}</h3>
          <p class="featured-quote">${s.quote}</p>
        </div>
        <a href="${s.url}" class="btn-read-story">📖 閱讀深度圖文遊記 →</a>
      </div>
    </article>
  `).join('');
}

function initFeaturedRandomizer() {
  const grid = document.querySelector('.featured-grid');
  const btnDice = document.getElementById('btnRandomStories');
  if (!grid) return;

  // 1. 首頁載入時自動隨機抽取 3 篇
  const initialStories = getRandomThreeStories();
  renderFeaturedStories(initialStories);

  // 2. 「🎲 換一批」按鈕互動微動畫
  if (btnDice) {
    btnDice.addEventListener('click', (e) => {
      e.preventDefault();
      
      // 平滑淡出
      grid.classList.add('fade-out');
      
      setTimeout(() => {
        const nextStories = getRandomThreeStories();
        renderFeaturedStories(nextStories);
        // 平滑淡入
        grid.classList.remove('fade-out');
        showToast('🎲 已為您精選全新 3 篇遊記！');
      }, 220);
    });
  }
}
