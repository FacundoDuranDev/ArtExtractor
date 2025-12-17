#!/bin/bash
# Script para instalar visualizadores de imágenes recomendados

echo "Instalando visualizadores de imágenes para Kali Linux..."
echo ""

# Instalar feh (ligero y rápido)
echo "Instalando feh..."
sudo apt update
sudo apt install -y feh

# Instalar nomacs (más completo con interfaz moderna)
echo "Instalando nomacs..."
sudo apt install -y nomacs

# Instalar sxiv (alternativa ligera)
echo "Instalando sxiv..."
sudo apt install -y sxiv

echo ""
echo "✓ Instalación completada!"
echo ""
echo "Visualizadores instalados:"
echo "  - feh: Ligero y rápido, perfecto para navegación rápida"
echo "  - nomacs: Completo con interfaz moderna"
echo "  - sxiv: Alternativa ligera"
echo ""
echo "Para usar con tus imágenes:"
echo "  feh imagenes_obras/"
echo "  nomacs imagenes_obras/"
echo "  sxiv imagenes_obras/"
