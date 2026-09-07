from shunting_yard import EPSILON

# Analisis de la pertenencia de la cadena w a la expresion r

# Estados alcanzables sin consumir un simbolo real
def cerradura_epsilon(estados, afn):
    resultado = set(estados)
    pendientes = list(estados)

    while pendientes:
        actual = pendientes.pop()
        for t in afn.transiciones_desde(actual):
            if t.simbolo == EPSILON and t.destino not in resultado:
                resultado.add(t.destino)
                pendientes.append(t.destino)

    return resultado


# Estados alcanzables consumiendo un simbolo real 
def mover(estados, simbolo, afn):
    destinos = set()
    for estado in estados:
        for t in afn.transiciones_desde(estado):
            if t.simbolo == simbolo and t.simbolo != EPSILON:
                destinos.add(t.destino)
    return destinos

# Recorre el afn con todos los caracteres de la cadena w completa; acepta si el estado final queda entre los alcanzados
def simular(afn, cadena):
    actuales = cerradura_epsilon({afn.inicial}, afn)

    for simbolo in cadena:
        movidos = mover(actuales, simbolo, afn)
        actuales = cerradura_epsilon(movidos, afn)

    return afn.aceptacion in actuales

# Recorre el afd con todos los caracteres de la cadena w; acepta si el estado final es de aceptación
def simular_afd(afd, cadena):
    actual = afd.inicial

    for simbolo in cadena:
        siguiente = None
        for t in afd.transiciones:
            if t.origen == actual and t.simbolo == simbolo:
                siguiente = t.destino
                break
        if siguiente is None:
            return False
        actual = siguiente

    return actual in afd.aceptacion
