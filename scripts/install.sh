#!/usr/bin/env bash
# Script de instalacao do kored no sistema Linux
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[kored] Iniciando instalacao..."

# Verifica se python3 esta disponivel
if ! command -v python3 &>/dev/null; then
    echo "[Erro] Python 3 nao encontrado. Instale o Python 3 antes de continuar."
    exit 1
fi

# Verifica se os modulos basicos estao acessiveis
python3 -c "import rich, yaml, requests" 2>/dev/null || {
    echo "[kored] Instalando dependencias Python necessarias..."
    pip3 install -r "${REPO_DIR}/requirements.txt" || python3 -m pip install -r "${REPO_DIR}/requirements.txt"
}

# Define destino conforme privilegios
if [ "$EUID" -eq 0 ]; then
    BIN_DIR="/usr/local/bin"
    COMP_DIR="/etc/bash_completion.d"
else
    BIN_DIR="${HOME}/.local/bin"
    COMP_DIR="${HOME}/.local/share/bash-completion/completions"
fi

mkdir -p "${BIN_DIR}"
mkdir -p "${COMP_DIR}"

# Cria o wrapper executavel
LAUNCHER="${BIN_DIR}/kored"
cat << EOF > "${LAUNCHER}"
#!/usr/bin/env bash
exec python3 "${REPO_DIR}/main.py" "\$@"
EOF

chmod +x "${LAUNCHER}"
chmod +x "${REPO_DIR}/main.py"
chmod +x "${REPO_DIR}/kored"

# Copia script de autocompletar
cp "${REPO_DIR}/scripts/kored_completion.bash" "${COMP_DIR}/kored"

echo "[kored] Instalacao concluida com sucesso!"
echo "[kored] Binario instalado em: ${LAUNCHER}"
echo "[kored] Autocompletar instalado em: ${COMP_DIR}/kored"

if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    echo ""
    echo "[Aviso] O diretorio '${BIN_DIR}' nao esta presente no seu PATH."
    echo "Adicione ao seu ~/.bashrc ou ~/.zshrc:"
    echo "  export PATH=\"${BIN_DIR}:\$PATH\""
fi

echo ""
echo "Agora voce pode executar 'kored' de qualquer diretorio no terminal."
