# Proyecto 1 - Teoria de la Computacion

Dada una expresion regular `r` y una cadena `w`, el programa:

1. Convierte `r` de infix a postfix (Shunting Yard).
2. Construye el arbol sintactico.
3. Construye un **AFN** con el algoritmo de **Thompson**.
4. Convierte el AFN en **AFD** por **construccion de subconjuntos**.
5. **Minimiza** el AFD por refinamiento de particiones (Moore).
6. Simula `w` sobre el AFN, el AFD y el AFD minimizado y dice si `w` pertenece
   al lenguaje de `r`.

Por cada expresion se generan en `salida/` las imagenes del arbol, del AFN,
del AFD y del AFD minimizado.

## Como ejecutar

Requiere Python 3, el paquete `graphviz` y el binario `dot` de Graphviz en el PATH.

```
pip install graphviz
python main.py ejemplos/problema1.txt
```

El archivo de entrada tiene **una expresion por linea**; se procesan todas.
Despues aparece un menu para probar cadenas `w` contra la expresion elegida.
La salida por cadena muestra el alfabeto y el veredicto de los tres automatas:

```
Alfabeto: {a, b}
Cadena: abb
  AFN            -> aceptada
  AFD            -> aceptada
  AFD minimizado -> aceptada
```

## Operadores soportados

| Operador | Significado                    |
|----------|-------------------------------|
| `|`      | union                         |
| (yuxtaposicion) | concatenacion (`ab`)   |
| `*`      | cero o mas                    |
| `+`      | una o mas (`a+` = `aa*`)      |
| `?`      | opcional (`a?` = `(a|ε)`)     |
| `( )`    | agrupacion                    |
| `[abc]`  | clase de caracteres = `(a|b|c)` |
| `/x`     | `x` literal (escape)          |

## Epsilon

- En la **entrada** epsilon (la cadena vacia) se escribe con la letra griega `ε`.
- **Internamente** cada transicion que no consume entrada se marca con `©`
  (`shunting_yard.EPSILON`). Se usa `©` porque se imprime bien en cualquier
  consola y es muy improbable como simbolo real del alfabeto; es un simbolo
  **reservado** y nunca forma parte del alfabeto del lenguaje.
- Si alguna vez se necesita un `ε` literal en el alfabeto, se escapa: `/ε`.

## Modulos

| Archivo            | Rol |
|--------------------|-----|
| `main.py`          | flujo principal y menu |
| `tokenizer.py`     | expresion -> lista de tokens |
| `shunting_yard.py` | infix -> postfix, expansion de `+` `?`, normalizacion de epsilon |
| `syntax_tree.py`, `tree_builder.py` | arbol sintactico desde el postfix |
| `tree_renderer.py` | PNG del arbol (y version ASCII) |
| `afn.py`           | estructura del AFN y su alfabeto |
| `thompson.py`      | postfix/arbol -> AFN (Thompson) |
| `afn_renderer.py`  | PNG del AFN |
| `afd.py`           | AFN -> AFD (subconjuntos), cerradura-epsilon |
| `minimizacion.py`  | AFD -> AFD minimizado (Moore) |
| `afd_renderer.py`  | PNG del AFD y del AFD minimizado |
| `simulador.py`     | simulacion de `w` sobre AFN (`simular`) y AFD (`simular_afd`) |
| `file_utils.py`, `stack.py` | utilidades |

## Pruebas

```
python -m unittest discover -s tests
```

Cubren minimizacion (estados equivalentes, inalcanzables, AFD ya minimo),
epsilon (en distintas posiciones, `?`, `\ε`), evaluacion de `w` (aceptada,
rechazada, vacia, simbolo fuera del alfabeto, transicion inexistente),
generacion de PNG y el flujo completo para cada linea de `ejemplos/problema1.txt`.
En todos los casos se comprueba que AFN, AFD y AFD minimizado dan el mismo
veredicto.
