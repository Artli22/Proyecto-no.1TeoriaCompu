from stack import Stack
from syntax_tree import Node
from shunting_yard import CONCAT

OPERADORES_BINARIOS = ("|", CONCAT)
OPERADORES_UNARIOS = ("*",)


def construir_arbol(postfix):
    """Construye el arbol sintactico a partir de una expresion en postfix.

    Usa una pila de nodos (igual que Shunting Yard usa una pila de
    operadores): los operandos se apilan directo como hojas, y cada
    operador saca de la pila los nodos que necesita, arma un nodo nuevo y
    lo vuelve a apilar. Al final queda un solo nodo en la pila: la raiz.

    Devuelve una tupla (raiz, pasos) para poder mostrar la construccion.
    """
    pila = Stack()
    pasos = []

    for token in postfix:
        if token in OPERADORES_BINARIOS:
            derecho = pila.pop()
            izquierdo = pila.pop()
            nodo = Node(token, izquierdo, derecho)
            pila.push(nodo)
            pasos.append(f"'{token}' combina '{izquierdo.valor}' y '{derecho.valor}' -> nodo '{token}'")

        elif token in OPERADORES_UNARIOS:
            hijo = pila.pop()
            nodo = Node(token, hijo)
            pila.push(nodo)
            pasos.append(f"'{token}' aplica sobre '{hijo.valor}' -> nodo '{token}'")

        else:
            pila.push(Node(token))
            pasos.append(f"'{token}' es operando -> hoja")

    raiz = pila.pop()
    return raiz, pasos
