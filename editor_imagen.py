from PIL import Image, ImageEnhance
import numpy as np


class EditorImagen:
    def __init__(self, imagen):
        self.imagen = imagen

    # =====================================================
    # ✨ BRILLO
    # =====================================================
    def cambiar_brillo(self, factor):
        enhancer = ImageEnhance.Brightness(
            self.imagen
        )
        self.imagen = enhancer.enhance(factor)
        return self.imagen

    # =====================================================
    # 🎨 SATURACIÓN
    # =====================================================
    def cambiar_saturacion(self, factor):
        enhancer = ImageEnhance.Color(
            self.imagen
        )
        self.imagen = enhancer.enhance(factor)

        return self.imagen

    # =====================================================
    # 📏 TAMAÑO
    # =====================================================
    def cambiar_tamano(self, ancho, alto):
        self.imagen = self.imagen.resize(
            (ancho, alto)
        )

        return self.imagen


    # =====================================================
    # 🖼️ APLICAR PALETA
    # =====================================================
    def aplicar_paleta(
        self,
        colores_originales,
        colores_nuevos
    ):
        img_array = np.array(self.imagen)
        for original, nuevo in zip(
            colores_originales,
            colores_nuevos
        ):
            mask = np.all(
                np.abs(img_array - original) < 47,
                axis=-1
            )
            img_array[mask] = nuevo

        imagen_nueva = Image.fromarray(
            img_array.astype('uint8')
        )

        return imagen_nueva