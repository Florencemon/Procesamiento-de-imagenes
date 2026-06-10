from PIL import Image, ImageDraw, ImageFont
import random
import string
import os
import unicodedata
from datetime import datetime


from analizador_paleta import AnalizadorPaleta
from generador_paleta import GeneradorPaletas
from editor_imagen import EditorImagen
from color import Color


def _normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.replace(" ", "_")

    return "".join(
        ch for ch in texto
        if ch.isalnum() or ch in "-_"
    )


def generar_nombre_archivo(nombre_paleta="", cantidad_colores="", nombre_original="", prefijo="", extension="png"):
    """Genera nombre con formato: [prefijo-]Paleta_NcoloresNombre_original.ext"""
    partes = []

    if prefijo:
        partes.append(_normalizar_texto(prefijo))

    if nombre_paleta:
        partes.append(_normalizar_texto(nombre_paleta))

    if cantidad_colores:
        partes.append(f"{cantidad_colores}colores")

    if nombre_original:
        nombre_base = os.path.splitext(
            os.path.basename(nombre_original)
        )[0]
        partes.append(_normalizar_texto(nombre_base))

    return f"{'_'.join(partes)}.{extension}"


# Pedir datos al usuario
image_path = None
while not image_path:
    ruta = input("Ingrese la ruta de la imagen: ").strip()
    if os.path.isfile(ruta):
        image_path = ruta
    else:
        print(f"ERROR!!! El archivo '{ruta}' no existe. Intente de nuevo.")

cantidad_colores = None
while not cantidad_colores:
    try:
        valor = int(input("¿Cuántos colores desea extraer?: "))
        if valor <= 0:
            print("ERROR!!! Debe ingresar un número mayor a 0.")
        elif valor > 8:
            print("ERROR!!! El máximo de colores es 8.")
        else:
            cantidad_colores = valor
    except ValueError:
        print("ERROR!!! Ingrese un número válido.")

# =====================================================
# ANALIZAR IMAGEN
# =====================================================

analizador = AnalizadorPaleta(
    image_path,
    n_colores=cantidad_colores
)

analizador.cargar_imagen()

colores = analizador.extraer_colores()

analizador.mostrar_resultados()

'''nombre_archivo = generar_nombre_aleatorio()
analizador.obtener_paleta_visual().save(nombre_archivo)'''

extension_original = os.path.splitext(image_path)[1].lstrip('.') or 'png'
nombre_archivo = generar_nombre_archivo(
    prefijo="PaletaOriginal",
    nombre_original=image_path,
    cantidad_colores=cantidad_colores,
    extension=extension_original
)

ruta_salida = os.path.join(
    "PaletaOriginal",
    nombre_archivo
)

os.makedirs("PaletaOriginal", exist_ok=True)

# Guardar la paleta visual como antes (no reemplazar)
analizador.obtener_paleta_visual().save(ruta_salida)
print(f"Paleta original guardada como: {nombre_archivo}")

# Además guardar la imagen original con recuadros de color (archivo distinto)
nombre_archivo_img = generar_nombre_archivo(
    prefijo="PaletaOriginalFoto",
    nombre_original=image_path,
    cantidad_colores=cantidad_colores,
    extension=extension_original
)
ruta_salida_img = os.path.join(
    "PaletaOriginal",
    nombre_archivo_img
)
analizador.obtener_paleta_original().save(ruta_salida_img)
print(f"Imagen original con recuadros guardada como: {nombre_archivo_img}")

# =====================================================
# GENERAR PALETAS
# =====================================================

generador = GeneradorPaletas(colores)

paletas = generador.generar_paletas()

