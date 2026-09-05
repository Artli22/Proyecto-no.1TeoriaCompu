"""
Minimizacion de un AFD por dos metodos que deben dar el mismo resultado:

  - minimizar_afd_particiones: refinamiento de particiones (algoritmo de
    Moore). Parte de {finales}/{no finales} y separa grupos mientras haya
    estados que, con algun simbolo, terminen en grupos distintos.
  - minimizar_afd_myhill_nerode: tabla de marcado de Myhill-Nerode. Marca
    pares de estados como "distinguibles" (aceptan distinto, o llevan a un
    par ya distinguible) hasta que no se puede marcar mas; lo que nunca se
    marca es equivalente.

Entrada de ambos: un AFD de afd.py (estados = frozensets de estados del
AFN). Salida: un AFDMin equivalente, con estados enteros, donde los
estados equivalentes del AFD original quedan agrupados en una sola clase.

Pasos comunes (ver _preparar):
  1. Se pasa el AFD a IDs enteros (se reutiliza afd.mapear_afd_a_ids).
  2. Se descartan los estados no alcanzables desde el inicial.
  3. Se completa el AFD con un estado trampa temporal para que la funcion
     de transicion sea total (necesario para comparar firmas / marcar
     pares). El estado trampa y las transiciones hacia el se descartan al
     armar el resultado final (ver _construir_desde_particion): el AFDMin
     queda parcial, igual que el AFD que produce afd.construir_afd.
"""

from afd import Transicion, mapear_afd_a_ids


class AFDMin:
    """AFD minimizado con estados enteros (0, 1, 2, ...).

    Misma interfaz basica que afd.AFD para poder reutilizar el mismo
    codigo de dibujo y de simulacion. 'grupos' guarda, para cada estado
    minimizado, la lista de estados del AFD original que representa.
    """

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


def _alcanzables(inicial, delta, alfabeto):
    """Estados a los que se puede llegar desde el inicial siguiendo delta."""
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


def _preparar(afd):
    """Aplana el AFD a ids, lo completa con un estado trampa y devuelve
    todo lo que necesitan los dos metodos de minimizacion:
    (inicial, finales, alfabeto, alcanzables, TRAMPA, mueve).
    """
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

    TRAMPA = plano['num_estados']  # id que no choca con ninguno existente

    def mueve(estado, simbolo):
        if estado == TRAMPA:
            return TRAMPA
        return delta.get((estado, simbolo), TRAMPA)

    return inicial, finales, alfabeto, alcanzables, TRAMPA, mueve


def _sin_trampa(particion, TRAMPA):
    """Copia una particion (lista de conjuntos de ids) sin el estado
    trampa, para mostrarsela al usuario."""
    return [
        sorted(e for e in grupo if e != TRAMPA)
        for grupo in particion
        if any(e != TRAMPA for e in grupo)
    ]


def _construir_desde_particion(particion, inicial, finales, alfabeto, mueve, TRAMPA):
    """Arma el AFDMin cociente a partir de la particion final (lista de
    conjuntos de ids, con el estado trampa incluido en alguno de ellos).
    Comun a los dos metodos de minimizacion.
    """
    clase_de = {}
    for i, grupo in enumerate(particion):
        for estado in grupo:
            clase_de[estado] = i

    clase_trampa = clase_de[TRAMPA]
    clase_inicial = clase_de[inicial]

    # Ids nuevos: 0 para la clase inicial, luego el resto (sin la trampa).
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


def minimizar_afd_particiones(afd, guardar_pasos=False):
    """Minimiza por refinamiento de particiones (algoritmo de Moore).

    Si guardar_pasos=True, devuelve (minimo, historial): historial es la
    lista de particiones por paso (particion inicial, iteracion 1,
    iteracion 2, ...), cada una como lista de grupos de ids de estado (sin
    el estado trampa), lista para imprimir con imprimir_particiones.
    """
    inicial, finales, alfabeto, alcanzables, TRAMPA, mueve = _preparar(afd)

    # --- Particion inicial (finales / no finales) ---
    finales_r = {e for e in alcanzables if e in finales}
    no_finales_r = {e for e in alcanzables if e not in finales} | {TRAMPA}
    particion = [g for g in (finales_r, no_finales_r) if g]

    historial = [_sin_trampa(particion, TRAMPA)]

    # --- Refinamiento hasta punto fijo ---
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


# Alias: nombre historico usado por el resto del proyecto (main.py, tests).
minimizar_afd = minimizar_afd_particiones


def minimizar_afd_myhill_nerode(afd, guardar_pasos=False):
    """Minimiza con la tabla de marcado de Myhill-Nerode.

    Se marca un par de estados (p, q) como distinguible si uno acepta y el
    otro no, o si para algun simbolo llevan a un par ya marcado. Se repite
    hasta que ninguna marca nueva aparece; los pares que nunca se marcan
    son equivalentes y se agrupan (union-find).

    Si guardar_pasos=True, devuelve (minimo, (estados, marcado)): estados
    es la lista de ids considerados (sin el estado trampa) y marcado es el
    conjunto de pares distinguibles (cada uno un frozenset de 2 ids),
    listo para imprimir con imprimir_tabla_myhill_nerode.
    """
    inicial, finales, alfabeto, alcanzables, TRAMPA, mueve = _preparar(afd)

    estados = sorted(alcanzables) + [TRAMPA]
    pares = [(estados[i], estados[j]) for i in range(len(estados)) for j in range(i)]

    # --- Marca inicial: un estado acepta y el otro no ---
    marcado = set()
    for p, q in pares:
        if (p in finales) != (q in finales):
            marcado.add(frozenset((p, q)))

    # --- Propagar marcas hasta punto fijo ---
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


def imprimir_particiones(historial):
    """Imprime, paso a paso, como se van separando los grupos de estados
    en el refinamiento de particiones (un {..} por grupo, qN por estado).
    """
    for i, grupos in enumerate(historial):
        etiqueta = "Particion inicial" if i == 0 else f"Iteracion {i}"
        texto = "  ".join(
            "{" + ", ".join(f"q{e}" for e in grupo) + "}" for grupo in grupos
        )
        print(f"  {etiqueta}: {texto}")


def imprimir_tabla_myhill_nerode(estados, marcado):
    """Imprime la tabla triangular de Myhill-Nerode: filas q1..qn-1,
    columnas q0..qn-2, con 'X' donde el par es distinguible.
    """
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
    """Representacion textual del AFD minimizado (para la consola)."""
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
