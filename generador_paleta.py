import colorsys

class GeneradorPaletas:
    """Genera variaciones de paleta a partir de una lista de colores base."""

    def __init__(self, colores):
        self.colores = colores

    def _cambiar_tono(self, color, delta):
        """Cambia el tono de un color RGB moviendo su valor de hue."""
        r, g, b = [x / 255 for x in color]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        h = h * 360
        nuevo_h = (h + delta) % 360
        nuevo_h = nuevo_h / 360
        r2, g2, b2 = colorsys.hsv_to_rgb(nuevo_h, s, v)

        return (
            int(r2 * 255),
            int(g2 * 255),
            int(b2 * 255)
        )

    def generar_complementaria(self):
        """Devuelve una paleta complementaria para cada color base."""
        return [self._cambiar_tono(c, 180) for c in self.colores]

    def generar_analogos(self):
        """Devuelve una paleta con tonos análogos complementarios."""
        return [self._cambiar_tono(c, d) for c in self.colores for d in [-30, 30]]

    def generar_triadicos(self):
        """Devuelve una paleta triádica con colores espaciados 120° en el círculo cromático."""
        return [self._cambiar_tono(c, d) for c in self.colores for d in [120, 240]]

    def generar_paletas(self):
        """Agrupa las paletas generadas en un diccionario con descripción y colores."""
        return {
            "Complementaria": {
                "descripcion": "Impacto inmediato y alto contraste. Orientada a captar interés de forma inmediata y sostener la atención.",
                "colores": self.generar_complementaria()
            },
            "Análoga": {
                "descripcion": "Armonía visual y coherencia. Perfecta para transmitir calma, confianza y una estética cuidada.",
                "colores": self.generar_analogos()
            },
            "Triádica": {
                "descripcion": "Equilibrio dinámico y versatilidad. Combina energía y balance, ideal para marcas creativas y modernas.",
                "colores": self.generar_triadicos()
            }
        }
    