import os
import tempfile
import unittest
from PIL import Image

from paleta_exportador import PaletaExportador
from paleta_visualizador import PaletaVisualizador


class PaletaComponentesTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_exportador_guarda_imagen_en_directorio(self):
        exportador = PaletaExportador(self.temp_dir.name)
        imagen = Image.new("RGB", (20, 20), "red")

        ruta = exportador.guardar(imagen, "prueba.png")

        self.assertTrue(os.path.exists(ruta))
        self.assertEqual(os.path.basename(ruta), "prueba.png")

    def test_visualizador_crea_paleta_visual_y_original(self):
        visualizador = PaletaVisualizador()
        colores = [(255, 0, 0), (0, 255, 0)]
        imagen = Image.new("RGB", (80, 80), "blue")

        paleta_visual = visualizador.crear_paleta_visual(colores)
        paleta_original = visualizador.crear_paleta_original(imagen, colores)

        self.assertEqual(paleta_visual.size[0], 300)
        self.assertTrue(paleta_visual.size[1] > 0)
        self.assertEqual(paleta_original.size, imagen.size)


if __name__ == "__main__":
    unittest.main()
