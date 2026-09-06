import re

from stack import Stack
from tokenizer import tokenizar_basico

# Notacion de epsilon (la cadena vacia):
#   - En la expresion de ENTRADA se escribe con la letra griega "ε".
#   - Internamente se marca cada transicion que no consume entrada con "©"
#     (codigo 169). Se usa "©" y no "ε" porque "©" se imprime bien en
#     cualquier consola y es muy improbable como simbolo real del alfabeto.
#   - Es un simbolo reservado: nunca forma parte del alfabeto del lenguaje.
#     Si alguna vez se necesita un "ε" literal, se escapa: "/ε".
EPSILON = "©"

# simbolo interno para la concatenacion implicita. No usamos "." porque
# ese caracter tambien aparece como literal en las expresiones (ej. ".com").
# Usamos un simbolo ASCII para evitar problemas de encoding en consola.
CONCAT = "&"

# --- Como se MUESTRA epsilon en las salidas ---------------------------------
# EPSILON ("©") es siempre el marcador interno; esto solo cambia con que
# caracter se imprime en pantalla, en los PNG y en las tablas. main.py lo
# pregunta al usuario al arrancar: "ε" (por defecto) o "©".
_EPSILON_VISIBLE = "ε"

# 'ε' escrito en la expresion de entrada, sin escapar con '/'.
_EPSILON_EN_ENTRADA = re.compile(r"(?<!/)ε")


def set_epsilon_visible(simbolo):
    """Fija con que caracter se muestra epsilon en todas las salidas."""
    global _EPSILON_VISIBLE
    _EPSILON_VISIBLE = simbolo


def epsilon_visible():
    """Caracter con el que se esta mostrando epsilon actualmente."""
    return _EPSILON_VISIBLE


def mostrar_simbolo(simbolo):
    """Traduce un simbolo interno a como debe verse en las salidas: el
    marcador de epsilon pasa al caracter elegido; cualquier otro va igual."""
    return _EPSILON_VISIBLE if simbolo == EPSILON else simbolo


def mostrar_expresion(expresion):
    """Devuelve la expresion lista para imprimir: el 'ε' escrito por el
    usuario (sin escapar) se reemplaza por el caracter de epsilon elegido.
    Solo para mostrar; nunca se vuelve a parsear."""
    return _EPSILON_EN_ENTRADA.sub(_EPSILON_VISIBLE, expresion)

PRECEDENCIA = {"|": 1, CONCAT: 2, "*": 3, "+": 3, "?": 3}

# '^N' y los operandos no son tokens fijos (N varia, el alfabeto tambien),
# asi que no pueden ser claves de PRECEDENCIA: se reconocen por regla (ver
# _es_elevacion) y su precedencia se agrupa aca en vez de en constantes sueltas.
PRECEDENCIA_VARIABLES = {"elevacion": 4, "operando": 5}


def _es_elevacion(token):
    """'^N' (ej. "^3") es el token que arma tokenizar_basico para 'X^N'."""
    return len(token) > 1 and token[0] == "^" and token[1:].isdigit()


def _es_escapado(token):
    """'/X' (ej. "/(", "/ε", "//") es el token que arma tokenizar_basico
    para un caracter literal escapado con '/'."""
    return len(token) == 2 and token[0] == "/"


def _resolver_escape(token):
    """Quita la '/' de escape y deja el caracter literal que representa.

    Se llama recien cuando un token ya fue clasificado como operando (ver
    convertir_a_postfix): antes de eso un token escapado debe seguir
    pareciendo distinto de su operador real (p. ej. '/(' no debe tratarse
    como el '(' de agrupacion), asi que resolverlo antes rompería esa
    distincion. Sirve por igual para cualquier simbolo reservado,
    incluido 'ε' ('/ε' -> 'ε') y el propio '/' ('//' -> '/').
    """
    return token[1] if _es_escapado(token) else token


def precedencia(token):
    """Precedencia de cualquier token, operandos incluidos, tal como se ve
    la tabla en clase: | =1, concat=2, *,+,? =3, ^ =4, variables=5 (la mas
    alta: por eso un operando nunca se compara, va directo a la salida).
    """
    if _es_elevacion(token):
        return PRECEDENCIA_VARIABLES["elevacion"]
    if token in PRECEDENCIA:
        return PRECEDENCIA[token]
    return PRECEDENCIA_VARIABLES["operando"]


def normalizar_epsilon(tokens):
    """Traduce el 'ε' de la entrada (sin escapar) al marcador interno.

    'ε' -> EPSILON (transicion que no consume entrada). Un 'ε' escapado
    ('/ε') no se toca aca: ya es un token de 2 caracteres distinto de 'ε',
    y se resuelve mas adelante junto con cualquier otro escape (ver
    _resolver_escape). En particular '©' escrito directamente tampoco se
    toca: no forma parte del alfabeto porque es el simbolo reservado para
    epsilon.
    """
    return [EPSILON if token == "ε" else token for token in tokens]


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
    return token not in ("(", ")", "|", "*", "+", "?") and not _es_elevacion(token)


def _termina_operando(token):
    return _es_operando(token) or token in (")", "*", "+", "?") or _es_elevacion(token)


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
            # el token escapado ('/x') se manda tal cual al postfix: si se
            # resolviera aca (a 'x'), un caso como '/*' quedaria como la
            # cadena "*" y tree_builder ya no podria distinguirlo del
            # operador real '*' al clasificarlo. Se resuelve recien en
            # tree_builder.py, al crear la hoja definitiva.
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