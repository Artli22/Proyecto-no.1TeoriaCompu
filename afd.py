from shunting_yard import EPSILON

# Definicion basica de un estado de transicion en afd
class Transicion:
    def __init__(self, origen, simbolo, destino):
        self.origen = origen       
        self.simbolo = simbolo     
        self.destino = destino     

    def __repr__(self):
        return f"T({self.origen} --{self.simbolo}--> {self.destino})"


# Cada estado es un frozenset de estados del AFN
class AFD:
    def __init__(self):
        self.transiciones = []
        self.estados = set()      
        self.inicial = None       
        self.aceptacion = set()   

    # Agrega una transicion y registra sus estados
    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones.append(Transicion(origen, simbolo, destino))
        self.estados.add(origen)
        self.estados.add(destino)

    def num_estados(self):
        return len(self.estados)


# Estados del AFN alcanzables desde estado_q sin consumir entrada
def epsilon_closure(estado_q, afn):
    closure = {estado_q}
    pila = [estado_q]

    while pila:
        q = pila.pop()
        for t in afn.transiciones_desde(q):
            if t.simbolo == EPSILON and t.destino not in closure:
                closure.add(t.destino)
                pila.append(t.destino)

    return frozenset(closure)


# Conjunto de estados (con cierre-epsilon) alcanzable desde conjunto_q consumiendo simbolo
def delta_con_cierre(conjunto_q, simbolo, afn):
    destinos_sin_cierre = set()
    for q in conjunto_q:
        for t in afn.transiciones_desde(q):
            if t.simbolo == simbolo:  
                destinos_sin_cierre.add(t.destino)

    if not destinos_sin_cierre:
        return None

    closure_completo = set()
    for q in destinos_sin_cierre:
        closure_completo.update(epsilon_closure(q, afn))

    return frozenset(closure_completo)


# Construccion de subconjuntos: cada estado del AFD es un frozenset de estados del AFN
def construir_afd(afn):
    afd = AFD()

    inicial_afn = afn.inicial
    inicial_con_cierre = epsilon_closure(inicial_afn, afn)

    afd.inicial = inicial_con_cierre
    afd.estados.add(inicial_con_cierre)

    alfabeto = set()
    for t in afn.transiciones:
        if t.simbolo != EPSILON:
            alfabeto.add(t.simbolo)

    visitados = {inicial_con_cierre}  
    cola = [inicial_con_cierre]      

    while cola:
        conjunto_actual = cola.pop(0)

        for simbolo in alfabeto:
            siguiente_conjunto = delta_con_cierre(conjunto_actual, simbolo, afn)

            if siguiente_conjunto is not None:
                # Agregar transición en el AFD
                afd.agregar_transicion(conjunto_actual, simbolo, siguiente_conjunto)

                # Si es un conjunto nuevo, agregarlo a la cola
                if siguiente_conjunto not in visitados:
                    visitados.add(siguiente_conjunto)
                    cola.append(siguiente_conjunto)

    for estado_afd in visitados:
        if afn.aceptacion in estado_afd:
            afd.aceptacion.add(estado_afd)

    return afd


# Traduce los estados frozensets del AFD a ids numericos simples
def mapear_afd_a_ids(afd):
    # Mapear cada frozenset a un ID
    mapeo = {}
    contador = 0
    for estado in sorted(afd.estados, key=lambda x: sorted(x)):
        mapeo[estado] = contador
        contador += 1
    
    # Construir estructura con IDs numéricos
    resultado = {
        'num_estados': len(afd.estados),
        'inicial': mapeo[afd.inicial],
        'aceptacion': [mapeo[e] for e in afd.aceptacion],
        'transiciones': [
            {
                'origen': mapeo[t.origen],
                'simbolo': t.simbolo,
                'destino': mapeo[t.destino]
            }
            for t in afd.transiciones
        ],
        'mapeo_estados': {
            str(mapeo[fs]): list(fs) 
            for fs in afd.estados
        }
    }
    
    return resultado
