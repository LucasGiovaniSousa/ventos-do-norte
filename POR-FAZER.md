# Por fazer — Ventos do Norte

Ordem de trabalho do `_PADRAO-LOJA`, adaptada a esta loja.
**A ordem não é sugestão:** os passos 1 e 2 têm de vir antes de existir
qualquer produto, senão ficam a arrastar dados errados.

Loja: `bn3vcf-f1.myshopify.com` · Tema publicado: **Ventos do Norte v1** (#189375807873)

---

## 1. Nome da loja — ANTES de criar produtos

**Definições → Detalhes da loja → Nome da loja** → `Ventos do Norte`

A Shopify copia o nome da loja para o campo **Fornecedor** de cada produto
criado nesse momento. Se os produtos entrarem com a loja ainda chamada
"A minha loja", essa frase passa a aparecer em cima de cada produto no site —
e mudar o nome depois **não corrige os produtos já criados**.

No CSV o Fornecedor já vai escrito à mão (`Ventos do Norte`, `Altiva`), por isso
este passo protege sobretudo o que fores criar a seguir.

## 2. Idioma — o passo que desbloqueia todo o resto

**Definições → Idiomas** → adicionar **Português (Portugal)** → *Publicar* →
**Definir como predefinido**.

> Sem isto o site continua em inglês. Não é texto por traduzir: é a loja a
> correr no idioma errado. O tema tem `pt-PT.default.json` **e** `en.json`; com
> o inglês como predefinido da loja, a Shopify escolhe o inglês por
> correspondência exacta. O sufixo `.default` marca o predefinido **do tema** —
> quem escolhe é a loja, e isso só se muda aqui.

## 3. Moeda, país e IVA

- **Mercados** → mercado principal **Portugal**, moeda **EUR**
- **Impostos e taxas → Portugal** → IVA **23 %**
- Ligar **«Todos os preços incluem impostos»**

Os preços do CSV já estão com IVA incluído. O tema escreve «IVA incluído» por
baixo do preço a contar com isto.

## 4. Envio

Zona **Portugal continental**. Decidir e preencher a taxa fixa.

O tema tem `free_shipping_threshold = 50`: acima desse valor promete portes
grátis na barra do carrinho. **Se não vais oferecer portes, põe 0** — a 0 a
promessa desaparece do site inteiro, sem ser preciso apagar texto.

## 5. Pagamentos

MB WAY · Multibanco · Cartão. O tema anuncia estes três nos selos de confiança
da ficha de produto — se activares outros, muda lá o texto, senão o site promete
um método que o checkout não tem.

> **Multibanco muda o fluxo de stock:** a encomenda fica pendente até a
> referência ser paga. O stock só deve sair depois da confirmação.

## 6. Coleções — 7 categorias, criadas ANTES de importar

**Produtos → Coleções → Criar → automáticas por etiqueta.**
Vale o trabalho: produto novo com a etiqueta certa entra sozinho na categoria.

| Nome | Handle | Condição (etiqueta é igual a) |
|---|---|---|
| Pipas | `pipas` | `Pipas` |
| Linhas | `linhas` | `Linhas` |
| Carretéis | `carreteis` | `Carretéis` |
| Rabiolas | `rabiolas` | `Rabiolas` |
| Petecas | `petecas` | `Petecas` |
| Futevôlei | `futevolei` | `Futevôlei` |
| Kits | `kits` | `Kits` |

Sete categorias fecham duas linhas de quatro na grelha da home, com o mosaico
«Ver todos». Com seis ou oito fica uma linha coxa.

## 7. Metacampos

**Definições → Metacampos personalizados → Produtos.** O espaço de nomes é
sempre `custom` e a chave tem de ser exactamente esta:

| Nome | Chave | Tipo |
|---|---|---|
| Linha técnica | `custom.linha_tecnica` | Texto de linha única |
| Componentes do kit | `custom.componentes` | **Lista** de texto de linha única |
| Para quem é | `custom.para` | Texto de linha única |

O `componentes` tem de ser **lista**, não texto — como texto simples o kit
mostra tudo numa linha só. O CSV já traz as três colunas preenchidas.

## 8. Imagens

**Conteúdo → Ficheiros** → carregar as 14 de `data/produto/`.

Depois copia o prefixo do URL público e substitui `SUBSTITUIR_PELO_URL_DO_ADMIN/`
no CSV. Ou — para 10 produtos é honestamente mais rápido — importa sem imagens e
arrasta-as em cada produto.

## 9. Produtos — duas vias

O texto dos produtos vive em `data/catalogo.py`, fonte única. Daí saem as duas
vias abaixo, para nunca divergirem: se mudares uma descrição, muda nas duas.

### Via A — Admin API (publico eu)

**Criar a app**

1. **Definições → Aplicações e canais de vendas → Desenvolver aplicações**
2. **Criar uma app** → nome: `Catálogo Ventos do Norte`
3. **Configurar âmbitos da Admin API** → marcar **apenas**:
   - `read_products`
   - `write_products`

   Nunca `read_orders`, `write_orders`, `read_customers`, `write_customers`.
   Construir um catálogo não precisa deles, e o que não é preciso não se pede.
4. **Guardar** → **Instalar app**
5. **Revelar token do Admin API uma vez** → copiar (começa por `shpat_`)

> O token só se mostra **uma vez**. Se o perderes, revoga e gera outro.

**Usar o token**

**Não o coles no chat nem em ficheiro nenhum do projecto.** Escreve-o só no
terminal, na sessão onde vais correr o script:

```bash
export SHOPIFY_ADMIN_TOKEN='shpat_...'

python3 data/publicar.py              # simulação — não escreve nada
python3 data/publicar.py --publicar   # escreve mesmo
```

O script cria os 10 produtos com descrições, preços, SKU, peso, stock,
etiquetas, SEO e metacampos, **todos em rascunho**. Se um handle já existir,
actualiza em vez de duplicar — dá para correr outra vez depois de mudar texto.

Fecha o terminal quando acabares: a variável desaparece com ele.

**Quando o trabalho terminar, revoga a app.** Um token vivo que ninguém usa é
só superfície de ataque à espera.

### Via B — CSV

**Produtos → Importar** → `data/produtos-ventos-do-norte.csv`

Gerado por `python3 data/gerar-csv.py`. Mesma informação da via A.

10 produtos, 20 variantes, todos com `Status = draft`. Rever preço, stock,
imagem e categoria **antes** de passar a activo.

> **Os preços são estimativas de mercado**, não saíram de custo de fornecedor.
> O padrão manda verificar cada PVP contra a concorrência, um a um, antes de
> publicar — é o passo que se salta e é o que custa dinheiro. Quando tiveres os
> custos de tabela, `_PADRAO-LOJA/scripts/precos.py` calcula com margem-alvo.

## 10. Ligar as categorias aos mosaicos da home

**Personalizar → Categorias em diagonal →** cada bloco → campo **Coleção**.
Sem essa ligação os mosaicos apontam ao vazio.

## 11. Políticas legais

Ver `_PADRAO-LOJA/06-LEGAL-PT.md`. Mínimo: Termos (com NIF e morada),
Privacidade, Cookies com banner, Envios, Devoluções (**14 dias** de livre
resolução) e Contactos. Mais o **Livro de Reclamações** no rodapé.

## 12. Publicar

Só com confirmação explícita. `./deploy.sh ao-vivo`.

---

## Lista de verificação antes de abrir ao público

- [ ] Nome da loja definitivo; campo Fornecedor correcto em todos os produtos
- [ ] Português (Portugal) publicado **e predefinido**
- [ ] Moeda EUR, IVA 23 %, preços com imposto incluído
- [ ] Zona de envio e taxa configuradas; `free_shipping_threshold` coerente
- [ ] Métodos de pagamento activos = os que o site anuncia
- [ ] As 7 coleções criadas e ligadas aos mosaicos
- [ ] Metacampos criados (`componentes` como **lista**)
- [ ] Preços revistos contra a concorrência, um a um
- [ ] Licenciamento das estampas confirmado com o fornecedor — ver `data/LEIA-ME.md`
- [ ] Políticas legais escritas e ligadas no rodapé
- [ ] Produtos passados de rascunho a activo
- [ ] Palavra-passe da loja retirada

---

## O que ainda falta no tema, face ao padrão

Adaptado até agora: estrutura de pastas, `.shopifyignore`, `deploy.sh` de duas
passagens, `verificar.py`, disciplina de CSV, sete categorias, metacampos,
padrão de imagem 2000×2000 com 8 % de margem.

Por adaptar — **decisões de identidade, não cópia**: o padrão da Braga Car
Studio usa azul de acção e Saira Condensed; a Ventos do Norte tem as cores das
três bandeiras e a Archivo, e isso mantém-se.

- [ ] Secção **faixa-topo** com duas mensagens rotativas
- [ ] Secção **garantias** (4 blocos) — hoje as promessas estão só no fim da home
- [ ] Secção **kits** com poupança calculada a partir do preço de comparação
- [ ] Ficha técnica na página de produto a ler os metacampos
- [ ] Aviso «últimas N unidades» no cartão (`stock_low_threshold`)
- [ ] Botão flutuante de **WhatsApp**
- [ ] Definições de morada/telefone/horário → JSON-LD de loja local
- [ ] Levantamento em loja — só se houver morada física
