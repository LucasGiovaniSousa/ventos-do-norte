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

O QUE É NOVO ENTRA EM RASCUNHO
status=DRAFT, como manda o _PADRAO-LOJA. Rever no admin antes de pôr à venda.
Num produto que já existe o estado NÃO é tocado: fica como estava.

O QUE ESTÁ À VENDA NÃO SE TOCA
A loja está aberta. Um produto ACTIVE é saltado, porque o catalogo.py pode
estar atrás da loja — os preços mudam-se no admin ou com o loja.py, e este
script reporia os antigos por cima. Em Novembro de 2026 era o caso: a peteca
estava a 7,90 € na loja e a 9,90 € aqui. Para escrever mesmo assim por cima de
um produto à venda, `--forcar` — depois de acertar o catálogo.

AS IMAGENS
Carregadas de data/produto/ por «staged upload» e ligadas ao produto na mesma
chamada. Só em produtos que ainda não têm nenhuma: a documentação não diz se
passar `files` substitui ou soma às que lá estão, e na dúvida não se mexe nas
fotos de um produto que já as tem. `--sem-imagens` salta este passo.

Uso:
    python3 data/publicar.py                          # simulação, não escreve
    python3 data/publicar.py --publicar               # escreve mesmo
    python3 data/publicar.py --apenas pipa-cruz-rosa,linha-10-vera-cruz
    python3 data/publicar.py --publicar --forcar      # inclui os que estão à venda

A simulação corre sem token: mostra o plano a partir do catálogo. Com token,
consulta a loja e diz o que criaria, actualizaria ou saltaria.
"""
import json, mimetypes, os, sys, time, uuid, urllib.request, urllib.error

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
FORCAR = "--forcar" in sys.argv
SEM_IMAGENS = "--sem-imagens" in sys.argv
APENAS = None
if "--apenas" in sys.argv:
    _i = sys.argv.index("--apenas")
    if _i + 1 >= len(sys.argv):
        raise SystemExit("\n  --apenas pede uma lista de handles separados por vírgula.\n")
    APENAS = [h.strip() for h in sys.argv[_i + 1].split(",") if h.strip()]

PASTA_IMAGENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "produto")


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
  products(first: 1, query: $q) {
    edges { node { id handle status media(first: 1) { nodes { id } } } }
  }
}"""

M_PREPARAR_ENVIO = """
mutation($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}"""

M_CRIAR = """
mutation($input: ProductSetInput!) {
  productSet(synchronous: true, input: $input) {
    product { id handle title variants(first: 10) { edges { node { sku } } } }
    userErrors { field message }
  }
}"""


def imagens_de(p):
    """Caminhos das imagens do produto que existem mesmo em data/produto/."""
    return [os.path.join(PASTA_IMAGENS, n) for n in (p.get("imagens") or [])
            if os.path.exists(os.path.join(PASTA_IMAGENS, n))]


