/* CareerRecommender — assessment.js */

document.addEventListener('DOMContentLoaded', function () {

  var groups      = Array.from(document.querySelectorAll('.question-group'));
  var stepDots    = Array.from(document.querySelectorAll('.cat-step'));
  var progressBar = document.getElementById('assessmentProgress');
  var progressTxt = document.getElementById('progressText');
  var btnPrev     = document.getElementById('btnPrev');
  var btnNext     = document.getElementById('btnNext');
  var btnSubmit   = document.getElementById('btnSubmit');
  var form        = document.getElementById('assessmentForm');

  if (!groups.length || !form) return;

  var current = 0;
  var total   = groups.length;

  function showStep(idx) {
    groups.forEach(function (g, i) {
      g.classList.toggle('active', i === idx);
    });
    stepDots.forEach(function (dot, i) {
      dot.classList.remove('active', 'done');
      if (i === idx) dot.classList.add('active');
      if (i < idx)   dot.classList.add('done');
    });

    var pct = Math.round(((idx + 1) / total) * 100);
    if (progressBar) progressBar.style.width = pct + '%';
    if (progressTxt) progressTxt.textContent =
      'Step ' + (idx + 1) + ' of ' + total;

    if (btnPrev)
      btnPrev.style.display = idx === 0 ? 'none' : 'inline-flex';
    if (btnNext)
      btnNext.style.display = idx < total - 1 ? 'inline-flex' : 'none';
    if (btnSubmit)
      btnSubmit.style.display = idx === total - 1 ? 'inline-flex' : 'none';

    var wrap = document.querySelector('.assessment-wrap');
    if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function validateCurrent() {
    var group   = groups[current];
    var radios  = group.querySelectorAll('input[type="radio"]');
    var names   = new Set(Array.from(radios).map(function (r) {
      return r.name;
    }));
    var missing = [];

    names.forEach(function (name) {
      if (!group.querySelector('input[name="' + name + '"]:checked')) {
        missing.push(name);
      }
    });

    group.querySelectorAll('.q-card').forEach(function (card) {
      var inputs = card.querySelectorAll('input[type="radio"]');
      if (!inputs.length) return;
      var unanswered = missing.includes(inputs[0].name);
      card.style.borderColor = unanswered ? '#ef4444' : '';
      card.style.boxShadow   =
        unanswered ? '0 0 0 2px rgba(239,68,68,.2)' : '';
    });

    if (missing.length) {
      toast(
        'Please answer all ' + missing.length +
        ' question(s) before continuing.',
        'error'
      );
      return false;
    }
    return true;
  }

  function toast(msg, type) {
    type = type || 'info';
    var container = document.querySelector('.flash-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'flash-container';
      document.body.appendChild(container);
    }
    var icons = {
      error:   'fa-circle-exclamation',
      success: 'fa-circle-check',
      info:    'fa-circle-info'
    };
    var el = document.createElement('div');
    el.className = 'flash-msg ' + type;
    el.innerHTML =
      '<i class="fa-solid ' + (icons[type] || icons.info) + '"></i> ' + msg;
    container.appendChild(el);
    el.addEventListener('click', function () { el.remove(); });
    setTimeout(function () { if (el.parentNode) el.remove(); }, 4500);
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      if (current > 0) { current--; showStep(current); }
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (!validateCurrent()) return;
      if (current < total - 1) { current++; showStep(current); }
    });
  }

  form.addEventListener('submit', function (e) {
    var firstFail = -1;
    groups.forEach(function (group, idx) {
      var radios = group.querySelectorAll('input[type="radio"]');
      var names  = new Set(Array.from(radios).map(function (r) {
        return r.name;
      }));
      names.forEach(function (name) {
        if (!group.querySelector('input[name="' + name + '"]:checked')) {
          if (firstFail === -1) firstFail = idx;
        }
      });
    });

    if (firstFail !== -1) {
      e.preventDefault();
      current = firstFail;
      showStep(current);
      validateCurrent();
      toast('Please answer all questions before submitting.', 'error');
    }
  });

  document.querySelectorAll('.q-card input[type="radio"]').forEach(
    function (radio) {
      radio.addEventListener('change', function () {
        var card = radio.closest('.q-card');
        if (card) {
          card.style.borderColor = '';
          card.style.boxShadow   = '';
        }
      });
    }
  );

  showStep(0);
});