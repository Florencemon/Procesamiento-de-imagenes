import os
from pathlib import Path

from PIL import Image


class PaletaExportador:
    """Responsable de guardar imágenes en disco en una carpeta específica."""

    def __init__(self, carpeta_salida):
        self.carpeta_salida = carpeta_salida
        self._crear_directorio()

    def guardar(self, imagen, nombre_archivo):
        """Guarda una imagen en la carpeta configurada y devuelve la ruta."""
        ruta_destino = self._ruta_completa(nombre_archivo)
        imagen.save(ruta_destino)
        return ruta_destino

    def _crear_directorio(self):
        Path(self.carpeta_salida).mkdir(parents=True, exist_ok=True)

    def _ruta_completa(self, nombre_archivo):
        return os.path.join(self.carpeta_salida, nombre_archivo)
