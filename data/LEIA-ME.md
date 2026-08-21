# Dados de arranque da loja

Material de apoio para pôr a loja com conteúdo real. **Nada nesta pasta é
enviado para o Shopify** — está excluída em `.shopifyignore`.

## `imagens/`

As fotos que já existiam, desduplicadas (eram 21 ficheiros para 15 imagens
únicas) e renomeadas com nomes semânticos.

| Ficheiro | O que é |
|---|---|
| `bola-futevolei-vdn-marca.jpg` | **A melhor foto do catálogo.** A bola com a marca Ventos do Norte impressa — usar como imagem principal do lançamento e no hero da home. |
| `bola-futevolei-ultratermo.jpg` · `-approved.jpg` · `-frente.jpg` · `-lisa.jpg` | Outros ângulos do mesmo mockup 3D. |
| `peteca-altiva-branca.jpg` · `-tricolor.jpg` · `-neon.jpg` | Petecas Altiva Sport, fundo amarelo. |
| `pipa-estrelas-rosa-recorte.jpg` | Pipa já recortada em fundo branco — a única pronta para catálogo. |
| `pipa-estrelas-rosa-loja.jpg` · `pipa-caveira-neon.jpg` | Fotos na loja, com fundo. |
| `pipa-personagem-*.jpg` | Pipas com estampas de personagens — **ver o aviso no fim.** |
| `video-bola-futevolei.mp4` · `video-loja-pipas.mp4` | Vídeos para o hero ou para redes sociais. |

> As fotos tiradas na loja têm fundo cheio (prateleiras, carretéis, etiquetas de
> preço). Para o catálogo, valem recortes com fundo transparente — como o
> `pipa-estrelas-rosa-recorte.jpg` já tem. Os mockups da bola trazem a legenda
> "imagem meramente ilustrativa" queimada: convém recortar essa faixa antes de
> publicar, ou substituir por fotos da bola real quando ela chegar.

## `produtos-ventos-do-norte.csv`

9 produtos, 19 variantes, com descrições em português europeu, preços em euros,
pesos, SKUs de stock e metadados de SEO preenchidos.

### Como importar

1. **Admin → Content → Files** e carrega as imagens de `imagens/`.
2. Copia o URL público de cada uma (botão de copiar link).
3. No CSV, substitui `COLOCAR_URL_DO_ADMIN/` pelo início desses URLs — o
   importador do Shopify precisa de URLs acessíveis, não aceita caminhos locais.
4. **Admin → Products → Import** e envia o CSV.
5. Cria as coleções (Pipas, Linhas, Petecas, Futevôlei, Rabiolas e acessórios) e
   liga-as aos blocos da secção "Categorias em diagonal" no editor de tema.

Em alternativa, importa o CSV sem imagens e carrega-as à mão em cada produto —
para 9 produtos é rápido e evita o passo dos URLs.

### Preços

São estimativas de mercado para posicionar a loja e ver a montra com números
credíveis. **Rever todos antes de abrir ao público.**

---

## ⚠️ Aviso sobre as pipas de personagens

Quatro das fotos mostram pipas com personagens protegidos por direitos de autor
(estúdios de cinema e animação). Vender artigos com estas estampas na União
Europeia sem licença expõe a loja a queixas por violação de propriedade
intelectual, e as plataformas de pagamento e publicidade costumam suspender
contas nestes casos.

No CSV, esses artigos foram reunidos num único produto neutro —
**"Pipa Ilustrada — sortida"** — sem nomear nenhuma personagem, o que reduz a
exposição em pesquisas mas **não resolve a questão de fundo**. Vale a pena
confirmar com o fornecedor se as estampas são licenciadas; se não forem, o mais
seguro é vender apenas os desenhos genéricos (estrelas, caveiras, geométricos),
que são a maioria do stock.

---

# `produto/` — fotos prontas para o catálogo

Recortadas com a Vision framework do macOS (o mesmo motor do "Remover fundo" da
Pré-visualização), compostas sobre branco puro e enquadradas em 2000×2000 com
8% de margem. A margem e o tamanho são iguais em todas de propósito: é isso que
faz a grelha do catálogo parecer alinhada em vez de cada produto flutuar num
sítio diferente do card.

O utilitário está em `/private/tmp/.../bgtool/` (temporário). Se for preciso
repetir, o código está no histórico desta conversa — são ~80 linhas de Swift.

## Prontas a usar (10)

| Ficheiro | Nota |
|---|---|
| `bola-futevolei-vdn-marca.jpg` | **A melhor do lote.** Bola com a marca impressa. Imagem principal do lançamento. |
| `bola-futevolei-ultratermo.jpg` · `-approved.jpg` · `-frente.jpg` · `-lisa.jpg` | Outros ângulos. A legenda "imagem meramente ilustrativa" foi removida no recorte. |
| `peteca-altiva-branca.jpg` · `-tricolor.jpg` · `-neon.jpg` | Recorte limpo, penas incluídas. |
| `pipa-estrelas-rosa-recorte.jpg` | A única pipa que já vinha em fundo limpo. |
| `pipa-personagem-heroi.jpg` | Recorte perfeito — estava pendurada, não pousada. |

## Em `produto/_rever/` (5) — precisam de refotografia

Nestas, a pipa está **pousada sobre o carretel de madeira**, sobreposta a ele.
Nenhum recorte automático os separa: para o segmentador são um só objeto. Testei
a Vision do macOS e o removedor do Higgsfield — os dois trazem o carretel junto.

Não é limitação da ferramenta, é da fotografia. A solução é rápida:

> Pendura a pipa contra uma parede lisa e clara (ou um lençol branco), com luz
> de dia por uma janela lateral, e fotografa de frente. Foi assim que a
> `pipa-personagem-heroi` saiu perfeita — e essa foi tirada na mesma loja.

Depois é só voltar a passar pelo recorte.
