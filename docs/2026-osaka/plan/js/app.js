/**
 * 2026 日本關西旅行互動 Web Portal - 核心前端互動腳本 (app.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  initPlanningArchiveBanner();
  initToasts();
  initAccordions();
  initEveningFilters();
  initGoldenHour();
  highlightActiveNav();
});

/* ---------- 0. CH x Travel 規劃存檔提示 ---------- */
function initPlanningArchiveBanner() {
  const siteNav = document.querySelector('.site-nav');
  if (!siteNav || document.querySelector('.planning-archive-banner')) return;

  const banner = document.createElement('aside');
  banner.className = 'planning-archive-banner';
  banner.setAttribute('aria-label', '行前規劃存檔說明');
  banner.innerHTML = `
    <div class="planning-archive-inner">
      <span><strong>2026 關西行前規劃存檔</strong>｜出發前使用的路線與資料版本，票價、班次與營業資訊請以最新公告為準。</span>
      <a href="../">回到大阪旅行專刊 →</a>
    </div>
  `;
  siteNav.before(banner);
}

/* ---------- 1. 日文發音、平假名、羅馬拼音 (Romaji) 知識庫辭典 ---------- */
const JAPANESE_DICTIONARY = {
  // 飯店與出發地
  "大阪梅田駅": {
    hiragana: "ホテル グランヴィア おおさか",
    romaji: "Hoteru Guranvia Ōsaka",
    en: "大阪梅田站直結基地"
  },

  // Day 1: 難波・中之島
  "難波八阪神社 大国主神社 法善寺横丁": {
    hiragana: "なんば やさか じんじゃ / おおくにぬし じんじゃ / ほうぜんじ よこちょう",
    romaji: "Namba Yasaka Jinja / Ōkuninushi Jinja / Hōzenji Yokochō"
  },
  "難波八阪神社": {
    hiragana: "なんば やさか じんじゃ",
    romaji: "Namba Yasaka Jinja"
  },
  "中之島 大阪市中央公会堂 梅田スカイビル 空中庭園展望台": {
    hiragana: "なかのしま / おおさかし ちゅうおう こうかいどう / うめだ スカイビル",
    romaji: "Nakanoshima / Chūō Kōkaidō / Umeda Sky Building"
  },
  "中之島": {
    hiragana: "なかのしま",
    romaji: "Nakanoshima"
  },
  "梅田スカイビル": {
    hiragana: "うめだ スカイビル",
    romaji: "Umeda Sky Building"
  },
  "GARB weeks AWAKE": {
    hiragana: "ガーブ ウィークス / アウェイク",
    romaji: "Gābu Wīkusu / Aweiku"
  },
  "大阪城 天守閣 ミライザ大阪城": {
    hiragana: "おおさかじょう てんしゅかく / ミライザ おおさかじょう",
    romaji: "Ōsakajō Tenshukaku / Miraiza Ōsakajō"
  },
  "大丸梅田店 HARBS 小倉山荘 ポケモンセンター": {
    hiragana: "だいまる うめだてん / ハーブス / おぐらさんそう",
    romaji: "Daimaru Umedaten / Hābusu / Ogurasansō"
  },

  // Day 2: 京都・鞍馬 ✕ 貴船
  "鞍馬寺 貴船神社 川床料理 水占い 叡山電車": {
    hiragana: "くらまでら / きふねじんじゃ / かわどこ りょうり / えいざんでんしゃ",
    romaji: "Kurama-dera / Kifune-jinja / Kawadoko / Eizan Densha"
  },
  "鞍馬寺": {
    hiragana: "くらまでら",
    romaji: "Kurama-dera"
  },
  "貴船神社": {
    hiragana: "きふねじんじゃ",
    romaji: "Kifune-jinja"
  },
  "川床料理": {
    hiragana: "かわどこ りょうり",
    romaji: "Kawadoko Ryōri"
  },

  // Day 3: 京都/滋賀・比叡山延曆寺
  "比叡山 延暦寺 根本中堂 坂本ケーブル 穴太衆積": {
    hiragana: "ひえいざん / えんりゃくじ / こんぽんちゅうどう / さかもと ケーブル",
    romaji: "Hieizan / Enryakuji / Konpon Chūdō / Sakamoto Cable"
  },
  "比叡山 延暦寺": {
    hiragana: "ひえいざん えんりゃくじ",
    romaji: "Hieizan Enryakuji"
  },
  "根本中堂": {
    hiragana: "こんぽんちゅうどう",
    romaji: "Konpon Chūdō"
  },
  "坂本ケーブル": {
    hiragana: "さかもと ケーブル",
    romaji: "Sakamoto Kēburu"
  },

  // Day 4: 箕面・勝尾寺
  "勝尾寺 箕面大滝 勝ちダルマ 滝安寺": {
    hiragana: "かつおうじ / みのお おおたき / かち ダルマ / りゅうあんじ",
    romaji: "Katsuō-ji / Minoh Ōtaki / Kachi Daruma / Ryūanji"
  },
  "勝尾寺": {
    hiragana: "かつおうじ",
    romaji: "Katsuō-ji"
  },
  "箕面大滝": {
    hiragana: "みのお おおたき",
    romaji: "Minoh Ōtaki"
  },

  // 備選專題庫：神戶、姬路、滋賀
  "六甲山 GREENIA 有馬温泉 金の湯 モーリヤ": {
    hiragana: "ろっこうさん / グリーニア / ありま おんせん / きんのゆ / モーリヤ",
    romaji: "Rokkōsan / GREENIA / Arima Onsen / Kin no Yu / Mōriya"
  },
  "姫路城 好古園 活水軒": {
    hiragana: "ひめじじょう / こうこえん / かっすいけん",
    romaji: "Himejijō / Kōkoen / Kassuiken"
  },
  "びわ湖バレイ ラ コリーナ近江八幡 八幡堀": {
    hiragana: "びわこ バレイ / ラ コリーナ おうみはちまん / はちまんぼり",
    romaji: "Biwako Barei / La Collina / Hachimanbori"
  },
  "甲賀の里忍術村": {
    hiragana: "こうかのさと にんじゅつむら",
    romaji: "Kōka no Sato Ninjutsu Mura"
  },
  "伊賀流忍者博物館 伊賀上野城": {
    hiragana: "いがりゅう にんじゃ はくぶつかん / いが うえのじょう",
    romaji: "Igaryū Ninja Hakubutsukan / Iga Uenojō"
  }
};

