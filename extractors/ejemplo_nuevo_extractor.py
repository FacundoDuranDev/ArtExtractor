"""
Ejemplo de cómo crear un nuevo extractor.

Este es un archivo de ejemplo que muestra cómo implementar un extractor
para una nueva fuente de datos. Puedes copiarlo y adaptarlo según tus necesidades.
"""

from bs4 import BeautifulSoup
import logging
from typing import Optional

from .base import BaseExtractor, ObraInfo
from utils.network_utils import fetch_html

logger = logging.getLogger(__name__)


class EjemploNuevoExtractor(BaseExtractor):
    """
    Ejemplo de extractor para un nuevo museo o fuente de datos.
    
    Para usar este extractor:
    1. Renombra la clase con el nombre apropiado
    2. Actualiza BASE_URL y BASE_IMAGE_URL según tu fuente
    3. Implementa extract_obra_info() según la estructura HTML de tu fuente
    4. Registra el extractor en extractors/__init__.py
    5. Agrega el origen en main.py en la función get_extractor()
    """
    
    BASE_URL = "https://ejemplo.com/obras/"
    BASE_IMAGE_URL = "https://ejemplo.com/"
    
    def __init__(self, output_dir: str = "imagenes_obras_new", delay: float = 1.0):
        """
        Inicializa el extractor.
        
        Args:
            output_dir: Directorio donde guardar las imágenes
            delay: Segundos de espera entre peticiones
        """
        super().__init__(output_dir, delay)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_obra_url(self, obra_id: str) -> str:
        """
        Construye la URL de una obra.
        
        Args:
            obra_id: ID de la obra
            
        Returns:
            URL completa de la obra
        """
        return f"{self.BASE_URL}{obra_id}/"
    
    def get_base_image_url(self) -> Optional[str]:
        """
        Obtiene la URL base para construir URLs de imágenes.
        
        Returns:
            URL base o None si no aplica
        """
        return self.BASE_IMAGE_URL
    
    def extract_obra_info(self, obra_id: str) -> Optional[ObraInfo]:
        """
        Extrae información de una obra desde el sitio web.
        
        Este método debe adaptarse según la estructura HTML del sitio web
        que quieras extraer. Usa BeautifulSoup para parsear el HTML.
        
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
            
            # ADAPTA ESTA SECCIÓN SEGÚN LA ESTRUCTURA HTML DE TU SITIO WEB
            
            # Ejemplo: Extraer título
            titulo_tag = soup.find('h1')  # Ajusta el selector según tu sitio
            titulo = titulo_tag.text.strip() if titulo_tag else None
            
            if not titulo:
                return None
            
            # Ejemplo: Extraer artista
            # Busca el elemento que contiene el nombre del artista
            artista_tag = soup.find('span', class_='artist')  # Ajusta según tu sitio
            artista = artista_tag.text.strip() if artista_tag else None
            
            # Ejemplo: Extraer URL de imagen
            img_tag = soup.find('img', class_='obra-image')  # Ajusta según tu sitio
            img_url = None
            if img_tag:
                img_url = img_tag.get('src') or img_tag.get('data-src')
            
            if not img_url:
                return None
            
            # Opcional: Extraer metadatos adicionales
            metadata = {}
            # metadata['año'] = soup.find('span', class_='year').text if soup.find('span', class_='year') else None
            # metadata['técnica'] = soup.find('span', class_='technique').text if soup.find('span', class_='technique') else None
            
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
