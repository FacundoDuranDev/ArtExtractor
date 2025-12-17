"""
Configuración global del proyecto.
"""

import logging
import os

# Configuración de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Directorio por defecto para imágenes
DEFAULT_OUTPUT_DIR = "imagenes_obras"

# Delay por defecto entre peticiones (segundos)
DEFAULT_DELAY = 1.0

# Timeout por defecto para peticiones HTTP (segundos)
DEFAULT_TIMEOUT = 30

# Rango por defecto de IDs
DEFAULT_START_ID = 0
DEFAULT_END_ID = 2000


def setup_logging(verbose: bool = False):
    """
    Configura el sistema de logging.
    
    Args:
        verbose: Si es True, activa el nivel DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
