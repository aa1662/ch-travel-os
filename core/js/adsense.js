/* One manual footer placement. Local preview never requests Google ads. */
function initArticleAd() {
  const section = document.querySelector('.article-ad');
  if (!section) return;
  const host = window.location.hostname;
  const slot = section.querySelector('.article-ad-slot');
  if (!slot) return;
  if (['localhost', '127.0.0.1', '[::1]'].includes(host)) {
    const preview = document.createElement('div');
    preview.className = 'article-ad-preview';
    preview.textContent = '文章底部廣告橫幅｜本機版位預覽，不載入正式廣告';
    slot.appendChild(preview);
    section.hidden = false;
    return;
  }
  // Remains off until site approval and consent/privacy setup are confirmed.
  if (!['chxtravel.com', 'www.chxtravel.com'].includes(host) ||
      section.dataset.enabled !== 'true') return;
  const client = section.dataset.client;
  const adSlot = section.dataset.slot;
  if (!/^ca-pub-\d{16}$/.test(client) || !/^\d+$/.test(adSlot)) return;
  section.hidden = false;
  if (slot.getBoundingClientRect().width < 250) {
    section.hidden = true;
    return;
  }
  const ad = document.createElement('ins');
  ad.className = 'adsbygoogle';
  ad.style.display = 'block';
  ad.dataset.adClient = client;
  ad.dataset.adSlot = adSlot;
  ad.dataset.adFormat = 'horizontal';
  ad.dataset.fullWidthResponsive = 'false';
  slot.appendChild(ad);
  // Collapse unfilled inventory without changing the ad iframe itself.
  const observer = new MutationObserver(() => {
    if (ad.dataset.adStatus === 'unfilled') {
      section.hidden = true;
      observer.disconnect();
    }
  });
  observer.observe(ad, { attributes: true, attributeFilter: ['data-ad-status'] });
  if (!document.querySelector('script[data-ch-adsense]')) {
    const script = document.createElement('script');
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.dataset.chAdsense = 'true';
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + client;
    script.onerror = () => { section.hidden = true; observer.disconnect(); };
    document.head.appendChild(script);
  }
  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (error) {
    section.hidden = true;
    observer.disconnect();
  }
}
document.addEventListener('DOMContentLoaded', initArticleAd);
