def tokenizar_basico(expresion):
    """Convierte una expresion en una lista de tokens.

    Cada caracter normal queda como su propio token. Un caracter escapado
    con '\\' se agrupa junto con el caracter que escapa en un solo token
    (por ejemplo "\\(" queda como un solo token de dos caracteres, distinto
    del token "(" ). Asi un parentesis literal escapado nunca se confunde
    con un parentesis de agrupacion.

    Los espacios se ignoran, ya que el enunciado los usa solo para dar
    legibilidad (ej. "a | b").
    """
    tokens = []
    i = 0
    while i < len(expresion):
        caracter = expresion[i]

        if caracter == " ":
            i += 1
            continue

        if caracter == "\\" and i + 1 < len(expresion):
            tokens.append(expresion[i:i + 2])
            i += 2
        else:
            tokens.append(caracter)
            i += 1

    return tokens
