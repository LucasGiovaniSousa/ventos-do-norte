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

   Construir um catálogo não precisa de mais nada, e o que não é preciso não
   se pede: cada âmbito a mais é superfície de ataque num token que fica no
   disco.

   Para o dia-a-dia da loja pelo `data/loja.py` há mais três pares que se
   acrescentam **quando forem precisos**, não antes:

   - `read_inventory` + `write_inventory` + `read_locations` — mexer em stock
   - `read_content` + `write_content` — páginas e menus
   - `read_themes` — listar temas

   `read_orders` e `read_customers` ficam de fora por omissão: trazem dados
   pessoais de clientes para um token que vive num ficheiro. Só se acrescentam
   com uma razão concreta, e revogam-se quando ela passar.
4. **Guardar** → **Instalar app**
5. **Revelar token do Admin API uma vez** → copiar (começa por `shpat_`)

> O token só se mostra **uma vez**. Se o perderes, revoga e gera outro.

**Usar o token**

Escreve-o num ficheiro na raiz do projecto. O `.gitignore` cobre-o, por isso
nunca entra no repositório:

```bash
printf '%s' 'shpat_cola-aqui' > .admin-api.token
```

`printf` e não `echo` de propósito: o `echo` acrescenta uma quebra de linha ao
fim, e há endpoints que a incluem no cabeçalho de autenticação e devolvem 401
sem explicar porquê.

Depois:

```bash
python3 data/publicar.py              # simulação — não escreve nada
python3 data/publicar.py --publicar   # escreve mesmo
```

(O `publicar.py` faz o carregamento inicial do catálogo. Para mudanças avulsas
depois disso — um preço, um stock, pôr um produto à venda — é o `data/loja.py`;
ver README, «Mexer na loja daqui».)

O script cria os produtos do catálogo com descrições, preços, SKU, peso,
etiquetas, SEO, metacampos e **imagens** (de `data/produto/`), **todos em
rascunho**. Se um handle já existir, actualiza em vez de duplicar — dá para
correr outra vez depois de mudar texto.

Três protecções, porque a loja já está aberta:

- **Um produto à venda (ACTIVE) é saltado.** O catálogo pode estar atrás da
  loja — em Novembro de 2026 a peteca estava a 7,90 € na loja e a 9,90 € no
  `catalogo.py`, a bola a 28,90 € e a 24,90 €. Sem isto, correr o script
  repunha os preços antigos. `--forcar` escreve por cima, depois de acertares
  o catálogo.
- **O estado de um produto que já existe não é tocado.** Só o que é novo
  entra em rascunho.
- **As imagens só entram em produtos que não têm nenhuma.**

Para publicar só alguns:

```bash
python3 data/publicar.py --apenas pipa-cruz-rosa,pipa-mosaico-tricolor
python3 data/publicar.py --apenas pipa-cruz-rosa,pipa-mosaico-tricolor --publicar
```

O stock não é escrito por aqui: fica a zero e põe-se com o `loja.py`.

Porquê ficheiro e não `export`: cada comando de shell abre um processo novo,
e uma variável exportada numa janela não é vista noutra. Com o ficheiro, o
token chega ao disco uma vez e qualquer comando o encontra — incluindo os que
eu corro. Também evita passá-lo como argumento, que ficaria visível no `ps` a
qualquer processo da máquina.

**Quando o trabalho acabar:**

```bash
rm .admin-api.token
```

E revoga a app no admin.

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
- [x] Botão flutuante de **WhatsApp** — feito. Só aparece quando o número
      estiver em Definições do tema → Marca → Número de WhatsApp
- [ ] Definições de morada/telefone/horário → JSON-LD de loja local
- [ ] Levantamento em loja — só se houver morada física

---

## Produtos de Novembro de 2026 — o que falta para estarem à venda

Estão no `catalogo.py`, com fotos em `data/produto/`, e **ainda não estão na
loja**: no dia em que foram preparados não havia token da Admin API no disco.

| Handle | Preço posto | O que confirmar |
|---|---|---|
| `pipa-mosaico-tricolor` | 5,90 € | preço · tamanho (não está na ficha) · vende-se à unidade ou em pacote? |
| `pipa-cruz-rosa` | 5,90 € | o mesmo |
| `linha-10-vera-cruz` | 9,90 € | preço · as 7 cores existem todas em stock? · «Tex 85» e «2012 m» lidos do rótulo |
| `vareta-fibra-vidro-66cm` | 34,90 € | preço · «cerca de 300 varetas» é conta feita pelo peso, não contagem |
| `carretel-madeira` | 14,90 / 19,90 € | já existia; ganhou fotos. Tamanhos 18 e 24 cm nunca foram medidos |

**Os preços são estimativas**, como os do resto do catálogo. Nenhum saiu de
custo de fornecedor.

Por ordem:

- [ ] Rever preços e os dados da tabela no `catalogo.py`
- [ ] Token em `.admin-api.token` (§9) e publicar em rascunho:
      `python3 data/publicar.py --apenas pipa-mosaico-tricolor,pipa-cruz-rosa,linha-10-vera-cruz,vareta-fibra-vidro-66cm,carretel-madeira --publicar`
- [ ] Ver cada um no admin — fotos, variantes, texto
- [ ] Stock real, SKU a SKU: `python3 data/loja.py stock <sku> <n> --escrever`
- [ ] Passar a activo: `python3 data/loja.py estado <handle> ACTIVE --escrever`
- [ ] Enviar o tema (`./deploy.sh ao-vivo`) — traz a secção **chegadas** e as
      amostras de cor novas. Pode ir antes ou depois: a secção só anuncia
      «As pipas chegaram» quando houver um produto destes activo e com stock;
      até lá mostra o texto de sempre, «estão a caminho»
- [ ] Coleção «Varetas» (§6), se quiseres a categoria no menu — hoje são sete
- [ ] O hero e a faixa ainda só falam de peteca e futevôlei: rever o texto
      quando as pipas estiverem mesmo à venda

**A home já os mostra — secção `ceu` (24 Nov).** No lugar da grelha `chegadas`
ficou uma secção desenhada para estes cinco: as duas pipas a voar, com linha e
rabiola, e por baixo a linha, o carretel e a vareta. Cada bloco lê o seu
produto: enquanto for rascunho ou não tiver stock mostra «A chegar», sem preço
e sem ligação; no momento em que passar a activo, publicado e com stock, ganha
preço e ligação sozinho, e a sobrelinha passa de «A chegar» a «Acabadas de
chegar». Não há nada para trocar à mão na home no dia do lançamento.

As fotos da secção viajam no tema (`assets/ceu-*.jpg`), porque um rascunho não
se lê do tema. A `chegadas.liquid` continua no tema, disponível no editor, mas
já não está na home — as duas fariam o mesmo trabalho.

Os produtos já estão criados na loja, em rascunho (importados por CSV a 24 Nov
— `data/importar-novembro.csv` — com as fotos carregadas à mão). O passo do
token e do `publicar.py` na lista acima deixou de ser preciso para estes cinco.
Faltam: stock, canal de vendas «Loja virtual», e passar a activo.

**`./deploy.sh` não corre neste momento.** O `shopify` do Homebrew falha ao
arrancar (`libsimdjson.33.dylib` em falta — o Node do Homebrew ficou partido
depois de uma actualização). `brew reinstall node` deve resolver. O tema foi
verificado na mesma, com `verificar.py` e com a biblioteca do theme check
corrida à parte: 0 problemas.
