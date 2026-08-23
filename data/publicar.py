#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""publicar.py — cria os produtos na Shopify pela Admin API.

PORQUÊ GRAPHQL E NÃO REST
A Shopify descontinuou a REST Admin API de produtos. Em apps novas, o
/admin/api/*/products.json já não aceita escritas com variantes. Este script usa
a GraphQL Admin API, que é o caminho suportado.

O TOKEN
Lido de SHOPIFY_ADMIN_TOKEN, nunca escrito em ficheiro nem passado por
argumento (argumentos ficam no histórico da shell e são visíveis no `ps`).

SEGURO DE CORRER DUAS VEZES
Antes de criar, procura o handle. Se já existir, ATUALIZA em vez de duplicar.
Correr o script outra vez depois de mudar uma descrição faz o que se espera.

TUDO EM RASCUNHO
status=DRAFT, como manda o _PADRAO-LOJA. Rever no admin antes de pôr à venda.

Uso:
    export SHOPIFY_ADMIN_TOKEN='shpat_...'
    python3 data/publicar.py              # simulação, não escreve nada
    python3 data/publicar.py --publicar   # escreve mesmo
"""
import json, os, sys, time, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalogo import CATALOGO, corpo_html

LOJA = os.environ.get("SHOPIFY_STORE", "bn3vcf-f1.myshopify.com")

# O token pode vir de duas origens:
#
#   1. SHOPIFY_ADMIN_TOKEN — para quem corre isto à mão numa só sessão.
#   2. .admin-api.token — um ficheiro na raiz do projecto, ignorado pelo git.
#
# A segunda existe porque cada comando de shell abre um processo novo: uma
# variável exportada numa janela não é vista noutra. Com o ficheiro, o token
# chega ao disco uma vez e qualquer comando o encontra — sem passar por
# histórico de chat nem por argumento de linha de comandos (que ficaria
# visível no `ps` a qualquer processo da máquina).
#
# APAGAR O FICHEIRO QUANDO O TRABALHO ACABAR.
FICHEIRO_TOKEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              ".admin-api.token")

TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
if not TOKEN and os.path.exists(FICHEIRO_TOKEN):
    TOKEN = open(FICHEIRO_TOKEN, encoding="utf-8").read().strip()
VERSAO = "2026-01"
URL = f"https://{LOJA}/admin/api/{VERSAO}/graphql.json"
A_SERIO = "--publicar" in sys.argv


def graphql(query, variaveis=None):
    corpo = json.dumps({"query": query, "variables": variaveis or {}}).encode()
    pedido = urllib.request.Request(URL, data=corpo, method="POST", headers={
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": TOKEN,
    })
    try:
        with urllib.request.urlopen(pedido, timeout=60) as r:
            dados = json.loads(r.read())
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode()[:400]
        if e.code == 401:
            raise SystemExit("\n  Token recusado (401). Confirma que o copiaste inteiro\n"
                             "  e que a app tem write_products.\n")
        if e.code == 403:
            raise SystemExit("\n  Sem permissão (403). A app precisa de write_products.\n")
        raise SystemExit(f"\n  HTTP {e.code}: {detalhe}\n")

    if "errors" in dados:
        raise SystemExit(f"\n  Erro GraphQL: {json.dumps(dados['errors'], ensure_ascii=False)[:500]}\n")

    # O custo vem em cada resposta; abrandar antes de a Shopify travar.
    custo = dados.get("extensions", {}).get("cost", {})
    restante = custo.get("throttleStatus", {}).get("currentlyAvailable", 999)
    if restante < 200:
        time.sleep(2)
    return dados["data"]


Q_PROCURAR = """
query($q: String!) {
  products(first: 1, query: $q) { edges { node { id handle } } }
}"""

M_CRIAR = """
mutation($input: ProductSetInput!) {
  productSet(synchronous: true, input: $input) {
    product { id handle title variants(first: 10) { edges { node { sku } } } }
    userErrors { field message }
  }
}"""


def entrada(p, id_existente=None):
    """Constrói o ProductSetInput a partir de uma linha do catálogo."""
    nome_opcao = p["opcao"]
    campo = {
        "handle": p["handle"],
        "title": p["titulo"],
        "descriptionHtml": corpo_html(p),
        "vendor": p["marca"],
        "productType": p["tipo"],
        "tags": p["etiquetas"],
        "status": "DRAFT",
        "seo": {"title": p["seo_titulo"], "description": p["seo_desc"]},
        "productOptions": [{
            "name": nome_opcao,
            "values": [{"name": v[0]} for v in p["variantes"]],
        }],
        "variants": [{
            "optionValues": [{"optionName": nome_opcao, "name": valor}],
            "price": preco,
            **({"compareAtPrice": comparar} if comparar else {}),
            "sku": f"{p['sku']}-{sufixo}",
            "inventoryPolicy": "DENY",
            "inventoryItem": {
                "tracked": True,
                "measurement": {"weight": {"value": float(p["gramas"]), "unit": "GRAMS"}},
                "requiresShipping": True,
            },
        } for (valor, preco, comparar, _stock, sufixo) in p["variantes"]],
    }

    metacampos = []
    if p.get("linha_tecnica"):
        metacampos.append({"namespace": "custom", "key": "linha_tecnica",
                           "type": "single_line_text_field", "value": p["linha_tecnica"]})
    if p.get("componentes"):
        metacampos.append({"namespace": "custom", "key": "componentes",
                           "type": "list.single_line_text_field",
                           "value": json.dumps(p["componentes"], ensure_ascii=False)})
    if p.get("para"):
        metacampos.append({"namespace": "custom", "key": "para",
                           "type": "single_line_text_field", "value": p["para"]})
    if metacampos:
        campo["metafields"] = metacampos

    if id_existente:
        campo["id"] = id_existente
    return campo


def main():
    if not TOKEN:
        raise SystemExit(
            "\n  Falta o token.\n\n"
            "  Escreve-o num ficheiro que o git ignora, na raiz do projecto:\n\n"
            "    printf '%s' 'shpat_...' > .admin-api.token\n\n"
            "  ou, para uma sessão só:\n\n"
            "    export SHOPIFY_ADMIN_TOKEN='shpat_...'\n\n"
            "  Ver POR-FAZER.md §9.\n")

    print(f"\n  Loja: {LOJA}")
    print(f"  Modo: {'PUBLICAR (escreve na loja)' if A_SERIO else 'simulação (não escreve nada)'}\n")

    criados = atualizados = falhas = 0

    for p in CATALOGO:
        existente = None
        if TOKEN:
            r = graphql(Q_PROCURAR, {"q": f"handle:{p['handle']}"})
            arestas = r["products"]["edges"]
            if arestas:
                existente = arestas[0]["node"]["id"]

        estado = "atualizar" if existente else "criar"
        n_var = len(p["variantes"])
        print(f"  [{estado:>9}] {p['handle']:<24} {n_var} variante(s)", end="")

        if not A_SERIO:
            print("   (simulação)")
            continue

        r = graphql(M_CRIAR, {"input": entrada(p, existente)})
        erros = r["productSet"]["userErrors"]
        if erros:
            falhas += 1
            print("   FALHOU")
            for e in erros:
                print(f"              → {'.'.join(e.get('field') or [])}: {e['message']}")
            continue

        if existente:
            atualizados += 1
        else:
            criados += 1
        print("   ok")

    print()
    if A_SERIO:
        print(f"  {criados} criados · {atualizados} atualizados · {falhas} falhas")
        print("\n  Todos em RASCUNHO. Rever no admin antes de pôr à venda:")
        print(f"  https://{LOJA}/admin/products?selectedView=all&status=DRAFT\n")
        print("  Falta ainda carregar as imagens (Conteúdo → Ficheiros, ou em cada produto)")
        print("  e criar os metacampos, se ainda não existirem — ver POR-FAZER.md §7.\n")
        if os.path.exists(FICHEIRO_TOKEN):
            print("  Quando terminares, apaga o token e revoga a app:")
            print("    rm .admin-api.token\n")
    else:
        print("  Nada foi escrito. Para publicar mesmo:\n")
        print("    python3 data/publicar.py --publicar\n")


if __name__ == "__main__":
    main()
