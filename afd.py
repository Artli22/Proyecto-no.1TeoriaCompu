"""
Conversión de AFN a AFD usando Opción 2 (Frozensets).

La idea central: cada estado del AFD es un frozenset de estados del AFN.
Un frozenset es un conjunto inmutable que puede usarse como clave en diccionarios.

Por ejemplo:
  - Estado AFD 1 = frozenset({0, 1, 3})  → Representa los estados 0, 1, 3 del AFN
  - Estado AFD 2 = frozenset({2, 5, 7})  → Representa los estados 2, 5, 7 del AFN
"""

from shunting_yard import EPSILON


class Transicion:
    """Una transición del AFD: de 'origen' a 'destino' consumiendo 'simbolo'.
    
    A diferencia del AFN, en el AFD:
    - 'origen' y 'destino' son frozensets de estados del AFN
    - 'simbolo' NUNCA es epsilon (ya está integrado en la cerradura)
    """

    def __init__(self, origen, simbolo, destino):
        self.origen = origen       # frozenset
        self.simbolo = simbolo     # str (nunca es epsilon)
        self.destino = destino     # frozenset

    def __repr__(self):
        return f"T({self.origen} --{self.simbolo}--> {self.destino})"


class AFD:
    """AFD donde los estados son frozensets de estados del AFN original.
    
    Ventaja: cada estado "lleva su documentación" - ves exactamente qué 
    estados del AFN lo forman.
    """

    def __init__(self):
        self.transiciones = []
        self.estados = set()      # Conjunto de todos los estados (frozensets)
        self.inicial = None       # frozenset del estado inicial
        self.aceptacion = set()   # Conjunto de frozensets de aceptación

    def agregar_transicion(self, origen, simbolo, destino):
        """Agrega una transición origen --simbolo--> destino.
        
        origen y destino son frozensets.
        """
        self.transiciones.append(Transicion(origen, simbolo, destino))
        self.estados.add(origen)
        self.estados.add(destino)

    def num_estados(self):
        """Retorna la cantidad de estados del AFD."""
        return len(self.estados)


# ============================================================================
# PASO 1: Calcular epsilon-cierre (cerradura-epsilon)
# ============================================================================

def epsilon_closure(estado_q, afn):
    """Calcula el conjunto de estados alcanzables desde 'estado_q' 
    usando SOLO transiciones epsilon.
    
    Args:
        estado_q: un estado del AFN (int)
        afn: el AFN (de afn.py)
    
    Returns:
        frozenset de todos los estados alcanzables con epsilon
    
    Algoritmo: BFS/DFS simple
        1. Empezar con {estado_q}
        2. Por cada estado en el conjunto, seguir todas sus transiciones epsilon
        3. Agregar los destinos al conjunto
        4. Repetir hasta no haya nuevos estados
    """
    closure = {estado_q}
    pila = [estado_q]

    while pila:
        q = pila.pop()
        # Revisar todas las transiciones desde q
        for t in afn.transiciones_desde(q):
            # Si es una transición epsilon Y el destino es nuevo:
            if t.simbolo == EPSILON and t.destino not in closure:
                closure.add(t.destino)
                pila.append(t.destino)

    return frozenset(closure)


# ============================================================================
# PASO 2: Delta con cierre (move + epsilon_closure combinados)
# ============================================================================

def delta_con_cierre(conjunto_q, simbolo, afn):
    """Dado un conjunto de estados del AFN y un símbolo, retorna 
    el CONJUNTO (con cierre-epsilon) de estados alcanzables.
    
    Args:
        conjunto_q: frozenset de estados del AFN
        simbolo: el símbolo a consumir (str, NUNCA epsilon)
        afn: el AFN
    
    Returns:
        frozenset del conjunto con cierre-epsilon, o None si no hay transición
    
    Algoritmo en 2 pasos:
        1. Para cada estado en conjunto_q, seguir el símbolo → recolectar destinos
        2. A TODOS los destinos, aplicarles epsilon_closure
    """
    # PASO 2A: Recolectar todos los destinos sin epsilon
    destinos_sin_cierre = set()
    for q in conjunto_q:
        for t in afn.transiciones_desde(q):
            if t.simbolo == simbolo:  # Solo transiciones con ese símbolo
                destinos_sin_cierre.add(t.destino)

    # Si no hay transición, retornar None
    if not destinos_sin_cierre:
        return None

    # PASO 2B: Aplicar epsilon_closure a TODOS los destinos
    closure_completo = set()
    for q in destinos_sin_cierre:
        closure_completo.update(epsilon_closure(q, afn))

    return frozenset(closure_completo)


# ============================================================================
# PASO 3: Construcción del AFD (BFS sobre frozensets)
# ============================================================================

