class Transicion:
    """Una arista del AFN: de 'origen' a 'destino' consumiendo 'simbolo'.

    'simbolo' puede ser un caracter normal ('a', '0', etc.) o el marcador
    de epsilon que use quien construya el AFN (Thompson usa el mismo '~'
    que ya definia shunting_yard.py para las hojas epsilon del arbol).
    """

    def __init__(self, origen, simbolo, destino):
        self.origen = origen
        self.simbolo = simbolo
        self.destino = destino


class AFN:
    """AFN que se arma de a poco: los estados son enteros 0..num_estados-1.

    No se fija inicial/aceptacion en el constructor porque, durante Thompson,
    se van creando fragmentos sueltos y recien al final se sabe cual es el
    estado inicial y cual el de aceptacion de todo el AFN.
    """

    def __init__(self):
        self.transiciones = []
        self.num_estados = 0
        self.inicial = None
        self.aceptacion = None

    def nuevo_estado(self):
        estado = self.num_estados
        self.num_estados += 1
        return estado

    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones.append(Transicion(origen, simbolo, destino))

    def transiciones_desde(self, estado):
        return [t for t in self.transiciones if t.origen == estado]
