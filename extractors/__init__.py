"""
Módulo de extractores para diferentes fuentes de datos.
"""

from .base import BaseExtractor
from .bellasartes import BellasArtesExtractor

__all__ = ['BaseExtractor', 'BellasArtesExtractor']
