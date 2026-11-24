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

O utilitário de recorte estava em `/private/tmp/.../bgtool/` (temporário) e
perdeu-se com a pasta. O enquadramento — fundo a branco puro, 2000×2000, 8 % de
margem — ficou em [`enquadrar.py`](enquadrar.py), que já vive no repositório:

```bash
python3 -m pip install pillow          # uma vez
python3 data/enquadrar.py origem.png data/produto/destino.jpg
```

Não recorta fundos: parte de uma foto que já tem fundo claro e limpo.

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

---

# Fotos geradas por IA — Novembro de 2026

Oito fotos de `produto/` não são fotografias: foram geradas por IA (Dreamina,
modelo GPT Image 2.5) a partir de fotos tiradas na loja e de capturas de ecrã,
e depois passadas pelo `enquadrar.py`.

| Ficheiro | Produto | Feita a partir de |
|---|---|---|
| `carretel-madeira-catrina.jpg` · `-chamas.jpg` · `-tamanhos.jpg` | Carretel de Madeira Estampado | foto da bancada com os carretéis |
| `pipa-cruz-rosa.jpg` | Pipa Cruz Rosa | fotograma de vídeo, pipa dentro do saco |
| `pipa-mosaico-tricolor.jpg` | Pipa Mosaico Tricolor | foto do pacote na loja |
| `linha-10-vera-cruz-cores.jpg` | Linha 10 Vera Cruz | foto dos cones na loja |
| `vareta-fibra-feixe.jpg` · `-detalhe.jpg` | Vareta de Fibra de Vidro | captura de um anúncio de outra loja |

**O que isto quer dizer na prática**

- Mostram o produto certo, com o desenho e as cores certas, mas não são a peça
  que o cliente recebe. As descrições dizem «a fotografia é ilustrativa» onde
  isso importa (pipas coladas à mão, estampa sortida do carretel). Não tirar
  essa frase enquanto as fotos forem estas.
- **A da Linha 10 Vera Cruz é a mais frágil.** O rótulo foi reconstruído a
  partir de uma foto de 309 px: o «10», o nome e «2012 metros» estão lá, o
  resto do desenho é aproximado. É a primeira a trocar por uma fotografia a
  sério — é o rótulo de uma marca que não é nossa.
- A das varetas foi refeita com outro enquadramento de propósito, para não
  ser uma cópia da fotografia do anúncio de onde partiu.
- Trocar qualquer uma por uma fotografia real é sempre melhor. O conselho de
  cima continua a valer: parede lisa, luz de janela, de frente.

**O que ficou de fora, e porquê**

Na foto dos carretéis, a maior parte tem personagens de cinema, banda desenhada
e videojogos, e no vídeo das pipas há uma com o símbolo de um super-herói. Não
gerei fotos dessas: é o mesmo problema das pipas de personagens descrito acima,
e uma foto de catálogo com a personagem em grande é o que mais expõe a loja. As
fotos mostram só as estampas sem personagens (a catrina e o padrão de chamas).
Se o lote que há para vender for sobretudo de personagens, a descrição
«estampa sortida» não resolve a questão de fundo — confirma o licenciamento
com o fornecedor antes de pôr o carretel activo.
