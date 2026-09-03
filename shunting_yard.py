from stack import Stack
from tokenizer import tokenizar_basico

# Simbolo auxiliar que representa epsilon (la cadena vacia) en las
# expresiones de entrada. Es un simbolo reservado: nunca forma parte del
# alfabeto real del lenguaje, solo marca una transicion que no consume
# entrada. Se elige "©" (codigo 169) porque es muy improbable que aparezca
# como simbolo del lenguaje y se imprime bien en cualquier consola.
EPSILON = "©"

# simbolo interno para la concatenacion implicita. No usamos "." porque
# ese caracter tambien aparece como literal en las expresiones (ej. ".com").
# Usamos un simbolo ASCII para evitar problemas de encoding en consola.
CONCAT = "&"

PRECEDENCIA = {"|": 1, CONCAT: 2, "*": 3}


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


def _extraer_operando_previo(tokens, indice):
    """Devuelve el rango [inicio, indice) del operando justo antes de indice.

    Si el token anterior es un ')', se busca hacia atras el '(' que le
    corresponde y se toma todo ese grupo como operando. Si no, el operando
    es simplemente el token anterior (un literal, un caracter escapado o
    una clase de caracteres ya agrupada).
    """
    inicio = indice - 1

    if tokens[inicio] == ")":
        profundidad = 0
        while inicio >= 0:
            if tokens[inicio] == ")":
                profundidad += 1
            elif tokens[inicio] == "(":
                profundidad -= 1
                if profundidad == 0:
                    break
            inicio -= 1

    return inicio


def expandir_extensiones(tokens):
    """Reescribe '+' y '?' en terminos de los operadores primitivos.

    'X+' se convierte en 'XX*' y 'X?' se convierte en '(X|~)', donde X es
    el operando (o grupo) inmediatamente anterior. Asi el resto del
    algoritmo solo tiene que conocer '|', '*' y la concatenacion.
    """
    resultado = list(tokens)
    i = 0

    while i < len(resultado):
        token = resultado[i]

        if token in ("+", "?") and i > 0:
            inicio = _extraer_operando_previo(resultado, i)
            operando = resultado[inicio:i]

            if token == "+":
                nuevo = operando + operando + ["*"]
            else:
                nuevo = ["("] + operando + ["|", EPSILON] + [")"]

            resultado = resultado[:inicio] + nuevo + resultado[i + 1:]
            i = inicio + len(nuevo)
        else:
            i += 1

    return resultado


def _es_operando(token):
    return token not in ("(", ")", "|", "*")


def _termina_operando(token):
    return _es_operando(token) or token in (")", "*")


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
    tokens = agrupar_clases(tokens)
    tokens = expandir_extensiones(tokens)
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
            if token == "*":
                accion = "Enviar operador unario a la salida"
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
