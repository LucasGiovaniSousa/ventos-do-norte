#!/usr/bin/env bash
# deploy.sh — envio do tema em duas passagens.
#
# PORQUÊ DUAS PASSAGENS
# A CLI da Shopify envia os ficheiros por ordem alfabética e valida cada um no
# momento em que chega. A ordem alfabética põe sistematicamente a configuração
# antes do código de que ela depende:
#
#   config/settings_data.json    antes de  config/settings_schema.json
#   sections/footer-group.json   antes de  sections/footer.liquid
#   templates/index.json         antes das secções que invoca
#
# O servidor rejeita, e a mensagem que sai — «o tipo deve ser definido no
# esquema», «must be a step in the range» — parece erro de código. Não é: o
# código está certo, ainda não chegou.
#
# Primeira passagem manda o código. Segunda manda a configuração, já com tudo
# a que ela se refere no sítio.
#
# USO
#   ./deploy.sh                tema de desenvolvimento
#   ./deploy.sh 123456789      tema específico, por ID
#   ./deploy.sh novo           cria tema novo, não publicado
#   ./deploy.sh ao-vivo        o tema PUBLICADO — pede confirmação escrita
set -euo pipefail

LOJA="${SHOPIFY_STORE:-bn3vcf-f1.myshopify.com}"
ALVO="${1:-dev}"
cd "$(dirname "$0")"

echo "── Verificações prévias ──────────────────────────────"
python3 verificar.py
shopify theme check

# Alvo
case "$ALVO" in
  dev)
    ARGS=(--development)
    echo "── Alvo: tema de desenvolvimento ─────────────────────" ;;
  novo)
    ARGS=(--unpublished --theme "Ventos do Norte $(date +%Y-%m-%d_%H%M)")
    echo "── Alvo: tema novo, não publicado ────────────────────" ;;
  ao-vivo)
    echo
    echo "  ATENÇÃO: isto escreve no tema PUBLICADO de $LOJA."
    echo "  Quem estiver na loja neste momento vê a mudança, e não há anular."
    echo "  Para repor, é preciso enviar outra vez a partir do git."
    echo
    read -r -p '  Escreve "ao vivo" para confirmar: ' RESPOSTA
    [ "$RESPOSTA" = "ao vivo" ] || { echo "  Cancelado."; exit 1; }
    ARGS=(--live --allow-live)
    echo "── Alvo: tema PUBLICADO ──────────────────────────────" ;;
  *)
    # Um ID escrito à pressa pode ser o tema publicado. O padrão diz que enviar
    # para o publicado tem de ser um alvo com nome próprio e uma pergunta — por
    # isso confirmamos aqui em vez de deixar passar.
    ID_AO_VIVO=$(shopify theme list --store "$LOJA" --json 2>/dev/null \
      | python3 -c 'import sys,json;[print(t["id"]) for t in json.load(sys.stdin) if t.get("role")=="live"]' 2>/dev/null || true)

    if [ -n "$ID_AO_VIVO" ] && [ "$ALVO" = "$ID_AO_VIVO" ]; then
      echo
      echo "  O tema #$ALVO é o tema PUBLICADO desta loja."
      echo "  Usa  ./deploy.sh ao-vivo  — existe de propósito, com confirmação."
      exit 1
    fi

    ARGS=(--theme "$ALVO")
    echo "── Alvo: tema #$ALVO ─────────────────────────────────" ;;
esac

# Primeira passagem: o código.
echo
echo "── 1/2 · código (liquid, css, js, fontes, traduções) ──"
shopify theme push --store "$LOJA" "${ARGS[@]}" --force --nodelete \
  --only assets/ \
  --only layout/ \
  --only locales/ \
  --only snippets/ \
  --only 'sections/*.liquid' \
  --only 'templates/*.liquid'

# Segunda passagem: a configuração, que depende do código acima.
echo
echo "── 2/2 · configuração (settings, templates, grupos) ───"
shopify theme push --store "$LOJA" "${ARGS[@]}" --force \
  --only config/ \
  --only 'sections/*.json' \
  --only 'templates/*.json'

echo
echo "── Feito ─────────────────────────────────────────────"
echo "  Lê a saída acima na íntegra. Não uses grep para a confirmar:"
echo "  a CLI parte mensagens em duas linhas e o grep devolve zero"
echo "  num envio que correu bem."
