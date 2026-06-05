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
        # Crear una imagen en blanco
        ancho = 100 * len(self.colores_dominantes)
        alto = 100
        paleta = Image.new("RGB", (ancho, alto), "white")
        draw = ImageDraw.Draw(paleta)

        # Dibujar cada color en la paleta
        for i, color in enumerate(self.colores_dominantes):
            x0 = i * 100
            x1 = x0 + 100
            draw.rectangle([x0, 0, x1, alto], fill=color)

        return paleta