for nombre, lista_colores in paletas.items():

    ancho = 150 * len(lista_colores["colores"])
    alto = 280

    paleta = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(paleta)

    try:
        font_grande = ImageFont.truetype("arial.ttf", 20)
        font_pequena = ImageFont.truetype("arial.ttf", 13)
    except IOError:
        font_grande = ImageFont.load_default()
        font_pequena = ImageFont.load_default()

    # Dibujar título con la paleta
    draw.text((10, 10), nombre, fill="black", font=font_grande)

    for i, color in enumerate(lista_colores["colores"]):
        x0 = i * 150
        x1 = x0 + 150
        
        # Rectángulo de color
        draw.rectangle([x0 + 10, 50, x1 - 10, 160], fill=color)
        
        # Obtener información del color
        color_obj = Color(color)
        hex_color = color_obj.rgb_to_hex()
        temperatura = color_obj.clasificar_temperatura()
        brillo = color_obj.clasificar_brillo()
        
        # Dibujar información debajo
        text_y = 170
        draw.text((x0 + 15, text_y), hex_color, fill="black", font=font_grande)
        draw.text((x0 + 15, text_y + 28), f"Temp: {temperatura}", fill="black", font=font_pequena)
        draw.text((x0 + 15, text_y + 48), f"Brillo: {brillo}", fill="black", font=font_pequena)

    extension_original = os.path.splitext(image_path)[1].lstrip('.') or 'png'
    nombre_archivo = generar_nombre_archivo(
        prefijo="PaletaGuardada",
        nombre_paleta=nombre,
        cantidad_colores=cantidad_colores,
        nombre_original=image_path,
        extension=extension_original
    )

    ruta_salida = os.path.join(
        "PaletasGuardadas",
        nombre_archivo
    )

    paleta.save(ruta_salida)

    print(f"Paleta guardada como: {nombre_archivo}")

# =====================================================
# APLICAR PALETA A LA IMAGEN
# =====================================================

opcion = input(
    "\n¿Qué paleta desea aplicar?\n"
    "1 - Complementaria\n"
    "2 - Análoga\n"
    "3 - Triádica\n"
    "Opción: "
)

if opcion == "1":
    nombre_paleta = "Complementaria"
elif opcion == "2":
    nombre_paleta = "Análoga"
elif opcion == "3":
    nombre_paleta = "Triádica"
else:
    print("Opción inválida")
    exit()

imagen = Image.open(image_path)

editor = EditorImagen(imagen)

nuevos_colores = paletas[nombre_paleta]["colores"][:len(colores)]

imagen_editada = editor.aplicar_paleta(
    colores,
    nuevos_colores
)

extension_original = os.path.splitext(image_path)[1].lstrip('.') or 'png'
nombre_archivo = generar_nombre_archivo(
    nombre_paleta=nombre_paleta,
    cantidad_colores=cantidad_colores,
    nombre_original=image_path,
    extension=extension_original
)

ruta_salida = os.path.join(
    "ImagenResultado",
    nombre_archivo
)

imagen_editada.save(ruta_salida)

print(f"Imagen editada guardada como: {nombre_archivo}")

# =====================================================
# CREAR IMAGEN COMPARATIVA
# =====================================================

# Redimensionar imágenes para que tengan la misma altura
altura_comparativa = min(imagen.height, imagen_editada.height)
imagen_original_redimensionada = imagen.resize((int(imagen.width * altura_comparativa / imagen.height), altura_comparativa))
imagen_editada_redimensionada = imagen_editada.resize((int(imagen_editada.width * altura_comparativa / imagen_editada.height), altura_comparativa))

# Margen blanco entre las imágenes
margen = 30

# Crear imagen compuesta con espacio para texto
espacio_texto = 100
ancho_total = imagen_original_redimensionada.width + margen + imagen_editada_redimensionada.width
alto_total = altura_comparativa + espacio_texto

imagen_comparativa = Image.new("RGB", (ancho_total, alto_total), "white")

# Pegar imágenes lado a lado con margen
imagen_comparativa.paste(imagen_original_redimensionada, (0, 0))
imagen_comparativa.paste(imagen_editada_redimensionada, (imagen_original_redimensionada.width + margen, 0))

# Agregar texto de información
draw_comparativa = ImageDraw.Draw(imagen_comparativa)
try:
    font_comparativa = ImageFont.truetype("arial.ttf", 32)
except IOError:
    font_comparativa = ImageFont.load_default()

texto_info = f"Paleta: {nombre_paleta} | Cantidad de colores: {cantidad_colores}"
draw_comparativa.text((10, altura_comparativa + 20), texto_info, fill="black", font=font_comparativa)

# Guardar imagen comparativa
nombre_comparativa = f"COMPARATIVA_{nombre_archivo}"
ruta_comparativa = os.path.join(
    "ImagenResultado",
    nombre_comparativa
)

imagen_comparativa.save(ruta_comparativa)

print(f"Imagen comparativa guardada como: {nombre_comparativa}")