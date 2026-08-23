/**
 * 2026 德國南部・冬季自駕與圖文遊記 - 核心互動引擎 (app.js)
 * 特色：德法雙語發音辭典、冬季藍調時刻預測、Bento 互動、燈箱整合與 Web Share
 */

document.addEventListener('DOMContentLoaded', () => {
  initReadingProgressBar();
  initMobileDockVisibility();
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

function initMobileDockVisibility() {
  const dock = document.querySelector('.mobile-dock');
  if (!dock) return;

  const updateDock = () => {
    document.body.classList.toggle('dock-visible', window.scrollY > 180);
  };

  updateDock();
  window.addEventListener('scroll', updateDock, { passive: true });
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
const ALL_STORIES = window.__JOURNEY_STORIES__ || [];

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
