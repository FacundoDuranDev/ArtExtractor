#!/usr/bin/env python3
"""
Script para extraer imágenes de obras de arte del Museo Nacional de Bellas Artes de Argentina.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import logging
import argparse
import re
from pathlib import Path
from urllib.parse import urljoin

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def sanitize_filename(filename):
    """
    Sanitiza un nombre de archivo eliminando caracteres inválidos.
    
    Args:
        filename: Nombre de archivo a sanitizar
        
    Returns:
        Nombre de archivo sanitizado
    """
    # Reemplazar caracteres inválidos por guiones bajos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Eliminar espacios múltiples y reemplazar por uno solo
    filename = re.sub(r'\s+', ' ', filename)
    # Eliminar espacios al inicio y final
    filename = filename.strip()
    # Limitar longitud (máximo 200 caracteres para evitar problemas)
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def extract_obra_info(soup):
    """
    Extrae información de una obra desde el HTML parseado.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Tupla con (título, artista, url_imagen) o (None, None, None) si no se encuentra
    """
    try:
        # Extraer el título de la obra
        titulo_tag = soup.find('h1')
        titulo = titulo_tag.text.strip() if titulo_tag else None
        
        # Extraer información del artista
        details_div = soup.find('dl', class_='row mt-3')
        artista = None
        if details_div:
            li_elements = details_div.find_all('li')
            if li_elements:
                artista = li_elements[0].text.strip().replace(",", "")
        
        # Extraer URL de la imagen
        img_tag = soup.find('a', {'data-fancybox': 'gallery'})
        img_url = None
        if img_tag and 'href' in img_tag.attrs:
            img_url = img_tag['href']
        
        return titulo, artista, img_url
    except Exception as e:
        logger.error(f"Error al extraer información de la obra: {e}")
        return None, None, None


def download_image(img_url, base_url_img, save_path):
    """
    Descarga una imagen desde una URL.
    
    Args:
        img_url: URL relativa o absoluta de la imagen
        base_url_img: URL base para construir URLs relativas
        save_path: Ruta donde guardar la imagen
        
    Returns:
        True si la descarga fue exitosa, False en caso contrario
    """
    try:
        # Construir URL completa
        if img_url.startswith('/'):
            full_img_url = urljoin(base_url_img, img_url)
        elif img_url.startswith('http'):
            full_img_url = img_url
        else:
            full_img_url = urljoin(base_url_img, img_url)
        
        # Descargar la imagen
        img_response = requests.get(full_img_url, timeout=30)
        img_response.raise_for_status()
        
        # Guardar la imagen
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(img_response.content)
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al descargar imagen {img_url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al guardar imagen: {e}")
        return False


def scrape_obras(start_id, end_id, delay, output_dir='imagenes_obras'):
    """
    Extrae imágenes de obras de arte del Museo Nacional de Bellas Artes.
    
    Args:
        start_id: ID inicial de obra a procesar
        end_id: ID final de obra a procesar
        delay: Segundos de espera entre peticiones
        output_dir: Directorio donde guardar las imágenes
    """
    base_url = "https://www.bellasartes.gob.ar/coleccion/obra/"
    base_url_img = "https://www.bellasartes.gob.ar/"
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    obras_encontradas = 0
    obras_descargadas = 0
    obras_fallidas = 0
    
    logger.info(f"Iniciando extracción de obras desde ID {start_id} hasta {end_id}")
    logger.info(f"Delay entre peticiones: {delay} segundos")
    
    for obra_id in range(start_id, end_id + 1):
        url = f"{base_url}{obra_id}/"
        
        try:
            # Hacer petición HTTP
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Analizar el contenido HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información de la obra
            titulo, artista, img_url = extract_obra_info(soup)
            
            if not titulo or not artista or not img_url:
                logger.debug(f"Obra {obra_id}: Información incompleta (título: {titulo}, artista: {artista}, img_url: {img_url})")
                continue
            
            obras_encontradas += 1
            logger.info(f"Obra encontrada [{obra_id}]: {titulo} - {artista}")
            
            # Sanitizar nombres
            artista_sanitizado = sanitize_filename(artista)
            titulo_sanitizado = sanitize_filename(titulo)
            
            # Crear ruta de guardado
            dir_path = os.path.join(output_dir, artista_sanitizado)
            img_filename = os.path.join(dir_path, f"{titulo_sanitizado}.jpg")
            
            # Descargar imagen
            if download_image(img_url, base_url_img, img_filename):
                obras_descargadas += 1
                logger.info(f"  ✓ Imagen guardada: {img_filename}")
            else:
                obras_fallidas += 1
                logger.warning(f"  ✗ Error al descargar imagen para obra {obra_id}")
        
        except requests.exceptions.RequestException as e:
            logger.debug(f"Obra {obra_id} no encontrada o error de conexión: {e}")
        except Exception as e:
            logger.error(f"Error inesperado procesando obra {obra_id}: {e}")
            obras_fallidas += 1
        
        # Aplicar delay entre peticiones (excepto en la última)
        if obra_id < end_id:
            time.sleep(delay)
    
    # Resumen final
    logger.info("=" * 60)
    logger.info("RESUMEN DE EXTRACCIÓN")
    logger.info("=" * 60)
    logger.info(f"Obras encontradas: {obras_encontradas}")
    logger.info(f"Obras descargadas exitosamente: {obras_descargadas}")
    logger.info(f"Obras con errores: {obras_fallidas}")
    logger.info(f"Total procesado: {end_id - start_id + 1}")


def main():
    """Función principal con argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Extrae imágenes de obras de arte del Museo Nacional de Bellas Artes de Argentina',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python origenes.py                    # Usa valores por defecto (0-2000)
  python origenes.py --start 100 --end 200
  python origenes.py --start 0 --end 100 --delay 2
  python origenes.py --start 1870 --end 1880 --output mi_carpeta
        """
    )
    
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='ID inicial de obra a procesar (por defecto: 0)'
    )
    
    parser.add_argument(
        '--end',
        type=int,
        default=2000,
        help='ID final de obra a procesar (por defecto: 2000)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Segundos de espera entre peticiones (por defecto: 1.0)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='imagenes_obras',
        help='Directorio donde guardar las imágenes (por defecto: imagenes_obras)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Activa modo verbose (muestra más información de debug)'
    )
    
    args = parser.parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validar argumentos
    if args.start < 0:
        logger.error("El ID inicial debe ser mayor o igual a 0")
        return
    
    if args.end < args.start:
        logger.error("El ID final debe ser mayor o igual al ID inicial")
        return
    
    if args.delay < 0:
        logger.error("El delay debe ser mayor o igual a 0")
        return
    
    # Ejecutar scraping
    try:
        scrape_obras(args.start, args.end, args.delay, args.output)
    except KeyboardInterrupt:
        logger.info("\nProceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)


if __name__ == "__main__":
    main()
