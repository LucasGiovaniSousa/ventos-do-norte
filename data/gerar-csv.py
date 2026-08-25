#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar-csv.py — escreve o CSV de importação a partir do catalogo.py.

O CSV é a via alternativa à Admin API: mesma informação, mesmo texto, formato
que o importador da Shopify aceita. Gerado e não escrito à mão para que as duas
vias nunca divirjam — se a descrição mudar no catalogo.py, muda nas duas.
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalogo import CATALOGO, corpo_html

COLS = ["Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
        "Option1 Name","Option1 Value","Variant SKU","Variant Grams",
        "Variant Inventory Tracker","Variant Inventory Qty","Variant Inventory Policy",
        "Variant Fulfillment Service","Variant Price","Variant Compare At Price",
        "Variant Requires Shipping","Variant Taxable","Variant Weight Unit",
        "Image Src","Image Position","Image Alt Text","SEO Title","SEO Description","Status",
        "Metafield: custom.linha_tecnica [single_line_text_field]",
        "Metafield: custom.componentes [list.single_line_text_field]",
        "Metafield: custom.para [single_line_text_field]"]

# Por omissão o CSV sai SEM imagens. O importador da Shopify precisa de URLs
# publicamente acessíveis na coluna "Image Src" — um caminho local ou um
# marcador de texto não servem, e a Shopify recusa o ficheiro inteiro com
# "O URL da imagem é inválido" em vez de ignorar só essa coluna.
#
# Para 10 produtos é mais rápido importar sem imagens e arrastá-las à mão em
# cada produto (Produtos → abrir → Multimédia) do que carregar tudo em
# Conteúdo → Ficheiros só para copiar URLs. Se um dia preferires o caminho das
# imagens no CSV, carrega os ficheiros de data/produto/ em Conteúdo →
# Ficheiros, copia os URLs públicos e passa-os aqui:
#
#   python3 data/gerar-csv.py --prefixo-imagens https://cdn.shopify.com/.../
PREFIXO_IMG = ""
if "--prefixo-imagens" in sys.argv:
    PREFIXO_IMG = sys.argv[sys.argv.index("--prefixo-imagens") + 1]

linhas = []

for p in CATALOGO:
    for i, (valor, preco, comparar, stock, sufixo) in enumerate(p["variantes"]):
        primeiro = i == 0
        imgs = p.get("imagens") or []
        linhas.append({c: "" for c in COLS} | {
            "Handle": p["handle"],
            "Title": p["titulo"] if primeiro else "",
            "Body (HTML)": corpo_html(p) if primeiro else "",
            "Vendor": p["marca"] if primeiro else "",
            "Type": p["tipo"] if primeiro else "",
            "Tags": ", ".join(p["etiquetas"]) if primeiro else "",
            "Published": "FALSE" if primeiro else "",
            "Option1 Name": p["opcao"] if primeiro else "",
            "Option1 Value": valor,
            "Variant SKU": f"{p['sku']}-{sufixo}",
            "Variant Grams": str(p["gramas"]),
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": str(stock),
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": preco,
            "Variant Compare At Price": comparar,
            "Variant Requires Shipping": "TRUE",
            "Variant Taxable": "TRUE",
            "Variant Weight Unit": "g",
            "Image Src": (PREFIXO_IMG + imgs[0]) if (primeiro and imgs and PREFIXO_IMG) else "",
            "Image Position": "1" if (primeiro and imgs and PREFIXO_IMG) else "",
            "Image Alt Text": p["alt"] if (primeiro and imgs and PREFIXO_IMG) else "",
            "SEO Title": p["seo_titulo"] if primeiro else "",
            "SEO Description": p["seo_desc"] if primeiro else "",
            "Status": "draft" if primeiro else "",
            "Metafield: custom.linha_tecnica [single_line_text_field]": p.get("linha_tecnica","") if primeiro else "",
            "Metafield: custom.componentes [list.single_line_text_field]": "|".join(p.get("componentes",[])) if primeiro else "",
            "Metafield: custom.para [single_line_text_field]": p.get("para","") if primeiro else "",
        })
    if PREFIXO_IMG:
        for pos, img in enumerate((p.get("imagens") or [])[1:], start=2):
            linhas.append({c: "" for c in COLS} | {
                "Handle": p["handle"], "Image Src": PREFIXO_IMG + img, "Image Position": str(pos)})

destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "produtos-ventos-do-norte.csv")
with open(destino, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(linhas)

print(f"{len({r['Handle'] for r in linhas})} produtos · "
      f"{len([r for r in linhas if r['Variant Price']])} variantes · {len(linhas)} linhas")

# Verificações do padrão
mau_seo_t = [r['SEO Title'] for r in linhas if len(r['SEO Title']) > 60]
mau_seo_d = [r['SEO Description'] for r in linhas if len(r['SEO Description']) > 155]
mau_preco = [r['Variant Price'] for r in linhas if r['Variant Price'] and not r['Variant Price'].endswith(('.90','.50'))]
print("SEO Title > 60:", mau_seo_t or "nenhum")
print("SEO Desc > 155:", mau_seo_d or "nenhum")
print("preços fora de ,90/,50:", mau_preco or "nenhum")
print("estados:", {r['Status'] for r in linhas if r['Status']})
