/* CareerRecommender — main.js */

const THEME_KEY = 'cp-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  var icon = document.getElementById('themeIcon');
  var text = document.getElementById('themeText');
  if (!icon || !text) return;
  if (theme === 'dark') {
    icon.className = 'fa-solid fa-sun';
    text.textContent = 'Light';
  } else {
    icon.className = 'fa-solid fa-moon';
    text.textContent = 'Dark';
  }
}

// Apply before paint to prevent flash
(function () {
  var t = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', t);
})();

function dismissFlash(el) {
  el.style.opacity = '0';
  el.style.transform = 'translateX(20px)';
  setTimeout(function () { if (el.parentNode) el.remove(); }, 300);
}

function initFlash() {
  document.querySelectorAll('.flash-msg').forEach(function (msg) {
    msg.addEventListener('click', function () { dismissFlash(msg); });
    setTimeout(function () { if (msg.parentNode) dismissFlash(msg); }, 5000);
  });
}

function initPasswordToggles() {
  document.querySelectorAll('.pw-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = btn.previousElementSibling;
      if (!input) return;
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.querySelector('i').className =
        show ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
    });
  });
}

function animateProgressBars() {
  document.querySelectorAll('.cp-progress-fill[data-width]').forEach(function (bar) {
    var target = bar.getAttribute('data-width');
    bar.style.width = '0%';
    requestAnimationFrame(function () {
      setTimeout(function () { bar.style.width = target; }, 100);
    });
  });
}

function animateHeroBars() {
  document.querySelectorAll('.match-bar-fill').forEach(function (bar) {
    var w = bar.style.width;
    bar.style.width = '0%';
    setTimeout(function () {
      bar.style.transition = 'width 1.4s cubic-bezier(.4,0,.2,1)';
      bar.style.width = w;
    }, 500);
  });
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function initNavScroll() {
  var nav = document.querySelector('.cp-nav');
  if (!nav) return;
  window.addEventListener('scroll', function () {
    nav.style.boxShadow =
      window.scrollY > 20 ? '0 4px 24px rgba(0,0,0,.12)' : 'none';
  }, { passive: true });
}

function initTooltips() {
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  }
}

document.addEventListener('DOMContentLoaded', function () {
  var saved = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(saved);

  var btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', function () {
      var current =
        document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  initFlash();
  initPasswordToggles();
  animateProgressBars();
  animateHeroBars();
  initSmoothScroll();
  initNavScroll();
  initTooltips();
});