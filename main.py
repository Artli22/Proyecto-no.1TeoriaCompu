import sys

from variables import expandir_variables
from shunting_yard import (
    convertir_a_postfix,
    CONCAT,
    epsilon_visible,
    mostrar_simbolo,
    mostrar_expresion,
)
from tree_builder import construir_arbol
from tree_renderer import dibujar_arbol
from thompson import construir_afn
from afn_renderer import dibujar_afn, dibujar_tabla_cerraduras
from afd import construir_afd
from afd_renderer import dibujar_afd, dibujar_afd_min, dibujar_tabla_subconjuntos
from minimizacion import (
    minimizar_afd_particiones,
    minimizar_afd_myhill_nerode,
    imprimir_particiones,
    imprimir_tabla_myhill_nerode,
)
from simulador import simular, simular_afd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _leer_lineas(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    return [linea.strip() for linea in lineas if linea.strip() != ""]


def mostrar_pasos_shunting_yard(pasos):
    for paso in pasos:
        print(f"\nSímbolo leído: {mostrar_simbolo(paso['simbolo'])}")
        print(f"Acción: {paso['accion']}")

        salida_str = ' '.join(mostrar_simbolo(s) for s in paso['salida']) if paso['salida'] else "(vacía)"
        print(f"Salida: {salida_str}")

        pila_str = ' '.join(mostrar_simbolo(s) for s in paso['pila']) if paso['pila'] else "Vacía"
        print(f"Pila: {pila_str}")


def construir_automatas_para_expresion(expresion, numero):
    print(f"\n{'='*44}")
    print(f"Expresión número {numero}")
    print(f"{'='*44}")
    print(f"Expresión: {mostrar_expresion(expresion)}")

    expresion_expandida = expandir_variables(expresion)
    if expresion_expandida != expresion:
        print(f"Expresión (variables expandidas): {mostrar_expresion(expresion_expandida)}")

    postfix, pasos_postfix = convertir_a_postfix(expresion_expandida)
    print("\nPasos de Shunting Yard:")
    mostrar_pasos_shunting_yard(pasos_postfix)
    
    print(f"\nResultado:")
    postfix_str = ''.join('.' if c == CONCAT else mostrar_simbolo(c) for c in postfix)
    print(f"Postfix final: {postfix_str}")

    raiz, pasos_arbol = construir_arbol(postfix)

    dibujar_arbol(raiz, f"salida/expresion_{numero}")

    afn = construir_afn(raiz)
    dibujar_afn(afn, f"salida/afn_{numero}")
    print("\nAFN:")
    print(f"  Estados: {afn.num_estados}")
    print(f"  Transiciones: {len(afn.transiciones)}")
    print(f"  Estado inicial: {afn.inicial}")
    print(f"  Estado de aceptación: {afn.aceptacion}")

    dibujar_tabla_cerraduras(afn, f"salida/tabla_cierres_{numero}")

    afd = construir_afd(afn)
    dibujar_afd(afd, f"salida/afd_{numero}")
    print("\nAFD:")
    print(f"  Estados: {afd.num_estados()}")
    print(f"  Transiciones: {len(afd.transiciones)}")
    print(f"  Estados de aceptacion: {len(afd.aceptacion)}")

    dibujar_tabla_subconjuntos(afd, afn, f"salida/tabla_subconjuntos_{numero}")

    print("\nMinimizacion por particion-refinamiento (Moore):")
    minimo_particiones, historial = minimizar_afd_particiones(afd, guardar_pasos=True)
    imprimir_particiones(historial)
    dibujar_afd_min(minimo_particiones, f"salida/afd_min_particiones_{numero}")
    print(f"  Estados: {minimo_particiones.num_estados()}")

    print("\nMinimizacion por Myhill-Nerode (tabla de marcado, 'X' = distinguibles):")
    minimo_myhill, (estados_myhill, marcado_myhill) = minimizar_afd_myhill_nerode(
        afd, guardar_pasos=True
    )
    imprimir_tabla_myhill_nerode(estados_myhill, marcado_myhill)
    dibujar_afd_min(minimo_myhill, f"salida/afd_min_myhill_{numero}")
    print(f"  Estados: {minimo_myhill.num_estados()}")

    if minimo_particiones.num_estados() == minimo_myhill.num_estados():
        print(f"\nAmbos metodos coinciden: {minimo_particiones.num_estados()} estados.")
    else:
        print("\nAviso: los dos metodos dieron un numero distinto de estados.")

    return afn, afd, minimo_particiones


def _leer_cadenas(ruta):
    lineas = _leer_lineas(ruta)
    return ["" if linea == "ε" else linea for linea in lineas]


def verificar_cadena(numero, expresion, cadena, afn, afd, minimo):
    print(f"\n{'='*30}")
    print(f"Expresion: {mostrar_expresion(expresion)}")
    print(f"{'='*30}")

    alfabeto = afn.alfabeto()
    print(f"\nAlfabeto: {{{', '.join(alfabeto)}}}")
    print("Cadena: (vacia)" if cadena == "" else f"Cadena: {cadena}")

    fuera = sorted({s for s in cadena if s not in alfabeto})
    if fuera:
        print(f"Aviso: {fuera} no pertenece(n) al alfabeto; w se rechaza.")

    pertenece = simular_afd(minimo, cadena)
    print(f"w {'pertenece' if pertenece else 'no pertenece'} a R")


def preguntar_representacion_epsilon():
    print(f"\n{'='*44}")
    print("Representacion de epsilon (la cadena vacia)")
    print(f"{'='*44}")
    print("¿Con que simbolo desea ver epsilon en las salidas?")
    print("  1. ε  (letra griega, por defecto)")
    print("  2. ©  (copyright)")

    while True:
        try:
            opcion = input("Seleccione una opcion [1/2]: ").strip()
        except (EOFError, KeyboardInterrupt):
            opcion = ""

        if opcion in ("", "1"):
            epsilon_visible("ε")
            break
        if opcion == "2":
            epsilon_visible("©")
            break
        print("Opcion invalida. Intente de nuevo.")

    print(f"Epsilon se mostrara como: {epsilon_visible()}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py <archivo_expresiones> <archivo_cadenas>")
        return

    preguntar_representacion_epsilon()

    expresiones = _leer_lineas(sys.argv[1])
    cadenas = _leer_cadenas(sys.argv[2])

    print(f"\nProcesando {len(expresiones)} expresion(es) de {sys.argv[1]}")
    automatas_cache = {}
    for i, expr in enumerate(expresiones, start=1):
        automatas_cache[i] = construir_automatas_para_expresion(expr, i)

    if len(expresiones) != len(cadenas):
        print(
            f"\nAviso: {len(expresiones)} expresion(es) pero {len(cadenas)} "
            f"cadena(s) en {sys.argv[2]}; se evaluaran solo las primeras "
            f"{min(len(expresiones), len(cadenas))} posicion(es)."
        )

    print(f"\n{'='*30}")
    print("Verificacion de cadena w")
    print(f"{'='*30}")
    for i, (expr, cadena) in enumerate(zip(expresiones, cadenas), start=1):
        afn, afd, minimo = automatas_cache[i]
        verificar_cadena(i, expr, cadena, afn, afd, minimo)

    print(f"\n{'='*30}")
    print("Programa finalizado.")


if __name__ == "__main__":
    main()
