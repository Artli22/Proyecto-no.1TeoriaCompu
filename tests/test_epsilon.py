"""Pruebas del manejo de epsilon.

  - En la entrada epsilon se escribe "ε"; internamente se marca con
    shunting_yard.EPSILON ("©").
  - "©" es un simbolo reservado: escrito en una expresion actua como
    epsilon, nunca como simbolo del alfabeto.
  - Un "ε" literal se escribe escapado: "\\ε".

Ejecutar desde la raiz del proyecto:
    python -m unittest tests.test_epsilon
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shunting_yard import convertir_a_postfix, EPSILON
from tree_builder import construir_arbol
from thompson import construir_afn
from afd import construir_afd
from minimizacion import minimizar_afd
from simulador import simular, simular_afd
from file_utils import leer_lineas


def construir_todo(expresion):
    postfix, _ = convertir_a_postfix(expresion)
    raiz, _ = construir_arbol(postfix)
    afn = construir_afn(raiz)
    afd = construir_afd(afn)
    return afn, afd, minimizar_afd(afd)


def acepta_en_los_tres(expresion, cadena):
    afn, afd, minimo = construir_todo(expresion)
    r = (simular(afn, cadena), simular_afd(afd, cadena), simular_afd(minimo, cadena))
    assert r[0] == r[1] == r[2], f"{expresion!r} / {cadena!r}: AFN/AFD/min discrepan {r}"
    return r[0]


class TestEpsilon(unittest.TestCase):

    def test_epsilon_sola(self):
        self.assertTrue(acepta_en_los_tres("ε", ""))
        self.assertFalse(acepta_en_los_tres("ε", "a"))

    def test_epsilon_en_distintas_posiciones(self):
        # concatenada al principio, en medio y al final: no cambia el lenguaje
        for expr in ("εabc", "aεbc", "abcε"):
            self.assertTrue(acepta_en_los_tres(expr, "abc"), expr)
            self.assertFalse(acepta_en_los_tres(expr, "ab"), expr)

    def test_epsilon_en_union(self):
        self.assertTrue(acepta_en_los_tres("a|ε", ""))
        self.assertTrue(acepta_en_los_tres("a|ε", "a"))
        self.assertFalse(acepta_en_los_tres("a|ε", "b"))

    def test_epsilon_en_grupo(self):
        # (a|ε)b  == b opcionalmente precedida de a
        self.assertTrue(acepta_en_los_tres("(a|ε)b", "b"))
        self.assertTrue(acepta_en_los_tres("(a|ε)b", "ab"))
        self.assertFalse(acepta_en_los_tres("(a|ε)b", "a"))

    def test_operador_interrogacion_usa_epsilon(self):
        # 'a?' se expande a (a|EPSILON)
        postfix, _ = convertir_a_postfix("a?")
        self.assertIn(EPSILON, postfix)
        self.assertTrue(acepta_en_los_tres("a?", ""))
        self.assertTrue(acepta_en_los_tres("a?", "a"))
        self.assertFalse(acepta_en_los_tres("a?", "aa"))

    def test_copyright_es_simbolo_reservado(self):
        # "©" escrito en la expresion actua como epsilon, no como simbolo
        self.assertTrue(acepta_en_los_tres("a©b", "ab"))
        self.assertFalse(acepta_en_los_tres("a©b", "a" + EPSILON + "b"))

    def test_epsilon_literal_escapada(self):
        # "\ε" si es un simbolo real del alfabeto
        afn, afd, minimo = construir_todo(r"a\εb")
        self.assertTrue(simular(afn, "aεb"))     # "aεb"
        self.assertFalse(simular(afn, "ab"))
        self.assertEqual(simular(afn, "aεb"), simular_afd(minimo, "aεb"))

    def test_expresion_del_archivo_de_ejemplo(self):
        # problema1.txt linea 2: ((ε|a)|b*)*  == (a|b)*
        exprs = leer_lineas(os.path.join(
            os.path.dirname(__file__), "..", "ejemplos", "problema1.txt"))
        expr = exprs[1]
        for w in ["", "a", "b", "ab", "abba", "bbbbaaa"]:
            self.assertTrue(acepta_en_los_tres(expr, w), f"{expr!r} deberia aceptar {w!r}")
        self.assertFalse(acepta_en_los_tres(expr, "abc"))


if __name__ == "__main__":
    unittest.main()
