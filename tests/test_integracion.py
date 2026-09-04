"""Prueba integral: el flujo completo para cada linea del archivo de entrada.

  infix -> postfix -> arbol -> AFN -> AFD -> AFD minimizado -> PNG + simulacion

Ejecutar desde la raiz del proyecto:
    python -m unittest tests.test_integracion
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shunting_yard import convertir_a_postfix
from tree_builder import construir_arbol
from tree_renderer import dibujar_arbol
from thompson import construir_afn
from afn_renderer import dibujar_afn
from afd import construir_afd
from afd_renderer import dibujar_afd, dibujar_afd_min
from minimizacion import minimizar_afd
from simulador import simular, simular_afd
from file_utils import leer_lineas

ARCHIVO = os.path.join(os.path.dirname(__file__), "..", "ejemplos", "problema1.txt")
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def flujo_completo(expresion, carpeta, numero):
    """Reproduce lo que hace main.py para una expresion. Devuelve
    (afn, afd, minimo) y deja los 4 PNG en 'carpeta'."""
    postfix, _ = convertir_a_postfix(expresion)
    raiz, _ = construir_arbol(postfix)
    dibujar_arbol(raiz, os.path.join(carpeta, f"expresion_{numero}"))

    afn = construir_afn(raiz)
    dibujar_afn(afn, os.path.join(carpeta, f"afn_{numero}"))

    afd = construir_afd(afn)
    dibujar_afd(afd, os.path.join(carpeta, f"afd_{numero}"))

    minimo = minimizar_afd(afd)
    dibujar_afd_min(minimo, os.path.join(carpeta, f"afd_min_{numero}"))

    return afn, afd, minimo


def es_png(ruta):
    with open(ruta, "rb") as f:
        return f.read(8) == FIRMA_PNG


class TestIntegracion(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.expresiones = leer_lineas(ARCHIVO)

    def test_todas_las_lineas_se_procesan(self):
        self.assertGreater(len(self.expresiones), 1, "el archivo debe tener varias lineas")

        for numero, expr in enumerate(self.expresiones, start=1):
            afn, afd, minimo = flujo_completo(expr, self.tmp, numero)

            # los 4 PNG existen y son validos
            for nombre in (f"expresion_{numero}", f"afn_{numero}",
                           f"afd_{numero}", f"afd_min_{numero}"):
                ruta = os.path.join(self.tmp, nombre + ".png")
                self.assertTrue(os.path.exists(ruta), f"falta {ruta}")
                self.assertTrue(es_png(ruta), f"{ruta} no es PNG")

            # el minimizado no tiene mas estados que el AFD
            self.assertLessEqual(minimo.num_estados(), afd.num_estados())

            # AFN, AFD y AFD minimizado coinciden en toda la bateria
            alfabeto = afn.alfabeto() or ["a", "b"]
            actual, palabras = [""], [""]
            for _ in range(5):
                actual = [p + s for p in actual for s in alfabeto]
                palabras.extend(actual)
            for w in palabras:
                a, b, c = simular(afn, w), simular_afd(afd, w), simular_afd(minimo, w)
                self.assertEqual(a, b, f"[{expr}] AFN vs AFD en {w!r}")
                self.assertEqual(b, c, f"[{expr}] AFD vs minimizado en {w!r}")

    def test_flujo_extremo_a_extremo_caso_conocido(self):
        afn, afd, minimo = flujo_completo("(a|b)*abb(a|b)*", self.tmp, 99)
        acepta = ["abb", "abba", "aabbb", "babbb", "abbabb"]
        rechaza = ["", "ab", "ba", "abab", "b"]
        for w in acepta:
            self.assertEqual((simular(afn, w), simular_afd(afd, w), simular_afd(minimo, w)),
                             (True, True, True), f"deberia aceptar {w!r}")
        for w in rechaza:
            self.assertEqual((simular(afn, w), simular_afd(afd, w), simular_afd(minimo, w)),
                             (False, False, False), f"deberia rechazar {w!r}")


if __name__ == "__main__":
    unittest.main()
