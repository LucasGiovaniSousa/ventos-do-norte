#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verificar.py — validações que o `shopify theme check` não faz.

O `theme check` valida sintaxe Liquid. O que se segue só é validado pelo
servidor da Shopify, no momento do envio — e aí o erro chega disfarçado de
problema de código quando é, quase sempre, um problema de dados.

Verifica:
  1. Nomes de secção e de bloco com mais de 25 caracteres (nos dois idiomas)
  2. Valores de `range` fora da grelha de passos, ou ranges com > 101 passos
  3. Chaves de tradução em falta entre pt-PT e en  ← falha o envio
  4. JSON inválido em config/, templates/ e sections/
  5. Blocos usados em templates que a secção não declara
  6. Ficheiros de locale `.default` duplicados por tipo

Sai com código 1 se houver erro. Avisos não impedem o envio.
"""
import json, re, sys, glob, os
from collections import OrderedDict

RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(RAIZ)

erros, avisos = [], []
LIMITE_NOME = 25


def carregar_json(caminho):
    try:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        erros.append(f"{caminho}: JSON inválido — linha {e.lineno}, {e.msg}")
        return None


def schema_da_seccao(caminho):
    src = open(caminho, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', src, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1), object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        erros.append(f"{caminho}: schema com JSON inválido — linha {e.lineno}, {e.msg}")
        return None


# Formas plurais do Shopify: uma chave pode ser uma string OU um objecto
# {one, other, zero, few, many}. As duas contam como chave existente.
PLURAIS = {'zero', 'one', 'two', 'few', 'many', 'other'}


def resolver(arvore, chave):
    """Devolve o texto da chave, ou None se não existir.

    Para chaves com formas plurais devolve a forma `other` — serve para medir
    comprimento de nomes, que é o único sítio onde o texto em si importa.
    """
    no = arvore
    for parte in chave.split('.'):
        if not isinstance(no, dict) or parte not in no:
            return None
        no = no[parte]
    if isinstance(no, str):
        return no
    if isinstance(no, dict) and PLURAIS & set(no):
        return no.get('other') or next(iter(no.values()))
    return None


# ── Carregar locales ────────────────────────────────────────────────
locais = {os.path.basename(p): carregar_json(p) for p in glob.glob('locales/*.json')}
schema_pt = locais.get('pt-PT.default.schema.json')
schema_en = locais.get('en.schema.json')
loja_pt = locais.get('pt-PT.default.json')
loja_en = locais.get('en.json')


# ── 6. Um só .default por tipo ──────────────────────────────────────
defaults_loja = [n for n in locais if n.endswith('.default.json') and '.schema.' not in n]
defaults_schema = [n for n in locais if n.endswith('.default.schema.json')]
if len(defaults_loja) > 1:
    erros.append(f"Mais do que um locale de loja `.default`: {defaults_loja}")
if len(defaults_schema) > 1:
    erros.append(f"Mais do que um locale de editor `.default`: {defaults_schema}")


# ── 3. Chaves de tradução em falta ──────────────────────────────────
def caminhos(d, pre=''):
    saida = set()
    if not isinstance(d, dict):
        return saida
    for k, v in d.items():
        p = f"{pre}.{k}" if pre else k
        saida |= caminhos(v, p) if isinstance(v, dict) else {p}
    return saida


for nome, a, b in (("loja", loja_pt, loja_en), ("editor", schema_pt, schema_en)):
    if not a or not b:
        continue
    ca, cb = caminhos(a), caminhos(b)
    for chave in sorted(ca - cb):
        erros.append(f"tradução {nome}: `{chave}` existe em pt-PT e falta em en")
    for chave in sorted(cb - ca):
        erros.append(f"tradução {nome}: `{chave}` existe em en e falta em pt-PT")

# Chaves usadas no código mas inexistentes
for caminho in glob.glob('sections/*.liquid') + glob.glob('snippets/*.liquid') + glob.glob('layout/*.liquid'):
    src = open(caminho, encoding='utf-8').read()
    corpo = re.sub(r'\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}', '', src, flags=re.S)
    for chave in set(re.findall(r"'([a-z0-9_]+(?:\.[a-z0-9_]+)+)'\s*\|\s*t\b", corpo)):
        if loja_pt and resolver(loja_pt, chave) is None:
            erros.append(f"{caminho}: usa `{chave}` que não existe em pt-PT.default.json")

for caminho in (glob.glob('sections/*.liquid') + glob.glob('sections/*.json')
                + glob.glob('templates/*.json') + glob.glob('config/*.json')):
    src = open(caminho, encoding='utf-8').read()
    for chave in set(re.findall(r'"t:([a-zA-Z0-9_.]+)"', src)):
        if schema_pt and resolver(schema_pt, chave) is None:
            erros.append(f"{caminho}: usa `t:{chave}` que não existe no schema pt-PT")


# ── 1 e 2. Nomes longos e ranges ────────────────────────────────────
seccoes = {}
for caminho in sorted(glob.glob('sections/*.liquid')):
    d = schema_da_seccao(caminho)
    if not d:
        continue
    seccoes[os.path.basename(caminho)[:-7]] = d

    for idioma, loc in (("pt-PT", schema_pt), ("en", schema_en)):
        if not loc:
            continue
        for rotulo, valor in [("secção", d.get('name'))] + [
                (f"bloco '{b.get('type')}'", b.get('name')) for b in d.get('blocks', [])]:
            texto = resolver(loc, valor[2:]) if isinstance(valor, str) and valor.startswith('t:') else valor
            if texto and len(texto) > LIMITE_NOME:
                erros.append(f"{caminho}: nome de {rotulo} em {idioma} tem "
                             f"{len(texto)} caracteres (máx {LIMITE_NOME}): {texto!r}")

# Ranges: no schema global e nos das secções
def validar_ranges(definicoes, valores, origem):
    for s in definicoes:
        if s.get('type') != 'range':
            continue
        mn, mx, passo = s.get('min', 0), s.get('max', 0), s.get('step', 1)
        if passo <= 0:
            erros.append(f"{origem}: range `{s.get('id')}` com passo {passo}")
            continue
        n = (mx - mn) / passo
        if n > 101:
            erros.append(f"{origem}: range `{s.get('id')}` tem {n:.0f} passos (máx 101)")
        if n != int(n):
            avisos.append(f"{origem}: range `{s.get('id')}` — (max−min) não é múltiplo do passo")
        for âmbito, vals in valores:
            if s.get('id') in vals:
                v = vals[s['id']]
                if isinstance(v, (int, float)) and (v < mn or v > mx or (v - mn) % passo != 0):
                    erros.append(f"{origem}: `{âmbito}.{s['id']}` = {v} não cai num passo "
                                 f"(min {mn}, max {mx}, passo {passo})")

dados = carregar_json('config/settings_data.json') or {}
âmbitos = [("current", dados.get('current', {}))] + \
          [(f"preset.{k}", v) for k, v in (dados.get('presets') or {}).items()]
esquema = carregar_json('config/settings_schema.json') or []
for grupo in esquema:
    if isinstance(grupo, dict) and grupo.get('settings'):
        validar_ranges(grupo['settings'], âmbitos, 'config/settings_schema.json')


# ── 5. Blocos usados em templates que a secção não declara ──────────
grupos = {os.path.basename(p): carregar_json(p) for p in glob.glob('sections/*-group.json')}
for caminho in sorted(glob.glob('templates/*.json')) + sorted(grupos):
    d = grupos.get(caminho) or carregar_json(caminho)
    if not d:
        continue
    nome = caminho if caminho.startswith('templates') else f"sections/{caminho}"
    for chave, sec in (d.get('sections') or {}).items():
        tipo = sec.get('type')
        if tipo not in seccoes:
            if not os.path.exists(f"sections/{tipo}.liquid"):
                erros.append(f"{nome}: secção `{tipo}` não existe")
            continue
        declarados = {b.get('type') for b in seccoes[tipo].get('blocks', [])}
        for bid, bloco in (sec.get('blocks') or {}).items():
            if bloco.get('type') not in declarados:
                erros.append(f"{nome}: bloco `{bid}` é do tipo `{bloco.get('type')}`, "
                             f"que a secção `{tipo}` não declara")


# ── Relatório ───────────────────────────────────────────────────────
for a in avisos:
    print(f"  aviso  {a}")
for e in erros:
    print(f"  ERRO   {e}")

print()
if erros:
    print(f"verificar.py: {len(erros)} erro(s), {len(avisos)} aviso(s) — envio cancelado")
    sys.exit(1)
print(f"verificar.py: tudo certo ({len(avisos)} aviso(s))")
