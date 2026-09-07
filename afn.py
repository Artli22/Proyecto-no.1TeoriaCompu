from shunting_yard import EPSILON

# Definicion basica de una transicion 
class Transicion:

    def __init__(self, origen, simbolo, destino):
        self.origen = origen
        self.simbolo = simbolo
        self.destino = destino

#  Estados numerados + lista de transiciones
class AFN:
    def __init__(self):
        self.transiciones = []
        self.num_estados = 0
        self.inicial = None
        self.aceptacion = None

    # Crea un estado nuevo y devuelve su id
    def nuevo_estado(self):
        estado = self.num_estados
        self.num_estados += 1
        return estado

    # Agrega una transicion al AFN
    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones.append(Transicion(origen, simbolo, destino))

    # Transiciones que salen de un estado dado
    def transiciones_desde(self, estado):
        return [t for t in self.transiciones if t.origen == estado]

    # Simbolos del afn sin incluir epsilon 
    def alfabeto(self):
        return sorted({t.simbolo for t in self.transiciones if t.simbolo != EPSILON})
