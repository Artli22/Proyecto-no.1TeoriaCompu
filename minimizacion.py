from afd import Transicion, mapear_afd_a_ids

# AFD minimizado: como AFD, pero cada estado guarda que estados del AFD original agrupo
class AFDMin:
    def __init__(self):
        self.transiciones = []
        self.estados = set()
        self.inicial = None
        self.aceptacion = set()
        self.grupos = {}

    def agregar_transicion(self, origen, simbolo, destino):
        self.transiciones.append(Transicion(origen, simbolo, destino))
        self.estados.add(origen)
        self.estados.add(destino)

    def num_estados(self):
        return len(self.estados)


# Estados alcanzables desde 'inicial' siguiendo el AFD
def _alcanzables(inicial, delta, alfabeto):
    vistos = set()
    pila = [inicial]
    while pila:
        estado = pila.pop()
        if estado in vistos:
            continue
        vistos.add(estado)
        for simbolo in alfabeto:
            if (estado, simbolo) in delta:
                pila.append(delta[(estado, simbolo)])
    return vistos


# Pasa el AFD a ids simples
def _preparar(afd):
    plano = mapear_afd_a_ids(afd)

    inicial = plano['inicial']
    finales = set(plano['aceptacion'])
    delta = {}
    alfabeto = set()
    for t in plano['transiciones']:
        delta[(t['origen'], t['simbolo'])] = t['destino']
        alfabeto.add(t['simbolo'])
    alfabeto = sorted(alfabeto)

    alcanzables = _alcanzables(inicial, delta, alfabeto)

    TRAMPA = plano['num_estados']  

    def mueve(estado, simbolo):
        if estado == TRAMPA:
            return TRAMPA
        return delta.get((estado, simbolo), TRAMPA)

    return inicial, finales, alfabeto, alcanzables, TRAMPA, mueve


# Quita el estado trampa de una particion, solo para mostrarla en pantalla
def _sin_trampa(particion, TRAMPA):
    return [
        sorted(e for e in grupo if e != TRAMPA)
        for grupo in particion
        if any(e != TRAMPA for e in grupo)
    ]


# Convierte una particion de estados equivalentes en el AFDMin final
def _construir_desde_particion(particion, inicial, finales, alfabeto, mueve, TRAMPA):
    clase_de = {}
    for i, grupo in enumerate(particion):
        for estado in grupo:
            clase_de[estado] = i

    clase_trampa = clase_de[TRAMPA]
    clase_inicial = clase_de[inicial]

    # Ids nuevos: 0 para la clase inicial
    orden = [clase_inicial]
    for c in range(len(particion)):
        if c != clase_inicial and c != clase_trampa:
            orden.append(c)
    id_nuevo = {c: k for k, c in enumerate(orden)}

    minimo = AFDMin()
    minimo.inicial = 0

    for c in orden:
        nuevo_id = id_nuevo[c]
        minimo.estados.add(nuevo_id)
        minimo.grupos[nuevo_id] = sorted(e for e in particion[c] if e != TRAMPA)
        if any(e in finales for e in particion[c]):
            minimo.aceptacion.add(nuevo_id)

    for c in orden:
        representante = next(iter(particion[c]))
        for simbolo in alfabeto:
            destino_clase = clase_de[mueve(representante, simbolo)]
            if destino_clase == clase_trampa:
                continue  # transicion al vacio: se omite (AFD parcial)
            minimo.agregar_transicion(id_nuevo[c], simbolo, id_nuevo[destino_clase])

    return minimo


# Minimizacion por particion-refinamiento 
def minimizar_afd_particiones(afd, guardar_pasos=False):
    inicial, finales, alfabeto, alcanzables, TRAMPA, mueve = _preparar(afd)

    # --- Particion inicial (finales / no finales) ---
    finales_r = {e for e in alcanzables if e in finales}
    no_finales_r = {e for e in alcanzables if e not in finales} | {TRAMPA}
    particion = [g for g in (finales_r, no_finales_r) if g]

    historial = [_sin_trampa(particion, TRAMPA)]

    # Refinamiento hasta punto fijo 
    cambio = True
    while cambio:
        cambio = False
        clase_de = {}
        for i, grupo in enumerate(particion):
            for estado in grupo:
                clase_de[estado] = i

        nueva_particion = []
        for grupo in particion:
            # Se agrupa por "firma": a que clase va cada simbolo.
            por_firma = {}
            for estado in grupo:
                firma = tuple(clase_de[mueve(estado, s)] for s in alfabeto)
                por_firma.setdefault(firma, set()).add(estado)
            if len(por_firma) > 1:
                cambio = True
            nueva_particion.extend(por_firma.values())
        particion = nueva_particion
        historial.append(_sin_trampa(particion, TRAMPA))

    minimo = _construir_desde_particion(particion, inicial, finales, alfabeto, mueve, TRAMPA)

    if guardar_pasos:
        return minimo, historial
    return minimo


