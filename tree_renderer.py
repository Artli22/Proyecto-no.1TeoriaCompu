from graphviz import Digraph
from shunting_yard import CONCAT, mostrar_simbolo


def dibujar_arbol(raiz, ruta_salida):
    """Dibuja el arbol sintactico con Graphviz y lo guarda como PNG.

    ruta_salida es la ruta del archivo sin extension (ej. "salida/expresion_1").
    Devuelve la ruta del PNG generado.
    """
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


def arbol_a_ascii(nodo, prefijo="", es_ultimo=True):
    """Convierte el árbol sintáctico a una representación ASCII.
    
    Usa conectores de árbol (└──, ├──, │) para visualizar la estructura.
    """
    if nodo is None:
        return ""
    
    # Mostrar el nodo actual
    simbolo = "·" if nodo.valor == CONCAT else mostrar_simbolo(nodo.valor)
    resultado = prefijo
    resultado += "└── " if es_ultimo else "├── "
    resultado += simbolo + "\n"
    
    # Preparar el prefijo para los hijos
    extension = "    " if es_ultimo else "│   "
    
    # Mostrar hijo izquierdo
    if nodo.izquierdo:
        tiene_derecho = nodo.derecho is not None
        resultado += arbol_a_ascii(nodo.izquierdo, prefijo + extension, not tiene_derecho)
    
    # Mostrar hijo derecho
    if nodo.derecho:
        resultado += arbol_a_ascii(nodo.derecho, prefijo + extension, True)
    
    return resultado


def mostrar_arbol(nodo):
    """Muestra el árbol en la consola con formato ASCII."""
    if nodo is None:
        return ""
    
    # Raíz
    simbolo = "·" if nodo.valor == CONCAT else mostrar_simbolo(nodo.valor)
    resultado = simbolo + "\n"
    
    # Hijos
    if nodo.izquierdo or nodo.derecho:
        if nodo.izquierdo:
            tiene_derecho = nodo.derecho is not None
            resultado += arbol_a_ascii(nodo.izquierdo, "", not tiene_derecho)
        if nodo.derecho:
            resultado += arbol_a_ascii(nodo.derecho, "", True)
    
    return resultado
