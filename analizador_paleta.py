from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from sklearn.cluster import KMeans

from color import Color

class AnalizadorPaleta:

    def __init__(
        self,
        ruta_imagen,
        n_colores=5
    ):

        self.ruta_imagen = ruta_imagen
        self.n_colores = n_colores

        self.imagen = None
        self.colores_dominantes = []
    # =====================================================
    # 🖼️ CARGAR IMAGEN
    # =====================================================
    def cargar_imagen(self):

        self.imagen = Image.open(
            self.ruta_imagen
        ).convert("RGB")
    # =====================================================
    # 🎨 EXTRAER COLORES DOMINANTES
    # =====================================================
    def extraer_colores(self):

        img = self.imagen.resize((200, 200))
        pixeles = np.array(img)
        pixeles = pixeles.reshape((-1, 3))
        modelo = KMeans(
            n_clusters=self.n_colores,
            random_state=42
        )

        modelo.fit(pixeles)

        colores = modelo.cluster_centers_

        self.colores_dominantes = [
            tuple(map(int, c))
            for c in colores
        ]

        return self.colores_dominantes
    # =====================================================
    # 🌈 FUSIONAR COLORES SIMILARES
    # =====================================================
    def fusionar_colores_similares(
        self,
        tolerancia=60
    ):

        colores_filtrados = []

        for color in self.colores_dominantes:

            agregar = True

            for existente in colores_filtrados:

                distancia = np.linalg.norm(
                    np.array(color)
                    -
                    np.array(existente)
                )

                if distancia < tolerancia:

                    agregar = False
                    break

            if agregar:
                colores_filtrados.append(color)

        self.colores_dominantes = colores_filtrados

        return self.colores_dominantes
    # =====================================================
    # 📊 MOSTRAR RESULTADOS
    # =====================================================
    def mostrar_resultados(self):

        print("\n🎨 COLORES DOMINANTES:\n")

        for i, color in enumerate(
            self.colores_dominantes,
            start=1
        ):

            color_obj = Color(color)

            print(f"Color {i}")
            print("HEX:",color_obj.rgb_to_hex())
            print("Temperatura:",color_obj.clasificar_temperatura())
            print("Brillo:",color_obj.clasificar_brillo())
            print("-" * 40)
    # =====================================================
    # 🟦 MOSTRAR PALETA VISUAL
    # =====================================================
    def obtener_paleta_visual(self):
        from PIL import ImageFont
        
        # Crear una imagen con espacio para colores e información
        ancho = 150 * len(self.colores_dominantes)
        alto = 280
        paleta = Image.new("RGB", (ancho, alto), "white")
        draw = ImageDraw.Draw(paleta)

        try:
            font_grande = ImageFont.truetype("arial.ttf", 20)
            font_pequena = ImageFont.truetype("arial.ttf", 13)
        except IOError:
            font_grande = ImageFont.load_default()
            font_pequena = ImageFont.load_default()

        # Dibujar cada color con información
        for i, color in enumerate(self.colores_dominantes):
            x0 = i * 150
            x1 = x0 + 150
            
            # Rectángulo de color
            draw.rectangle([x0 + 10, 10, x1 - 10, 120], fill=color)
            
            # Obtener información del color
            color_obj = Color(color)
            hex_color = color_obj.rgb_to_hex()
            temperatura = color_obj.clasificar_temperatura()
            brillo = color_obj.clasificar_brillo()
            
            # Dibujar información debajo
            text_y = 130
            draw.text((x0 + 15, text_y), hex_color, fill="black", font=font_grande)
            draw.text((x0 + 15, text_y + 28), f"Temp: {temperatura}", fill="black", font=font_pequena)
            draw.text((x0 + 15, text_y + 48), f"Brillo: {brillo}", fill="black", font=font_pequena)
            
            # Número del color
            draw.text((x0 + 15, text_y + 68), f"Color {i+1}", fill="black", font=font_pequena)

        return paleta

    # =====================================================
    # 🟦 ORIGINAL CON PALETA
    # =====================================================
    def obtener_paleta_original(self, espacio_inferior=240):
        from PIL import ImageFont

        original = self.imagen.copy()
        ancho_original, alto_original = original.size

        num_colores = len(self.colores_dominantes)

        # Caja relativa al ancho de la imagen (centrada)
        ancho_cuadro = int(ancho_original * 0.6)
        espacio_entre = 20
        # Altura de cada recuadro escalable pero limitada
        caja_min = 120
        caja_max = 360
        caja_propuesta = int(alto_original * 0.12)
        alto_cuadro = max(caja_min, min(caja_max, caja_propuesta))

        total_altura = num_colores * alto_cuadro + (num_colores - 1) * espacio_entre

        # Usar la imagen original, aplicar blur y dibujar encima
        paleta = original.copy().filter(ImageFilter.GaussianBlur(radius=12))
        draw = ImageDraw.Draw(paleta)

        try:
            # Fuente grande escalada al tamaño del recuadro
            font_size = max(28, int(alto_cuadro * 0.4))
            font_grande = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font_grande = ImageFont.load_default()

        # Posición inicial para centrar verticalmente
        top_start = (alto_original - total_altura) // 2
        left = (ancho_original - ancho_cuadro) // 2

        border_width = max(8, int(ancho_cuadro * 0.02))

        for i, color in enumerate(self.colores_dominantes):
            y0 = top_start + i * (alto_cuadro + espacio_entre)
            y1 = y0 + alto_cuadro
            x0 = left
            x1 = left + ancho_cuadro

            # Dibujar recuadro de color con borde blanco grueso
            draw.rectangle([x0, y0, x1, y1], fill=color, outline="white", width=border_width)

            color_obj = Color(color)
            hex_color = color_obj.rgb_to_hex()
            brillo = color_obj.calcular_brillo()

            text_fill = "black" if brillo > 180 else "white"

            # Medir texto con compatibilidad
            try:
                texto_ancho, texto_alto = font_grande.getsize(hex_color)
            except AttributeError:
                bbox = draw.textbbox((0, 0), hex_color, font=font_grande)
                texto_ancho = bbox[2] - bbox[0]
                texto_alto = bbox[3] - bbox[1]

            text_x = x0 + ((x1 - x0) - texto_ancho) / 2
            text_y = y0 + ((y1 - y0) - texto_alto) / 2

            draw.text((text_x, text_y), hex_color, fill=text_fill, font=font_grande)

        return paleta
