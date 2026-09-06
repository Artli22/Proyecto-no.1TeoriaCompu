class Node:
    """Nodo de un arbol sintactico para una expresion regular en postfix.

    Un operando (letra, digito, ~, clase de caracteres, escapado) es una
    hoja: izquierdo y derecho quedan en None. Los operadores '*', '+', '?'
    y '^N' (elevacion, ej. '^3') son unarios y solo usan izquierdo. Los
    operadores '|' y '&' (concatenacion) son binarios y usan ambos hijos.
    """

    def __init__(self, valor, izquierdo=None, derecho=None):
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho

    def es_hoja(self):
        return self.izquierdo is None and self.derecho is None
