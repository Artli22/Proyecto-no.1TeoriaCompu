"""Variables predefinidas para las expresiones regulares.

Una "variable" es un nombre corto que se escribe dentro de una expresion
(en el archivo de ejemplos o en el menu) y que el programa reemplaza por
su expresion regular equivalente antes de procesarla. Asi se puede escribir

    letter(letter|digits)*

en vez del alfabeto completo escrito a mano.

El reemplazo lo hace `expandir_variables`, que `main.py` llama sobre cada
linea del archivo de entrada antes de construir los automatas.

Reglas:
  - Solo se reemplaza un nombre que aparezca "suelto", es decir una
    secuencia maxima de letras/digitos que coincida EXACTAMENTE con el
    nombre de una variable. `abb` sigue siendo la literal "abb", y
    `digits` no se confunde con `digit` + `s`.
  - Si de verdad se necesita la literal "digit", "digits" o "letter",
    hay que escapar una de sus letras (por ejemplo di\\git) o usar una clase.
"""

import re


def _union(caracteres):
    """"abc" -> "(a|b|c)"  (grupo listo para llevar *, +, ?, concatenacion...)."""
    return "(" + "|".join(caracteres) + ")"


class Variables:
    """Catalogo de variables. Cada atributo es el nombre tal como se
    escribe en la expresion; su valor es la expresion regular que lo
    sustituye."""

    # 0 y 1 unicamente (digito binario)
    digit = _union("01")

    # digitos decimales, del 0 al 9
    digits = _union("0123456789")

    # 'a' y 'b', minusculas y mayusculas
    letter = _union("abAB")

    @classmethod
    def como_dict(cls):
        """{nombre: expresion} con todas las variables definidas arriba."""
        return {
            nombre: valor
            for nombre, valor in vars(cls).items()
            if not nombre.startswith("_") and isinstance(valor, str)
        }


# Diccionario {nombre: expresion} que usa expandir_variables.
VARIABLES = Variables.como_dict()

# Un identificador = secuencia de letras/'_' seguida de letras/digitos/'_'.
# Se captura completo para reemplazar solo cuando coincide EXACTO con una
# variable (y no, p. ej., dentro de "abbletter").
_IDENTIFICADOR = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def expandir_variables(expresion, variables=None):
    """Devuelve `expresion` con cada nombre de variable ya reemplazado por
    su expresion regular. Si no hay ninguna variable, la devuelve igual.

    >>> expandir_variables("digit*")
    '(0|1)*'
    >>> expandir_variables("abb")
    'abb'
    """
    tabla = VARIABLES if variables is None else variables

    def reemplazo(match):
        nombre = match.group(0)
        return tabla.get(nombre, nombre)

    return _IDENTIFICADOR.sub(reemplazo, expresion)


if __name__ == "__main__":
    # Pequena demostracion al ejecutar el modulo directamente.
    for nombre, valor in VARIABLES.items():
        print(f"{nombre:8} -> {valor}")
    print()
    for ejemplo in ("digit*", "(letter|digits)", "digits^3", "abb"):
        print(f"{ejemplo:18} -> {expandir_variables(ejemplo)}")
