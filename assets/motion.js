/*
  ============================================================
  motion.js — Movimento do tema Ventos do Norte
  ============================================================

  O QUE FAZ:
  Três comportamentos, todos opcionais e progressivos (a página funciona
  na íntegra sem este ficheiro):

  1. REVEAL — elementos com [data-reveal] entram no ecrã com fade + deslize.
     Use [data-reveal-stagger] num contentor para escalonar os filhos.
  2. PARALLAX — elementos com [data-parallax] deslocam-se a uma fração da
     velocidade do scroll. O valor é o multiplicador (ex: data-parallax="0.15").
  3. HEADER — publica a distância de scroll e um estado no <html>, para o
     cabeçalho encolher/mudar de cor só com CSS.

  ACESSIBILIDADE:
  Se o utilizador pedir prefers-reduced-motion, nada disto arranca: os elementos
  são revelados imediatamente e o parallax nunca é registado. A media query é
  observada em tempo real — mudar a preferência no sistema operativo tem efeito
  sem recarregar a página.

  PERFORMANCE:
  - O reveal usa IntersectionObserver e deixa de observar cada elemento assim que
    ele aparece (one-shot).
  - O parallax só corre dentro de requestAnimationFrame e apenas para os
    elementos que estão no viewport, e só escreve em transform (nunca em top /
    margin), portanto não força reflow.
*/
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var root = document.documentElement;

  /* --------------------------------------------------------
     1. REVEAL
     -------------------------------------------------------- */

  function revealNow(el) {
    el.classList.add('is-revealed');
  }

  function setupReveal() {
    var items = document.querySelectorAll('[data-reveal]');
    if (!items.length) return;

    // Sem IntersectionObserver ou com movimento reduzido: mostrar tudo já.
    if (reduceMotion.matches || !('IntersectionObserver' in window)) {
      items.forEach(revealNow);
      return;
    }

    // Escalonar os filhos de cada contentor marcado.
    document.querySelectorAll('[data-reveal-stagger]').forEach(function (group) {
      var step = parseInt(group.getAttribute('data-reveal-stagger'), 10) || 80;
      var children = group.querySelectorAll(':scope > [data-reveal]');
      children.forEach(function (child, i) {
        child.style.setProperty('--reveal-delay', i * step + 'ms');
      });
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          revealNow(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.08 }
    );

    items.forEach(function (el) {
      // Já visível no carregamento (acima da dobra): revelar sem esperar o scroll.
      if (el.getBoundingClientRect().top < window.innerHeight * 0.9) {
        revealNow(el);
        return;
      }
      observer.observe(el);
    });
  }

  /* --------------------------------------------------------
     2. PARALLAX
     -------------------------------------------------------- */

  var parallaxItems = [];
  var ticking = false;

  function readParallax() {
    parallaxItems = [];
    if (reduceMotion.matches) return;

    document.querySelectorAll('[data-parallax]').forEach(function (el) {
      var speed = parseFloat(el.getAttribute('data-parallax'));
      if (!speed) return;
      parallaxItems.push({ el: el, speed: speed });
    });
  }

  function applyParallax() {
    ticking = false;
    var vh = window.innerHeight;

    for (var i = 0; i < parallaxItems.length; i++) {
      var item = parallaxItems[i];
      var rect = item.el.getBoundingClientRect();

      // Fora do ecrã (com margem): não vale gastar transform.
      if (rect.bottom < -200 || rect.top > vh + 200) continue;

      // Distância do centro do elemento ao centro do viewport.
      var offset = rect.top + rect.height / 2 - vh / 2;
      item.el.style.transform = 'translate3d(0,' + (-offset * item.speed).toFixed(2) + 'px,0)';
    }
  }

  function onScroll() {
    if (ticking || !parallaxItems.length) return;
    ticking = true;
    window.requestAnimationFrame(applyParallax);
  }

  /* --------------------------------------------------------
     3. ESTADO DE SCROLL PARA O CABEÇALHO
     -------------------------------------------------------- */

  var lastY = 0;

  function onScrollHeader() {
    var y = window.pageYOffset || root.scrollTop || 0;

    root.classList.toggle('is-scrolled', y > 24);
    // Esconder o cabeçalho ao descer, mostrar ao subir (só depois da dobra).
    root.classList.toggle('is-scrolling-down', y > lastY && y > 400);

    lastY = y;
  }

  /* --------------------------------------------------------
     4. ANIMAÇÕES SMIL DO SVG
     -------------------------------------------------------- */

  // As <animate> dentro de SVG são SMIL, não CSS: a media query
  // prefers-reduced-motion não lhes toca. Quem as pára é o pauseAnimations()
  // do próprio elemento <svg>. Sem isto, quem pede movimento reduzido
  // continuaria a ver as linhas de vento a ondular.
  function applySvgMotion() {
    document.querySelectorAll('svg').forEach(function (svg) {
      if (typeof svg.pauseAnimations !== 'function') return;
      if (reduceMotion.matches) {
        svg.pauseAnimations();
        svg.setCurrentTime(0);
      } else {
        svg.unpauseAnimations();
      }
    });
  }

  /* --------------------------------------------------------
     Arranque
     -------------------------------------------------------- */

  function init() {
    applySvgMotion();
    setupReveal();
    readParallax();
    applyParallax();
    onScrollHeader();

    window.addEventListener(
      'scroll',
      function () {
        onScroll();
        onScrollHeader();
      },
      { passive: true }
    );

    window.addEventListener('resize', function () {
      readParallax();
      onScroll();
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // O editor de tema recria secções sem recarregar a página.
  document.addEventListener('shopify:section:load', function () {
    applySvgMotion();
    setupReveal();
    readParallax();
  });

  // Reagir à mudança de preferência de movimento sem recarregar.
  var onMotionChange = function () {
    if (reduceMotion.matches) {
      document.querySelectorAll('[data-parallax]').forEach(function (el) {
        el.style.transform = '';
      });
      document.querySelectorAll('[data-reveal]').forEach(revealNow);
    }
    applySvgMotion();
    readParallax();
    onScroll();
  };

  if (typeof reduceMotion.addEventListener === 'function') {
    reduceMotion.addEventListener('change', onMotionChange);
  } else if (typeof reduceMotion.addListener === 'function') {
    reduceMotion.addListener(onMotionChange);
  }
})();
