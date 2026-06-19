/* ================================================================
   CareerRecommender  —  main.js
   Handles: dark mode toggle, flash messages, general interactions
================================================================ */

const THEME_KEY = 'cp-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  const btn  = document.getElementById('themeToggle');
  const icon = document.getElementById('themeIcon');
  const text = document.getElementById('themeText');
  if (!btn) return;

  if (theme === 'dark') {
    icon.className = 'fa-solid fa-sun';
    text.textContent = 'Light';
  } else {
    icon.className = 'fa-solid fa-moon';
    text.textContent = 'Dark';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

(function () {
  const saved = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', saved);
})();

function dismissFlash(el) {
  el.style.animation = 'slideIn .25s ease reverse';
  setTimeout(() => el.remove(), 250);
}

function initFlashMessages() {
  document.querySelectorAll('.flash-msg').forEach(msg => {
    msg.addEventListener('click', () => dismissFlash(msg));
    setTimeout(() => {
      if (msg.parentNode) dismissFlash(msg);
    }, 5000);
  });
}

function initPasswordToggles() {
  document.querySelectorAll('.pw-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (!input) return;
      const isPass = input.type === 'password';
      input.type = isPass ? 'text' : 'password';
      btn.querySelector('i').className = isPass ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
    });
  });
}

function animateProgressBars() {
  document.querySelectorAll('.cp-progress-fill[data-width]').forEach(bar => {
    const target = bar.getAttribute('data-width');
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = target; }, 100);
    });
  });
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function initNavScroll() {
  const nav = document.querySelector('.cp-nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      nav.style.boxShadow = '0 4px 24px rgba(0,0,0,.1)';
    } else {
      nav.style.boxShadow = 'none';
    }
  }, { passive: true });
}

function animateHeroBars() {
  document.querySelectorAll('.match-bar-fill').forEach(bar => {
    const w = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.transition = 'width 1.2s cubic-bezier(.4,0,.2,1)';
      bar.style.width = w;
    }, 600);
  });
}

function initTooltips() {
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(saved);

  initFlashMessages();
  initPasswordToggles();
  animateProgressBars();
  initSmoothScroll();
  initNavScroll();
  animateHeroBars();
  initTooltips();

  const btn = document.getElementById('themeToggle');
  if (btn) btn.addEventListener('click', toggleTheme);
});