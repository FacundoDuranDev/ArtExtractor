#!/bin/bash
# Script helper para visualizar imágenes organizadas por artista

IMAGES_DIR="${1:-imagenes_obras}"

if [ ! -d "$IMAGES_DIR" ]; then
    echo "Error: El directorio '$IMAGES_DIR' no existe"
    exit 1
fi

echo "Visualizador de imágenes de obras de arte"
echo "=========================================="
echo "Directorio: $IMAGES_DIR"
echo ""

# Verificar qué visualizadores están disponibles
if command -v feh &> /dev/null; then
    echo "Usando feh (ligero y rápido)..."
    echo "Controles:"
    echo "  ← → : Navegar imágenes"
    echo "  q   : Salir"
    echo "  f   : Pantalla completa"
    echo "  r   : Recargar"
    echo ""
    feh --auto-zoom --recursive --sort filename "$IMAGES_DIR"
elif command -v nomacs &> /dev/null; then
    echo "Usando nomacs (interfaz moderna)..."
    nomacs "$IMAGES_DIR"
elif command -v sxiv &> /dev/null; then
    echo "Usando sxiv (alternativa ligera)..."
    sxiv -r "$IMAGES_DIR"
elif command -v eog &> /dev/null; then
    echo "Usando Eye of GNOME..."
    eog "$IMAGES_DIR"
else
    echo "No se encontró ningún visualizador de imágenes instalado."
    echo ""
    echo "Para instalar visualizadores, ejecuta:"
    echo "  ./install_viewers.sh"
    echo ""
    echo "O instala manualmente:"
    echo "  sudo apt install feh nomacs sxiv"
    exit 1
fi
