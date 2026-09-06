from stack import Stack
from syntax_tree import Node
from shunting_yard import CONCAT, _es_elevacion, _resolver_escape

OPERADORES_BINARIOS = ("|", CONCAT)
OPERADORES_UNARIOS = ("*", "+", "?")

# Obtiene el arbol sintactico a partir de una expresion en postfix
def construir_arbol(postfix):
    pila = Stack()
    pasos = []

    for token in postfix:
        if token in OPERADORES_BINARIOS:
            derecho = pila.pop()
            izquierdo = pila.pop()
            nodo = Node(token, izquierdo, derecho)
            pila.push(nodo)
            pasos.append(f"'{token}' combina '{izquierdo.valor}' y '{derecho.valor}' -> nodo '{token}'")

        elif token in OPERADORES_UNARIOS or _es_elevacion(token):
            hijo = pila.pop()
            nodo = Node(token, hijo)
            pila.push(nodo)
            pasos.append(f"'{token}' aplica sobre '{hijo.valor}' -> nodo '{token}'")

        else:
            pila.push(Node(_resolver_escape(token)))
            pasos.append(f"'{token}' es operando -> hoja")

    raiz = pila.pop()
    return raiz, pasos
