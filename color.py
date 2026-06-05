


class Color:

    def __init__(self, rgb):
        self.rgb = tuple(int(x) for x in rgb)

    def rgb_to_hex(self):
        return '#%02x%02x%02x' % self.rgb

    def calcular_brillo(self):
        r, g, b = self.rgb
        return round((r + g + b) / 3, 2)

    def clasificar_brillo(self):

        brillo = self.calcular_brillo()

        if brillo < 85:
            return "Oscuro"
        elif brillo < 170:
            return "Medio"
        else:
            return "Claro"

    def clasificar_temperatura(self):

        r, g, b = self.rgb

        if r > b:
            return "Cálido"
        elif b > r:
            return "Frío"
        else:
            return "Neutro"
        
