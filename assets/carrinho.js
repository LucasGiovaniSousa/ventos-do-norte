/*
  ============================================================
  carrinho.js — Carrinho AJAX + painel lateral
  ============================================================

  O QUE FAZ:
  1. Intercepta os formulários de add-to-cart e envia-os para /cart/add.js.
  2. Trata dos controlos de quantidade e de remover dentro do painel.
  3. Guarda a nota da encomenda.
  4. Mantém o contador do cabeçalho sincronizado (com animação).

  A SECTION RENDERING API:
  Todos os pedidos incluem `sections: 'cart-drawer'`. O Shopify devolve o HTML
  já atualizado do painel na MESMA resposta da alteração, o que evita o padrão
  habitual de dois pedidos ("altera" seguido de "volta a ler o carrinho") e
  elimina o estado intermédio em que o painel mostra dados velhos.

  SEM JAVASCRIPT:
  Nada aqui é obrigatório. O formulário de produto submete nativamente para
  /cart/add, e os botões de quantidade/remover do painel são links reais para
  /cart/change. Se um pedido falhar, fazemos fallback para a navegação normal
  em vez de deixar o utilizador preso.

  DEPENDÊNCIAS:
  - assets/overlay.js  → abrir/fechar o painel, scrim, foco
  - snippets/alerta.liquid → window.mostrarAlerta para as confirmações
*/
(function () {
  'use strict';

  var SECTION = 'cart-drawer';

  function root() {
    return (window.Shopify && window.Shopify.routes && window.Shopify.routes.root) || '/';
  }

  function strings() {
    return window.themeStrings || {};
  }

  function toast(message, type) {
    if (typeof window.mostrarAlerta === 'function') {
      window.mostrarAlerta(message, type || 'positivo');
    }
  }

  /* --------------------------------------------------------
     Contador do cabeçalho
     -------------------------------------------------------- */

  function setCount(count) {
    document.querySelectorAll('[data-cart-count]').forEach(function (el) {
      var previous = parseInt(el.textContent, 10) || 0;

      el.textContent = count;
      el.classList.toggle('is-empty', count === 0);

      if (count > previous) {
        el.classList.remove('is-bumped');
        void el.offsetWidth;
        el.classList.add('is-bumped');
      }
    });
  }

  /* --------------------------------------------------------
     Painel
     -------------------------------------------------------- */

  function drawer() {
    return document.querySelector('[data-cart-drawer]');
  }

  function openDrawer(trigger) {
    var el = drawer();
    if (!el || !window.VDN || !window.VDN.overlay) return false;
    window.VDN.overlay.open(el, trigger);
    return true;
  }

  // Substitui o conteúdo do painel pelo HTML devolvido pela Section Rendering API,
  // preservando o estado de aberto (o markup novo vem sempre fechado).
  function render(html) {
    var host = document.getElementById('shopify-section-' + SECTION);
    if (!host || !html) return;

    var wasOpen = window.VDN && window.VDN.overlay && window.VDN.overlay.isOpen(drawer());

    var parsed = new DOMParser().parseFromString(html, 'text/html');
    var fresh = parsed.getElementById('shopify-section-' + SECTION);
    host.innerHTML = fresh ? fresh.innerHTML : html;

    var el = drawer();
    if (el && wasOpen) {
      el.hidden = false;
      void el.offsetWidth;
      el.classList.add('is-open');
    }
  }

  function busy(state) {
    var el = drawer();
    if (el) el.setAttribute('aria-busy', String(!!state));
  }

  /* --------------------------------------------------------
     Pedidos à Cart AJAX API
     -------------------------------------------------------- */

  function post(url, body, isForm) {
    var options = { method: 'POST', headers: { Accept: 'application/json' } };

    if (isForm) {
      options.body = body;
    } else {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }

    return fetch(root() + url, options).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok) throw data;
        return data;
      });
    });
  }

  function applyCart(data) {
    if (data && data.sections && data.sections[SECTION]) render(data.sections[SECTION]);

    // O painel re-renderizado carrega o total atualizado, por isso não é
    // preciso um pedido extra a /cart.js só para o contador.
    var el = drawer();
    if (el && el.hasAttribute('data-item-count')) {
      setCount(parseInt(el.getAttribute('data-item-count'), 10) || 0);
    } else if (data && typeof data.item_count === 'number') {
      setCount(data.item_count);
    }
  }

  /* --------------------------------------------------------
     1. Adicionar ao carrinho
     -------------------------------------------------------- */

  function onSubmit(event) {
    var form = event.target;
    if (!form.matches('form[action$="/cart/add"], form[data-type="add-to-cart-form"]')) return;

    event.preventDefault();

    var button = form.querySelector('[type="submit"], [name="add"]');
    if (button) button.setAttribute('aria-busy', 'true');

    var data = new FormData(form);
    data.append('sections', SECTION);

    post('cart/add.js', data, true)
      .then(function (result) {
        applyCart(result);
        // Se o painel não existir (carrinho em página), confirmar com um toast.
        if (!openDrawer(button)) {
          toast(strings().addedToCart || 'Adicionado ao carrinho', 'positivo');
        }
      })
      .catch(function (err) {
        var message = (err && (err.description || err.message)) || strings().cartError;
        if (message) {
          toast(message, 'negativo');
        } else {
          form.submit();
        }
      })
      .finally(function () {
        if (button) button.removeAttribute('aria-busy');
      });
  }

  /* --------------------------------------------------------
     2. Quantidade e remover (dentro do painel)
     -------------------------------------------------------- */

  function onClick(event) {
    var toggle = event.target.closest('[data-cart-toggle]');
    if (toggle && drawer()) {
      event.preventDefault();
      openDrawer(toggle);
      return;
    }

    if (event.target.closest('[data-cart-close]')) {
      event.preventDefault();
      if (window.VDN && window.VDN.overlay) window.VDN.overlay.close();
      return;
    }

    var change = event.target.closest('[data-qty-change]');
    if (!change) return;

    var item = change.closest('[data-cart-item]');
    if (!item) return;

    event.preventDefault();
    busy(true);

    post('cart/change.js', {
      line: parseInt(item.getAttribute('data-line'), 10),
      quantity: parseInt(change.getAttribute('data-qty-change'), 10),
      sections: SECTION
    })
      .then(applyCart)
      .catch(function () {
        // Cair para a navegação normal: o href do link faz a mesma alteração.
        window.location.href = change.getAttribute('href');
      })
      .finally(function () { busy(false); });
  }

  /* --------------------------------------------------------
     3. Nota da encomenda
     -------------------------------------------------------- */

  var noteTimer = null;

  function onInput(event) {
    var note = event.target.closest('[data-cart-note]');
    if (!note) return;

    window.clearTimeout(noteTimer);
    noteTimer = window.setTimeout(function () {
      post('cart/update.js', { note: note.value }).catch(function () {});
    }, 600);
  }

  /* --------------------------------------------------------
     Arranque
     -------------------------------------------------------- */

  document.addEventListener('submit', onSubmit);
  document.addEventListener('click', onClick);
  document.addEventListener('input', onInput);
})();
