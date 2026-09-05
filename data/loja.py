#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""loja.py — consola da loja: ler e mudar o que está na Shopify, daqui.

PARA QUE SERVE
O `deploy.sh` trata do TEMA (o código: liquid, css, js). Este script trata da
LOJA (os dados: produtos, preços, stock, colecções, páginas, menus, encomendas).
São coisas diferentes e vivem em sítios diferentes — mudar o preço de uma pipa
não é mudar código, e enviar o tema não mexe num único preço.

O `publicar.py` faz uma coisa só: despeja o catalogo.py na loja. Este faz o
resto, a pedido, uma operação de cada vez.

O TOKEN
Lido de .admin-api.token (raiz do projecto, ignorado pelo git) ou de
SHOPIFY_ADMIN_TOKEN. Nunca passado por argumento: argumentos ficam no histórico
da shell e são visíveis no `ps` a qualquer processo da máquina.

NADA ESCREVE SEM `--escrever`
Todos os comandos que mudam alguma coisa correm em simulação por omissão e
dizem o que fariam. Só com `--escrever` é que tocam na loja. A leitura não
precisa de nada.

USO
  python3 data/loja.py info                       loja, moeda, plano, âmbitos
  python3 data/loja.py produtos [termo]           lista (com preço, sku, stock)
  python3 data/loja.py produto <handle>           ficha completa
  python3 data/loja.py preco <sku> <valor> [--comparar <valor>]
  python3 data/loja.py stock <sku> <quantidade>
  python3 data/loja.py estado <handle> <ACTIVE|DRAFT|ARCHIVED>
  python3 data/loja.py descricao <handle> <ficheiro.html>
  python3 data/loja.py colecoes | paginas | menus | locais | temas
  python3 data/loja.py encomendas [quantas]
  python3 data/loja.py gql <ficheiro|-> [variaveis.json]    ← escotilha

A escotilha `gql` é o que torna isto completo: aceita qualquer query ou mutação
da Admin API. Os comandos com nome acima são só atalhos para o que se faz todos
os dias. O que não tiver atalho, faz-se por ali.
"""
import json, os, sys, time, urllib.request, urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOJA = os.environ.get("SHOPIFY_STORE", "bn3vcf-f1.myshopify.com")
VERSAO = os.environ.get("SHOPIFY_API_VERSION", "2026-01")
URL = "https://%s/admin/api/%s/graphql.json" % (LOJA, VERSAO)

FICHEIRO_TOKEN = os.path.join(RAIZ, ".admin-api.token")
TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
if not TOKEN and os.path.exists(FICHEIRO_TOKEN):
    TOKEN = open(FICHEIRO_TOKEN, encoding="utf-8").read().strip()

ARGS = sys.argv[1:]
A_SERIO = "--escrever" in ARGS
CRU = "--json" in ARGS
ARGS = [a for a in ARGS if a not in ("--escrever", "--json")]


def opcao(nome, omissao=None):
    """Lê --nome valor e retira-o da lista de argumentos."""
    if nome in ARGS:
        i = ARGS.index(nome)
        valor = ARGS[i + 1] if i + 1 < len(ARGS) else omissao
        del ARGS[i:i + 2]
        return valor
    return omissao


SEM_TOKEN = """
  Falta o token da Admin API.

  Escreve-o num ficheiro na raiz do projecto (o git ignora-o):

    printf '%s' 'shpat_cola-aqui' > .admin-api.token

  `printf` e não `echo`: o echo acrescenta uma quebra de linha ao fim, e há
  endpoints que a incluem no cabeçalho e devolvem 401 sem explicar porquê.

  Como gerar: POR-FAZER.md §9.
