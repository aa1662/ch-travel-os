/**
 * 2026 德國南部・冬季自駕與圖文遊記 - 核心互動引擎 (app.js)
 * 特色：德法雙語發音辭典、冬季藍調時刻預測、Bento 互動、燈箱整合與 Web Share
 */

const GA4_MEASUREMENT_ID = 'G-T54CXJ3E73';
const GA4_PRODUCTION_HOSTS = new Set(['chxtravel.com', 'www.chxtravel.com']);
const GA4_CROSS_DOMAIN_HOSTS = ['chxtravel.com', 'snaplog-c77.pages.dev'];

function initGoogleAnalytics() {
  if (!GA4_PRODUCTION_HOSTS.has(window.location.hostname)) return;
  if (document.querySelector(`script[data-ga4-id="${GA4_MEASUREMENT_ID}"]`)) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function() {
    window.dataLayer.push(arguments);
  };

  window.gtag('js', new Date());
  window.gtag('config', GA4_MEASUREMENT_ID, {
    linker: { domains: GA4_CROSS_DOMAIN_HOSTS }
  });

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_MEASUREMENT_ID}`;
  script.dataset.ga4Id = GA4_MEASUREMENT_ID;
  document.head.appendChild(script);
}

initGoogleAnalytics();

document.addEventListener('DOMContentLoaded', () => {
  initReadingProgressBar();
  initMobileDockVisibility();
  initAudioButtons();
  initShareButton();
  initTimelineCards();
  initGLightbox();
  initFeaturedRandomizer();
  initInlineAutoplayVideos();
  initReaderFeedback();
});

function initInlineAutoplayVideos() {
  document.querySelectorAll('video[autoplay][muted]').forEach(video => {
    video.muted = true;
    const startPlayback = () => {
      const playback = video.play();
      if (playback && typeof playback.catch === 'function') {
        playback.catch(() => {});
      }
    };

    if (video.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
      startPlayback();
    } else {
      video.addEventListener('canplay', startPlayback, { once: true });
    }
  });
}

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
      openCurrentPageGallery(btn.dataset.galleryTarget);
    });
  });

  // 內文照片只作為入口；燈箱項目由頁面的唯一 registry 管理。
  document.querySelectorAll('[data-gallery-open]').forEach(opener => {
    opener.addEventListener('click', (e) => {
      e.preventDefault();
      openGalleryImage(opener.dataset.galleryOpen);
    });
  });
}

function openGalleryImage(imageId) {
  const target = Array.from(document.querySelectorAll('.glightbox[data-gallery-image]'))
    .find(link => link.dataset.galleryImage === imageId);
  if (target) target.click();
}

function openCurrentPageGallery(galleryTarget) {
  const links = Array.from(document.querySelectorAll('.glightbox'));
  const firstLink = galleryTarget
    ? links.find(link => link.dataset.gallery === galleryTarget)
    : links[0];
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

/* ==========================================================================
   7. 讀者點讚與私密留言 (Reader Feedback Client Engine)
   ========================================================================== */
function initReaderFeedback() {
  const section = document.querySelector('.reader-feedback-section');
  if (!section) return;

  const articleId = section.dataset.articleId;
  if (!articleId) return;

  function getReaderClientId() {
    const key = 'ch_reader_cid';
    let cid = '';
    try {
      cid = localStorage.getItem(key);
      if (!cid || typeof cid !== 'string' || cid.length < 16 || cid.length > 64) {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
          cid = crypto.randomUUID();
        } else {
          cid = 'cid-' + Math.random().toString(36).slice(2) + '-' + Date.now().toString(36);
        }
        localStorage.setItem(key, cid);
      }
    } catch (e) {
      cid = 'cid-fallback-' + Math.random().toString(36).slice(2);
    }
    return cid;
  }

  const clientId = getReaderClientId();
  const btnLike = document.getElementById('btnFeedbackLike');
  const likeText = btnLike ? btnLike.querySelector('.like-text') : null;
  const likeIcon = btnLike ? btnLike.querySelector('.like-icon') : null;
  const statusMsg = document.getElementById('feedbackLikeStatus');
  const btnToggleComment = document.getElementById('btnToggleComment');
  const commentPane = document.getElementById('feedbackCommentPane');
  const form = document.getElementById('readerFeedbackForm');
  const nicknameInput = document.getElementById('feedbackNickname');
  const contentInput = document.getElementById('feedbackContent');
  const charCount = document.getElementById('charCount');
  const formAlert = document.getElementById('feedbackFormAlert');
  const btnCancel = document.getElementById('btnCancelComment');
  const btnSubmit = document.getElementById('btnSubmitFeedback');
  const submitSpinner = btnSubmit ? btnSubmit.querySelector('.submit-spinner') : null;
  const submitLabel = btnSubmit ? btnSubmit.querySelector('.submit-label') : null;
  const successCard = document.getElementById('feedbackSuccessCard');
  const btnSendAnother = document.getElementById('btnSendAnother');

  const btnRetry = document.getElementById('btnRetryFeedback');
  let serviceReady = false;
  let checkingStatus = false;
  let isLiked = false;
  let currentSubmissionId = null;

  function updateLikeUI(liked) {
    isLiked = liked;
    if (!btnLike) return;
    btnLike.setAttribute('aria-pressed', liked ? 'true' : 'false');
    btnLike.classList.toggle('active', liked);
    if (likeIcon) likeIcon.textContent = liked ? '❤️' : '🤍';
    if (likeText) likeText.textContent = liked ? '謝謝你喜歡 (取消)' : '喜歡這篇';
  }

  function setServiceReady(ready) {
    serviceReady = ready;
    [btnLike, btnToggleComment, btnSubmit].forEach(button => {
      if (button) button.disabled = !ready;
    });
  }

  function serviceUnavailable() {
    setServiceReady(false);
    if (statusMsg) statusMsg.textContent = '互動服務暫時無法連線，請重試。輸入內容已保留，文章可繼續閱讀。';
    if (btnRetry) btnRetry.hidden = false;
  }

  async function feedbackRequest(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      if (response.status >= 500) throw new Error('Feedback service unavailable');
      // Keep the timeout active while reading the response body too.
      return { response, data: await response.json() };
    } finally {
      clearTimeout(timeout);
    }
  }

  async function checkServiceStatus() {
    if (checkingStatus) return;
    checkingStatus = true;
    setServiceReady(false);
    if (btnRetry) btnRetry.hidden = true;
    if (statusMsg) statusMsg.textContent = '正在確認互動服務…';
    try {
      const { response, data } = await feedbackRequest('/api/feedback/status?article_id=' + encodeURIComponent(articleId) + '&client_id=' + encodeURIComponent(clientId));
      if (!response.ok || data.success !== true || data.article_id !== articleId || typeof data.liked !== 'boolean') {
        throw new Error('Invalid feedback status');
      }
      updateLikeUI(data.liked);
      setServiceReady(true);
      if (statusMsg) statusMsg.textContent = '';
    } catch (error) {
      serviceUnavailable();
    } finally {
      checkingStatus = false;
    }
  }

  setServiceReady(false);
  if (btnRetry) btnRetry.addEventListener('click', checkServiceStatus);
  checkServiceStatus();

  // 1. 僅在確認服務與文章資格後允許互動
  if (btnLike) {
    btnLike.addEventListener('click', async () => {
      if (!serviceReady || btnLike.disabled) return;
      btnLike.disabled = true;
      const nextAction = isLiked ? 'unlike' : 'like';
      try {
        const { response: res, data } = await feedbackRequest('/api/feedback/like', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            article_id: articleId,
            client_id: clientId,
            action: nextAction
          })
        });
        if (res.ok && data.success) {
          updateLikeUI(data.liked);
          if (statusMsg) {
            statusMsg.textContent = data.liked
              ? '謝謝你喜歡這篇記錄！若想分享心得，也歡迎在下方留幾句話喔。'
              : '已取消喜歡。隨時歡迎再與我們交流！';
          }
        } else if (statusMsg) {
          statusMsg.textContent = data.error || '點讚操作失敗，請稍後再試。';
        }
      } catch (err) {
        serviceUnavailable();
        if (statusMsg) statusMsg.textContent = '互動服務連線異常，請重試連線。';
      } finally {
        btnLike.disabled = !serviceReady;
      }
    });
  }

  // 2. 展開 / 收合留言表單
  if (btnToggleComment && commentPane) {
    btnToggleComment.addEventListener('click', () => {
      if (!serviceReady) return;
      const isHidden = commentPane.hidden;
      commentPane.hidden = !isHidden;
      btnToggleComment.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
      btnToggleComment.classList.toggle('active', isHidden);
      if (isHidden && contentInput) {
        contentInput.focus();
      }
    });
  }

  if (btnCancel && commentPane && btnToggleComment) {
    btnCancel.addEventListener('click', () => {
      commentPane.hidden = true;
      btnToggleComment.setAttribute('aria-expanded', 'false');
      btnToggleComment.classList.remove('active');
    });
  }

  // 3. 字數計數器
  if (contentInput && charCount) {
    contentInput.addEventListener('input', () => {
      charCount.textContent = contentInput.value.length;
    });
  }

  // 4. 留言表單送出（重試防重複、失敗保留內容）
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!serviceReady || (btnSubmit && btnSubmit.disabled)) return;
      if (formAlert) {
        formAlert.hidden = true;
        formAlert.className = 'feedback-form-alert';
        formAlert.textContent = '';
      }

      const nickname = (nicknameInput ? nicknameInput.value : '').trim();
      const content = (contentInput ? contentInput.value : '').trim();

      if (!content) {
        if (formAlert) {
          formAlert.textContent = '請輸入想對 CH 說的留言內容。';
          formAlert.classList.add('error');
          formAlert.hidden = false;
        }
        if (contentInput) contentInput.focus();
        return;
      }

      if (content.length > 1000) {
        if (formAlert) {
          formAlert.textContent = '留言長度不得超過 1000 字。';
          formAlert.classList.add('error');
          formAlert.hidden = false;
        }
        return;
      }

      if (nickname.length > 40) {
        if (formAlert) {
          formAlert.textContent = '暱稱長度不得超過 40 字。';
          formAlert.classList.add('error');
          formAlert.hidden = false;
        }
        return;
      }

      if (!currentSubmissionId) {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
          currentSubmissionId = crypto.randomUUID();
        } else {
          currentSubmissionId = 'sub-' + Math.random().toString(36).slice(2) + '-' + Date.now();
        }
      }

      if (btnSubmit) btnSubmit.disabled = true;
      if (submitSpinner) submitSpinner.hidden = false;
      if (submitLabel) submitLabel.textContent = '傳送中...';

      try {
        const { response: res, data } = await feedbackRequest('/api/feedback/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            article_id: articleId,
            client_id: clientId,
            client_submission_id: currentSubmissionId,
            nickname: nickname || null,
            content: content
          })
        });

        if (res.ok && data.success) {
          // 成功：清空輸入並顯示成功卡片
          form.reset();
          if (charCount) charCount.textContent = '0';
          currentSubmissionId = null;
          form.hidden = true;
          if (successCard) successCard.hidden = false;
        } else {
          // 失敗：保留當頁文字，顯示錯誤
          if (formAlert) {
            formAlert.textContent = data.error || '傳送失敗，請稍後再試。';
            formAlert.classList.add('error');
            formAlert.hidden = false;
          }
        }
      } catch (err) {
        serviceUnavailable();
        // 網路異常：保留當頁文字
        if (formAlert) {
          formAlert.textContent = '伺服器未回應或連線中斷，輸入內容已保留，請檢查後重試。';
          formAlert.classList.add('error');
          formAlert.hidden = false;
        }
      } finally {
        if (btnSubmit) btnSubmit.disabled = !serviceReady;
        if (submitSpinner) submitSpinner.hidden = true;
        if (submitLabel) submitLabel.textContent = '送出私密留言';
      }
    });
  }

  if (btnSendAnother && successCard && form) {
    btnSendAnother.addEventListener('click', () => {
      successCard.hidden = true;
      form.hidden = false;
      if (formAlert) formAlert.hidden = true;
      if (contentInput) contentInput.focus();
    });
  }
}