def construir_afd(afn):
    """Construye el AFD a partir del AFN usando la técnica de subconjuntos.
    
    Algoritmo de Construcción de Subconjuntos (Subset Construction):
    
    1. Calcular epsilon_closure del estado inicial del AFN
       → Ese frozenset es el estado inicial del AFD
    
    2. Inicializar cola con ese frozenset
    
    3. MIENTRAS la cola no esté vacía:
       a. Desencolar un conjunto de estados C
       b. Para cada símbolo en el alfabeto:
          - Calcular delta_con_cierre(C, símbolo)
          - Si el resultado es nuevo, encolarlo
          - Agregar transición en AFD
    
    4. Un estado del AFD es de aceptación si contiene 
       al estado de aceptación del AFN
    
    Args:
        afn: el AFN (de afn.py)
    
    Returns:
        AFD con sus estados, transiciones e información de aceptación
    """
    afd = AFD()

    # ==================== PASO 1: Estado Inicial ====================
    # Calcular epsilon_closure del estado inicial del AFN
    inicial_afn = afn.inicial
    inicial_con_cierre = epsilon_closure(inicial_afn, afn)

    # Este frozenset es el estado inicial del AFD
    afd.inicial = inicial_con_cierre
    afd.estados.add(inicial_con_cierre)

    # ==================== PASO 2: Extraer Alfabeto ====================
    # Recolectar todos los símbolos del AFN (excepto epsilon)
    alfabeto = set()
    for t in afn.transiciones:
        if t.simbolo != EPSILON:
            alfabeto.add(t.simbolo)

    # ==================== PASO 3: BFS sobre Frozensets ====================
    visitados = {inicial_con_cierre}  # Conjuntos que ya procesamos
    cola = [inicial_con_cierre]       # Cola de conjuntos por procesar

    while cola:
        conjunto_actual = cola.pop(0)

        # Para cada símbolo del alfabeto
        for simbolo in alfabeto:
            # Calcular a dónde se puede ir desde este conjunto con este símbolo
            siguiente_conjunto = delta_con_cierre(conjunto_actual, simbolo, afn)

            # Si hay transición válida
            if siguiente_conjunto is not None:
                # Agregar transición en el AFD
                afd.agregar_transicion(conjunto_actual, simbolo, siguiente_conjunto)

                # Si es un conjunto nuevo, agregarlo a la cola
                if siguiente_conjunto not in visitados:
                    visitados.add(siguiente_conjunto)
                    cola.append(siguiente_conjunto)

    # ==================== PASO 4: Estados de Aceptación ====================
    # Un estado del AFD acepta si contiene el estado de aceptación del AFN
    for estado_afd in visitados:
        if afn.aceptacion in estado_afd:
            afd.aceptacion.add(estado_afd)

    return afd


# ============================================================================
# UTILIDADES PARA DEBUG Y VISUALIZACIÓN
# ============================================================================

def imprimir_afd(afd, nombre="AFD"):
    """Imprime una representación textual del AFD."""
    print(f"\n{'='*60}")
    print(f"{nombre}")
    print(f"{'='*60}")
    
    print(f"\nEstado inicial:")
    print(f"  {afd.inicial}")
    
    print(f"\nEstados de aceptación ({len(afd.aceptacion)} total):")
    for estado in sorted(afd.aceptacion, key=lambda x: sorted(x)):
        print(f"  {estado}")
    
    print(f"\nTransiciones ({len(afd.transiciones)} total):")
    for t in afd.transiciones:
        marca_aceptacion = " ← ACEPTACIÓN" if t.destino in afd.aceptacion else ""
        print(f"  {t.origen} --{t.simbolo}--> {t.destino}{marca_aceptacion}")
    
    print(f"\nTotal de estados: {afd.num_estados()}")
    print(f"{'='*60}\n")


def mapear_afd_a_ids(afd):
    """Convierte un AFD con frozensets a un AFD con IDs numéricos.
    
    Útil si necesitas output más limpio para JSON/archivo.
    
    Returns:
        Diccionario con estructura similar al AFD pero con IDs numéricos
    """
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


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Este código se ejecuta si corres: python afd.py
    
    from thompson import construir_afn
    from tree_builder import construir_arbol
    from shunting_yard import convertir_a_postfix
    
    # Ejemplo: expresión (a|b)*abb
    expresion = "(a|b)*abb"
    print(f"Expresión: {expresion}")
    
    # Convertir a postfijo (devuelve tupla: (postfijo, pasos))
    tokens_postfijo, _ = convertir_a_postfix(expresion)
    print(f"Postfijo: {tokens_postfijo}")
    
    # Construir árbol y AFN
    arbol, _ = construir_arbol(tokens_postfijo)  # ← Desempacar tupla
    afn = construir_afn(arbol)
    print(f"AFN: {afn.num_estados} estados")
    
    # Construir AFD
    afd = construir_afd(afn)
    imprimir_afd(afd)
    
    # Convertir a IDs numéricos
    afd_ids = mapear_afd_a_ids(afd)
    print("\nAFD con IDs numéricos:")
    print(f"  Inicial: {afd_ids['inicial']}")
    print(f"  Aceptación: {afd_ids['aceptacion']}")
    print(f"  Transiciones:")
    for t in afd_ids['transiciones']:
        print(f"    {t['origen']} --{t['simbolo']}--> {t['destino']}")