minimizar_afd = minimizar_afd_particiones


# Minimizacion por Myhill-Nerode
def minimizar_afd_myhill_nerode(afd, guardar_pasos=False):
    inicial, finales, alfabeto, alcanzables, TRAMPA, mueve = _preparar(afd)

    estados = sorted(alcanzables) + [TRAMPA]
    pares = [(estados[i], estados[j]) for i in range(len(estados)) for j in range(i)]

    # Marca inicial
    marcado = set()
    for p, q in pares:
        if (p in finales) != (q in finales):
            marcado.add(frozenset((p, q)))

    # Propagar marcas hasta punto fijo 
    cambio = True
    while cambio:
        cambio = False
        for p, q in pares:
            par = frozenset((p, q))
            if par in marcado:
                continue
            for s in alfabeto:
                p2, q2 = mueve(p, s), mueve(q, s)
                if p2 != q2 and frozenset((p2, q2)) in marcado:
                    marcado.add(par)
                    cambio = True
                    break

    # --- Agrupar los pares que nunca se marcaron (equivalentes) ---
    padre = {e: e for e in estados}

    def raiz(e):
        while padre[e] != e:
            e = padre[e]
        return e

    for p, q in pares:
        if frozenset((p, q)) not in marcado:
            ra, rb = raiz(p), raiz(q)
            if ra != rb:
                padre[ra] = rb

    grupos_por_raiz = {}
    for e in estados:
        grupos_por_raiz.setdefault(raiz(e), set()).add(e)
    particion = list(grupos_por_raiz.values())

    minimo = _construir_desde_particion(particion, inicial, finales, alfabeto, mueve, TRAMPA)

    if guardar_pasos:
        estados_sin_trampa = [e for e in estados if e != TRAMPA]
        return minimo, (estados_sin_trampa, marcado)
    return minimo


# Imprime, como se fue creando cada particion 
def imprimir_particiones(historial):
    for i, grupos in enumerate(historial):
        etiqueta = "Particion inicial" if i == 0 else f"Iteracion {i}"
        texto = "  ".join(
            "{" + ", ".join(f"q{e}" for e in grupo) + "}" for grupo in grupos
        )
        print(f"  {etiqueta}: {texto}")


# Imprime la tabla de marcado de Myhill-Nerode: 
def imprimir_tabla_myhill_nerode(estados, marcado):
    ancho = 5
    encabezado = " " * ancho + "".join(
        f"q{estados[j]}".rjust(ancho) for j in range(len(estados) - 1)
    )
    print(f"  {encabezado}")
    for i in range(1, len(estados)):
        fila = f"q{estados[i]}".rjust(ancho)
        for j in range(i):
            marca = "X" if frozenset((estados[i], estados[j])) in marcado else "."
            fila += marca.rjust(ancho)
        print(f"  {fila}")


def imprimir_afd_min(minimo, nombre="AFD minimizado"):
    print(f"\n{'='*60}")
    print(nombre)
    print(f"{'='*60}")

    print(f"\nEstado inicial: {minimo.inicial}")

    print(f"\nEstados de aceptacion ({len(minimo.aceptacion)}): "
          f"{sorted(minimo.aceptacion)}")

    print(f"\nAgrupacion (estado minimizado -> estados del AFD):")
    for estado in sorted(minimo.estados):
        print(f"  {estado} <- {minimo.grupos.get(estado, [])}")

    print(f"\nTransiciones ({len(minimo.transiciones)}):")
    for t in sorted(minimo.transiciones, key=lambda x: (x.origen, x.simbolo)):
        marca = " (aceptacion)" if t.destino in minimo.aceptacion else ""
        print(f"  {t.origen} --{t.simbolo}--> {t.destino}{marca}")

    print(f"\nTotal de estados: {minimo.num_estados()}")
    print(f"{'='*60}\n")
