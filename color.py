


class Color:
    """Utilidad para manejar colores RGB y obtener datos como HEX, brillo y temperatura."""

    def __init__(self, rgb):
        self.rgb = tuple(int(x) for x in rgb)

    def rgb_to_hex(self):
        """Convierte un color RGB a su representación hexadecimal."""
        return '#%02x%02x%02x' % self.rgb

    def calcular_brillo(self):
        """Calcula el brillo promedio del color como el promedio de los canales RGB."""
        r, g, b = self.rgb
        return round((r + g + b) / 3, 2)

    def clasificar_brillo(self):
        """Clasifica el brillo en Oscuro, Medio o Claro."""
        brillo = self.calcular_brillo()

        if brillo < 85:
            return "Oscuro"
        elif brillo < 170:
            return "Medio"
        else:
            return "Claro"

    def clasificar_temperatura(self):
        """Clasifica el color como Cálido, Frío o Neutro según la dominancia de R y B."""
        r, g, b = self.rgb

        if r > b:
            return "Cálido"
        elif b > r:
            return "Frío"
        else:
            return "Neutro"
        
