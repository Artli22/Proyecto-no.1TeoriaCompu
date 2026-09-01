from graphviz import Digraph

from shunting_yard import EPSILON


def dibujar_afn(afn, ruta_salida):
    """Dibuja el AFN con Graphviz y lo guarda como PNG.

    ruta_salida es la ruta del archivo sin extension (ej. "salida/afn_1").
    Devuelve la ruta del PNG generado.
    """
    grafo = Digraph()
    grafo.attr(rankdir="LR")

    # flecha de entrada al inicial, sin nodo visible antes (convencion usual)
    grafo.node("flecha_inicial", shape="point")
    grafo.edge("flecha_inicial", str(afn.inicial))

    for estado in range(afn.num_estados):
        forma = "doublecircle" if estado == afn.aceptacion else "circle"
        grafo.node(str(estado), str(estado), shape=forma)

    for t in afn.transiciones:
        simbolo = "ε" if t.simbolo == EPSILON else t.simbolo
        grafo.edge(str(t.origen), str(t.destino), label=simbolo)

    return grafo.render(ruta_salida, format="png", cleanup=True)