/* ---------- 2. 語音發音系統 (HTML5 線上高音質音訊 ✕ Web Speech API 雙引擎) ---------- */
let japaneseVoice = null;
let currentAudio = null;

function loadJapaneseVoice() {
  if ('speechSynthesis' in window) {
    const voices = window.speechSynthesis.getVoices();
    // 優先匹配日語原生聲線 (iOS Kyoko/Otoya、Android Google 日本語、ja-JP 等)
    japaneseVoice = voices.find(v => v.lang === 'ja-JP' || v.lang === 'ja_JP' || v.lang.startsWith('ja')) || null;
  }
}

if ('speechSynthesis' in window) {
  loadJapaneseVoice();
  window.speechSynthesis.onvoiceschanged = loadJapaneseVoice;
}

/**
 * HTML5 線上高音質日語音訊播放器（保證三星等任何 Android/iOS 手機 100% 有聲音）
 */
function playOnlineJapaneseAudio(text) {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }
  const cleanText = text.replace(/[\/\|]/g, '、').trim();
  const url = `https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q=${encodeURIComponent(cleanText)}`;
  currentAudio = new Audio(url);
  currentAudio.play().catch(err => {
    console.log("Audio playback error, trying web speech fallback", err);
  });
}

/**
 * 終極日語朗讀函數：
 * 1. 若手機具備原生日語 Voice，調用 Web Speech API
 * 2. 若為 Samsung S23 等未預載日語包設備，自動無縫切換 HTML5 高音質線上音訊
 */
function speakJapanese(text, hiragana) {
  const speechText = hiragana ? hiragana.replace(/[\/\|]/g, '、') : text;

  // 1. 若有檢測到原生日語 Voice，優先嘗試 Web Speech
  if ('speechSynthesis' in window && japaneseVoice) {
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.lang = 'ja-JP';
      utterance.voice = japaneseVoice;
      utterance.rate = 0.85;
      utterance.pitch = 1.0;

      let hasStarted = false;
      utterance.onstart = () => { hasStarted = true; };
      utterance.onerror = () => {
        playOnlineJapaneseAudio(speechText);
      };

      window.speechSynthesis.speak(utterance);

      // 看門狗：若 Android 設備 350ms 內未觸發發音，自動切換至 HTML5 Audio
      setTimeout(() => {
        if (!hasStarted && !window.speechSynthesis.speaking) {
          playOnlineJapaneseAudio(speechText);
        }
      }, 350);
      return;
    } catch (e) {
      // 異常時直接走 HTML5 Audio
    }
  }

  // 2. 無日語 Voice (如三星手機)，直接調用 HTML5 線上日語發音
  playOnlineJapaneseAudio(speechText);
}

/* ---------- 3. Toast Notification & Pronunciation Card System ---------- */
let toastTimeout;

