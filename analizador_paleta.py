from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from sklearn.cluster import KMeans

from color import Color


class AnalizadorPaleta:
    """Analiza una imagen y extrae sus colores dominantes."""

    def __init__(self, ruta_imagen=None, n_colores=5):
        self.ruta_imagen = ruta_imagen
        self.n_colores = n_colores
        self.imagen = None
        self.colores_dominantes = []

    def cargar_imagen(self, ruta_imagen=None):
        """Carga la imagen desde la ruta proporcionada y la convierte a RGB."""
        if ruta_imagen is not None:
            self.ruta_imagen = ruta_imagen
        if not self.ruta_imagen:
            raise ValueError("Debe proporcionar una ruta de imagen.")

        self.imagen = Image.open(self.ruta_imagen).convert("RGB")
        return self.imagen

    def cargar_imagen_desde_pil(self, imagen):
        """Carga una imagen ya abierta desde un objeto PIL."""
        self.imagen = imagen.convert("RGB")
        self.ruta_imagen = None
        return self.imagen

    def extraer_colores(self):
        """Extrae los colores principales usando KMeans sobre los píxeles."""
        self._validar_imagen()
        pixeles = self._obtener_pixeles()
        colores = self._aplicar_kmeans(pixeles)
        self.colores_dominantes = self._normalizar_colores(colores)
        return self.colores_dominantes

    def fusionar_colores_similares(self, tolerancia=60):
        """Elimina colores muy parecidos dentro de la paleta."""
        colores_filtrados = []
        for color in self.colores_dominantes:
            if self._es_color_nuevo(color, colores_filtrados, tolerancia):
                colores_filtrados.append(color)

        self.colores_dominantes = colores_filtrados
        return self.colores_dominantes

    def mostrar_resultados(self, salida=None):
        """Muestra por consola los colores extraídos y sus características."""
        salida = salida or print
        salida("\n🎨 COLORES DOMINANTES:\n")
        for i, color in enumerate(self.colores_dominantes, start=1):
            self._mostrar_color(color, i, salida)

    def obtener_paleta_visual(self, ancho_por_color=150, alto=280):
        """Construye una imagen que muestra cada color y sus datos asociados."""
        from PIL import ImageFont

        ancho = max(1, ancho_por_color * len(self.colores_dominantes))
        paleta = Image.new("RGB", (ancho, alto), "white")
        draw = ImageDraw.Draw(paleta)
        font_grande, font_pequena = self._obtener_fuentes()

        for i, color in enumerate(self.colores_dominantes):
            self._dibujar_color_en_paleta(draw, color, i, ancho_por_color, font_grande, font_pequena)

        return paleta

    def obtener_paleta_original(self, espacio_inferior=240):
        """Devuelve una copia de la imagen original con recuadros de colores superpuestos."""
        original = self.imagen.copy()
        layout = self._preparar_layout(original.size, espacio_inferior)
        return self._dibujar_paleta_original(original, layout)

    def _preparar_layout(self, tamaño, espacio_inferior):
        ancho_original, alto_original = tamaño
        num_colores = len(self.colores_dominantes)
        margen = self._calcular_margen(ancho_original)
        ancho_disponible = ancho_original - (margen * 2)
        alto_disponible = alto_original - (margen * 2) - espacio_inferior
        alto_cuadro = self._calcular_alto_cuadro(alto_disponible, num_colores)
        ancho_cuadro = ancho_disponible
        espacio_entre = max(10, alto_cuadro // 10)
        total_altura = self._calcular_total_altura(num_colores, alto_cuadro, espacio_entre)

        if total_altura > alto_disponible:
            alto_cuadro = self._ajustar_alto_cuadro(alto_disponible, num_colores, espacio_entre)
            total_altura = self._calcular_total_altura(num_colores, alto_cuadro, espacio_entre)

        return {
            "margen": margen,
            "ancho_cuadro": ancho_cuadro,
            "alto_cuadro": alto_cuadro,
            "espacio_entre": espacio_entre,
            "total_altura": total_altura,
            "alto_original": alto_original,
        }

    def _dibujar_paleta_original(self, original, layout):
        paleta = original.copy().filter(ImageFilter.GaussianBlur(radius=12))
        draw = ImageDraw.Draw(paleta)
        font_grande = self._obtener_fuente_tamanio(layout["alto_cuadro"])
        top_start = (layout["alto_original"] - layout["total_altura"]) // 2
        left = layout["margen"]
        border_width = max(3, layout["alto_cuadro"] // 40)

        for i, color in enumerate(self.colores_dominantes):
            self._dibujar_recuadro_color(
                draw,
                color,
                i,
                top_start,
                left,
                layout["ancho_cuadro"],
                layout["alto_cuadro"],
                layout["espacio_entre"],
                border_width,
                font_grande,
            )

        return paleta

    def _validar_imagen(self):
        if self.imagen is None:
            raise ValueError("Primero debe cargar una imagen.")

    def _obtener_pixeles(self):
        img = self.imagen.resize((200, 200))
        pixeles = np.array(img)
        return pixeles.reshape((-1, 3))

    def _aplicar_kmeans(self, pixeles):
        modelo = KMeans(n_clusters=self.n_colores, random_state=42)
        modelo.fit(pixeles)
        return modelo.cluster_centers_

    def _normalizar_colores(self, colores):
        return [tuple(map(int, c)) for c in colores]

    def _es_color_nuevo(self, color, colores_filtrados, tolerancia):
        for existente in colores_filtrados:
            distancia = np.linalg.norm(np.array(color) - np.array(existente))
            if distancia < tolerancia:
                return False
        return True

    def _mostrar_color(self, color, i, salida):
        color_obj = Color(color)
        salida(f"Color {i}")
        salida("HEX:" + color_obj.rgb_to_hex())
        salida("Temperatura:" + color_obj.clasificar_temperatura())
        salida("Brillo:" + color_obj.clasificar_brillo())
        salida("-" * 40)

    def _obtener_fuentes(self):
        from PIL import ImageFont

        try:
            return ImageFont.truetype("arial.ttf", 20), ImageFont.truetype("arial.ttf", 13)
        except IOError:
            return ImageFont.load_default(), ImageFont.load_default()

    def _dibujar_color_en_paleta(self, draw, color, index, ancho_por_color, font_grande, font_pequena):
        x0 = index * ancho_por_color
        x1 = x0 + ancho_por_color
        draw.rectangle([x0 + 10, 10, x1 - 10, 120], fill=color)

        color_obj = Color(color)
        hex_color = color_obj.rgb_to_hex()
        temperatura = color_obj.clasificar_temperatura()
        brillo = color_obj.clasificar_brillo()

        text_y = 130
        draw.text((x0 + 15, text_y), hex_color, fill="black", font=font_grande)
        draw.text((x0 + 15, text_y + 28), f"Temp: {temperatura}", fill="black", font=font_pequena)
        draw.text((x0 + 15, text_y + 48), f"Brillo: {brillo}", fill="black", font=font_pequena)
        draw.text((x0 + 15, text_y + 68), f"Color {index + 1}", fill="black", font=font_pequena)

    def _calcular_margen(self, ancho_original):
        return max(40, min(80, ancho_original // 20))

    def _calcular_alto_cuadro(self, alto_disponible, num_colores):
        return max(60, min(200, alto_disponible // (num_colores + 1)))

    def _ajustar_alto_cuadro(self, alto_disponible, num_colores, espacio_entre):
        return (alto_disponible - (num_colores - 1) * espacio_entre) // num_colores

    def _calcular_total_altura(self, num_colores, alto_cuadro, espacio_entre):
        return num_colores * alto_cuadro + (num_colores - 1) * espacio_entre

    def _obtener_fuente_tamanio(self, alto_cuadro):
        from PIL import ImageFont

        try:
            font_size = max(16, int(alto_cuadro * 0.35))
            return ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            return ImageFont.load_default()

    def _dibujar_recuadro_color(
        self,
        draw,
        color,
        index,
        top_start,
        left,
        ancho_cuadro,
        alto_cuadro,
        espacio_entre,
        border_width,
        font_grande,
    ):
        y0, y1, x0, x1 = self._calcular_bordes(index, top_start, left, ancho_cuadro, alto_cuadro, espacio_entre)
        draw.rectangle([x0, y0, x1, y1], fill=color, outline="white", width=border_width)

        hex_color, text_fill = self._obtener_texto_color(color)
        text_x, text_y = self._calcular_posicion_texto(draw, hex_color, font_grande, x0, x1, y0, y1)
        draw.text((text_x, text_y), hex_color, fill=text_fill, font=font_grande)

    def _calcular_bordes(self, index, top_start, left, ancho_cuadro, alto_cuadro, espacio_entre):
        y0 = top_start + index * (alto_cuadro + espacio_entre)
        y1 = y0 + alto_cuadro
        x0 = left
        x1 = left + ancho_cuadro
        return y0, y1, x0, x1

    def _obtener_texto_color(self, color):
        color_obj = Color(color)
        hex_color = color_obj.rgb_to_hex()
        brillo = color_obj.calcular_brillo()
        text_fill = "black" if brillo > 180 else "white"
        return hex_color, text_fill

    def _calcular_posicion_texto(self, draw, hex_color, font_grande, x0, x1, y0, y1):
        try:
            bbox = draw.textbbox((0, 0), hex_color, font=font_grande)
            texto_ancho = bbox[2] - bbox[0]
            texto_alto = bbox[3] - bbox[1]
        except Exception:
            texto_ancho, texto_alto = 50, 20

        text_x = x0 + ((x1 - x0) - texto_ancho) / 2
        text_y = y0 + ((y1 - y0) - texto_alto) / 2
        return text_x, text_y
#fin
