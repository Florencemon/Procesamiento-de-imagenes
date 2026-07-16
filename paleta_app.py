import os
import unicodedata

from PIL import Image, ImageDraw, ImageFont

from analizador_paleta import AnalizadorPaleta
from generador_paleta import GeneradorPaletas
from editor_imagen import EditorImagen
from paleta_exportador import PaletaExportador
from paleta_visualizador import PaletaVisualizador


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
        self.exportador = None
        self.visualizador = PaletaVisualizador()

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
        self.exportador = PaletaExportador("PaletaOriginal")
        self.analizador = AnalizadorPaleta(
            ruta_imagen=self.image_path,
            n_colores=self.cantidad_colores,
        )
        self.analizador.cargar_imagen()
        self.colores = self.analizador.extraer_colores()
        self.analizador.mostrar_resultados()
        self.extension_original = os.path.splitext(self.image_path)[1].lstrip('.') or 'png'
        self._guardar_paleta_originales()

    def _guardar_paleta_originales(self):
        nombre_archivo = self._generar_nombre_archivo(
            prefijo="PaletaOriginal",
            nombre_original=self.image_path,
            cantidad_colores=self.cantidad_colores,
            extension=self.extension_original
        )
        ruta_salida = self.exportador.guardar(
            self.visualizador.crear_paleta_visual(self.colores),
            nombre_archivo
        )
        print(f"Paleta original guardada como: {os.path.basename(ruta_salida)}")

        nombre_archivo_img = self._generar_nombre_archivo(
            prefijo="PaletaOriginalFoto",
            nombre_original=self.image_path,
            cantidad_colores=self.cantidad_colores,
            extension=self.extension_original
        )
        ruta_salida_img = self.exportador.guardar(
            self.visualizador.crear_paleta_original(Image.open(self.image_path), self.colores),
            nombre_archivo_img
        )
        print(f"Imagen original con recuadros guardada como: {os.path.basename(ruta_salida_img)}")

    def _generar_y_guardar_paletas(self):
        """Genera todas las paletas alternativas y las guarda en disco."""
        exportador_guardadas = PaletaExportador("PaletasGuardadas")
        generador = GeneradorPaletas(self.colores)
        self.paletas = generador.generar_paletas()

        img_original = Image.open(self.image_path)
        ancho_max = img_original.width if img_original.width > 400 else 800

        for nombre, lista_colores in self.paletas.items():
            num_colores = len(lista_colores["colores"])
            ancho_por_color = max(80, min(150, ancho_max // num_colores))
            paleta = self.visualizador.crear_paleta_visual(lista_colores["colores"], ancho_por_color=ancho_por_color)

            nombre_archivo = self._generar_nombre_archivo(
                prefijo="PaletaGuardada",
                nombre_paleta=nombre,
                cantidad_colores=self.cantidad_colores,
                nombre_original=self.image_path,
                extension=self.extension_original
            )
            ruta_salida = exportador_guardadas.guardar(paleta, nombre_archivo)
            print(f"Paleta guardada como: {os.path.basename(ruta_salida)}")

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

        exportador_resultado = PaletaExportador("ImagenResultado")
        ruta_salida = exportador_resultado.guardar(self.imagen_editada, self.nombre_archivo)
        print(f"Imagen editada guardada como: {os.path.basename(ruta_salida)}")

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
        imagenes_redimensionadas = self._redimensionar_imagenes_comparativa(imagen_original)
        imagen_comparativa = self._crear_canvas_comparativo(imagenes_redimensionadas)
        self._agregar_texto_comparativa(imagen_comparativa, imagenes_redimensionadas[0].height)
        self._guardar_comparativa(imagen_comparativa)

    def _redimensionar_imagenes_comparativa(self, imagen_original):
        altura_comparativa = min(imagen_original.height, self.imagen_editada.height)
        imagen_original_redimensionada = imagen_original.resize(
            (int(imagen_original.width * altura_comparativa / imagen_original.height), altura_comparativa)
        )
        imagen_editada_redimensionada = self.imagen_editada.resize(
            (int(self.imagen_editada.width * altura_comparativa / self.imagen_editada.height), altura_comparativa)
        )
        return imagen_original_redimensionada, imagen_editada_redimensionada

    def _crear_canvas_comparativo(self, imagenes_redimensionadas):
        imagen_original_redimensionada, imagen_editada_redimensionada = imagenes_redimensionadas
        margen = 30
        espacio_texto = 100
        ancho_total = imagen_original_redimensionada.width + margen + imagen_editada_redimensionada.width
        alto_total = imagen_original_redimensionada.height + espacio_texto

        imagen_comparativa = Image.new("RGB", (ancho_total, alto_total), "white")
        imagen_comparativa.paste(imagen_original_redimensionada, (0, 0))
        imagen_comparativa.paste(imagen_editada_redimensionada, (imagen_original_redimensionada.width + margen, 0))
        return imagen_comparativa

    def _agregar_texto_comparativa(self, imagen_comparativa, altura_imagen):
        draw_comparativa = ImageDraw.Draw(imagen_comparativa)
        font_comparativa = self._obtener_fuente_comparativa()
        texto_info = f"Paleta: {self.nombre_archivo.split('_')[0]} | Cantidad de colores: {self.cantidad_colores}"
        draw_comparativa.text((10, altura_imagen + 20), texto_info, fill="black", font=font_comparativa)

    def _obtener_fuente_comparativa(self):
        try:
            return ImageFont.truetype("arial.ttf", 32)
        except IOError:
            return ImageFont.load_default()

    def _guardar_comparativa(self, imagen_comparativa):
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
