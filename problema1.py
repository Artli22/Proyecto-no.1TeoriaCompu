import sys

from file_utils import leer_lineas
from shunting_yard import convertir_a_postfix, CONCAT
from tree_builder import construir_arbol
from tree_renderer import dibujar_arbol, mostrar_arbol
from thompson import construir_afn
from afn_renderer import dibujar_afn
from simulador import simular


def mostrar_pasos_shunting_yard(pasos):
    """Muestra los pasos del algoritmo Shunting Yard en formato detallado."""
    for paso in pasos:
        print(f"\nSímbolo leído: {paso['simbolo']}")
        print(f"Acción: {paso['accion']}")
        
        salida_str = ' '.join(paso['salida']) if paso['salida'] else "(vacía)"
        print(f"Salida: {salida_str}")
        
        pila_str = ' '.join(paso['pila']) if paso['pila'] else "Vacía"
        print(f"Pila: {pila_str}")


def construir_afn_para_expresion(expresion, numero):
    """Construye el AFN para una expresión y retorna (afn, ruta_afn)."""
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

    return afn, ruta_afn


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


def verificar_cadena(numero, expresion, afn):
    """Verifica una cadena w contra el AFN y muestra el resultado."""
    print(f"\n{'='*30}")
    print(f"Expresion: {expresion}")
    print(f"{'='*30}")
    
    try:
        cadena = input("Ingrese w: ")
        aceptada = simular(afn, cadena)
        resultado = "si" if aceptada else "no"
        print(f"\n¿w ∈ L(r)? {resultado}")
    except KeyboardInterrupt:
        print("\nOperacion cancelada.")
        return


def main():
    if len(sys.argv) < 2:
        print("Uso: python problema1.py <archivo_expresiones>")
        return

    expresiones = leer_lineas(sys.argv[1])
    afns_cache = {}

    while True:
        opcion = mostrar_menu(expresiones)
        
        if opcion == 0:
            print(f"\n{'='*30}")
            print("Programa finalizado.")
            break
        
        numero = opcion
        
        # Construir AFN si no está en caché
        if numero not in afns_cache:
            afn, ruta_afn = construir_afn_para_expresion(expresiones[numero - 1], numero)
            afns_cache[numero] = afn
        else:
            print(f"\n(Usando AFN en caché para expresion {numero})")
            afn = afns_cache[numero]
        
        # Verificar cadenas
        while True:
            verificar_cadena(numero, expresiones[numero - 1], afn)
            
            try:
                continuar = input("\n¿Verificar otra cadena? (s/n): ").strip().lower()
                if continuar != 's':
                    break
            except KeyboardInterrupt:
                print("\nVolviendo al menu principal.")
                break


if __name__ == "__main__":
    main()
