#!/bin/sh
echo "Iniciando Memorama Arcade Retro..."

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Lanzar servidor en background
if command -v python3 >/dev/null 2>&1; then
  python3 server.py &
elif command -v python >/dev/null 2>&1; then
  python server.py &
else
  echo "ERROR: No se encontro Python instalado."
  echo "Instala Python desde https://python.org"
  exit 1
fi

# Esperar a que el servidor arranque
sleep 2

# Abrir navegador
URL="http://localhost:8080/index.html"
if [ "$(uname)" = "Darwin" ]; then
  open "$URL"
else
  xdg-open "$URL"
fi
