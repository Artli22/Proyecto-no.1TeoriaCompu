import re

from stack import Stack
from tokenizer import tokenizar_basico

# Dentro del analisis interno epsilon siempre se identifica con ©
EPSILON = "©"

# Dentro del analisis interno la concatenacion se identifica con &
CONCAT = "&"

# Para las salidas PNG y terminal epsilon vuelve a identificarse con ε, si el usuario lo solicito
_EPSILON_VISIBLE = "ε"

_EPSILON_EN_ENTRADA = re.compile(r"(?<!/)ε")



def epsilon_visible(nuevo=None):
    global _EPSILON_VISIBLE
    if nuevo is not None:
        _EPSILON_VISIBLE = nuevo
    return _EPSILON_VISIBLE

def mostrar_simbolo(simbolo):
    return _EPSILON_VISIBLE if simbolo == EPSILON else simbolo


def mostrar_expresion(expresion):
    return _EPSILON_EN_ENTRADA.sub(_EPSILON_VISIBLE, expresion)

# Precedencia de operadores fijos 
PRECEDENCIA = {"|": 1, CONCAT: 2, "*": 3, "+": 3, "?": 3}
# Precedencia de operadores y operandos variables 
PRECEDENCIA_VARIABLES = {"elevacion": 4, "operando": 5}

# Funcion para reconocer ^
def _es_elevacion(token):
    return len(token) > 1 and token[0] == "^" and token[1:].isdigit()

# Funcion para reconocer y manejar el comportamiento de /
def _es_escapado(token):
    return len(token) == 2 and token[0] == "/"

def _resolver_escape(token):
    return token[1] if _es_escapado(token) else token

# Unificacion de ambos listados de precedencia 
def precedencia(token):
    if _es_elevacion(token):
        return PRECEDENCIA_VARIABLES["elevacion"]
    if token in PRECEDENCIA:
        return PRECEDENCIA[token]
    return PRECEDENCIA_VARIABLES["operando"]


def normalizar_epsilon(tokens):
    return [EPSILON if token == "ε" else token for token in tokens]

# Agrupa clases de caracteres [] en un solo token
def agrupar_clases(tokens):
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
                clase += tokens[i]
                i += 1
            resultado.append(clase)
        else:
            resultado.append(token)
            i += 1

    return resultado


def _es_operando(token):
    return token not in ("(", ")", "|", "*", "+", "?") and not _es_elevacion(token)


def _termina_operando(token):
    return _es_operando(token) or token in (")", "*", "+", "?") or _es_elevacion(token)


def _inicia_operando(token):
    return _es_operando(token) or token == "("

# Ingresar la concatenacion implicita
def insertar_concatenacion(tokens):
    resultado = []

    for i, token in enumerate(tokens):
        if i > 0 and _termina_operando(tokens[i - 1]) and _inicia_operando(token):
            resultado.append(CONCAT)
        resultado.append(token)

    return resultado

# Funcion para generar la salida postfix 
def convertir_a_postfix(expresion):
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
            pila.pop()  
            pasos.append({
                "simbolo": token,
                "accion": "Extraer operadores hasta encontrar '('",
                "salida": list(salida),
                "pila": pila.to_list()
            })

        elif token in PRECEDENCIA or _es_elevacion(token):
            accion = "Comparar precedencia e insertar operador"
            if token in ("*", "+", "?") or _es_elevacion(token):
                accion = f"Enviar operador unario '{token}' a la salida"
                salida.append(token)
                pila_estado = pila.to_list()
            else:
                while (
                    not pila.is_empty()
                    and pila.peek() != "("
                    and precedencia(pila.peek()) >= precedencia(token)
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