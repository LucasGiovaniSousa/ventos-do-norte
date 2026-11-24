#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enquadrar.py — põe uma foto de produto no padrão do catálogo.

O PADRÃO
2000×2000, branco puro, produto centrado com 8 % de margem a toda a volta. A
margem e o tamanho são iguais em todas de propósito: é isso que faz a grelha
parecer alinhada em vez de cada produto flutuar num sítio diferente do card.

O QUE FAZ, POR ORDEM
  1. Leva o fundo quase-branco a branco puro. Fotos de estúdio (e as geradas
     por IA) saem com o fundo em 247–254, não em 255 — ao lado do branco do
     site nota-se um quadrado acinzentado à volta do produto.
  2. Encontra o produto. Manchas soltas e pequenas (pó, selos de canto,
     marcas de água) são ignoradas e apagadas: contam menos de 0,4 % da
     imagem e não tocam no objecto principal.
  3. Escala e centra o produto, sombra incluída, para ocupar 84 % do lado.

QUANDO O PRODUTO TOCA NA BORDA
Uma foto de pormenor, cortada de propósito, não tem margem para dar: centrá-la
deixaria o corte à vista no meio do branco. Nesse caso a foto fica a toda a
largura — só se limpa o fundo e se ajusta o tamanho. O script avisa.

USO
  python3 data/enquadrar.py origem.png destino.jpg
  python3 data/enquadrar.py origem.png destino.jpg --margem 0.10

Precisa do Pillow:  python3 -m pip install pillow
"""
import sys

try:
    from PIL import Image
except ImportError:
    raise SystemExit("\n  Falta o Pillow:  python3 -m pip install pillow\n")

LADO = 2000
MARGEM = 0.08
GRELHA = 128           # a imagem é lida em 128×128 células para achar manchas
MANCHA_MINIMA = 60     # células: abaixo disto é pó ou selo, não é produto
FUNDO_DE, FUNDO_ATE = 232, 247   # daqui para cima passa a branco puro


def limpar_fundo(im):
    """Estica os quase-brancos até 255 sem tocar nas cores do produto."""
    def curva(v):
        if v <= FUNDO_DE:
            return v
        if v >= FUNDO_ATE:
            return 255
        return int(FUNDO_DE + (v - FUNDO_DE) * (255 - FUNDO_DE) / (FUNDO_ATE - FUNDO_DE))
    return im.point([curva(v) for v in range(256)] * 3)


def manchas(mascara):
    """Agrupa as células ocupadas em manchas ligadas. Devolve lista de conjuntos."""
    pequena = mascara.resize((GRELHA, GRELHA), Image.BOX).point(lambda v: 255 if v > 4 else 0)
    px = pequena.load()
    vistas, grupos = set(), []
    for y in range(GRELHA):
        for x in range(GRELHA):
            if not px[x, y] or (x, y) in vistas:
                continue
            grupo, fila = set(), [(x, y)]
            vistas.add((x, y))
            while fila:
                cx, cy = fila.pop()
                grupo.add((cx, cy))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (cx + dx, cy + dy)
                        if (0 <= n[0] < GRELHA and 0 <= n[1] < GRELHA
                                and n not in vistas and px[n[0], n[1]]):
                            vistas.add(n)
                            fila.append(n)
            grupos.append(grupo)
    return grupos


def enquadrar(origem, destino, margem=MARGEM):
    im = limpar_fundo(Image.open(origem).convert("RGB"))
    larg, alt = im.size
    mascara = im.convert("L").point(lambda v: 255 if v < 253 else 0)

    grupos = manchas(mascara)
    if not grupos:
        raise SystemExit(f"  {origem}: não encontrei produto — a imagem é toda branca?")
    cx, cy = larg / GRELHA, alt / GRELHA

    # Apaga as manchas pequenas e soltas, na imagem e na máscara.
    apagadas = 0
    for g in grupos:
        if len(g) >= MANCHA_MINIMA:
            continue
        apagadas += 1
        xs, ys = [c[0] for c in g], [c[1] for c in g]
        caixa = (int(min(xs) * cx), int(min(ys) * cy),
                 int((max(xs) + 1) * cx) + 1, int((max(ys) + 1) * cy) + 1)
        im.paste((255, 255, 255), caixa)
        mascara.paste(0, caixa)

    caixa = mascara.getbbox()
    x0, y0, x1, y1 = caixa
    toca = x0 <= 2 or y0 <= 2 or x1 >= larg - 2 or y1 >= alt - 2

    tela = Image.new("RGB", (LADO, LADO), (255, 255, 255))
    if toca:
        # Pormenor cortado de propósito: fica a toda a largura.
        lado = min(larg, alt)
        recorte = im.crop(((larg - lado) // 2, (alt - lado) // 2,
                           (larg - lado) // 2 + lado, (alt - lado) // 2 + lado))
        tela = recorte.resize((LADO, LADO), Image.LANCZOS)
        nota = "toca na borda — fica a toda a largura, sem margem"
    else:
        util = LADO * (1 - 2 * margem)
        escala = util / max(x1 - x0, y1 - y0)
        produto = im.crop(caixa).resize(
            (round((x1 - x0) * escala), round((y1 - y0) * escala)), Image.LANCZOS)
        tela.paste(produto, ((LADO - produto.width) // 2, (LADO - produto.height) // 2))
        nota = f"escala {escala:.2f}, margem {margem:.0%}"

    tela.save(destino, "JPEG", quality=90, optimize=True, progressive=True)
    extra = f", {apagadas} mancha(s) solta(s) apagada(s)" if apagadas else ""
    print(f"  {destino.split('/')[-1]:<34} {nota}{extra}")


if __name__ == "__main__":
    args = sys.argv[1:]
    margem = MARGEM
    if "--margem" in args:
        i = args.index("--margem")
        margem = float(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)
    enquadrar(args[0], args[1], margem)
