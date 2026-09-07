import os

from graphviz import Digraph

from shunting_yard import epsilon_visible, mostrar_simbolo

# Renderizacion de todos los elementos del AFN
def dibujar_afn(afn, ruta_salida):
    grafo = Digraph()
    grafo.attr(rankdir="LR")

    # flecha de entrada al inicial
    grafo.node("flecha_inicial", shape="point")
    grafo.edge("flecha_inicial", str(afn.inicial))

    for estado in range(afn.num_estados):
        forma = "doublecircle" if estado == afn.aceptacion else "circle"
        grafo.node(str(estado), str(estado), shape=forma)

    for t in afn.transiciones:
        grafo.edge(str(t.origen), str(t.destino), label=mostrar_simbolo(t.simbolo))

    return grafo.render(ruta_salida, format="png", cleanup=True)


def _celda(contenido, color=None):
    atributo = f' BGCOLOR="{color}"' if color else ""
    return f"<TD{atributo}>{contenido}</TD>"


# Renderizacion del formato de la tabla de cerraduras epsilon del AFN
def dibujar_tabla_cerraduras(afn, ruta_salida):
    from afd import epsilon_closure  

    alfabeto = afn.alfabeto()

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    encabezado = (
        _celda("<B>Estado</B>", "lightgray")
        + "".join(_celda(f"<B>{simbolo}</B>", "lightgray") for simbolo in alfabeto)
        + _celda(f"<B>{epsilon_visible()}-cierre</B>", "lightgray")
    )

    filas = []
    for estado in range(afn.num_estados):
        es_aceptacion = estado == afn.aceptacion
        color = "lightyellow" if es_aceptacion else None

        etiqueta = str(estado)
        if estado == afn.inicial:
            etiqueta = "&#8594; " + etiqueta
        if es_aceptacion:
            etiqueta += " *"

        celdas_simbolos = []
        for simbolo in alfabeto:
            destinos = sorted(
                t.destino for t in afn.transiciones_desde(estado) if t.simbolo == simbolo
            )
            texto = ", ".join(str(d) for d in destinos) if destinos else "-"
            celdas_simbolos.append(_celda(texto, color))

        cierre = sorted(epsilon_closure(estado, afn))
        conjunto = "{" + ", ".join(str(e) for e in cierre) + "}"

        fila = (
            _celda(etiqueta, color)
            + "".join(celdas_simbolos)
            + _celda(conjunto, color)
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
