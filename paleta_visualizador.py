from PIL import Image, ImageDraw, ImageFilter, ImageFont


class PaletaVisualizador:
    """Responsable de construir representaciones visuales de una paleta."""

    def crear_paleta_visual(self, colores, ancho_por_color=150, alto=280):
        """Genera una imagen con los colores de la paleta y su información."""
        ancho = max(1, ancho_por_color * len(colores))
        paleta = Image.new("RGB", (ancho, alto), "white")
        draw = ImageDraw.Draw(paleta)
        font_grande, font_pequena = self._obtener_fuentes()

        for i, color in enumerate(colores):
            self._dibujar_color(draw, color, i, ancho_por_color, font_grande, font_pequena)

        return paleta

    def crear_paleta_original(self, imagen_original, colores, espacio_inferior=240):
        """Genera una copia de la imagen original con recuadros de colores superpuestos."""
        original = imagen_original.copy()
        ancho_original, alto_original = original.size
        num_colores = len(colores)

        margen = max(40, min(80, ancho_original // 20))
        ancho_disponible = max(1, ancho_original - (margen * 2))
        alto_disponible = max(1, alto_original - (margen * 2) - espacio_inferior)
        alto_cuadro = max(1, min(200, alto_disponible // (num_colores + 1)))
        ancho_cuadro = ancho_disponible
        espacio_entre = max(1, alto_cuadro // 10)
        total_altura = num_colores * alto_cuadro + (num_colores - 1) * espacio_entre

        if total_altura > alto_disponible:
            alto_cuadro = max(1, (alto_disponible - (num_colores - 1) * espacio_entre) // max(1, num_colores))
            total_altura = num_colores * alto_cuadro + (num_colores - 1) * espacio_entre

        paleta = original.filter(ImageFilter.GaussianBlur(radius=12))
        draw = ImageDraw.Draw(paleta)
        font_grande = self._obtener_fuente_tamanio(alto_cuadro)
        top_start = max(0, (alto_original - total_altura) // 2)
        left = margen
        border_width = max(3, alto_cuadro // 40)

        for i, color in enumerate(colores):
            y0 = top_start + i * (alto_cuadro + espacio_entre)
            y1 = y0 + alto_cuadro
            x0 = left
            x1 = left + ancho_cuadro
            draw.rectangle([x0, y0, x1, y1], fill=color, outline="white", width=border_width)

        return paleta

    def _obtener_fuentes(self):
        try:
            return ImageFont.truetype("arial.ttf", 20), ImageFont.truetype("arial.ttf", 13)
        except IOError:
            return ImageFont.load_default(), ImageFont.load_default()

    def _dibujar_color(self, draw, color, index, ancho_por_color, font_grande, font_pequena):
        x0 = index * ancho_por_color
        x1 = x0 + ancho_por_color
        draw.rectangle([x0 + 10, 10, x1 - 10, 120], fill=color)
        draw.text((x0 + 15, 130), self._hex_color(color), fill="black", font=font_grande)
        draw.text((x0 + 15, 158), f"Color {index + 1}", fill="black", font=font_pequena)

    def _hex_color(self, color):
        return "#{:02x}{:02x}{:02x}".format(*color)

    def _obtener_fuente_tamanio(self, alto_cuadro):
        try:
            font_size = max(16, int(alto_cuadro * 0.35))
            return ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            return ImageFont.load_default()
