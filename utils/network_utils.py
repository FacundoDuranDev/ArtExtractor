"""
Utilidades para operaciones de red.
"""

import requests
import logging
from urllib.parse import urljoin
from typing import Optional

logger = logging.getLogger(__name__)


def download_image(img_url: str, base_url: Optional[str] = None, save_path: str = None, timeout: int = 30) -> bool:
    """
    Descarga una imagen desde una URL.
    
    Args:
        img_url: URL relativa o absoluta de la imagen
        base_url: URL base para construir URLs relativas (opcional)
        save_path: Ruta donde guardar la imagen
        timeout: Timeout en segundos para la petición
        
    Returns:
        True si la descarga fue exitosa, False en caso contrario
    """
    try:
        # Construir URL completa
        if img_url.startswith('http://') or img_url.startswith('https://'):
            full_img_url = img_url
        elif base_url:
            full_img_url = urljoin(base_url, img_url)
        else:
            logger.error(f"No se puede construir URL completa: base_url no proporcionada para {img_url}")
            return False
        
        # Descargar la imagen
        img_response = requests.get(full_img_url, timeout=timeout)
        img_response.raise_for_status()
        
        # Guardar la imagen si se proporciona save_path
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(img_response.content)
            logger.debug(f"Imagen guardada en: {save_path}")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al descargar imagen {img_url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al guardar imagen: {e}")
        return False


def fetch_html(url: str, timeout: int = 30) -> Optional[str]:
    """
    Obtiene el contenido HTML de una URL.
    
    Args:
        url: URL a obtener
        timeout: Timeout en segundos
        
    Returns:
        Contenido HTML como string, o None si hay error
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.debug(f"Error al obtener HTML de {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al obtener HTML: {e}")
        return None
