from shunting_yard import EPSILON, CONCAT, _es_elevacion
from afn import AFN


def construir_afn(raiz):
    """Aplica el algoritmo de Thompson sobre el arbol sintactico del Lab3.

    Recorre el arbol en postorden: primero arma el fragmento de los hijos y
    despues conecta ese fragmento segun el operador del nodo actual. Al
    terminar, el fragmento de la raiz es el AFN completo.
    """
    afn = AFN()
    inicio, fin = _construir_fragmento(raiz, afn)
    afn.inicial = inicio
    afn.aceptacion = fin
    _renumerar_desde_inicial(afn)
    return afn


def _renumerar_desde_inicial(afn):
    """Renumera los estados para que el inicial quede siempre como 0.

    Thompson construye de adentro hacia afuera (los hijos antes que el
    envoltorio), asi que el estado inicial real casi nunca queda con id 0
    tras la construccion. Se recorre por BFS desde el inicial, probando en
    cada estado sus transiciones ordenadas por simbolo, y se reasignan los
    ids en ese orden de descubrimiento (el mismo que usa la tabla de
    cierres y el diagrama del AFN).
    """
    por_origen = {}
    for t in afn.transiciones:
        por_origen.setdefault(t.origen, []).append(t)
    for lista in por_origen.values():
        lista.sort(key=lambda t: (t.simbolo, t.destino))

    mapeo = {afn.inicial: 0}
    cola = [afn.inicial]
    contador = 1
    while cola:
        actual = cola.pop(0)
        for t in por_origen.get(actual, []):
            if t.destino not in mapeo:
                mapeo[t.destino] = contador
                contador += 1
                cola.append(t.destino)

    # Por si quedara algun estado no alcanzado (no deberia pasar: en
    # Thompson todo estado esta en algun camino desde el inicial).
    for estado in range(afn.num_estados):
        if estado not in mapeo:
            mapeo[estado] = contador
            contador += 1

    for t in afn.transiciones:
        t.origen = mapeo[t.origen]
        t.destino = mapeo[t.destino]
    afn.inicial = mapeo[afn.inicial]
    afn.aceptacion = mapeo[afn.aceptacion]


def _construir_fragmento(nodo, afn):
    if nodo.es_hoja():
        return _fragmento_simbolo(nodo.valor, afn)

    if nodo.valor == "*":
        return _fragmento_estrella(nodo, afn)

    if nodo.valor == "+":
        return _fragmento_mas(nodo, afn)

    if nodo.valor == "?":
        return _fragmento_opcional(nodo, afn)

    if _es_elevacion(nodo.valor):
        return _fragmento_elevado(nodo, afn)

    if nodo.valor == "|":
        return _fragmento_union(nodo, afn)

    if nodo.valor == CONCAT:
        return _fragmento_concat(nodo, afn)

    raise ValueError(f"operador no soportado en Thompson: '{nodo.valor}'")


def _fragmento_simbolo(simbolo, afn):
    # sirve tanto para un simbolo normal (a, 0, 1...) como para una hoja
    # epsilon (EPSILON), ya que en ambos casos es una sola transicion i -> f
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, simbolo, fin)
    return inicio, fin


def _fragmento_estrella(nodo, afn):
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  # entrar a repetir
    afn.agregar_transicion(inicio, EPSILON, fin)      # saltar (cero veces)
    afn.agregar_transicion(f_hijo, EPSILON, i_hijo)   # repetir de nuevo
    afn.agregar_transicion(f_hijo, EPSILON, fin)       # salir
    return inicio, fin


def _fragmento_mas(nodo, afn):
    # igual que la estrella, pero sin el salto de "cero veces": obliga a
    # pasar por el cuerpo al menos una vez.
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  # entrar (obligatorio)
    afn.agregar_transicion(f_hijo, EPSILON, i_hijo)   # repetir de nuevo
    afn.agregar_transicion(f_hijo, EPSILON, fin)       # salir
    return inicio, fin


def _fragmento_opcional(nodo, afn):
    # igual que la estrella, pero sin la transicion de "repetir": el
    # cuerpo se recorre cero o una vez, nunca mas.
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  # entrar
    afn.agregar_transicion(inicio, EPSILON, fin)      # saltar (cero veces)
    afn.agregar_transicion(f_hijo, EPSILON, fin)       # salir (una vez)
    return inicio, fin


def _fragmento_elevado(nodo, afn):
    # 'X^n': concatena n copias independientes de X. A diferencia de *, +
    # y ?, una repeticion exacta no se puede armar con un ciclo de
    # epsilon (un NFA no "cuenta"): hay que construir cada copia de nuevo.
    n = int(nodo.valor[1:])

    if n == 0:
        return _fragmento_simbolo(EPSILON, afn)

    inicio, fin = _construir_fragmento(nodo.izquierdo, afn)
    for _ in range(n - 1):
        i_siguiente, f_siguiente = _construir_fragmento(nodo.izquierdo, afn)
        afn.agregar_transicion(fin, EPSILON, i_siguiente)
        fin = f_siguiente

    return inicio, fin


def _fragmento_union(nodo, afn):
    i1, f1 = _construir_fragmento(nodo.izquierdo, afn)
    i2, f2 = _construir_fragmento(nodo.derecho, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i1)
    afn.agregar_transicion(inicio, EPSILON, i2)
    afn.agregar_transicion(f1, EPSILON, fin)
    afn.agregar_transicion(f2, EPSILON, fin)
    return inicio, fin


def _fragmento_concat(nodo, afn):
    i1, f1 = _construir_fragmento(nodo.izquierdo, afn)
    i2, f2 = _construir_fragmento(nodo.derecho, afn)
    afn.agregar_transicion(f1, EPSILON, i2)  # pega el final del primero con el inicio del segundo
    return i1, f2
