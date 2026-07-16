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

- `main.py`: lanzador principal que ejecuta la aplicación en consola.
- `app_streamlit.py`: interfaz web interactiva con Streamlit.
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

### Opción 1: Interfaz web (Streamlit) - Recomendado

```bash
streamlit run app_streamlit.py
```

Esta interfaz proporciona una experiencia visual completa:

- Subir imagen mediante interfaz gráfica
- Ajustar parámetros en tiempo real (cantidad de colores, brillo, saturación, tamaño)
- Vista previa inmediata de resultados
- Comparativa lado a lado entre imagen original y editada
- Descargar resultados (imagen procesada, comparativa, paleta visual)

### Opción 2: Script de consola

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

## Refactorización y arquitectura

El módulo de análisis fue reorganizado para reducir el acoplamiento y facilitar la reutilización del código:

- El constructor ya no obliga a recibir una ruta de imagen al instanciar la clase.
- Se incorporaron métodos explícitos como `cargar_imagen()` y `cargar_imagen_desde_pil()` para reutilizar la misma instancia con imágenes nuevas.
- La lógica de extracción de colores y de dibujo de paletas quedó separada en métodos más pequeños y con responsabilidades claras.
- El flujo sigue siendo compatible con la consola y con la interfaz Streamlit.

## Características de la interfaz Streamlit

### Panel de configuración (Sidebar)

**Extracción de colores:**
- Controles para seleccionar cantidad de colores (1-8)
- Botones para analizar imagen y limpiar resultados

**Paleta alternativa:**
- Opciones de paleta: Complementaria, Análoga o Triádica

**Ajustes de imagen:**
- **Brillo**: de 0.1 (muy oscuro) a 3.0 (muy claro)
- **Saturación**: de 0 (escala de grises) a 3.0 (altamente saturado)
- **Tamaño**: de 10% a 200% del tamaño original

### Visualización de resultados

- Imagen original + paleta dominante
- Colores extraídos con información de HEX, temperatura y brillo
- Paleta alternativa seleccionada
- Imagen procesada con todos los ajustes aplicados
- Comparativa visual original vs. procesada
- Descarga de resultados en formato PNG


