import os
import tempfile
import unittest
from PIL import Image

from analizador_paleta import AnalizadorPaleta


class AnalizadorPaletaTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _crear_imagen(self, nombre_archivo, color, size=(120, 120)):
        ruta = os.path.join(self.temp_dir.name, nombre_archivo)
        Image.new("RGB", size, color).save(ruta)
        return ruta

    def test_reutiliza_instancia_al_cargar_otra_imagen(self):
        analizador = AnalizadorPaleta(n_colores=3)
        primera_ruta = self._crear_imagen("primera.png", (255, 0, 0))
        segunda_ruta = self._crear_imagen("segunda.png", (0, 0, 255))

        analizador.cargar_imagen(primera_ruta)
        colores_primera = analizador.extraer_colores()
        self.assertEqual(len(colores_primera), 3)

        analizador.cargar_imagen(segunda_ruta)
        colores_segunda = analizador.extraer_colores()

        self.assertEqual(len(colores_segunda), 3)
        self.assertTrue(colores_segunda)

    def test_carga_directa_desde_pil(self):
        analizador = AnalizadorPaleta(n_colores=2)
        imagen = Image.new("RGB", (80, 80), "green")

        analizador.cargar_imagen_desde_pil(imagen)
        colores = analizador.extraer_colores()

        self.assertEqual(len(colores), 2)
        self.assertTrue(all(isinstance(color, tuple) for color in colores))


if __name__ == "__main__":
    unittest.main()
