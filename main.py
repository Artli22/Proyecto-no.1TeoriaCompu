import sys

from file_utils import leer_lineas
from variables import expandir_variables
from shunting_yard import (
    convertir_a_postfix,
    CONCAT,
    set_epsilon_visible,
    epsilon_visible,
    mostrar_simbolo,
    mostrar_expresion,
)
from tree_builder import construir_arbol
from tree_renderer import dibujar_arbol, mostrar_arbol
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

# La salida usa algunos caracteres fuera de ASCII (ε, ·, arboles). En
# consolas de Windows con codificacion por defecto eso puede fallar, asi
# que se fuerza UTF-8 y, si no se puede, se reemplazan los caracteres
# problematicos en vez de cortar el programa.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def mostrar_pasos_shunting_yard(pasos):
    """Muestra los pasos del algoritmo Shunting Yard en formato detallado."""
    for paso in pasos:
        print(f"\nSímbolo leído: {mostrar_simbolo(paso['simbolo'])}")
        print(f"Acción: {paso['accion']}")

        salida_str = ' '.join(mostrar_simbolo(s) for s in paso['salida']) if paso['salida'] else "(vacía)"
        print(f"Salida: {salida_str}")

        pila_str = ' '.join(mostrar_simbolo(s) for s in paso['pila']) if paso['pila'] else "Vacía"
        print(f"Pila: {pila_str}")


def construir_automatas_para_expresion(expresion, numero):
    """Construye AFN, AFD y AFD minimizado y retorna (afn, afd, minimo).

    Genera además los PNG del árbol, del AFN, del AFD y del AFD
    minimizado en salida/.
    """
    print(f"\n{'='*44}")
    print(f"Expresión número {numero}")
    print(f"{'='*44}")
    print(f"Expresión: {mostrar_expresion(expresion)}")

    # Reemplaza las variables predefinidas (digit, digits, letter, ...) por
    # su expresion regular. Si la linea no usa ninguna, queda igual.
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
    print("\nÁrbol sintáctico:")
    arbol_ascii = mostrar_arbol(raiz)
    print(arbol_ascii)

    ruta_arbol = dibujar_arbol(raiz, f"salida/expresion_{numero}")
    print(f"Árbol guardado en: {ruta_arbol}")

    afn = construir_afn(raiz)
    ruta_afn = dibujar_afn(afn, f"salida/afn_{numero}")
    print(f"AFN guardado en: {ruta_afn}")
    print(f"  Estados: {afn.num_estados}")
    print(f"  Transiciones: {len(afn.transiciones)}")
    print(f"  Estado inicial: {afn.inicial}")
    print(f"  Estado de aceptación: {afn.aceptacion}")

    ruta_tabla_cierres = dibujar_tabla_cerraduras(afn, f"salida/tabla_cierres_{numero}")
    print(f"Tabla de cierres-{epsilon_visible()} del AFN guardada en: {ruta_tabla_cierres}")

    afd = construir_afd(afn)
    ruta_afd = dibujar_afd(afd, f"salida/afd_{numero}")
    print(f"\nAFD guardado en: {ruta_afd}")
    print(f"  Estados: {afd.num_estados()}")
    print(f"  Transiciones: {len(afd.transiciones)}")
    print(f"  Estados de aceptacion: {len(afd.aceptacion)}")

    ruta_tabla_afd = dibujar_tabla_subconjuntos(afd, afn, f"salida/tabla_subconjuntos_{numero}")
    print(f"Tabla de construccion de subconjuntos guardada en: {ruta_tabla_afd}")

    print("\nMinimizacion por particion-refinamiento (Moore):")
    minimo_particiones, historial = minimizar_afd_particiones(afd, guardar_pasos=True)
    imprimir_particiones(historial)
    ruta_min_particiones = dibujar_afd_min(
        minimo_particiones, f"salida/afd_min_particiones_{numero}"
    )
    print(f"AFD minimizado (particiones) guardado en: {ruta_min_particiones}")
    print(f"  Estados: {minimo_particiones.num_estados()}")

    print("\nMinimizacion por Myhill-Nerode (tabla de marcado, 'X' = distinguibles):")
    minimo_myhill, (estados_myhill, marcado_myhill) = minimizar_afd_myhill_nerode(
        afd, guardar_pasos=True
    )
    imprimir_tabla_myhill_nerode(estados_myhill, marcado_myhill)
    ruta_min_myhill = dibujar_afd_min(minimo_myhill, f"salida/afd_min_myhill_{numero}")
    print(f"AFD minimizado (Myhill-Nerode) guardado en: {ruta_min_myhill}")
    print(f"  Estados: {minimo_myhill.num_estados()}")

    if minimo_particiones.num_estados() == minimo_myhill.num_estados():
        print(f"\nAmbos metodos coinciden: {minimo_particiones.num_estados()} estados.")
    else:
        print("\nAviso: los dos metodos dieron un numero distinto de estados.")

    return afn, afd, minimo_particiones


