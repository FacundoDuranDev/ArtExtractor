#!/usr/bin/env python3
"""
Punto de entrada principal para el extractor de obras de arte.
Permite elegir entre diferentes orígenes de datos.
"""

import argparse
import sys
import logging
import os

from config import setup_logging, DEFAULT_START_ID, DEFAULT_END_ID, DEFAULT_DELAY, DEFAULT_OUTPUT_DIR
from extractors import BellasArtesExtractor, BaseExtractor

logger = logging.getLogger(__name__)


def get_extractor(source: str, output_dir: str, delay: float, 
                 use_registry: bool = True, check_existing_files: bool = True) -> BaseExtractor:
    """
    Obtiene un extractor según el origen especificado.
    
    Args:
        source: Nombre del origen de datos
        output_dir: Directorio de salida
        delay: Delay entre peticiones
        use_registry: Si es True, usa el sistema de registro
        check_existing_files: Si es True, verifica archivos existentes
        
    Returns:
        Instancia del extractor correspondiente
        
    Raises:
        ValueError: Si el origen no es válido
    """
    source_lower = source.lower()
    
    if source_lower in ['bellasartes', 'bellas-artes', 'museo-bellas-artes', 'mnba']:
        return BellasArtesExtractor(
            output_dir=output_dir, 
            delay=delay,
            use_registry=use_registry,
            check_existing_files=check_existing_files
        )
    else:
        raise ValueError(f"Origen de datos no válido: {source}. Orígenes disponibles: bellasartes")


def list_sources():
    """Lista los orígenes de datos disponibles."""
    sources = {
        'bellasartes': 'Museo Nacional de Bellas Artes de Argentina (https://www.bellasartes.gob.ar/)',
    }
    
    print("\nOrígenes de datos disponibles:")
    print("=" * 60)
    for key, description in sources.items():
        print(f"  {key:20} - {description}")
    print()


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Extractor de obras de arte desde múltiples fuentes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Extraer del Museo de Bellas Artes (valores por defecto)
  python main.py --source bellasartes
  
  # Especificar rango de IDs
  python main.py --source bellasartes --start 100 --end 200
  
  # Ajustar delay y directorio de salida
  python main.py --source bellasartes --start 0 --end 100 --delay 2 --output mi_carpeta
  
  # Modo verbose
  python main.py --source bellasartes --verbose
  
  # Ver estadísticas del registro
  python main.py --show-registry --output imagenes_obras
  
  # Desactivar registro (procesar todo sin verificar duplicados)
  python main.py --source bellasartes --no-registry
  
  # Listar orígenes disponibles
  python main.py --list-sources
        """
    )
    
    parser.add_argument(
        '--source',
        '-s',
        type=str,
        default='bellasartes',
        help='Origen de datos (por defecto: bellasartes). Usa --list-sources para ver opciones'
    )
    
    parser.add_argument(
        '--start',
        type=int,
        default=DEFAULT_START_ID,
        help=f'ID inicial de obra a procesar (por defecto: {DEFAULT_START_ID})'
    )
    
    parser.add_argument(
        '--end',
        type=int,
        default=DEFAULT_END_ID,
        help=f'ID final de obra a procesar (por defecto: {DEFAULT_END_ID})'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=DEFAULT_DELAY,
        help=f'Segundos de espera entre peticiones (por defecto: {DEFAULT_DELAY})'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f'Directorio donde guardar las imágenes (por defecto: {DEFAULT_OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Activa modo verbose (muestra más información de debug)'
    )
    
    parser.add_argument(
        '--list-sources',
        action='store_true',
        help='Lista los orígenes de datos disponibles y sale'
    )
    
    parser.add_argument(
        '--no-registry',
        action='store_true',
        help='Desactiva el sistema de registro (procesa todas las obras sin verificar duplicados)'
    )
    
    parser.add_argument(
        '--no-check-files',
        action='store_true',
        help='No verifica si los archivos ya existen antes de descargar'
    )
    
    parser.add_argument(
        '--show-registry',
        action='store_true',
        help='Muestra estadísticas del registro y sale'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    # Listar orígenes si se solicita
    if args.list_sources:
        list_sources()
        return
    
    # Validar argumentos
    if args.start < 0:
        logger.error("El ID inicial debe ser mayor o igual a 0")
        sys.exit(1)
    
    if args.end < args.start:
        logger.error("El ID final debe ser mayor o igual al ID inicial")
        sys.exit(1)
    
    if args.delay < 0:
        logger.error("El delay debe ser mayor o igual a 0")
        sys.exit(1)
    
    # Mostrar registro si se solicita
    if args.show_registry:
        from utils.registry_utils import ExtractionRegistry
        registry_file = os.path.join(args.output, ".extraction_registry.json")
        registry = ExtractionRegistry(registry_file)
        registry.print_stats()
        return
    
    # Obtener extractor
    try:
        extractor = get_extractor(
            args.source, 
            args.output, 
            args.delay,
            use_registry=not args.no_registry,
            check_existing_files=not args.no_check_files
        )
        logger.info(f"Usando extractor: {extractor.__class__.__name__}")
        logger.info(f"Origen: {args.source}")
        if not args.no_registry:
            logger.info("Sistema de registro: ACTIVADO")
        else:
            logger.info("Sistema de registro: DESACTIVADO")
    except ValueError as e:
        logger.error(str(e))
        logger.info("Usa --list-sources para ver los orígenes disponibles")
        sys.exit(1)
    
    # Ejecutar extracción
    try:
        extractor.extract_range(args.start, args.end)
    except KeyboardInterrupt:
        logger.info("\nProceso interrumpido por el usuario")
        extractor.print_summary()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
