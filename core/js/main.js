/**
 * 2026 德國南部冬季旅遊網頁 - 主要 JavaScript
 * 版本：1.0
 */

(function() {
  'use strict';

  // ========== 手機版選單切換 ==========
  function initMobileMenu() {
    const toggle = document.querySelector('.navbar-toggle');
    const menu = document.querySelector('.navbar-menu');
    
    if (toggle && menu) {
      toggle.addEventListener('click', function() {
        menu.classList.toggle('open');
        const isOpen = menu.classList.contains('open');
        toggle.setAttribute('aria-expanded', isOpen);
        toggle.innerHTML = isOpen ? '✕' : '☰';
      });

      // 點擊選單項目後自動收合
      menu.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
          menu.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.innerHTML = '☰';
        });
      });
    }
  }

  // ========== 分享功能 ==========
  function initShareButton() {
    const shareBtn = document.querySelector('.navbar-share');
    
    if (shareBtn) {
      shareBtn.addEventListener('click', async function() {
        const url = window.location.href;
        const title = document.title;
        
        // 嘗試使用 Web Share API（手機上）
        if (navigator.share) {
          try {
            await navigator.share({
              title: title,
              url: url
            });
          } catch (err) {
            // 用戶取消分享，忽略錯誤
            if (err.name !== 'AbortError') {
              console.error('分享失敗:', err);
            }
          }
        } else {
          // 桌機上複製到剪貼簿
          try {
            await navigator.clipboard.writeText(url);
            showToast('已複製網址！');
          } catch (err) {
            // 備用方案
            const textarea = document.createElement('textarea');
            textarea.value = url;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('已複製網址！');
          }
        }
      });
    }
  }

  // ========== Toast 提示 ==========
  function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      background: #333;
      color: white;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      z-index: 1000;
      animation: fadeInUp 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
      toast.style.animation = 'fadeOut 0.3s ease';
      setTimeout(function() {
        toast.remove();
      }, 300);
    }, 2000);
  }

  // ========== 可收合區塊 ==========
  function initCollapsibles() {
    const collapsibles = document.querySelectorAll('.collapsible');
    
    collapsibles.forEach(function(item) {
      const header = item.querySelector('.collapsible-header');
      
      if (header) {
        header.addEventListener('click', function() {
          item.classList.toggle('open');
        });
      }
    });
  }

  // ========== Day 切換按鈕狀態 ==========
  function initDaySwitcher() {
    const currentPath = window.location.pathname;
    const dayBtns = document.querySelectorAll('.day-btn');
    
    dayBtns.forEach(function(btn) {
      const href = btn.getAttribute('href');
      if (href && currentPath.includes(href.replace('./', ''))) {
        btn.classList.add('active');
      }
    });
  }

  // ========== 時間軸卡片點擊 ==========
  function initTimelineCards() {
    const cards = document.querySelectorAll('.timeline-card');
    
    cards.forEach(function(card) {
      card.addEventListener('click', function() {
        const link = card.getAttribute('data-href');
        if (link) {
          window.location.href = link;
        }
      });
    });
  }

  // ========== 初始化 ==========
  document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initShareButton();
    initCollapsibles();
    initDaySwitcher();
    initTimelineCards();
  });

  // 加入 CSS 動畫
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeInUp {
      from { opacity: 0; transform: translate(-50%, 10px); }
      to { opacity: 1; transform: translate(-50%, 0); }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
  `;
  document.head.appendChild(style);

})();