"""


def pedir(query, variaveis=None):
    if not TOKEN:
        raise SystemExit(SEM_TOKEN)
    corpo = json.dumps({"query": query, "variables": variaveis or {}}).encode()
    pedido = urllib.request.Request(URL, data=corpo, method="POST", headers={
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": TOKEN,
    })
    try:
        with urllib.request.urlopen(pedido, timeout=60) as r:
            dados = json.loads(r.read())
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode()[:500]
        if e.code == 401:
            raise SystemExit("\n  Token recusado (401). Confirma que o copiaste inteiro.\n")
        if e.code == 403:
            raise SystemExit("\n  Sem permissão (403). Falta um âmbito à app.\n"
                             "  Vê `python3 data/loja.py info` para os que ela tem,\n"
                             "  e acrescenta o que falta em Definições → Aplicações →\n"
                             "  a app → Configurar âmbitos da Admin API.\n")
        if e.code == 429:
            raise SystemExit("\n  Demasiados pedidos (429). Espera um pouco e repete.\n")
        raise SystemExit("\n  HTTP %s: %s\n" % (e.code, detalhe))

    if "errors" in dados:
        # Um âmbito em falta chega aqui como erro GraphQL, não como 403.
        texto = json.dumps(dados["errors"], ensure_ascii=False)
        if "access denied" in texto.lower() or "scope" in texto.lower():
            raise SystemExit("\n  A app não tem âmbito para isto:\n  %s\n\n"
                             "  Acrescenta-o no admin e reinstala a app.\n" % texto[:400])
        raise SystemExit("\n  Erro GraphQL: %s\n" % texto[:800])

    custo = dados.get("extensions", {}).get("cost", {})
    if custo.get("throttleStatus", {}).get("currentlyAvailable", 999) < 200:
        time.sleep(2)

    verificar_erros(dados.get("data") or {})
    return dados.get("data") or {}


def verificar_erros(no):
    """Uma mutação da Shopify devolve HTTP 200 com a falha lá dentro.

    Se ninguém ler `userErrors`, um preço que não mudou parece ter mudado. Por
    isso procuramos o campo em toda a resposta, a qualquer profundidade.
    """
    if isinstance(no, dict):
        for chave, valor in no.items():
            if chave.endswith("serErrors") and valor:
                linhas = ["    %s: %s" % (".".join(e.get("field") or ["-"]), e.get("message"))
                          for e in valor]
                raise SystemExit("\n  A Shopify recusou:\n" + "\n".join(linhas) + "\n")
            verificar_erros(valor)
    elif isinstance(no, list):
        for item in no:
            verificar_erros(item)


def mostrar(dados):
    print(json.dumps(dados, ensure_ascii=False, indent=2))


def so_simulacao(descricao):
    """Devolve True se não devemos escrever — e explica como escrever."""
    if A_SERIO:
        return False
    print("\n  SIMULAÇÃO — nada foi escrito.")
    print("  Faria: %s" % descricao)
    print("\n  Para escrever mesmo, repete com --escrever\n")
    return True


# ── leitura ──────────────────────────────────────────────────────────────

def cmd_info():
    d = pedir("""{
      shop { name myshopifyDomain primaryDomain { url } currencyCode ianaTimezone
             plan { displayName } }
      currentAppInstallation { accessScopes { handle } }
    }""")
    loja, app = d["shop"], d.get("currentAppInstallation") or {}
    if CRU:
        return mostrar(d)
    print("\n  %s" % loja["name"])
    print("  %s   →  %s" % (loja["myshopifyDomain"], loja["primaryDomain"]["url"]))
    print("  Moeda: %s · Fuso: %s · Plano: %s"
          % (loja["currencyCode"], loja["ianaTimezone"], loja["plan"]["displayName"]))
    ambitos = sorted(a["handle"] for a in app.get("accessScopes") or [])
    print("\n  Âmbitos desta app (%d):" % len(ambitos))
    for a in ambitos:
        print("    · %s" % a)
    print("\n  O que não estiver nesta lista devolve 403. Acrescenta-se no admin.\n")


Q_PRODUTOS = """
query($q: String, $n: Int!) {
  products(first: $n, query: $q, sortKey: TITLE) {
    nodes {
      id handle title status totalInventory
      variants(first: 20) { nodes { sku title price compareAtPrice inventoryQuantity } }
    }
  }
}"""


def cmd_produtos():
    termo = ARGS[1] if len(ARGS) > 1 else None
    d = pedir(Q_PRODUTOS, {"q": termo, "n": 100})
    nos = d["products"]["nodes"]
    if CRU:
        return mostrar(nos)
    print()
    for p in nos:
        print("  %-9s %-28s %s" % (p["status"], p["handle"], p["title"]))
        for v in p["variants"]["nodes"]:
            comp = "  (antes %s)" % v["compareAtPrice"] if v["compareAtPrice"] else ""
            print("      %-18s %-22s %8s€%s   stock %s"
                  % (v["sku"] or "-", v["title"], v["price"], comp, v["inventoryQuantity"]))
    print("\n  %d produto(s).\n" % len(nos))


def cmd_produto():
    if len(ARGS) < 2:
        raise SystemExit("\n  Uso: loja.py produto <handle>\n")
    d = pedir("""
    query($h: String!) {
      products(first: 1, query: $h) {
        nodes {
          id handle title status vendor productType tags descriptionHtml
          seo { title description }
          onlineStoreUrl totalInventory
          options { name optionValues { name } }
          variants(first: 50) { nodes { id sku title price compareAtPrice inventoryQuantity
                                        inventoryItem { id } } }
          media(first: 20) { nodes { ... on MediaImage { image { url altText } } } }
          metafields(first: 20) { nodes { namespace key value } }
        }
      }
    }""", {"h": "handle:%s" % ARGS[1]})
    nos = d["products"]["nodes"]
    if not nos:
        raise SystemExit("\n  Não existe produto com o handle '%s'.\n" % ARGS[1])
    mostrar(nos[0])


def listagem(nome, query, campo):
    def cmd():
        d = pedir(query)
        mostrar(d[campo])
    cmd.__name__ = nome
    return cmd


cmd_colecoes = listagem("cmd_colecoes", """{
  collections(first: 50) { nodes { id handle title productsCount { count }
                                   sortOrder ruleSet { rules { column relation condition } } } }
}""", "collections")

cmd_paginas = listagem("cmd_paginas", """{
  pages(first: 50) { nodes { id handle title isPublished updatedAt } }
}""", "pages")

cmd_menus = listagem("cmd_menus", """{
  menus(first: 20) { nodes { id handle title
                             items { title url type items { title url type } } } }
}""", "menus")

cmd_locais = listagem("cmd_locais", """{
  locations(first: 20) { nodes { id name isActive address { city country } } }
}""", "locations")

cmd_temas = listagem("cmd_temas", """{
  themes(first: 25) { nodes { id name role updatedAt } }
}""", "themes")


def cmd_encomendas():
    quantas = int(ARGS[1]) if len(ARGS) > 1 else 20
    d = pedir("""
    query($n: Int!) {
      orders(first: $n, sortKey: CREATED_AT, reverse: true) {
        nodes { name createdAt displayFinancialStatus displayFulfillmentStatus
                currentTotalPriceSet { shopMoney { amount currencyCode } }
                lineItems(first: 20) { nodes { title quantity sku } } }
      }
    }""", {"n": quantas})
    mostrar(d["orders"]["nodes"])


# ── escrita ──────────────────────────────────────────────────────────────

def variante_por_sku(sku):
    d = pedir("""
    query($q: String!) {
      productVariants(first: 2, query: $q) {
        nodes { id sku title price inventoryQuantity
                inventoryItem { id } product { id title } }
      }
    }""", {"q": "sku:%s" % sku})
    nos = d["productVariants"]["nodes"]
    if not nos:
        raise SystemExit("\n  Não existe variante com o SKU '%s'.\n" % sku)
    if len(nos) > 1:
        raise SystemExit("\n  Há %d variantes com o SKU '%s'. Corrige o duplicado\n"
                         "  no admin antes de mudar preço ou stock por SKU.\n" % (len(nos), sku))
    return nos[0]


def cmd_preco():
    comparar = opcao("--comparar")
    if len(ARGS) < 3:
        raise SystemExit("\n  Uso: loja.py preco <sku> <valor> [--comparar <valor>]\n")
    sku, novo = ARGS[1], ARGS[2]
    v = variante_por_sku(sku)
    desc = "%s (%s · %s): %s€ → %s€%s" % (
        sku, v["product"]["title"], v["title"], v["price"], novo,
        "  e preço-antes %s€" % comparar if comparar else "")
    if so_simulacao(desc):
        return
    entrada = {"id": v["id"], "price": novo}
    if comparar is not None:
        entrada["compareAtPrice"] = None if comparar in ("", "nenhum") else comparar
    d = pedir("""
    mutation($p: ID!, $v: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $p, variants: $v) {
        productVariants { sku price compareAtPrice }
        userErrors { field message }
      }
    }""", {"p": v["product"]["id"], "v": [entrada]})
    print("\n  Feito: %s\n" % json.dumps(d["productVariantsBulkUpdate"]["productVariants"],
                                         ensure_ascii=False))


def cmd_stock():
    if len(ARGS) < 3:
        raise SystemExit("\n  Uso: loja.py stock <sku> <quantidade>\n")
    sku, qtd = ARGS[1], int(ARGS[2])
    v = variante_por_sku(sku)
    locais = pedir("{ locations(first: 1, includeInactive: false) { nodes { id name } } }")
    local = locais["locations"]["nodes"][0]
    desc = "%s (%s): stock %s → %s em %s" % (sku, v["product"]["title"],
                                             v["inventoryQuantity"], qtd, local["name"])
    if so_simulacao(desc):
        return
    d = pedir("""
    mutation($i: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $i) {
        inventoryAdjustmentGroup { createdAt reason }
        userErrors { field message }
      }
    }""", {"i": {
        "name": "available",
        "reason": "correction",
        "ignoreCompareQuantity": True,
        "quantities": [{"inventoryItemId": v["inventoryItem"]["id"],
                        "locationId": local["id"], "quantity": qtd}],
    }})
    print("\n  Feito. %s\n" % json.dumps(d["inventorySetQuantities"]["inventoryAdjustmentGroup"],
                                         ensure_ascii=False))


def produto_por_handle(handle):
    d = pedir("query($q: String!) { products(first: 1, query: $q) "
              "{ nodes { id handle title status } } }", {"q": "handle:%s" % handle})
    nos = d["products"]["nodes"]
    if not nos:
        raise SystemExit("\n  Não existe produto com o handle '%s'.\n" % handle)
    return nos[0]


def cmd_estado():
    if len(ARGS) < 3:
        raise SystemExit("\n  Uso: loja.py estado <handle> <ACTIVE|DRAFT|ARCHIVED>\n")
    handle, estado = ARGS[1], ARGS[2].upper()
    if estado not in ("ACTIVE", "DRAFT", "ARCHIVED"):
        raise SystemExit("\n  Estado tem de ser ACTIVE, DRAFT ou ARCHIVED.\n")
    p = produto_por_handle(handle)
    if estado == "ACTIVE" and p["status"] != "ACTIVE":
        print("\n  ATENÇÃO: ACTIVE põe '%s' à venda, visível a quem entrar na loja." % p["title"])
    if so_simulacao("%s: %s → %s" % (handle, p["status"], estado)):
        return
    d = pedir("""
    mutation($i: ProductInput!) {
      productUpdate(input: $i) { product { handle status } userErrors { field message } }
    }""", {"i": {"id": p["id"], "status": estado}})
    print("\n  Feito: %s\n" % json.dumps(d["productUpdate"]["product"], ensure_ascii=False))


def cmd_descricao():
    if len(ARGS) < 3:
        raise SystemExit("\n  Uso: loja.py descricao <handle> <ficheiro.html>\n")
    handle, caminho = ARGS[1], ARGS[2]
    if not os.path.exists(caminho):
        raise SystemExit("\n  Não encontro o ficheiro '%s'.\n" % caminho)
    html = open(caminho, encoding="utf-8").read()
    p = produto_por_handle(handle)
    if so_simulacao("descrição de %s ← %s (%d caracteres)" % (handle, caminho, len(html))):
        return
    d = pedir("""
    mutation($i: ProductInput!) {
      productUpdate(input: $i) { product { handle } userErrors { field message } }
    }""", {"i": {"id": p["id"], "descriptionHtml": html}})
    print("\n  Feito: %s\n" % json.dumps(d["productUpdate"]["product"], ensure_ascii=False))


def cmd_gql():
    """Escotilha: corre qualquer query ou mutação da Admin API.

    A query vem de um ficheiro (ou de `-` para stdin) e nunca de um argumento:
    argumentos ficam no histórico da shell, e uma mutação repetida por engano a
    partir do histórico é a maneira mais fácil de escrever duas vezes na loja.
    """
    if len(ARGS) < 2:
        raise SystemExit("\n  Uso: loja.py gql <ficheiro|-> [variaveis.json]\n")
    origem = ARGS[1]
    query = sys.stdin.read() if origem == "-" else open(origem, encoding="utf-8").read()
    variaveis = json.loads(open(ARGS[2], encoding="utf-8").read()) if len(ARGS) > 2 else {}
    if query.lstrip().startswith("mutation") and so_simulacao("correr a mutação de %s" % origem):
        return
    mostrar(pedir(query, variaveis))


COMANDOS = {
    "info": cmd_info, "produtos": cmd_produtos, "produto": cmd_produto,
    "colecoes": cmd_colecoes, "paginas": cmd_paginas, "menus": cmd_menus,
    "locais": cmd_locais, "temas": cmd_temas, "encomendas": cmd_encomendas,
    "preco": cmd_preco, "stock": cmd_stock, "estado": cmd_estado,
    "descricao": cmd_descricao, "gql": cmd_gql,
}

if __name__ == "__main__":
    if not ARGS or ARGS[0] in ("-h", "--help", "ajuda"):
        raise SystemExit(__doc__)
    if ARGS[0] not in COMANDOS:
        raise SystemExit("\n  Não conheço '%s'. Comandos: %s\n"
                         % (ARGS[0], ", ".join(sorted(COMANDOS))))
    COMANDOS[ARGS[0]]()
