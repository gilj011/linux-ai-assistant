#!/usr/bin/env bash
# Script para construcao de pacote Debian (.deb) do kored
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="0.3.0"
ARCH="all"
PACKAGE_NAME="kored_${VERSION}_${ARCH}"
BUILD_ROOT="${REPO_DIR}/dist/${PACKAGE_NAME}"

echo "[kored] Construindo pacote Debian ${PACKAGE_NAME}.deb..."

# Limpa build anterior
rm -rf "${REPO_DIR}/dist"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/lib/kored"
mkdir -p "${BUILD_ROOT}/usr/share/bash-completion/completions"
mkdir -p "${BUILD_ROOT}/usr/share/doc/kored"

# 1. Cria arquivo de controle Debian
cat << EOF > "${BUILD_ROOT}/DEBIAN/control"
Package: kored
Version: ${VERSION}
Section: admin
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-rich, python3-yaml, python3-requests
Maintainer: gilj011 <gilbertoearn@gmail.com>
Description: Linux Systems Intelligence & Assistant
 Copiloto local de engenharia de sistemas, troubleshooting e assistencia tecnica para Linux.
 Inspeciona estado do sistema, executa sondas de diagnostico e propoe acoes sob aprovacao humana explicita.
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN"
chmod 644 "${BUILD_ROOT}/DEBIAN/control"

# 2. Copia arquivos de codigo para /usr/lib/kored
cp -r "${REPO_DIR}/src" "${BUILD_ROOT}/usr/lib/kored/"
cp -r "${REPO_DIR}/config" "${BUILD_ROOT}/usr/lib/kored/"
cp "${REPO_DIR}/main.py" "${BUILD_ROOT}/usr/lib/kored/"
find "${BUILD_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${BUILD_ROOT}" -type f -name "*.pyc" -delete 2>/dev/null || true

# 3. Cria o wrapper executavel em /usr/bin/kored
cat << 'EOF' > "${BUILD_ROOT}/usr/bin/kored"
#!/usr/bin/env bash
exec /usr/bin/python3 /usr/lib/kored/main.py "$@"
EOF
chmod 755 "${BUILD_ROOT}/usr/bin/kored"

# 4. Copia script de autocompletar
cp "${REPO_DIR}/scripts/kored_completion.bash" "${BUILD_ROOT}/usr/share/bash-completion/completions/kored"
chmod 644 "${BUILD_ROOT}/usr/share/bash-completion/completions/kored"

# 5. Documentacao
cp "${REPO_DIR}/README.md" "${BUILD_ROOT}/usr/share/doc/kored/"
[ -f "${REPO_DIR}/LICENSE" ] && cp "${REPO_DIR}/LICENSE" "${BUILD_ROOT}/usr/share/doc/kored/copyright"

# 6. Constroi o pacote .deb
dpkg-deb --build --root-owner-group "${BUILD_ROOT}" "${REPO_DIR}/dist/${PACKAGE_NAME}.deb"

echo "[kored] Pacote gerado com sucesso em: ${REPO_DIR}/dist/${PACKAGE_NAME}.deb"
echo "Para instalar no sistema:"
echo "  sudo dpkg -i dist/${PACKAGE_NAME}.deb"
