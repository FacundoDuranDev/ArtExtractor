"""
Extractor para el Museo Nacional de Bellas Artes de Argentina.
"""

from bs4 import BeautifulSoup
import logging
from typing import Optional

from .base import BaseExtractor, ObraInfo
from utils.network_utils import fetch_html

logger = logging.getLogger(__name__)


class BellasArtesExtractor(BaseExtractor):
    """
    Extractor para obras de arte del Museo Nacional de Bellas Artes.
    
    URL base: https://www.bellasartes.gob.ar/coleccion/obra/
    """
    
    BASE_URL = "https://www.bellasartes.gob.ar/coleccion/obra/"
    BASE_IMAGE_URL = "https://www.bellasartes.gob.ar/"
    
    def __init__(self, output_dir: str = "imagenes_obras_new", delay: float = 1.0,
                 use_registry: bool = True, check_existing_files: bool = True):
        """
        Inicializa el extractor de Bellas Artes.
        
        Args:
            output_dir: Directorio donde guardar las imágenes
            delay: Segundos de espera entre peticiones
            use_registry: Si es True, usa el sistema de registro
            check_existing_files: Si es True, verifica archivos existentes
        """
        super().__init__(output_dir, delay, use_registry, check_existing_files)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_obra_url(self, obra_id: str) -> str:
        """Construye la URL de una obra."""
        return f"{self.BASE_URL}{obra_id}/"
    
    def get_base_image_url(self) -> Optional[str]:
        """Obtiene la URL base para imágenes."""
        return self.BASE_IMAGE_URL
    
    def extract_obra_info(self, obra_id: str) -> Optional[ObraInfo]:
        """
        Extrae información de una obra desde el sitio web.
        
        Args:
            obra_id: ID de la obra
            
        Returns:
            ObraInfo con la información de la obra, o None si no se encuentra
        """
        url = self.get_obra_url(obra_id)
        html = fetch_html(url)
        
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraer el título de la obra
            titulo_tag = soup.find('h1')
            titulo = titulo_tag.text.strip() if titulo_tag else None
            
            if not titulo:
                return None
            
            # Extraer información del artista
            details_div = soup.find('dl', class_='row mt-3')
            artista = None
            metadata = {}
            
            if details_div:
                li_elements = details_div.find_all('li')
                if li_elements:
                    artista = li_elements[0].text.strip().replace(",", "")
                    # Guardar otros metadatos si existen
                    for i, li in enumerate(li_elements[1:], 1):
                        metadata[f'detalle_{i}'] = li.text.strip()
            
            # Extraer URL de la imagen
            img_tag = soup.find('a', {'data-fancybox': 'gallery'})
            img_url = None
            if img_tag and 'href' in img_tag.attrs:
                img_url = img_tag['href']
            
            if not img_url:
                return None
            
            return ObraInfo(
                titulo=titulo,
                artista=artista,
                url_imagen=img_url,
                metadata=metadata if metadata else None,
                obra_id=obra_id
            )
            
        except Exception as e:
            self.logger.error(f"Error al parsear HTML de obra {obra_id}: {e}")
            return None
