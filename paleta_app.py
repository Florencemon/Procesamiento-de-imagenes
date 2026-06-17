import os
import unicodedata

from PIL import Image, ImageDraw, ImageFont

from analizador_paleta import AnalizadorPaleta
from generador_paleta import GeneradorPaletas
from editor_imagen import EditorImagen
from color import Color


class PaletaApp:
    """Clase principal que coordina el flujo de análisis y edición de la paleta."""

    def __init__(self):
        self.image_path = None
        self.cantidad_colores = None
        self.analizador = None
        self.colores = []
        self.paletas = {}
        self.imagen_editada = None
        self.extension_original = "png"
        self.nombre_archivo = ""

    def ejecutar(self):
        """Ejecuta el flujo completo de la aplicación."""
        self._pedir_datos_usuario()
        self._analizar_imagen()
        self._generar_y_guardar_paletas()
        self._aplicar_paleta_seleccionada()
        self._crear_imagen_comparativa()

    def _pedir_datos_usuario(self):
        self.image_path = self._pedir_ruta_imagen()
        self.cantidad_colores = self._pedir_cantidad_colores()

    def _pedir_ruta_imagen(self):
        """Solicita al usuario la ruta de la imagen hasta que ésta exista."""
        ruta = None
        while not ruta:
            valor = input("Ingrese la ruta de la imagen: ").strip()
            if os.path.isfile(valor):
                ruta = valor
            else:
                print(f"ERROR!!! El archivo '{valor}' no existe. Intente de nuevo.")
        return ruta

    def _pedir_cantidad_colores(self):
        """Solicita al usuario la cantidad de colores y valida el valor."""
        cantidad = None
        while cantidad is None:
            try:
                valor = int(input("¿Cuántos colores desea extraer?: "))
                if valor <= 0:
                    print("ERROR!!! Debe ingresar un número mayor a 0.")
                elif valor > 8:
                    print("ERROR!!! El máximo de colores es 8.")
                else:
                    cantidad = valor
            except ValueError:
                print("ERROR!!! Ingrese un número válido.")
        return cantidad

    def _analizar_imagen(self):
        """Carga la imagen, extrae los colores dominantes y guarda los resultados iniciales."""
        self.analizador = AnalizadorPaleta(
            self.image_path,
            n_colores=self.cantidad_colores
        )
        self.analizador.cargar_imagen()
        self.colores = self.analizador.extraer_colores()
        self.analizador.mostrar_resultados()
        self.extension_original = os.path.splitext(self.image_path)[1].lstrip('.') or 'png'
        self._guardar_paleta_originales()

    def _guardar_paleta_originales(self):
        os.makedirs("PaletaOriginal", exist_ok=True)

        nombre_archivo = self._generar_nombre_archivo(
            prefijo="PaletaOriginal",
            nombre_original=self.image_path,
            cantidad_colores=self.cantidad_colores,
            extension=self.extension_original
        )
        ruta_salida = os.path.join("PaletaOriginal", nombre_archivo)
        self.analizador.obtener_paleta_visual().save(ruta_salida)
        print(f"Paleta original guardada como: {nombre_archivo}")

        nombre_archivo_img = self._generar_nombre_archivo(
            prefijo="PaletaOriginalFoto",
            nombre_original=self.image_path,
            cantidad_colores=self.cantidad_colores,
            extension=self.extension_original
        )
        ruta_salida_img = os.path.join("PaletaOriginal", nombre_archivo_img)
        self.analizador.obtener_paleta_original().save(ruta_salida_img)
        print(f"Imagen original con recuadros guardada como: {nombre_archivo_img}")

    def _generar_y_guardar_paletas(self):
        """Genera todas las paletas alternativas y las guarda en disco."""
        os.makedirs("PaletasGuardadas", exist_ok=True)
        generador = GeneradorPaletas(self.colores)
        self.paletas = generador.generar_paletas()

        for nombre, lista_colores in self.paletas.items():
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

            draw.text((10, 10), nombre, fill="black", font=font_grande)

            for i, color in enumerate(lista_colores["colores"]):
                x0 = i * 150
                x1 = x0 + 150
                draw.rectangle([x0 + 10, 50, x1 - 10, 160], fill=color)

                color_obj = Color(color)
                hex_color = color_obj.rgb_to_hex()
                temperatura = color_obj.clasificar_temperatura()
                brillo = color_obj.clasificar_brillo()

                text_y = 170
                draw.text((x0 + 15, text_y), hex_color, fill="black", font=font_grande)
                draw.text((x0 + 15, text_y + 28), f"Temp: {temperatura}", fill="black", font=font_pequena)
                draw.text((x0 + 15, text_y + 48), f"Brillo: {brillo}", fill="black", font=font_pequena)

            nombre_archivo = self._generar_nombre_archivo(
                prefijo="PaletaGuardada",
                nombre_paleta=nombre,
                cantidad_colores=self.cantidad_colores,
                nombre_original=self.image_path,
                extension=self.extension_original
            )
            ruta_salida = os.path.join("PaletasGuardadas", nombre_archivo)
            paleta.save(ruta_salida)
            print(f"Paleta guardada como: {nombre_archivo}")

    def _aplicar_paleta_seleccionada(self):
        """Aplica la paleta elegida por el usuario sobre la imagen original."""
        nombre_paleta = self._seleccionar_paleta()
        if not nombre_paleta:
            print("Opción inválida")
            exit()

        imagen = Image.open(self.image_path)
        editor = EditorImagen(imagen)
        nuevos_colores = self.paletas[nombre_paleta]["colores"][:len(self.colores)]
        self.imagen_editada = editor.aplicar_paleta(self.colores, nuevos_colores)

        self.nombre_archivo = self._generar_nombre_archivo(
            nombre_paleta=nombre_paleta,
            cantidad_colores=self.cantidad_colores,
            nombre_original=self.image_path,
            extension=self.extension_original
        )

        os.makedirs("ImagenResultado", exist_ok=True)
        ruta_salida = os.path.join("ImagenResultado", self.nombre_archivo)
        self.imagen_editada.save(ruta_salida)
        print(f"Imagen editada guardada como: {self.nombre_archivo}")

    def _seleccionar_paleta(self):
        """Muestra el menú de selección de paleta y devuelve el nombre elegido."""
        opcion = input(
            "\n¿Qué paleta desea aplicar?\n"
            "1 - Complementaria\n"
            "2 - Análoga\n"
            "3 - Triádica\n"
            "Opción: "
        )

        if opcion == "1":
            return "Complementaria"
        if opcion == "2":
            return "Análoga"
        if opcion == "3":
            return "Triádica"
        return None

    def _crear_imagen_comparativa(self):
        """Genera una imagen comparativa entre la original y la editada."""
        if self.imagen_editada is None:
            return

        imagen_original = Image.open(self.image_path)
        altura_comparativa = min(imagen_original.height, self.imagen_editada.height)
        imagen_original_redimensionada = imagen_original.resize(
            (int(imagen_original.width * altura_comparativa / imagen_original.height), altura_comparativa)
        )
        imagen_editada_redimensionada = self.imagen_editada.resize(
            (int(self.imagen_editada.width * altura_comparativa / self.imagen_editada.height), altura_comparativa)
        )

        margen = 30
        espacio_texto = 100
        ancho_total = imagen_original_redimensionada.width + margen + imagen_editada_redimensionada.width
        alto_total = altura_comparativa + espacio_texto

        imagen_comparativa = Image.new("RGB", (ancho_total, alto_total), "white")
        imagen_comparativa.paste(imagen_original_redimensionada, (0, 0))
        imagen_comparativa.paste(imagen_editada_redimensionada, (imagen_original_redimensionada.width + margen, 0))

        draw_comparativa = ImageDraw.Draw(imagen_comparativa)
        try:
            font_comparativa = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            font_comparativa = ImageFont.load_default()

        texto_info = f"Paleta: {self.nombre_archivo.split('_')[0]} | Cantidad de colores: {self.cantidad_colores}"
        draw_comparativa.text((10, altura_comparativa + 20), texto_info, fill="black", font=font_comparativa)

        nombre_comparativa = f"COMPARATIVA_{self.nombre_archivo}"
        ruta_comparativa = os.path.join("ImagenResultado", nombre_comparativa)
        imagen_comparativa.save(ruta_comparativa)
        print(f"Imagen comparativa guardada como: {nombre_comparativa}")

    @staticmethod
    def _normalizar_texto(texto):
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", "ignore").decode("ascii")
        texto = texto.replace(" ", "_")
        return "".join(
            ch for ch in texto
            if ch.isalnum() or ch in "-_"
        )

    def _generar_nombre_archivo(self, nombre_paleta="", cantidad_colores="", nombre_original="", prefijo="", extension="png"):
        partes = []
        if prefijo:
            partes.append(self._normalizar_texto(prefijo))
        if nombre_paleta:
            partes.append(self._normalizar_texto(nombre_paleta))
        if cantidad_colores:
            partes.append(f"{cantidad_colores}colores")
        if nombre_original:
            nombre_base = os.path.splitext(os.path.basename(nombre_original))[0]
            partes.append(self._normalizar_texto(nombre_base))
        return f"{'_'.join(partes)}.{extension}"
