from shunting_yard import EPSILON, CONCAT
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
    return afn


def _construir_fragmento(nodo, afn):
    if nodo.es_hoja():
        return _fragmento_simbolo(nodo.valor, afn)

    if nodo.valor == "*":
        return _fragmento_estrella(nodo, afn)

    if nodo.valor == "|":
        return _fragmento_union(nodo, afn)

    if nodo.valor == CONCAT:
        return _fragmento_concat(nodo, afn)

    raise ValueError(f"operador no soportado en Thompson: '{nodo.valor}'")


def _fragmento_simbolo(simbolo, afn):
    # sirve tanto para un simbolo normal (a, 0, 1...) como para una hoja
    # epsilon ('~'), ya que en ambos casos es una sola transicion i -> f
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
