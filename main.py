from PIL import Image, ImageDraw, ImageFont
import random
import string
import os
from datetime import datetime


from analizador_paleta import AnalizadorPaleta
from generador_paleta import GeneradorPaletas
from editor_imagen import EditorImagen


# Función para generar un nombre de archivo aleatorio
# creimos que era buena idea reutilizar esa función y modificarla para que admita un nombre más descriptivo: fecha y hora
def generar_nombre_aleatorio(prefijo="", extension="png"):
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")

    if prefijo:
        return f"{prefijo}_{fecha_hora}.{extension}"

    return f"{fecha_hora}.{extension}"


# Pedir datos al usuario
image_path = input("Ingrese la ruta de la imagen: ")
cantidad_colores = int(input("¿Cuántos colores desea extraer?: "))

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

nombre_archivo = generar_nombre_aleatorio()

ruta_salida = os.path.join(
    "PaletaOriginal",
    nombre_archivo
)

analizador.obtener_paleta_visual().save(ruta_salida)



print(f"Paleta original guardada como: {nombre_archivo}")

# =====================================================
# GENERAR PALETAS
# =====================================================

generador = GeneradorPaletas(colores)

paletas = generador.generar_paletas()

for nombre, lista_colores in paletas.items():

    ancho = 100 * len(lista_colores["colores"])
    alto = 150

    paleta = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(paleta)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    draw.text((10, 10), nombre, fill="black", font=font)

    for i, color in enumerate(lista_colores["colores"]):
        x0 = i * 100
        x1 = x0 + 100
        draw.rectangle([x0, 50, x1, 150], fill=color)

    nombre_archivo = generar_nombre_aleatorio()

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

nombre_archivo = generar_nombre_aleatorio()

ruta_salida = os.path.join(
    "ImagenResultado",
    nombre_archivo
)

imagen_editada.save(ruta_salida)



print(f"Imagen editada guardada como: {nombre_archivo}")