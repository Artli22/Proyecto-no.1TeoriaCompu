import os

from graphviz import Digraph

from afd import mapear_afd_a_ids

# Renderizacion de los elementos individualesque conforman el AFD y AFD minimizado
def _dibujar(nodos, inicial, aceptacion, aristas, ruta_salida):
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

# Renderizacion los caminos por los que son dibujados los difernetes estados del AFD
def dibujar_afd(afd, ruta_salida):
    plano = mapear_afd_a_ids(afd)

    nodos = [(i, str(i)) for i in range(plano["num_estados"])]
    aristas = [(t["origen"], t["simbolo"], t["destino"]) for t in plano["transiciones"]]

    return _dibujar(nodos, plano["inicial"], set(plano["aceptacion"]), aristas, ruta_salida)

# Renderizacion del AFD minimizado
def dibujar_afd_min(minimo, ruta_salida):
    nodos = []
    for estado in sorted(minimo.estados):
        grupo = minimo.grupos.get(estado, [])
        etiqueta = str(estado)
        if grupo:
            etiqueta += "\n{" + ",".join(str(e) for e in grupo) + "}"
        nodos.append((estado, etiqueta))

    aristas = [(t.origen, t.simbolo, t.destino) for t in minimo.transiciones]

    return _dibujar(nodos, minimo.inicial, set(minimo.aceptacion), aristas, ruta_salida)


def _celda(contenido, color=None):
    atributo = f' BGCOLOR="{color}"' if color else ""
    return f"<TD{atributo}>{contenido}</TD>"

# Renderizacion del formato de la tabla de subconjuntos formados tras analizar las cerraduras de AFN
def dibujar_tabla_subconjuntos(afd, afn, ruta_salida):
    plano = mapear_afd_a_ids(afd)
    alfabeto = afn.alfabeto()

    delta = {(t["origen"], t["simbolo"]): t["destino"] for t in plano["transiciones"]}

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    encabezado = (
        _celda("<B>Estado</B>", "lightgray")
        + _celda("<B>Estados AFN</B>", "lightgray")
        + "".join(_celda(f"<B>{simbolo}</B>", "lightgray") for simbolo in alfabeto)
    )

    filas = []
    for id_estado in range(plano["num_estados"]):
        etiqueta = str(id_estado)
        if id_estado == plano["inicial"]:
            etiqueta = "&#8594; " + etiqueta

        conjunto = sorted(plano["mapeo_estados"][str(id_estado)])
        conjunto_str = "{" + ", ".join(str(e) for e in conjunto) + "}"

        fila = (
            _celda(etiqueta)
            + _celda(conjunto_str)
            + "".join(
                _celda(delta.get((id_estado, simbolo), "-"))
                for simbolo in alfabeto
            )
        )
        filas.append(f"<TR>{fila}</TR>")

    html = (
        '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">'
        f"<TR>{encabezado}</TR>{''.join(filas)}"
        "</TABLE>>"
    )

    grafo = Digraph()
    grafo.node("tabla", html, shape="plain")
    return grafo.render(ruta_salida, format="png", cleanup=True)
