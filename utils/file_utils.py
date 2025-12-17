"""
Utilidades para manejo de archivos.
"""

import re
import os
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres inválidos.
    
    Args:
        filename: Nombre de archivo a sanitizar
        
    Returns:
        Nombre de archivo sanitizado
    """
    if not filename:
        return "sin_nombre"
    
    # Reemplazar caracteres inválidos por guiones bajos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Eliminar espacios múltiples y reemplazar por uno solo
    filename = re.sub(r'\s+', ' ', filename)
    # Eliminar espacios al inicio y final
    filename = filename.strip()
    # Limitar longitud (máximo 200 caracteres para evitar problemas)
    if len(filename) > 200:
        filename = filename[:200]
    # Si queda vacío después de sanitizar, usar nombre por defecto
    if not filename:
        filename = "sin_nombre"
    
    return filename


def ensure_directory(path: str) -> None:
    """
    Asegura que un directorio exista, creándolo si es necesario.
    
    Args:
        path: Ruta del directorio
    """
    os.makedirs(path, exist_ok=True)


def get_save_path(base_dir: str, subdir: Optional[str], filename: str, extension: str = "jpg") -> str:
    """
    Construye una ruta completa para guardar un archivo.
    
    Args:
        base_dir: Directorio base
        subdir: Subdirectorio (opcional, puede ser None)
        filename: Nombre del archivo
        extension: Extensión del archivo (sin punto)
        
    Returns:
        Ruta completa del archivo
    """
    if subdir:
        dir_path = os.path.join(base_dir, sanitize_filename(subdir))
    else:
        dir_path = base_dir
    
    ensure_directory(dir_path)
    
    sanitized_filename = sanitize_filename(filename)
    if not sanitized_filename.endswith(f'.{extension}'):
        sanitized_filename = f"{sanitized_filename}.{extension}"
    
    return os.path.join(dir_path, sanitized_filename)
