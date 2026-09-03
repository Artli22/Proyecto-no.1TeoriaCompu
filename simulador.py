from shunting_yard import EPSILON


def cerradura_epsilon(estados, afn):
    """Expande un conjunto de estados siguiendo todas las transiciones epsilon.

    Se usa una pila de pendientes: cada vez que se agrega un estado nuevo al
    resultado, tambien hay que revisar sus transiciones epsilon.
    """
    resultado = set(estados)
    pendientes = list(estados)

    while pendientes:
        actual = pendientes.pop()
        for t in afn.transiciones_desde(actual):
            if t.simbolo == EPSILON and t.destino not in resultado:
                resultado.add(t.destino)
                pendientes.append(t.destino)

    return resultado


def mover(estados, simbolo, afn):
    """Estados alcanzables desde 'estados' consumiendo 'simbolo' (sin cerradura).

    Las transiciones epsilon nunca consumen entrada, asi que se ignoran
    aunque 'simbolo' coincidiera con el marcador EPSILON (caso de una w que
    trae ese caracter reservado: simplemente no avanza y se rechaza).
    """
    destinos = set()
    for estado in estados:
        for t in afn.transiciones_desde(estado):
            if t.simbolo == simbolo and t.simbolo != EPSILON:
                destinos.add(t.destino)
    return destinos


def simular(afn, cadena):
    """Recorre el AFN con la cadena y dice si termina en el estado de aceptacion.

    En cada paso se hace mover() y despues cerradura_epsilon(), como en la
    construccion de subconjuntos: asi no hace falta armar un DFA aparte.
    """
    actuales = cerradura_epsilon({afn.inicial}, afn)

    for simbolo in cadena:
        movidos = mover(actuales, simbolo, afn)
        actuales = cerradura_epsilon(movidos, afn)

    return afn.aceptacion in actuales


def simular_afd(afd, cadena):
    """Recorre un AFD con la cadena. Sirve para el AFD de subconjuntos
    (afd.AFD) y para el AFD minimizado (minimizacion.AFDMin): ambos tienen
    transiciones (origen, simbolo, destino), un estado inicial y un
    conjunto de estados de aceptacion.

    Al ser determinista solo hay un estado actual. Si para el simbolo que
    toca no existe transicion, la cadena se rechaza de una vez.
    """
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
