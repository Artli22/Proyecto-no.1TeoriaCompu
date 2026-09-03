import os

from graphviz import Digraph

from afd import mapear_afd_a_ids

# Mismo estilo que afn_renderer.dibujar_afn: rankdir LR, un punto invisible
# como flecha de entrada al inicial, doublecircle para los de aceptacion y
# una arista por transicion con el simbolo como etiqueta.


def _dibujar(nodos, inicial, aceptacion, aristas, ruta_salida):
    """Nucleo de dibujo, compartido por el AFD y el AFD minimizado.

    nodos      : lista de (id, etiqueta)
    inicial    : id del estado inicial
    aceptacion : conjunto de ids de aceptacion
    aristas    : lista de (origen, simbolo, destino)
    """
    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    grafo = Digraph()
    grafo.attr(rankdir="LR")

    grafo.node("flecha_inicial", shape="point")
    grafo.edge("flecha_inicial", str(inicial))

    for id_estado, etiqueta in nodos:
        forma = "doublecircle" if id_estado in aceptacion else "circle"
        grafo.node(str(id_estado), etiqueta, shape=forma)

    for origen, simbolo, destino in aristas:
        grafo.edge(str(origen), str(destino), label=simbolo)

    return grafo.render(ruta_salida, format="png", cleanup=True)


def dibujar_afd(afd, ruta_salida):
    """Dibuja el AFD de subconjuntos y lo guarda como PNG.

    Los estados (frozensets de estados del AFN) se numeran 0,1,2... con
    mapear_afd_a_ids, la misma numeracion que usa la salida textual.
    """
    plano = mapear_afd_a_ids(afd)

    nodos = [(i, str(i)) for i in range(plano["num_estados"])]
    aristas = [(t["origen"], t["simbolo"], t["destino"]) for t in plano["transiciones"]]

    return _dibujar(nodos, plano["inicial"], set(plano["aceptacion"]), aristas, ruta_salida)


def dibujar_afd_min(minimo, ruta_salida):
    """Dibuja el AFD minimizado y lo guarda como PNG.

    La etiqueta de cada estado muestra su id y, debajo, los estados del AFD
    original que agrupa (asi se ve el resultado real de la minimizacion).
    """
    nodos = []
    for estado in sorted(minimo.estados):
        grupo = minimo.grupos.get(estado, [])
        etiqueta = str(estado)
        if grupo:
            etiqueta += "\n{" + ",".join(str(e) for e in grupo) + "}"
        nodos.append((estado, etiqueta))

    aristas = [(t.origen, t.simbolo, t.destino) for t in minimo.transiciones]

    return _dibujar(nodos, minimo.inicial, set(minimo.aceptacion), aristas, ruta_salida)