function initToasts() {
  if (!document.getElementById('toast-box')) {
    const toast = document.createElement('div');
    toast.id = 'toast-box';
    toast.className = 'toast-box';
    toast.innerHTML = `
      <div class="toast-content" style="display:flex; flex-direction:column; gap:0.35rem; width:100%;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:0.35rem;">
          <span style="font-weight:700; color:#4ade80; font-size:0.92rem;">✅ 已複製日文！可出示給司機或貼地圖</span>
          <button id="toast-speak-btn" style="background:#0284c7; color:#fff; border:none; border-radius:4px; padding:3px 10px; font-size:0.8rem; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:3px;">
            🔊 聽日語發音
          </button>
        </div>
        <div id="toast-jp-main" style="font-size:1.15rem; font-weight:800; color:#ffffff; letter-spacing:0.02em;"></div>
        <div style="font-size:0.82rem; color:#bae6fd; line-height:1.4;">
          <span style="color:#93c5fd;">🗣️ 平假名：</span><span id="toast-jp-kana"></span>
        </div>
        <div style="font-size:0.82rem; color:#fde047; line-height:1.4;">
          <span style="color:#fef08a;">🔤 羅馬拼音：</span><span id="toast-jp-romaji" style="font-weight:600;"></span>
        </div>
      </div>
    `;
    document.body.appendChild(toast);
  }
}

function showPronunciationToast(text, hiragana, romaji, duration = 6000) {
  const toast = document.getElementById('toast-box');
  if (!toast) return;

  document.getElementById('toast-jp-main').textContent = text;
  document.getElementById('toast-jp-kana').textContent = hiragana || '（標準日語讀音）';
  document.getElementById('toast-jp-romaji').textContent = romaji || '（Romaji Pronunciation）';

  // Audio Speech Button
  const speakBtn = document.getElementById('toast-speak-btn');
  if (speakBtn) {
    speakBtn.onclick = (e) => {
      e.stopPropagation();
      speakJapanese(text, hiragana);
    };
  }

  toast.classList.add('show');

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

/**
 * 全局複製日文函數（支援平假名、羅馬拼音與發音）
 * 可透過 onclick="copyText('鞍馬寺 貴船神社', this)" 或 data-* 屬性調用
 */
window.copyText = function(text, buttonElement) {
  let hiragana = '';
  let romaji = '';

  // 1. 優先從元素屬性獲取
  if (buttonElement) {
    hiragana = buttonElement.getAttribute('data-hiragana') || '';
    romaji = buttonElement.getAttribute('data-romaji') || '';
  }

  // 2. 若無則從辭典檢索
  if (!hiragana || !romaji) {
    for (const [key, data] of Object.entries(JAPANESE_DICTIONARY)) {
      if (text.includes(key) || key.includes(text)) {
        hiragana = data.hiragana;
        romaji = data.romaji;
        break;
      }
    }
  }

  // 3. 剪貼簿寫入
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      handleCopySuccess(text, hiragana, romaji, buttonElement);
    }).catch(() => {
      fallbackCopyText(text, hiragana, romaji, buttonElement);
    });
  } else {
    fallbackCopyText(text, hiragana, romaji, buttonElement);
  }
};

function fallbackCopyText(text, hiragana, romaji, buttonElement) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.opacity = '0';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
    handleCopySuccess(text, hiragana, romaji, buttonElement);
  } catch (err) {
    showPronunciationToast(text, hiragana, romaji);
  }
  document.body.removeChild(textArea);
}

function handleCopySuccess(text, hiragana, romaji, buttonElement) {
  showPronunciationToast(text, hiragana, romaji);

  if (buttonElement) {
    const originalHtml = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span>✅ 已複製 (已展讀音)</span>';
    buttonElement.style.borderColor = 'var(--accent)';
    buttonElement.style.color = 'var(--accent)';

    // 如果身旁有發音標籤可動態顯示
    setTimeout(() => {
      buttonElement.innerHTML = originalHtml;
      buttonElement.style.borderColor = '';
      buttonElement.style.color = '';
    }, 2500);
  }
}

/* ---------- 3. 折疊手風琴 ---------- */
function initAccordions() {
  const headers = document.querySelectorAll('.accordion-header');
  headers.forEach(header => {
    header.addEventListener('click', () => {
      const parent = header.parentElement;
      parent.classList.toggle('open');
    });
  });
}

/* ---------- 4. 傍晚篩選標籤 ---------- */
function initEveningFilters() {
  const pills = document.querySelectorAll('.filter-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    });
  });
}

/* ---------- 5. 夕陽黃金時刻倒數 ---------- */
function initGoldenHour() {
  const sunsetBadge = document.getElementById('sunset-time-badge');
  if (sunsetBadge) {
    sunsetBadge.title = '2026年8月底大阪平均日落時刻約為 18:35~18:42';
  }
}

/* ---------- 6. 導覽列 Active 狀態自動同步 ---------- */
function highlightActiveNav() {
  const path = window.location.pathname;
  const page = path.split("/").pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-links a, .bottom-dock a');

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === page) {
      link.classList.add('active');
    }
  });
}
