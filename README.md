# ArtExtractor

Sistema modular para extraer imágenes de obras de arte desde múltiples fuentes de datos.

## Descripción

Este proyecto permite descargar imágenes de obras de arte desde diferentes museos y fuentes de datos. Actualmente soporta:

- **Museo Nacional de Bellas Artes de Argentina** (https://www.bellasartes.gob.ar/)

El sistema está diseñado de forma modular, permitiendo agregar fácilmente nuevos extractores para otras fuentes de datos.

## Características

- ✅ **Arquitectura modular**: Fácil agregar nuevos orígenes de datos
- ✅ **Extracción automática**: Descarga y organiza obras de arte
- ✅ **Organización inteligente**: Organiza por artista automáticamente
- ✅ **Manejo robusto de errores**: Captura y registra errores de forma segura
- ✅ **Logging detallado**: Sistema de logging profesional
- ✅ **Sanitización de archivos**: Limpia caracteres inválidos automáticamente
- ✅ **Argumentos CLI**: Configuración flexible desde línea de comandos
- ✅ **Delay configurable**: Respeta tiempos de espera entre peticiones
- ✅ **Resumen estadístico**: Muestra estadísticas al finalizar

## Estructura del Proyecto

```
ArtExtractor/
├── main.py                 # Punto de entrada principal
├── config.py              # Configuración global
├── requirements.txt       # Dependencias
├── extractors/            # Módulo de extractores
│   ├── __init__.py
│   ├── base.py           # Clase base abstracta para extractores
│   └── bellasartes.py    # Extractor del Museo de Bellas Artes
├── utils/                 # Utilidades comunes
│   ├── __init__.py
│   ├── file_utils.py     # Utilidades para archivos
│   └── network_utils.py  # Utilidades de red
└── imagenes_obras/        # Directorio de salida (generado)
```

## Requisitos

- Python 3.7 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clona o descarga este repositorio

2. Crea un entorno virtual (recomendado):
```bash
python3 -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Uso básico

Extraer del Museo de Bellas Artes con valores por defecto (IDs 0-2000):
```bash
python main.py --source bellasartes
```

O simplemente (bellasartes es el valor por defecto):
```bash
python main.py
```

### Uso avanzado

Especificar rango de IDs:
```bash
python main.py --source bellasartes --start 100 --end 200
```

Ajustar delay y directorio de salida:
```bash
python main.py --source bellasartes --start 0 --end 100 --delay 2 --output mi_carpeta
```

Modo verbose (más información):
```bash
python main.py --source bellasartes --verbose
```

Listar orígenes disponibles:
```bash
python main.py --list-sources
```

### Opciones disponibles

- `--source` o `-s`: Origen de datos (por defecto: bellasartes)
- `--start`: ID inicial de obra a procesar (por defecto: 0)
- `--end`: ID final de obra a procesar (por defecto: 2000)
- `--delay`: Segundos de espera entre peticiones (por defecto: 1.0)
- `--output` o `-o`: Directorio donde guardar las imágenes (por defecto: imagenes_obras)
- `--verbose` o `-v`: Activa modo verbose para más información de debug
- `--list-sources`: Lista los orígenes de datos disponibles

## Estructura de salida

Las imágenes se guardan organizadas por artista:

```
imagenes_obras/
├── Picasso Pablo/
│   ├── Figura.jpg
│   ├── Le bain (El baño).jpg
│   └── ...
├── Pettoruti Emilio/
│   └── Arlequín.jpg
└── ...
```

## Agregar nuevos extractores

El sistema está diseñado para facilitar la adición de nuevos orígenes de datos. Para agregar un nuevo extractor:

1. **Crea un nuevo archivo** en `extractors/` (ej: `museo_nuevo.py`)

2. **Hereda de `BaseExtractor`** e implementa los métodos requeridos:

```python
from extractors.base import BaseExtractor, ObraInfo

class NuevoMuseoExtractor(BaseExtractor):
    BASE_URL = "https://ejemplo.com/obras/"
    
    def get_obra_url(self, obra_id: str) -> str:
        return f"{self.BASE_URL}{obra_id}/"
    
    def extract_obra_info(self, obra_id: str) -> Optional[ObraInfo]:
        # Tu lógica de extracción aquí
        return ObraInfo(
            titulo="Título de la obra",
            artista="Nombre del artista",
            url_imagen="url_de_la_imagen",
            obra_id=obra_id
        )
```

3. **Registra el extractor** en `extractors/__init__.py`:
```python
from .museo_nuevo import NuevoMuseoExtractor
```

4. **Agrega el origen** en `main.py` en la función `get_extractor()`:
```python
if source_lower in ['nuevomuseo', 'nuevo-museo']:
    return NuevoMuseoExtractor(output_dir=output_dir, delay=delay)
```

5. **Actualiza la documentación** en `main.py` y `README.md`

## Arquitectura

### Clase Base (`BaseExtractor`)

Todos los extractores heredan de `BaseExtractor`, que proporciona:

- Gestión de estadísticas de extracción
- Procesamiento de obras (extracción + descarga)
- Manejo de delays entre peticiones
- Resumen de resultados

### Métodos abstractos a implementar

- `extract_obra_info(obra_id)`: Extrae información de una obra
- `get_obra_url(obra_id)`: Construye la URL de una obra

### Utilidades

- **`file_utils`**: Sanitización de nombres, gestión de directorios
- **`network_utils`**: Descarga de imágenes, obtención de HTML

## Mejoras implementadas

- ✅ **Arquitectura modular**: Fácil extensión con nuevos extractores
- ✅ **Clase base abstracta**: Interfaz consistente para todos los extractores
- ✅ **Separación de responsabilidades**: Código organizado en módulos
- ✅ **Manejo robusto de errores**: Captura y registra errores de forma segura
- ✅ **Sanitización**: Limpia caracteres inválidos de nombres de archivos
- ✅ **Logging profesional**: Sistema de logging con niveles
- ✅ **Argumentos CLI**: Configuración flexible desde línea de comandos
- ✅ **Validaciones**: Verifica argumentos y datos antes de procesar

## Visualización de Imágenes

Para visualizar las imágenes descargadas, se recomienda usar visualizadores de imágenes open source:

### Instalación de Visualizadores

Ejecuta el script de instalación:
```bash
./install_viewers.sh
```

O instala manualmente:
```bash
sudo apt install feh nomacs sxiv
```

### Visualizadores Recomendados

1. **feh** - Ligero y rápido, perfecto para navegación rápida
   ```bash
   feh --auto-zoom --recursive imagenes_obras/
   ```

2. **nomacs** - Completo con interfaz moderna
   ```bash
   nomacs imagenes_obras/
   ```

3. **sxiv** - Alternativa ligera
   ```bash
   sxiv -r imagenes_obras/
   ```

### Script Helper

Usa el script helper para abrir automáticamente el mejor visualizador disponible:
```bash
./view_images.sh imagenes_obras
```

O simplemente:
```bash
./view_images.sh
```

## Notas

- El script respeta un delay entre peticiones para no sobrecargar los servidores
- Los nombres de archivos se sanitizan automáticamente para evitar problemas
- Se genera un resumen al finalizar con estadísticas de la extracción
- El proceso puede interrumpirse con Ctrl+C de forma segura
- El código original (`origenes.py`) se mantiene para referencia

## Roadmap y Futuro del Proyecto

Para ver las mejoras planificadas y nuevas funcionalidades, consulta:
- **[ROADMAP.md](ROADMAP.md)**: Plan de desarrollo a corto, mediano y largo plazo
- **[FUTURE_IDEAS.md](FUTURE_IDEAS.md)**: Ideas detalladas y propuestas técnicas

### Próximas Mejoras
- 🗄️ Base de datos SQLite para mejor rendimiento
- ⚡ Descarga paralela con control de rate limiting
- 🌐 Interfaz web con FastAPI
- 🎨 Análisis de imágenes (colores, duplicados, calidad)
- 🖼️ Generador de galerías HTML estáticas
- 📊 Dashboard de estadísticas

## Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Abre un issue para discutir cambios grandes
2. Fork el proyecto
3. Crea una rama para tu feature
4. Envía un pull request

## Licencia

Este proyecto es solo para fines educativos y de investigación personal. Asegúrate de respetar los términos de uso de los sitios web de los museos.