def carregar_imagem(caminho):
    """Envia um ficheiro para a Shopify e devolve o URL a usar em `files`.

    Dois passos: a Shopify entrega um destino assinado (stagedUploadsCreate) e o
    ficheiro vai para lá em multipart, com os parâmetros que ela deu ANTES do
    campo `file` — o armazenamento rejeita o envio se o ficheiro vier primeiro.
    """
    nome = os.path.basename(caminho)
    tipo = mimetypes.guess_type(nome)[0] or "image/jpeg"
    dados = open(caminho, "rb").read()

    r = graphql(M_PREPARAR_ENVIO, {"input": [{
        "filename": nome, "mimeType": tipo, "httpMethod": "POST",
        "resource": "IMAGE", "fileSize": str(len(dados)),
    }]})["stagedUploadsCreate"]
    if r["userErrors"]:
        raise RuntimeError("; ".join(e["message"] for e in r["userErrors"]))
    alvo = r["stagedTargets"][0]

    fronteira = "----vdn" + uuid.uuid4().hex
    corpo = b""
    for par in alvo["parameters"]:
        corpo += (f"--{fronteira}\r\nContent-Disposition: form-data; "
                  f"name=\"{par['name']}\"\r\n\r\n{par['value']}\r\n").encode()
    corpo += (f"--{fronteira}\r\nContent-Disposition: form-data; name=\"file\"; "
              f"filename=\"{nome}\"\r\nContent-Type: {tipo}\r\n\r\n").encode()
    corpo += dados + f"\r\n--{fronteira}--\r\n".encode()

    pedido = urllib.request.Request(alvo["url"], data=corpo, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={fronteira}"})
    try:
        with urllib.request.urlopen(pedido, timeout=120) as resposta:
            if resposta.status >= 300:
                raise RuntimeError(f"envio devolveu HTTP {resposta.status}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"envio devolveu HTTP {e.code}: {e.read().decode()[:200]}")
    return alvo["resourceUrl"]


def entrada(p, id_existente=None, ficheiros=None):
    """Constrói o ProductSetInput a partir de uma linha do catálogo.

    `ficheiros` é a lista de URLs já carregados (ver carregar_imagem). O estado
    só vai em produtos novos: num que já existe, omiti-lo deixa-o como está.
    """
    nome_opcao = p["opcao"]
    campo = {
        "handle": p["handle"],
        "title": p["titulo"],
        "descriptionHtml": corpo_html(p),
        "vendor": p["marca"],
        "productType": p["tipo"],
        "tags": p["etiquetas"],
        **({} if id_existente else {"status": "DRAFT"}),
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

    if ficheiros:
        campo["files"] = [{"originalSource": url, "contentType": "IMAGE", "alt": p["alt"]}
                          for url in ficheiros]

    if id_existente:
        campo["id"] = id_existente
    return campo


def main():
    catalogo = CATALOGO
    if APENAS:
        desconhecidos = [h for h in APENAS if h not in {p["handle"] for p in CATALOGO}]
        if desconhecidos:
            raise SystemExit(f"\n  Não estão no catalogo.py: {', '.join(desconhecidos)}\n")
        catalogo = [p for p in CATALOGO if p["handle"] in APENAS]

    if A_SERIO and not TOKEN:
        raise SystemExit(
            "\n  Falta o token.\n\n"
            "  Escreve-o num ficheiro que o git ignora, na raiz do projecto:\n\n"
            "    printf '%s' 'shpat_...' > .admin-api.token\n\n"
            "  ou, para uma sessão só:\n\n"
            "    export SHOPIFY_ADMIN_TOKEN='shpat_...'\n\n"
            "  Ver POR-FAZER.md §9.\n")

    print(f"\n  Loja: {LOJA}")
    print(f"  Modo: {'PUBLICAR (escreve na loja)' if A_SERIO else 'simulação (não escreve nada)'}")
    if not TOKEN:
        print("  Sem token: o plano sai só do catálogo, sem consultar a loja.")
    print()

    criados = atualizados = saltados = falhas = 0

    for p in catalogo:
        existente = estado_loja = None
        tem_imagens = False
        if TOKEN:
            r = graphql(Q_PROCURAR, {"q": f"handle:{p['handle']}"})
            arestas = r["products"]["edges"]
            # A pesquisa por handle é por prefixo de termo: "pipa-cruz" também
            # apanha "pipa-cruz-rosa". Só conta a correspondência exacta.
            arestas = [a for a in arestas if a["node"]["handle"] == p["handle"]]
            if arestas:
                no = arestas[0]["node"]
                existente, estado_loja = no["id"], no["status"]
                tem_imagens = bool(no["media"]["nodes"])

        locais = [] if SEM_IMAGENS else imagens_de(p)
        em_falta = [n for n in (p.get("imagens") or [])
                    if not os.path.exists(os.path.join(PASTA_IMAGENS, n))]
        vai_imagens = bool(locais) and not tem_imagens

        if estado_loja == "ACTIVE" and not FORCAR:
            saltados += 1
            print(f"  [   saltar] {p['handle']:<26} está à venda — não toco (--forcar para escrever)")
            continue

        accao = "atualizar" if existente else ("criar" if TOKEN else "plano")
        n_var = len(p["variantes"])
        nota_img = (f"{len(locais)} imagem(ns)" if vai_imagens
                    else "imagens: já tem, não mexo" if (locais and tem_imagens)
                    else "sem imagens")
        print(f"  [{accao:>9}] {p['handle']:<26} {n_var} variante(s) · {nota_img}", end="")
        if em_falta:
            print(f" · FALTAM em data/produto/: {', '.join(em_falta)}", end="")

        if not A_SERIO:
            entrada(p, existente, ["simulação"] if vai_imagens else None)   # valida a construção
            print("   (simulação)")
            continue

        try:
            urls = [carregar_imagem(c) for c in locais] if vai_imagens else None
        except RuntimeError as e:
            # Um produto sem foto resolve-se no admin; um produto por criar não.
            print(f"\n              → imagens falharam ({e}); crio o produto sem elas", end="")
            urls = None

        r = graphql(M_CRIAR, {"input": entrada(p, existente, urls)})
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
        print(f"  {criados} criados · {atualizados} atualizados · {saltados} saltados · {falhas} falhas")
        print("\n  O que é novo ficou em RASCUNHO. Rever no admin antes de pôr à venda:")
        print(f"  https://{LOJA}/admin/products?selectedView=all&status=DRAFT\n")
        print("  Falta o stock (entra a zero) e passar a activo:")
        print("    python3 data/loja.py stock <sku> <quantidade> --escrever")
        print("    python3 data/loja.py estado <handle> ACTIVE --escrever\n")
        if os.path.exists(FICHEIRO_TOKEN):
            print("  Quando terminares, apaga o token e revoga a app:")
            print("    rm .admin-api.token\n")
    else:
        print("  Nada foi escrito. Para publicar mesmo:\n")
        print("    python3 data/publicar.py --publicar" +
              (f" --apenas {','.join(APENAS)}" if APENAS else "") + "\n")


if __name__ == "__main__":
    main()
