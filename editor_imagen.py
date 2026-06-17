from PIL import Image, ImageEnhance
import numpy as np


class EditorImagen:
    """Encapsula operaciones de edición simples sobre una imagen PIL."""

    def __init__(self, imagen):
        self.imagen = imagen

    # =====================================================
    # ✨ BRILLO
    # =====================================================
    def cambiar_brillo(self, factor):
        """Ajusta el brillo de la imagen usando ImageEnhance."""
        enhancer = ImageEnhance.Brightness(
            self.imagen
        )
        self.imagen = enhancer.enhance(factor)
        return self.imagen

    # =====================================================
    # 🎨 SATURACIÓN
    # =====================================================
    def cambiar_saturacion(self, factor):
        """Aumenta o reduce la saturación del color de la imagen."""
        enhancer = ImageEnhance.Color(
            self.imagen
        )
        self.imagen = enhancer.enhance(factor)
        return self.imagen

    # =====================================================
    # 📏 TAMAÑO
    # =====================================================
    def cambiar_tamano(self, ancho, alto):
        """Redimensiona la imagen a las dimensiones indicadas."""
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
        """Reemplaza colores similares en la imagen por la nueva paleta."""
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