import sys

from file_utils import leer_lineas
from shunting_yard import convertir_a_postfix, CONCAT
from tree_builder import construir_arbol
from tree_renderer import dibujar_arbol, mostrar_arbol
from thompson import construir_afn
from afn_renderer import dibujar_afn
from afd import construir_afd
from afd_renderer import dibujar_afd, dibujar_afd_min
from minimizacion import minimizar_afd
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
        print(f"\nSímbolo leído: {paso['simbolo']}")
        print(f"Acción: {paso['accion']}")
        
        salida_str = ' '.join(paso['salida']) if paso['salida'] else "(vacía)"
        print(f"Salida: {salida_str}")
        
        pila_str = ' '.join(paso['pila']) if paso['pila'] else "Vacía"
        print(f"Pila: {pila_str}")


def construir_automatas_para_expresion(expresion, numero):
    """Construye AFN, AFD y AFD minimizado y retorna (afn, afd, minimo).

    Genera además los PNG del árbol, del AFN, del AFD y del AFD
    minimizado en salida/.
    """
    print(f"\n{'='*44}")
    print(f"Expresión número {numero}")
    print(f"{'='*44}")
    print(f"Expresión: {expresion}")

    postfix, pasos_postfix = convertir_a_postfix(expresion)
    print("\nPasos de Shunting Yard:")
    mostrar_pasos_shunting_yard(pasos_postfix)
    
    print(f"\nResultado:")
    postfix_str = ''.join(c if c != CONCAT else '.' for c in postfix)
    print(f"Postfix antes de convertir + y ?: {postfix_str}")
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

    afd = construir_afd(afn)
    ruta_afd = dibujar_afd(afd, f"salida/afd_{numero}")
    print(f"\nAFD guardado en: {ruta_afd}")
    print(f"  Estados: {afd.num_estados()}")
    print(f"  Transiciones: {len(afd.transiciones)}")
    print(f"  Estados de aceptacion: {len(afd.aceptacion)}")

    minimo = minimizar_afd(afd)
    ruta_min = dibujar_afd_min(minimo, f"salida/afd_min_{numero}")
    print(f"\nAFD minimizado guardado en: {ruta_min}")
    print(f"  Estados: {minimo.num_estados()}")
    print(f"  Transiciones: {len(minimo.transiciones)}")
    print(f"  Estados de aceptacion: {len(minimo.aceptacion)}")

    return afn, afd, minimo


def mostrar_menu(expresiones):
    """Muestra el menú principal y retorna la opción seleccionada."""
    while True:
        print(f"\n{'='*30}")
        print("Verificacion de Cadena w")
        print(f"{'='*30}")
        print("-Seleccione la expresion a verificar:")
        
        for i, expr in enumerate(expresiones, start=1):
            print(f"{i}. {expr}")
        
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


def verificar_cadena(numero, expresion, afn, afd, minimo):
    """Verifica w con el AFN, el AFD y el AFD minimizado y muestra los tres."""
    print(f"\n{'='*30}")
    print(f"Expresion: {expresion}")
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


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo_expresiones>")
        return

    expresiones = leer_lineas(sys.argv[1])
    automatas_cache = {}

    while True:
        opcion = mostrar_menu(expresiones)

        if opcion == 0:
            print(f"\n{'='*30}")
            print("Programa finalizado.")
            break

        numero = opcion

        # Construir los automatas si no estan en cache
        if numero not in automatas_cache:
            afn, afd, minimo = construir_automatas_para_expresion(expresiones[numero - 1], numero)
            automatas_cache[numero] = (afn, afd, minimo)
        else:
            print(f"\n(Usando automatas en cache para expresion {numero})")
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
