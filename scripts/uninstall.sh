#!/usr/bin/env bash
# Script de desinstalacao do kored do sistema
set -e

echo "[kored] Iniciando desinstalacao..."

REMOVED=0

# Locais possiveis de instalacao
TARGETS=(
    "/usr/local/bin/kored"
    "/etc/bash_completion.d/kored"
    "${HOME}/.local/bin/kored"
    "${HOME}/.local/share/bash-completion/completions/kored"
)

for target in "${TARGETS[@]}"; do
    if [ -f "$target" ]; then
        if [ -w "$(dirname "$target")" ]; then
            rm -f "$target"
            echo "[kored] Removido: $target"
            REMOVED=$((REMOVED + 1))
        else
            echo "[Aviso] Permissao negada para remover $target. Execute com sudo se foi instalado como root."
        fi
    fi
done

if [ "$REMOVED" -eq 0 ]; then
    echo "[kored] Nenhum binario instalado foi encontrado nos caminhos padrao."
else
    echo "[kored] Desinstalacao concluida."
fi
