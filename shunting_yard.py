from stack import Stack
from tokenizer import tokenizar_basico

# Notacion de epsilon (la cadena vacia):
#   - En la expresion de ENTRADA se escribe con la letra griega "ε".
#   - Internamente se marca cada transicion que no consume entrada con "©"
#     (codigo 169). Se usa "©" y no "ε" porque "©" se imprime bien en
#     cualquier consola y es muy improbable como simbolo real del alfabeto.
#   - Es un simbolo reservado: nunca forma parte del alfabeto del lenguaje.
#     Si alguna vez se necesita un "ε" literal, se escapa: "\ε".
EPSILON = "©"

# simbolo interno para la concatenacion implicita. No usamos "." porque
# ese caracter tambien aparece como literal en las expresiones (ej. ".com").
# Usamos un simbolo ASCII para evitar problemas de encoding en consola.
CONCAT = "&"

PRECEDENCIA = {"|": 1, CONCAT: 2, "*": 3, "+": 3, "?": 3}


def normalizar_epsilon(tokens):
    """Traduce el epsilon de la entrada al marcador interno.

    'ε'   -> EPSILON  (transicion que no consume entrada)
    '\\ε'  -> 'ε'      (simbolo literal del alfabeto, caso poco comun)

    Cualquier otro token pasa sin cambios. En particular '©' escrito
    directamente NO se toca: no forma parte del alfabeto porque es el
    simbolo reservado para epsilon.
    """
    salida = []
    for token in tokens:
        if token == "ε":
            salida.append(EPSILON)
        elif token == "\\ε":
            salida.append("ε")
        else:
            salida.append(token)
    return salida


def agrupar_clases(tokens):
    """Fusiona una clase de caracteres [xyz] en un solo token.

    Para Shunting Yard una clase de caracteres se trata como un unico
    operando (equivale a (x|y|z)), a diferencia del validador de balanceo
    del problema 2, que si necesita ver cada corchete por separado.
    """
    resultado = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == "[":
            clase = token
            i += 1
            while i < len(tokens) and tokens[i] != "]":
                clase += tokens[i]
                i += 1
            if i < len(tokens):
                clase += tokens[i]  # el ']' de cierre
                i += 1
            resultado.append(clase)
        else:
            resultado.append(token)
            i += 1

    return resultado


def _es_operando(token):
    return token not in ("(", ")", "|", "*", "+", "?")


def _termina_operando(token):
    return _es_operando(token) or token in (")", "*", "+", "?")


def _inicia_operando(token):
    return _es_operando(token) or token == "("


def insertar_concatenacion(tokens):
    """Inserta el operador de concatenacion implicita entre dos tokens.

    En estas expresiones "ab" significa "a seguido de b", sin ningun
    simbolo entre medio. Aqui se hace explicita esa concatenacion para
    poder tratarla como un operador mas dentro de Shunting Yard.
    """
    resultado = []

    for i, token in enumerate(tokens):
        if i > 0 and _termina_operando(tokens[i - 1]) and _inicia_operando(token):
            resultado.append(CONCAT)
        resultado.append(token)

    return resultado


def convertir_a_postfix(expresion):
    """Convierte una expresion regular de infix a postfix (Shunting Yard).

    Devuelve una tupla (postfix, pasos): postfix es la lista de tokens en
    orden postfix, y pasos es una lista de dicts con info detallada de cada paso.
    """
    tokens = tokenizar_basico(expresion)
    tokens = normalizar_epsilon(tokens)
    tokens = agrupar_clases(tokens)
    tokens = insertar_concatenacion(tokens)

    pila = Stack()
    salida = []
    pasos = []

    for token in tokens:
        if token == "(":
            pila.push(token)
            pasos.append({
                "simbolo": token,
                "accion": "Insertar apertura en la pila",
                "salida": list(salida),
                "pila": pila.to_list()
            })

        elif token == ")":
            while not pila.is_empty() and pila.peek() != "(":
                operador = pila.pop()
                salida.append(operador)
            pila.pop()  # descarta el '(' que le corresponde a este ')'
            pasos.append({
                "simbolo": token,
                "accion": "Extraer operadores hasta encontrar '('",
                "salida": list(salida),
                "pila": pila.to_list()
            })

        elif token in PRECEDENCIA:
            accion = "Comparar precedencia e insertar operador"
            if token in ("*", "+", "?"):
                accion = f"Enviar operador unario '{token}' a la salida"
                salida.append(token)
                pila_estado = pila.to_list()
            else:
                while (
                    not pila.is_empty()
                    and pila.peek() != "("
                    and PRECEDENCIA.get(pila.peek(), 0) >= PRECEDENCIA[token]
                ):
                    operador = pila.pop()
                    salida.append(operador)
                pila.push(token)
                pila_estado = pila.to_list()
            
            pasos.append({
                "simbolo": token,
                "accion": accion,
                "salida": list(salida),
                "pila": pila_estado
            })

        else:
            salida.append(token)
            pasos.append({
                "simbolo": token,
                "accion": "Enviar operando a la salida",
                "salida": list(salida),
                "pila": pila.to_list()
            })

    # Vaciado final
    pasos_vaciado = []
    while not pila.is_empty():
        operador = pila.pop()
        salida.append(operador)
        pasos_vaciado.append({
            "simbolo": operador,
            "accion": f"Extraer '{operador}' en vaciado final",
            "salida": list(salida),
            "pila": pila.to_list()
        })
    
    pasos.extend(pasos_vaciado)

    return salida, pasos
