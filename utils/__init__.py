"""
Módulo de utilidades comunes para los extractores.
"""

from .file_utils import sanitize_filename
from .network_utils import download_image

__all__ = ['sanitize_filename', 'download_image']
