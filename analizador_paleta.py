from PIL import Image, ImageDraw
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
