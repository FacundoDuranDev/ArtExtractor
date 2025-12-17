"""
Clase base abstracta para extractores de obras de arte.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class ObraInfo:
    """Información de una obra de arte."""
    titulo: str
    artista: Optional[str] = None
    url_imagen: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    obra_id: Optional[str] = None


@dataclass
class ExtractionStats:
    """Estadísticas de una extracción."""
    obras_encontradas: int = 0
    obras_descargadas: int = 0
    obras_fallidas: int = 0
    total_procesado: int = 0


class BaseExtractor(ABC):
    """
    Clase base abstracta para extractores de obras de arte.
    
    Todos los extractores deben heredar de esta clase e implementar
    los métodos abstractos.
    """
    
    def __init__(self, output_dir: str = "imagenes_obras", delay: float = 1.0, 
                 use_registry: bool = True, check_existing_files: bool = True):
        """
        Inicializa el extractor.
        
        Args:
            output_dir: Directorio donde guardar las imágenes
            delay: Segundos de espera entre peticiones
            use_registry: Si es True, usa el sistema de registro para evitar duplicados
            check_existing_files: Si es True, verifica si el archivo ya existe antes de descargar
        """
        self.output_dir = output_dir
        self.delay = delay
        self.stats = ExtractionStats()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.use_registry = use_registry
        self.check_existing_files = check_existing_files
        
        # Inicializar registro si está habilitado
        if self.use_registry:
            from utils.registry_utils import ExtractionRegistry
            registry_file = os.path.join(output_dir, ".extraction_registry.json")
            self.registry = ExtractionRegistry(registry_file)
        else:
            self.registry = None
    
    @abstractmethod
    def extract_obra_info(self, obra_id: str) -> Optional[ObraInfo]:
        """
        Extrae información de una obra específica.
        
        Args:
            obra_id: Identificador único de la obra
            
        Returns:
            ObraInfo con la información de la obra, o None si no se encuentra
        """
        pass
    
    @abstractmethod
    def get_obra_url(self, obra_id: str) -> str:
        """
        Construye la URL de una obra.
        
        Args:
            obra_id: Identificador único de la obra
            
        Returns:
            URL completa de la obra
        """
        pass
    
    def download_obra(self, obra_info: ObraInfo) -> bool:
        """
        Descarga la imagen de una obra.
        
        Args:
            obra_info: Información de la obra a descargar
            
        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        if not obra_info.url_imagen:
            self.logger.warning(f"No hay URL de imagen para {obra_info.titulo}")
            return False
        
        from utils.file_utils import get_save_path
        from utils.network_utils import download_image
        
        # Construir ruta de guardado
        save_path = get_save_path(
            base_dir=self.output_dir,
            subdir=obra_info.artista,
            filename=obra_info.titulo,
            extension="jpg"
        )
        
        # Verificar si el archivo ya existe
        if self.check_existing_files and os.path.exists(save_path):
            self.logger.debug(f"Archivo ya existe, omitiendo descarga: {save_path}")
            # Registrar en el registro si está habilitado
            if self.registry and obra_info.obra_id:
                self.registry.register_obra(
                    obra_info.obra_id,
                    'descargado',
                    titulo=obra_info.titulo,
                    artista=obra_info.artista,
                    file_path=save_path
                )
            return True
        
        # Descargar imagen
        base_url = self.get_base_image_url()
        success = download_image(obra_info.url_imagen, base_url, save_path)
        
        # Registrar en el registro si está habilitado
        if self.registry and obra_info.obra_id:
            if success:
                self.registry.register_obra(
                    obra_info.obra_id,
                    'descargado',
                    titulo=obra_info.titulo,
                    artista=obra_info.artista,
                    file_path=save_path
                )
            else:
                self.registry.register_obra(
                    obra_info.obra_id,
                    'fallido',
                    titulo=obra_info.titulo,
                    artista=obra_info.artista,
                    error="Error al descargar imagen"
                )
        
        return success
    
    def get_base_image_url(self) -> Optional[str]:
        """
        Obtiene la URL base para construir URLs de imágenes.
        
        Returns:
            URL base o None si no aplica
        """
        return None
    
    def process_obra(self, obra_id: str) -> bool:
        """
        Procesa una obra completa: extrae información y descarga imagen.
        
        Args:
            obra_id: Identificador único de la obra
            
        Returns:
            True si el proceso fue exitoso, False en caso contrario
        """
        # Verificar si ya fue procesada (si el registro está habilitado)
        if self.registry and self.registry.is_processed(obra_id, check_file=self.check_existing_files):
            status = self.registry.get_status(obra_id)
            self.logger.debug(f"Obra {obra_id} ya procesada (estado: {status}), omitiendo")
            # Actualizar estadísticas según el estado registrado
            if status == 'descargado':
                self.stats.obras_encontradas += 1
                self.stats.obras_descargadas += 1
            elif status == 'encontrado':
                self.stats.obras_encontradas += 1
            return status == 'descargado'
        
        try:
            # Extraer información
            obra_info = self.extract_obra_info(obra_id)
            
            if not obra_info:
                # Registrar como no encontrada
                if self.registry:
                    self.registry.register_obra(obra_id, 'no_encontrado')
                return False
            
            self.stats.obras_encontradas += 1
            self.logger.info(f"Obra encontrada [{obra_id}]: {obra_info.titulo} - {obra_info.artista or 'Sin artista'}")
            
            # Registrar como encontrada (antes de intentar descargar)
            if self.registry:
                self.registry.register_obra(
                    obra_id,
                    'encontrado',
                    titulo=obra_info.titulo,
                    artista=obra_info.artista
                )
            
            # Descargar imagen
            if self.download_obra(obra_info):
                self.stats.obras_descargadas += 1
                self.logger.info(f"  ✓ Imagen descargada exitosamente")
                return True
            else:
                self.stats.obras_fallidas += 1
                self.logger.warning(f"  ✗ Error al descargar imagen")
                return False
                
        except Exception as e:
            self.stats.obras_fallidas += 1
            self.logger.error(f"Error procesando obra {obra_id}: {e}")
            # Registrar error
            if self.registry:
                self.registry.register_obra(obra_id, 'fallido', error=str(e))
            return False
    
    def extract_range(self, start_id: int, end_id: int) -> ExtractionStats:
        """
        Extrae obras en un rango de IDs.
        
        Args:
            start_id: ID inicial
            end_id: ID final
            
        Returns:
            Estadísticas de la extracción
        """
        import time
        
        self.logger.info(f"Iniciando extracción desde ID {start_id} hasta {end_id}")
        self.logger.info(f"Delay entre peticiones: {self.delay} segundos")
        self.logger.info(f"Directorio de salida: {self.output_dir}")
        
        # Reiniciar estadísticas
        self.stats = ExtractionStats()
        
        for obra_id in range(start_id, end_id + 1):
            obra_id_str = str(obra_id)
            self.stats.total_procesado += 1
            
            self.process_obra(obra_id_str)
            
            # Aplicar delay entre peticiones (excepto en la última)
            if obra_id < end_id:
                time.sleep(self.delay)
        
        self.print_summary()
        return self.stats
    
    def print_summary(self):
        """Imprime un resumen de la extracción."""
        self.logger.info("=" * 60)
        self.logger.info("RESUMEN DE EXTRACCIÓN")
        self.logger.info("=" * 60)
        self.logger.info(f"Obras encontradas: {self.stats.obras_encontradas}")
        self.logger.info(f"Obras descargadas exitosamente: {self.stats.obras_descargadas}")
        self.logger.info(f"Obras con errores: {self.stats.obras_fallidas}")
        self.logger.info(f"Total procesado: {self.stats.total_procesado}")
        
        # Mostrar estadísticas del registro si está habilitado
        if self.registry:
            self.registry.print_stats()
