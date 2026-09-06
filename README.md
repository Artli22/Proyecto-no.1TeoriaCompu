# Proyecto 1 - Teoria de la Computacion

Dada una expresion regular `r` y una cadena `w`, el programa:

1. Convierte `r` de infix a postfix (Shunting Yard), mostrando cada paso.
2. Construye el arbol sintactico.
3. Construye un **AFN** con el algoritmo de **Thompson**.
4. Convierte el AFN en **AFD** por **construccion de subconjuntos**.
5. **Minimiza** el AFD por dos metodos y compara el resultado:
   refinamiento de particiones (Moore) y Myhill-Nerode (tabla de marcado).
6. Simula `w` sobre el AFN, el AFD y el AFD minimizado y dice si `w` pertenece
   al lenguaje de `r`.

Por cada expresion se generan en `salida/` los PNG del arbol, del AFN, de la
tabla de cierres-ε, del AFD, de la tabla de construccion de subconjuntos y de
los dos AFD minimizados (particiones y Myhill-Nerode).

## Como ejecutar

Requiere Python 3, el paquete `graphviz` y el binario `dot` de Graphviz en el PATH.

```
pip install graphviz
python main.py ejemplos/problema1.txt
```

Al arrancar pregunta con que simbolo mostrar epsilon (`ε` o `©`, ver
[Epsilon](#epsilon)). El archivo de entrada tiene **una expresion por linea**;
se procesan todas. Despues aparece un menu para probar cadenas `w` contra la
expresion elegida.
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
| `^n`     | repeticion exacta (`a^3` = `aaa`) |
| `( )`    | agrupacion                    |
| `[abc]`  | clase de caracteres = `(a|b|c)` |
| `/x`     | `x` literal (escape; `//` = `/` literal) |
| `ε`      | cadena vacia (epsilon)        |

## Variables predefinidas

En `variables.py` hay nombres que se pueden escribir dentro de una expresion;
`main.py` los reemplaza por su expresion regular antes de construir los automatas.

| Variable | Equivale a            |
|----------|-----------------------|
| `digit`  | `(0|1)`               |
| `digits` | `(0|1|2|...|9)`       |
| `letter` | `(a|b|A|B)`           |

Solo se reemplaza el nombre cuando aparece suelto (una secuencia de
letras/digitos igual **exacta** al nombre): `digit*` se expande, pero `abb`
sigue siendo literal y `digitos` no se toca. Para agregar mas variables se
edita la clase `Variables` en `variables.py`.

```
python main.py ejemplos/variables.txt
```

## Epsilon

- En la **entrada** epsilon (la cadena vacia) se escribe con la letra griega `ε`.
- **Internamente** cada transicion que no consume entrada se marca con `©`
  (`shunting_yard.EPSILON`). Se usa `©` porque se imprime bien en cualquier
  consola y es muy improbable como simbolo real del alfabeto; es un simbolo
  **reservado** y nunca forma parte del alfabeto del lenguaje.
- Si alguna vez se necesita un `ε` literal en el alfabeto, se escapa: `/ε`.
- Al arrancar, `main.py` pregunta con que simbolo mostrar epsilon en **todas
  las salidas** (pasos de Shunting Yard, postfix, arbol, diagrama del AFN,
  tabla de cierres): `ε` (por defecto) o `©`. Es solo cosmetico; el marcador
  interno no cambia.

## Ejemplos

| Archivo                 | Contenido |
|-------------------------|-----------|
| `ejemplos/problema1.txt`| expresiones del enunciado (Thompson / AFD / minimizacion) |
| `ejemplos/problema2.txt`| union grande de simbolos |
| `ejemplos/variables.txt`| uso de `digit`, `digits`, `letter` |
| `ejemplos/cadenas.txt`  | cadenas `w` de prueba |

## Modulos

| Archivo            | Rol |
|--------------------|-----|
| `main.py`          | flujo principal, pregunta de epsilon y menu |
| `variables.py`     | nombres predefinidos (`digit`, `digits`, `letter`) y su expansion |
| `tokenizer.py`     | expresion -> lista de tokens (escapes `/x`, `^n`) |
| `shunting_yard.py` | infix -> postfix, expansion de `+` `?`, epsilon y su simbolo visible |
| `syntax_tree.py`, `tree_builder.py` | arbol sintactico desde el postfix |
| `tree_renderer.py` | PNG del arbol (y version ASCII) |
| `afn.py`           | estructura del AFN y su alfabeto |
| `thompson.py`      | postfix/arbol -> AFN (Thompson) |
| `afn_renderer.py`  | PNG del AFN y de la tabla de cierres-ε |
| `afd.py`           | AFN -> AFD (subconjuntos), cerradura-epsilon |
| `minimizacion.py`  | AFD -> AFD minimizado por particiones (Moore) y Myhill-Nerode |
| `afd_renderer.py`  | PNG del AFD, del AFD minimizado y de la tabla de subconjuntos |
| `simulador.py`     | simulacion de `w` sobre AFN (`simular`) y AFD (`simular_afd`) |
| `file_utils.py`, `stack.py` | utilidades |
