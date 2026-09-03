"""
Minimizacion de un AFD por refinamiento de particiones (algoritmo de Moore).

Entrada: un AFD de afd.py (estados = frozensets de estados del AFN).
Salida: un AFDMin equivalente, con estados enteros, donde los estados
equivalentes del AFD original quedan agrupados en una sola clase.

Pasos:
  1. Se pasa el AFD a IDs enteros (se reutiliza afd.mapear_afd_a_ids).
  2. Se descartan los estados no alcanzables desde el inicial.
  3. Se completa el AFD con un estado trampa temporal para que la funcion
     de transicion sea total (necesario para comparar firmas).
  4. Particion inicial: {finales} y {no finales}.
  5. Se refina: dentro de un grupo, dos estados siguen juntos solo si con
     cada simbolo van a estados del mismo grupo. Se repite hasta que
     ninguna particion cambie.
  6. Se arma el AFD cociente (un estado por clase). El estado trampa y las
     transiciones hacia el se descartan: el resultado queda como AFD
     parcial, igual que el AFD que produce afd.construir_afd.
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


def minimizar_afd(afd):
    """Devuelve un AFDMin equivalente al AFD recibido."""
    plano = mapear_afd_a_ids(afd)

    inicial = plano['inicial']
    finales = set(plano['aceptacion'])
    delta = {}
    alfabeto = set()
    for t in plano['transiciones']:
        delta[(t['origen'], t['simbolo'])] = t['destino']
        alfabeto.add(t['simbolo'])
    alfabeto = sorted(alfabeto)

    # --- Paso 2: quedarnos solo con lo alcanzable ---
    alcanzables = _alcanzables(inicial, delta, alfabeto)

    # --- Paso 3: estado trampa para volver total la transicion ---
    TRAMPA = plano['num_estados']  # id que no choca con ninguno existente

    def mueve(estado, simbolo):
        if estado == TRAMPA:
            return TRAMPA
        return delta.get((estado, simbolo), TRAMPA)

    # --- Paso 4: particion inicial (finales / no finales) ---
    finales_r = {e for e in alcanzables if e in finales}
    no_finales_r = {e for e in alcanzables if e not in finales} | {TRAMPA}
    particion = [g for g in (finales_r, no_finales_r) if g]

    # --- Paso 5: refinamiento hasta punto fijo ---
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

    # --- Paso 6: construir el AFD cociente ---
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
