from graphviz import Digraph
from shunting_yard import CONCAT, mostrar_simbolo

# Dibujo del arbol en formato png con ayuda de Graphviz
def dibujar_arbol(raiz, ruta_salida):
    grafo = Digraph()
    contador = [0]

    def agregar_nodo(nodo):
        id_nodo = str(contador[0])
        contador[0] += 1
        valor_nodo = "·" if nodo.valor == CONCAT else mostrar_simbolo(nodo.valor)
        grafo.node(id_nodo, valor_nodo)

        if nodo.izquierdo:
            id_izquierdo = agregar_nodo(nodo.izquierdo)
            grafo.edge(id_nodo, id_izquierdo)
        if nodo.derecho:
            id_derecho = agregar_nodo(nodo.derecho)
            grafo.edge(id_nodo, id_derecho)

        return id_nodo

    agregar_nodo(raiz)

    return grafo.render(ruta_salida, format="png", cleanup=True)
