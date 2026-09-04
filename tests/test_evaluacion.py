"""Pruebas de la evaluacion de w sobre AFN, AFD y AFD minimizado.

Cubre: cadena aceptada, rechazada, vacia, simbolo fuera del alfabeto y
transicion inexistente. En todos los casos los tres automatas deben dar
el mismo veredicto.

Ejecutar desde la raiz del proyecto:
    python -m unittest tests.test_evaluacion
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shunting_yard import convertir_a_postfix
from tree_builder import construir_arbol
from thompson import construir_afn
from afd import construir_afd
from minimizacion import minimizar_afd
from simulador import simular, simular_afd


def construir_todo(expresion):
    postfix, _ = convertir_a_postfix(expresion)
    raiz, _ = construir_arbol(postfix)
    afn = construir_afn(raiz)
    afd = construir_afd(afn)
    return afn, afd, minimizar_afd(afd)


def veredictos(expresion, cadena):
    afn, afd, minimo = construir_todo(expresion)
    return simular(afn, cadena), simular_afd(afd, cadena), simular_afd(minimo, cadena)


class TestEvaluacion(unittest.TestCase):

    def test_cadena_aceptada(self):
        r = veredictos("(a|b)*abb", "aabb")
        self.assertEqual(r, (True, True, True))

    def test_cadena_rechazada(self):
        r = veredictos("(a|b)*abb", "abab")
        self.assertEqual(r, (False, False, False))

    def test_cadena_vacia_aceptada(self):
        # a* acepta la cadena vacia
        self.assertEqual(veredictos("a*", ""), (True, True, True))

    def test_cadena_vacia_rechazada(self):
        # abb no acepta la cadena vacia
        self.assertEqual(veredictos("abb", ""), (False, False, False))

    def test_simbolo_fuera_del_alfabeto(self):
        # 'x' no aparece en (a|b)*abb -> rechazo en los tres
        self.assertEqual(veredictos("(a|b)*abb", "abx"), (False, False, False))

    def test_transicion_inexistente(self):
        # tras leer "ab" en 'abb' el unico simbolo valido es 'b'
        self.assertEqual(veredictos("abb", "aba"), (False, False, False))

    def test_alfabeto_del_afn(self):
        afn, _, _ = construir_todo("0?(1?)?0*")
        self.assertEqual(afn.alfabeto(), ["0", "1"])
        afn2, _, _ = construir_todo("(a|b)*abb")
        self.assertEqual(afn2.alfabeto(), ["a", "b"])

    def test_consistencia_en_bateria(self):
        casos = [
            ("(a|b)*abb", "ab"),
            ("(a*|b*)+", "ab"),
            ("0?(1?)?0*", "01"),
            ("((ε|a)|b*)*", "ab"),
        ]
        for expr, alfabeto in casos:
            afn, afd, minimo = construir_todo(expr)
            palabras = [""]
            actual = [""]
            for _ in range(6):
                actual = [p + s for p in actual for s in alfabeto]
                palabras.extend(actual)
            for w in palabras:
                a, b, c = simular(afn, w), simular_afd(afd, w), simular_afd(minimo, w)
                self.assertEqual(a, b, f"[{expr}] AFN vs AFD en {w!r}")
                self.assertEqual(b, c, f"[{expr}] AFD vs minimizado en {w!r}")


if __name__ == "__main__":
    unittest.main()
