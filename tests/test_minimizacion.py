"""Pruebas de la minimizacion del AFD y de la consistencia AFN / AFD / AFD minimizado.

Ejecutar desde la raiz del proyecto:
    python -m unittest tests.test_minimizacion
o directamente:
    python tests/test_minimizacion.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shunting_yard import convertir_a_postfix
from tree_builder import construir_arbol
from thompson import construir_afn
from afd import AFD, construir_afd
from minimizacion import minimizar_afd
from simulador import simular, simular_afd


def construir_todo(expresion):
    """expresion -> (afn, afd, afd_minimizado)."""
    postfix, _ = convertir_a_postfix(expresion)
    raiz, _ = construir_arbol(postfix)
    afn = construir_afn(raiz)
    afd = construir_afd(afn)
    minimo = minimizar_afd(afd)
    return afn, afd, minimo


def palabras(alfabeto, largo_max):
    """Todas las cadenas sobre 'alfabeto' de longitud 0..largo_max."""
    actual = [""]
    todas = [""]
    for _ in range(largo_max):
        siguiente = [p + s for p in actual for s in alfabeto]
        todas.extend(siguiente)
        actual = siguiente
    return todas


class TestConsistencia(unittest.TestCase):
    """El AFN, el AFD y el AFD minimizado deben aceptar/rechazar lo mismo."""

    CASOS = [
        ("(a|b)*abb", "ab", 6),
        ("(a|b)*abb(a|b)*", "ab", 6),
        ("a*|b*", "ab", 6),
        ("(a*|b*)+", "ab", 6),
        ("((ε|a)|b*)*", "ab", 6),
        ("0?(1?)?0*", "01", 6),
        ("(ab)*", "ab", 6),
        ("a(a|b)*b", "ab", 6),
    ]

    def test_afn_afd_minimo_coinciden(self):
        for expr, alfabeto, largo in self.CASOS:
            afn, afd, minimo = construir_todo(expr)
            for w in palabras(alfabeto, largo):
                r_afn = simular(afn, w)
                r_afd = simular_afd(afd, w)
                r_min = simular_afd(minimo, w)
                self.assertEqual(
                    r_afn, r_afd,
                    f"[{expr}] AFN vs AFD difieren en {w!r}")
                self.assertEqual(
                    r_afd, r_min,
                    f"[{expr}] AFD vs AFD minimizado difieren en {w!r}")


class TestMinimizacion(unittest.TestCase):

    def test_no_agrega_estados(self):
        for expr, _, _ in TestConsistencia.CASOS:
            _, afd, minimo = construir_todo(expr)
            self.assertLessEqual(minimo.num_estados(), afd.num_estados(),
                                 f"[{expr}] el minimizado tiene mas estados")

    def test_estados_equivalentes_se_agrupan(self):
        # ((ε|a)|b*)* reconoce (a|b)*: el AFD tiene varios estados, todos
        # equivalentes -> el minimizado debe quedar con un solo estado.
        _, afd, minimo = construir_todo("((ε|a)|b*)*")
        self.assertGreater(afd.num_estados(), 1)
        self.assertEqual(minimo.num_estados(), 1)
        self.assertEqual(minimo.aceptacion, {0})

    def test_afd_ya_minimo_no_cambia(self):
        # "abb": 4 estados en cadena, ninguno equivalente al otro.
        _, afd, minimo = construir_todo("abb")
        self.assertEqual(afd.num_estados(), 4)
        self.assertEqual(minimo.num_estados(), 4)

    def test_conserva_inicial_y_finales(self):
        _, _, minimo = construir_todo("(a|b)*abb")
        self.assertEqual(minimo.inicial, 0)
        self.assertTrue(len(minimo.aceptacion) >= 1)
        # el inicial no acepta la cadena vacia para esta expresion
        self.assertNotIn(0, minimo.aceptacion)

    def test_descarta_estados_inalcanzables(self):
        # AFD armado a mano. s0 solo tiene transicion con 'a'; s1 acepta.
        # Lenguaje: empieza con 'a', y toda 'b' va seguida de una 'a'.
        # Se agrega un estado extra (frozenset({2})) que nadie alcanza.
        afd = AFD()
        s0, s1, s2 = frozenset({0}), frozenset({1}), frozenset({2})
        afd.inicial = s0
        afd.agregar_transicion(s0, "a", s1)
        afd.agregar_transicion(s1, "a", s1)
        afd.agregar_transicion(s1, "b", s0)
        afd.agregar_transicion(s2, "a", s2)  # inalcanzable
        afd.estados.add(s2)
        afd.aceptacion.add(s1)

        minimo = minimizar_afd(afd)

        self.assertEqual(minimo.num_estados(), 2)
        agrupados = [e for grupo in minimo.grupos.values() for e in grupo]
        self.assertNotIn(2, agrupados)  # el estado inalcanzable no aparece
        # el minimizado reconoce el mismo lenguaje que el AFD original
        for w in palabras("ab", 6):
            self.assertEqual(simular_afd(minimo, w), simular_afd(afd, w),
                             f"w={w!r}")


if __name__ == "__main__":
    unittest.main()
