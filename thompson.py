from shunting_yard import EPSILON, CONCAT, _es_elevacion
from afn import AFN

# Definicion general del diagrama AFN
def construir_afn(raiz):
    afn = AFN()
    inicio, fin = _construir_fragmento(raiz, afn)
    afn.inicial = inicio
    afn.aceptacion = fin
    _renumerar_desde_inicial(afn)
    return afn


def _renumerar_desde_inicial(afn):
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

    for estado in range(afn.num_estados):
        if estado not in mapeo:
            mapeo[estado] = contador
            contador += 1

    for t in afn.transiciones:
        t.origen = mapeo[t.origen]
        t.destino = mapeo[t.destino]
    afn.inicial = mapeo[afn.inicial]
    afn.aceptacion = mapeo[afn.aceptacion]

# Relacion de cada simbolo a su definicion correspondiente
def _construir_fragmento(nodo, afn):
    if nodo.es_hoja():
        return _fragmento_simbolo(nodo.valor, afn)

    if nodo.valor == "*":
        return _fragmento_estrella(nodo, afn)

    if nodo.valor == "+":
        return _fragmento_mas(nodo, afn)

    if nodo.valor == "?":
        return _fragmento_pregunta(nodo, afn)

    if _es_elevacion(nodo.valor):
        return _fragmento_elevado(nodo, afn)

    if nodo.valor == "|":
        return _fragmento_union(nodo, afn)

    if nodo.valor == CONCAT:
        return _fragmento_concat(nodo, afn)

    raise ValueError(f"operador no soportado en Thompson: '{nodo.valor}'")

# Definicion general de un estado 
def _fragmento_simbolo(simbolo, afn):
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, simbolo, fin)
    return inicio, fin

# Definicion de como manejar el operador kleene *
def _fragmento_estrella(nodo, afn):
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  
    afn.agregar_transicion(inicio, EPSILON, fin)      
    afn.agregar_transicion(f_hijo, EPSILON, i_hijo)   
    afn.agregar_transicion(f_hijo, EPSILON, fin)       
    return inicio, fin

# Definicion de como manejar el operador de kleene mas +
def _fragmento_mas(nodo, afn):
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  
    afn.agregar_transicion(f_hijo, EPSILON, i_hijo)   
    afn.agregar_transicion(f_hijo, EPSILON, fin)      
    return inicio, fin

# Definicion de como manejar el operador kleene pregunta ?
def _fragmento_pregunta(nodo, afn):
    i_hijo, f_hijo = _construir_fragmento(nodo.izquierdo, afn)
    inicio = afn.nuevo_estado()
    fin = afn.nuevo_estado()
    afn.agregar_transicion(inicio, EPSILON, i_hijo)  
    afn.agregar_transicion(inicio, EPSILON, fin)      
    afn.agregar_transicion(f_hijo, EPSILON, fin)       
    return inicio, fin

# Definicion de como manejar el operador de elevacion ^
def _fragmento_elevado(nodo, afn):
    n = int(nodo.valor[1:])

    if n == 0:
        return _fragmento_simbolo(EPSILON, afn)

    inicio, fin = _construir_fragmento(nodo.izquierdo, afn)
    for _ in range(n - 1):
        i_siguiente, f_siguiente = _construir_fragmento(nodo.izquierdo, afn)
        afn.agregar_transicion(fin, EPSILON, i_siguiente)
        fin = f_siguiente

    return inicio, fin

# Definicion de como manejar el operador de union |
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

# Definicion de como manejar el operador de concatenacion 
def _fragmento_concat(nodo, afn):
    i1, f1 = _construir_fragmento(nodo.izquierdo, afn)
    i2, f2 = _construir_fragmento(nodo.derecho, afn)
    afn.agregar_transicion(f1, EPSILON, i2)  
    return i1, f2
