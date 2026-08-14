/*
  ============================================================
  overlay.js — Controlador partilhado de painéis sobrepostos
  ============================================================

  O QUE FAZ:
  Um único dono para tudo o que abre "por cima" da página: menu mobile, overlay
  de pesquisa e painel do carrinho. Trata do scrim, do bloqueio de scroll do
  body, da tecla Escape, da prisão de foco e da devolução do foco ao botão que
  abriu o painel.

  PORQUÊ CENTRALIZAR:
  Estes painéis partilham um só scrim e um só estado de scroll do body. Se cada
  um gerisse o seu, abrir o carrinho com o menu aberto deixaria o scrim órfão ou
  o body preso em overflow:hidden. Com um controlador único, abrir um painel
  fecha automaticamente o anterior.

  API:
    VDN.overlay.open(elemento, botaoQueAbriu)
    VDN.overlay.close()
    VDN.overlay.isOpen(elemento)   → booleano
    VDN.overlay.current()          → elemento aberto ou null

  CONTRATO DO PAINEL:
  O elemento tem de começar com [hidden] e o seu CSS deve animar a entrada
  através da classe .is-open (normalmente um transform). O controlador remove o
  [hidden], força um reflow e só então aplica .is-open, para que a transição
  de entrada corra sempre.

  ACESSIBILIDADE:
  Enquanto um painel está aberto, o Tab circula apenas dentro dele e o Escape
  fecha-o. O foco volta sempre ao elemento que o abriu.
*/
(function () {
  'use strict';

  var FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
    'textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

  // Tem de acompanhar a transição mais lenta dos painéis (--dur-3 = 400ms).
  var EXIT_MS = 450;

  var openEl = null;
  var lastTrigger = null;
  var hideTimer = null;

  function scrim() {
    return document.querySelector('[data-scrim]');
  }

  function visibleFocusable(container) {
    return Array.prototype.filter.call(container.querySelectorAll(FOCUSABLE), function (el) {
      return el.offsetParent !== null || el === document.activeElement;
    });
  }

  function open(el, trigger) {
    if (!el) return;
    if (openEl === el) return;
    if (openEl) close({ silent: true });

    window.clearTimeout(hideTimer);

    openEl = el;
    lastTrigger = trigger || document.activeElement;

    var s = scrim();
    el.hidden = false;
    if (s) s.hidden = false;

    // Forçar reflow para que .is-open produza transição em vez de salto.
    void el.offsetWidth;

    el.classList.add('is-open');
    if (s) s.classList.add('is-open');
    document.body.classList.add('overlay-open');

    if (trigger && trigger.hasAttribute('aria-expanded')) {
      trigger.setAttribute('aria-expanded', 'true');
    }

    var target = el.querySelector('[data-overlay-focus]') || visibleFocusable(el)[0];
    if (target) target.focus();

    el.dispatchEvent(new CustomEvent('overlay:open', { bubbles: true }));
  }

  function close(opts) {
    if (!openEl) return;

    var el = openEl;
    var trigger = lastTrigger;
    openEl = null;
    lastTrigger = null;

    var s = scrim();
    el.classList.remove('is-open');
    if (s) s.classList.remove('is-open');
    document.body.classList.remove('overlay-open');

    document.querySelectorAll('[aria-expanded="true"]').forEach(function (btn) {
      btn.setAttribute('aria-expanded', 'false');
    });

    // Esconder só no fim da animação de saída, senão o painel desaparece de golpe.
    hideTimer = window.setTimeout(function () {
      if (openEl !== el) el.hidden = true;
      if (!openEl && s) s.hidden = true;
    }, EXIT_MS);

    if (trigger && !(opts && opts.silent)) {
      try { trigger.focus(); } catch (e) { /* o botão pode já não existir */ }
    }

    el.dispatchEvent(new CustomEvent('overlay:close', { bubbles: true }));
  }

  document.addEventListener('keydown', function (e) {
    if (!openEl) return;

    if (e.key === 'Escape') {
      close();
      return;
    }

    if (e.key !== 'Tab') return;

    var items = visibleFocusable(openEl);
    if (!items.length) return;

    var first = items[0];
    var last = items[items.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    } else if (!openEl.contains(document.activeElement)) {
      // O foco escapou (ex.: painel re-renderizado): trazer de volta.
      e.preventDefault();
      first.focus();
    }
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-scrim]')) close();
  });

  window.VDN = window.VDN || {};
  window.VDN.overlay = {
    open: open,
    close: close,
    current: function () { return openEl; },
    isOpen: function (el) { return openEl === el; }
  };
})();
