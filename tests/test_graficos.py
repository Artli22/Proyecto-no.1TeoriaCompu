"""Pruebas de generacion de PNG (AFN, AFD, AFD minimizado).

Comprueba que cada PNG se crea y empieza con la firma de un archivo PNG.
Ejecutar desde la raiz del proyecto:
    python -m unittest tests.test_graficos
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shunting_yard import convertir_a_postfix
from tree_builder import construir_arbol
from thompson import construir_afn
from afd import construir_afd
from minimizacion import minimizar_afd
from afn_renderer import dibujar_afn
from afd_renderer import dibujar_afd, dibujar_afd_min

FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def es_png(ruta):
    with open(ruta, "rb") as f:
        return f.read(8) == FIRMA_PNG


class TestGraficos(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        postfix, _ = convertir_a_postfix("(a|b)*abb")
        raiz, _ = construir_arbol(postfix)
        self.afn = construir_afn(raiz)
        self.afd = construir_afd(self.afn)
        self.minimo = minimizar_afd(self.afd)

    def test_png_afn(self):
        ruta = dibujar_afn(self.afn, os.path.join(self.tmp, "afn"))
        self.assertTrue(os.path.exists(ruta))
        self.assertTrue(es_png(ruta))

    def test_png_afd(self):
        ruta = dibujar_afd(self.afd, os.path.join(self.tmp, "afd"))
        self.assertTrue(os.path.exists(ruta))
        self.assertTrue(es_png(ruta))

    def test_png_afd_min(self):
        ruta = dibujar_afd_min(self.minimo, os.path.join(self.tmp, "afd_min"))
        self.assertTrue(os.path.exists(ruta))
        self.assertTrue(es_png(ruta))

    def test_crea_carpeta_si_no_existe(self):
        destino = os.path.join(self.tmp, "sub", "carpeta", "afd")
        ruta = dibujar_afd(self.afd, destino)
        self.assertTrue(os.path.exists(ruta))


if __name__ == "__main__":
    unittest.main()
