## Integrantes:
- Castaño Alma
- Castelao Bravo María del Mar
- Chirino Florencia

## Materia: Procesamiento digital de Imágenes
## Profesor: Juan Ignacio Bonini  
## IFTS 18
### JUNIO 2026

# Procesador de Paletas de Color

Esta aplicación extrae los colores dominantes de una imagen y genera varias paletas alternativas.
También guarda versiones visuales de la paleta original y una imagen comparativa entre la foto original y la foto con la paleta aplicada.

## Qué hace

- Carga una imagen de entrada.
- Extrae los colores dominantes usando `KMeans`.
- Muestra información de cada color (HEX, temperatura, brillo).
- Genera y guarda una paleta visual de los colores extraídos.
- Crea variaciones de paletas:
  - Complementaria
  - Análoga
  - Triádica
- Aplica la paleta seleccionada a la imagen original.
- Genera una imagen comparativa con la versión original y la imagen editada.

## Estructura principal

- `main.py`: lanzador principal que ejecuta la aplicación.
- `paleta_app.py`: clase principal que coordina el flujo de trabajo.
- `analizador_paleta.py`: carga la imagen y extrae colores dominantes.
- `generador_paleta.py`: crea paletas alternativas basadas en tonos.
- `editor_imagen.py`: aplica los nuevos colores a la imagen.
- `color.py`: utilidades para convertir colores y calcular brillo/temperatura.

## Requisitos

Instalar dependencias con:

```bash
pip install -r requirements.txt
```

## Uso

Ejecutar el script principal:

```bash
python main.py
```

La aplicación preguntará por:

1. La ruta de la imagen.
2. La cantidad de colores a extraer (entre 1 y 8).
3. La paleta a aplicar (complementaria, análoga o triádica).

Los resultados se guardan en las carpetas:

- `PaletaOriginal/`
- `PaletasGuardadas/`
- `ImagenResultado/`


