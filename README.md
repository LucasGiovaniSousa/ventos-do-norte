# Ventos do Norte — loja online

Tema Shopify (Online Store 2.0) da **Ventos do Norte**: pipas, linhas, rabiolas,
petecas, bolas de futevôlei e acessórios. Do Brasil para Portugal.

**Stack:** Shopify · Liquid · Online Store 2.0 · CSS · JavaScript sem
dependências · pt-PT + EN

---

## Arrancar

```bash
shopify theme dev  --store SUA-LOJA.myshopify.com   # preview ao vivo
shopify theme check                                  # lint (tem de dar 0 offenses)
shopify theme push --store SUA-LOJA.myshopify.com --unpublished
```

Primeira instalação: ver [`data/LEIA-ME.md`](data/LEIA-ME.md) para importar os
produtos e as imagens.

---

## Linguagem visual

O conceito é **o vento como elemento gráfico**: a pipa corta o céu na diagonal, e
o layout herda esse gesto — cortes diagonais, linhas de vento em SVG, tipografia
itálica-expandida.

A página alterna **momentos de marca em preto** (hero, faixas, lançamento,
rodapé) com **áreas de compra em fundo areia** (grelhas, coleção, ficha de
produto). O preto vende a marca; o claro vende o produto.

### Cores

| Token | Valor | Uso |
|---|---|---|
| `--vdn-ink` | `#0a0a0b` | Fundo escuro |
| `--vdn-sand` | `#faf8f3` | Fundo claro |
| `--vdn-verde` | `#00a544` | Brasil — ação primária (comprar) |
| `--vdn-amarelo` | `#ffc800` | Brasil — destaques e etiquetas |
| `--vdn-azul` | `#1b4fd8` | UE / "NORTE" — links e foco |
| `--vdn-vermelho` | `#e63329` | Portugal — promoções |

Regra de contraste: `--vdn-azul` só sobre fundo claro; sobre escuro usar
`--vdn-azul-lit`. O amarelo nunca como texto sobre claro — só como fundo.

### Tipografia

**Archivo** variable, auto-hospedada em `assets/` (eixo de largura 62–125% e
itálico real). É a mesma família para display e corpo: o itálico expandido a 125%
reproduz o wordmark do logótipo; a 100% normal serve de texto corrido.

Auto-hospedada de propósito — usar o CDN do Google Fonts numa loja da UE levanta
problemas de RGPD.

---

## Arquitetura

```
layout/theme.liquid    moldura HTML · SEO · scripts · scrim global
templates/*.json       que secções aparecem em cada página
sections/              blocos configuráveis no editor de tema
snippets/              pedaços reutilizáveis
assets/                CSS, JS e as fontes
locales/               pt-PT (padrão) + EN
data/                  fotos e CSV de arranque — NÃO vai para a loja
```

### Onde vive o CSS

| Camada | Onde | Porquê |
|---|---|---|
| Tokens + `@font-face` | `snippets/css-variables.liquid` (inline no `<head>`) | Evita a cascata `<link>` → fonte; as fontes começam a descarregar no primeiro parse |
| Componentes globais | `assets/base.css` | Botões, campos, cards, preços, grelha, movimento |
| Específico de uma secção | `<style>` dentro do ficheiro da secção | Cada secção é autocontida; o editor pode removê-la sem deixar CSS órfão |

### Sistema de tema por secção

Cada secção declara `.vdn-section--dark` ou `.vdn-section--light`. Isso redefine
`--sec-bg`, `--sec-fg`, `--sec-line`, `--sec-accent`… que todos os componentes lá
dentro consomem. Um botão ou um card herdam o contraste certo automaticamente —
não há variantes "no escuro" espalhadas pelo CSS.

### JavaScript

Três ficheiros pequenos, sem dependências, todos carregados com `defer`:

| Ficheiro | Responsabilidade |
|---|---|
| `overlay.js` | **Dono único** de tudo o que abre por cima: menu mobile, pesquisa, carrinho e filtros. Trata do scrim, do bloqueio de scroll, do Escape e da prisão de foco. Existe para os painéis não disputarem o mesmo scrim. |
| `motion.js` | Reveal por `IntersectionObserver`, parallax e o estado de scroll do cabeçalho. Desliga-se por completo com `prefers-reduced-motion`. |
| `carrinho.js` | Carrinho AJAX. Cada pedido inclui `sections: 'cart-drawer'`, por isso o Shopify devolve o painel já atualizado na mesma resposta — um pedido em vez de dois. |

**Tudo funciona sem JavaScript.** Formulários nativos em todo o lado: o produto
submete para `/cart/add`, os filtros e a ordenação são `GET`, os botões de
quantidade do carrinho são links para `/cart/change`. O JS só torna a experiência
mais rápida.

---

## Secções

### Página inicial
| Secção | O que é |
|---|---|
| `hero-pipa` | Hero escuro: linhas de vento animadas, produto com parallax, slogan |
| `faixa-marca` | Faixa deslizante infinita com o slogan e as bandeiras |
| `categorias-diagonais` | Categorias em cartões com corte diagonal; o primeiro é destaque 2×2 |
| `featured-collection` | Grelha de produtos de uma coleção (claro ou escuro) |
| `produto-lancamento` | Montra escura de um produto, com compra direta |
| `pilares` | Promessas de serviço (envios, devoluções, pagamento) |
| `rich-text` | Texto livre |

### Loja
| Secção | O que é |
|---|---|
| `nav` | Cabeçalho sticky, mega-menu, pesquisa preditiva, menu mobile |
| `footer` | Os 5 pilares do logótipo, newsletter, bandeiras, políticas |
| `cart-drawer` | Painel do carrinho com barra de progresso de portes grátis |
| `collection-banner` + `main-collection` | Coleção com filtros em painel e chips removíveis |
| `main-product` | Ficha de produto: galeria em coluna, info sticky, amostras, acordeões |

---

## Definições do editor

Além das habituais (cores, tipografia, layout, cards, carrinho), há um grupo
**"Marca — Ventos do Norte"**:

- **Slogan** — usado no rodapé e no menu mobile
- **Texto da faixa deslizante** — itens separados por `·`
- **Portes grátis a partir de (€)** — alimenta a barra de progresso do carrinho
- **Número de WhatsApp**

---

## Acessibilidade

- Painéis prendem o foco, fecham com Escape e devolvem o foco ao botão de origem
- Amostras de variante são `<fieldset>` + radios reais (navegáveis com as setas)
- Alvos de toque de 44 px (WCAG 2.5.5)
- Contraste AA verificado nos pares claro e escuro
- `prefers-reduced-motion` desliga parallax, marquee e reveals numa regra global

---

## Antes de abrir ao público

- [ ] Rever os preços do CSV (são estimativas)
- [ ] Confirmar o licenciamento das pipas de personagens — ver `data/LEIA-ME.md`
- [ ] Carregar o logótipo em PNG transparente e o favicon
- [ ] Criar as coleções e ligá-las aos blocos de categorias
- [ ] Preencher as políticas da loja (privacidade, devoluções, envios)
- [ ] `shopify theme check` a dar 0 offenses e um `push --unpublished` de teste
