"""
Utilidades para el registro de obras procesadas.
"""

import json
import os
import logging
from typing import Dict, Optional, Set
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ExtractionRegistry:
    """
    Registro de obras procesadas para evitar duplicados y permitir reanudar extracciones.
    """
    
    def __init__(self, registry_file: str = ".extraction_registry.json"):
        """
        Inicializa el registro.
        
        Args:
            registry_file: Ruta al archivo de registro (JSON)
        """
        self.registry_file = registry_file
        self.registry: Dict[str, Dict] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Carga el registro desde el archivo."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                logger.debug(f"Registro cargado: {len(self.registry)} obras registradas")
            except Exception as e:
                logger.warning(f"Error al cargar registro: {e}. Iniciando registro vacío.")
                self.registry = {}
        else:
            self.registry = {}
    
    def _save_registry(self) -> None:
        """Guarda el registro en el archivo."""
        try:
            # Asegurar que el directorio existe
            registry_dir = os.path.dirname(self.registry_file)
            if registry_dir and not os.path.exists(registry_dir):
                os.makedirs(registry_dir, exist_ok=True)
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error al guardar registro: {e}")
    
    def register_obra(self, obra_id: str, status: str, 
                     titulo: Optional[str] = None,
                     artista: Optional[str] = None,
                     file_path: Optional[str] = None,
                     error: Optional[str] = None) -> None:
        """
        Registra una obra procesada.
        
        Args:
            obra_id: ID de la obra
            status: Estado ('encontrado', 'descargado', 'fallido', 'no_encontrado')
            titulo: Título de la obra (opcional)
            artista: Artista de la obra (opcional)
            file_path: Ruta del archivo descargado (opcional)
            error: Mensaje de error si hubo (opcional)
        """
        self.registry[obra_id] = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'titulo': titulo,
            'artista': artista,
            'file_path': file_path,
            'error': error
        }
        self._save_registry()
    
    def is_processed(self, obra_id: str, check_file: bool = False) -> bool:
        """
        Verifica si una obra ya fue procesada.
        
        Args:
            obra_id: ID de la obra
            check_file: Si es True, también verifica que el archivo exista
            
        Returns:
            True si la obra ya fue procesada (y el archivo existe si check_file=True)
        """
        if obra_id not in self.registry:
            return False
        
        entry = self.registry[obra_id]
        
        # Si check_file=True, verificar que el archivo exista
        if check_file and entry.get('file_path'):
            if not os.path.exists(entry['file_path']):
                logger.debug(f"Obra {obra_id} registrada pero archivo no existe: {entry['file_path']}")
                return False
        
        # Considerar procesada si está descargada o encontrada
        return entry.get('status') in ('descargado', 'encontrado')
    
    def get_status(self, obra_id: str) -> Optional[str]:
        """
        Obtiene el estado de una obra.
        
        Args:
            obra_id: ID de la obra
            
        Returns:
            Estado de la obra o None si no está registrada
        """
        if obra_id in self.registry:
            return self.registry[obra_id].get('status')
        return None
    
    def get_processed_ids(self, status: Optional[str] = None) -> Set[str]:
        """
        Obtiene el conjunto de IDs procesados.
        
        Args:
            status: Filtrar por estado específico (opcional)
            
        Returns:
            Conjunto de IDs procesados
        """
        if status:
            return {obra_id for obra_id, entry in self.registry.items() 
                   if entry.get('status') == status}
        return set(self.registry.keys())
    
    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas del registro.
        
        Returns:
            Diccionario con conteos por estado
        """
        stats = {
            'total': len(self.registry),
            'descargado': 0,
            'encontrado': 0,
            'fallido': 0,
            'no_encontrado': 0
        }
        
        for entry in self.registry.values():
            status = entry.get('status', 'unknown')
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def print_stats(self) -> None:
        """Imprime estadísticas del registro."""
        stats = self.get_stats()
        logger.info("=" * 60)
        logger.info("ESTADÍSTICAS DEL REGISTRO")
        logger.info("=" * 60)
        logger.info(f"Total de obras registradas: {stats['total']}")
        logger.info(f"  - Descargadas: {stats['descargado']}")
        logger.info(f"  - Encontradas (sin descargar): {stats['encontrado']}")
        logger.info(f"  - Fallidas: {stats['fallido']}")
        logger.info(f"  - No encontradas: {stats['no_encontrado']}")
    
    def clear(self) -> None:
        """Limpia el registro."""
        self.registry = {}
        self._save_registry()
        logger.info("Registro limpiado")
    
    def remove_entry(self, obra_id: str) -> None:
        """
        Elimina una entrada del registro.
        
        Args:
            obra_id: ID de la obra a eliminar
        """
        if obra_id in self.registry:
            del self.registry[obra_id]
            self._save_registry()
            logger.debug(f"Entrada {obra_id} eliminada del registro")