def mostrar_menu(expresiones):
    """Muestra el menú principal y retorna la opción seleccionada."""
    while True:
        print(f"\n{'='*30}")
        print("Verificacion de Cadena w")
        print(f"{'='*30}")
        print("-Seleccione la expresion a verificar:")
        
        for i, expr in enumerate(expresiones, start=1):
            print(f"{i}. {mostrar_expresion(expr)}")
        
        print(f"{len(expresiones) + 1}. Salir")
        
        try:
            opcion = input("\nSeleccione una opcion: ").strip()
            opcion_num = int(opcion)

            if 1 <= opcion_num <= len(expresiones):
                return opcion_num
            elif opcion_num == len(expresiones) + 1:
                return 0
            else:
                print("Opcion invalida. Intente de nuevo.")
        except ValueError:
            print("Por favor ingrese un numero valido.")
        except (EOFError, KeyboardInterrupt):
            return 0


def verificar_cadena(numero, expresion, afn, afd, minimo):
    """Verifica w con el AFN, el AFD y el AFD minimizado y muestra los tres."""
    print(f"\n{'='*30}")
    print(f"Expresion: {mostrar_expresion(expresion)}")
    print(f"{'='*30}")

    try:
        cadena = input("Ingrese w: ")
    except KeyboardInterrupt:
        print("\nOperacion cancelada.")
        return

    alfabeto = afn.alfabeto()
    print(f"\nAlfabeto: {{{', '.join(alfabeto)}}}")
    print("Cadena: (vacia)" if cadena == "" else f"Cadena: {cadena}")

    fuera = sorted({s for s in cadena if s not in alfabeto})
    if fuera:
        print(f"Aviso: {fuera} no pertenece(n) al alfabeto; w se rechaza.")

    def marca(aceptada):
        return "aceptada" if aceptada else "rechazada"

    print(f"  AFN            -> {marca(simular(afn, cadena))}")
    print(f"  AFD            -> {marca(simular_afd(afd, cadena))}")
    print(f"  AFD minimizado -> {marca(simular_afd(minimo, cadena))}")


def preguntar_representacion_epsilon():
    """Pregunta al usuario con que simbolo mostrar epsilon (la cadena vacia)
    en todas las salidas: la letra griega 'ε' o '©' (copyright).

    Solo cambia como se IMPRIME; internamente epsilon sigue siendo el mismo
    marcador (shunting_yard.EPSILON).
    """
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
            set_epsilon_visible("ε")
            break
        if opcion == "2":
            set_epsilon_visible("©")
            break
        print("Opcion invalida. Intente de nuevo.")

    print(f"Epsilon se mostrara como: {epsilon_visible()}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo_expresiones>")
        return

    preguntar_representacion_epsilon()

    expresiones = leer_lineas(sys.argv[1])

    # Se procesa cada linea del archivo: infix -> postfix -> AFN -> AFD ->
    # AFD minimizado, con sus PNG. Los automatas quedan en cache para
    # despues probar cadenas contra cualquiera de ellos desde el menu.
    print(f"\nProcesando {len(expresiones)} expresion(es) de {sys.argv[1]}")
    automatas_cache = {}
    for i, expr in enumerate(expresiones, start=1):
        automatas_cache[i] = construir_automatas_para_expresion(expr, i)

    while True:
        opcion = mostrar_menu(expresiones)

        if opcion == 0:
            print(f"\n{'='*30}")
            print("Programa finalizado.")
            break

        numero = opcion
        afn, afd, minimo = automatas_cache[numero]

        # Verificar cadenas
        while True:
            verificar_cadena(numero, expresiones[numero - 1], afn, afd, minimo)
            
            try:
                continuar = input("\n¿Verificar otra cadena? (s/n): ").strip().lower()
                if continuar != 's':
                    break
            except KeyboardInterrupt:
                print("\nVolviendo al menu principal.")
                break


if __name__ == "__main__":
    main()
