/* ================================================================
   CareerRecommender  —  assessment.js
   Multi-step assessment wizard with category navigation
================================================================ */

(function () {
  const groups     = Array.from(document.querySelectorAll('.question-group'));
  const catSteps   = Array.from(document.querySelectorAll('.cat-step'));
  const progressFill = document.getElementById('assessmentProgress');
  const progressText = document.getElementById('progressText');
  const btnPrev    = document.getElementById('btnPrev');
  const btnNext    = document.getElementById('btnNext');
  const btnSubmit  = document.getElementById('btnSubmit');
  const form       = document.getElementById('assessmentForm');

  let current = 0;

  if (!groups.length) return;

  function showStep(idx) {
    groups.forEach((g, i) => {
      g.classList.toggle('active', i === idx);
    });
    catSteps.forEach((s, i) => {
      s.classList.remove('active', 'done');
      if (i === idx)  s.classList.add('active');
      if (i < idx)    s.classList.add('done');
    });

    const pct = Math.round(((idx + 1) / groups.length) * 100);
    if (progressFill) progressFill.style.width = pct + '%';
    if (progressText) progressText.textContent  = `Step ${idx + 1} of ${groups.length}`;

    if (btnPrev)   btnPrev.style.display   = idx === 0 ? 'none' : 'inline-flex';
    if (btnNext)   btnNext.style.display   = idx < groups.length - 1 ? 'inline-flex' : 'none';
    if (btnSubmit) btnSubmit.style.display = idx === groups.length - 1 ? 'inline-flex' : 'none';

    const top = document.querySelector('.assessment-wrap');
    if (top) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function validateCurrent() {
    const group   = groups[current];
    const radios  = group.querySelectorAll('input[type="radio"]');
    const names   = new Set(Array.from(radios).map(r => r.name));
    const missing = [];

    names.forEach(name => {
      const answered = group.querySelector(`input[name="${name}"]:checked`);
      if (!answered) missing.push(name);
    });

    group.querySelectorAll('.q-card').forEach(card => {
      const inputs = card.querySelectorAll('input[type="radio"]');
      if (!inputs.length) return;
      const answered = card.querySelector('input[type="radio"]:checked');
      if (answered) {
        card.style.borderColor = '';
      } else if (missing.includes(inputs[0].name)) {
        card.style.borderColor = '#ff4d6d';
      }
    });

    if (missing.length) {
      showToast(`Please answer all ${missing.length} question(s) in this section.`, 'error');
      return false;
    }
    return true;
  }

  function showToast(msg, type='info') {
    let container = document.querySelector('.flash-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'flash-container';
      document.body.appendChild(container);
    }
    const icons = { error: 'fa-circle-exclamation', success: 'fa-circle-check', info: 'fa-circle-info' };
    const div = document.createElement('div');
    div.className = `flash-msg ${type}`;
    div.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i> ${msg}`;
    container.appendChild(div);
    div.addEventListener('click', () => div.remove());
    setTimeout(() => { if (div.parentNode) div.remove(); }, 4000);
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (current > 0) { current--; showStep(current); }
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (!validateCurrent()) return;
      if (current < groups.length - 1) { current++; showStep(current); }
    });
  }

  if (form) {
    form.addEventListener('submit', e => {
      let firstFail = -1;
      groups.forEach((group, idx) => {
        const radios = group.querySelectorAll('input[type="radio"]');
        const names  = new Set(Array.from(radios).map(r => r.name));
        names.forEach(name => {
          if (!group.querySelector(`input[name="${name}"]:checked`)) {
            if (firstFail === -1) firstFail = idx;
          }
        });
      });

      if (firstFail !== -1) {
        e.preventDefault();
        current = firstFail;
        showStep(current);
        validateCurrent();
        showToast('Please answer all questions before submitting.', 'error');
      }
    });
  }

  document.querySelectorAll('.q-card input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', () => {
      const card = radio.closest('.q-card');
      if (card) card.style.borderColor = '';
    });
  });

  showStep(0);
})();