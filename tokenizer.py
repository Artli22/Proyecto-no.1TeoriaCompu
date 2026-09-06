def tokenizar_basico(expresion):
    """Convierte una expresion en una lista de tokens.

    Cada caracter normal queda como su propio token. Un caracter escapado
    con '/' se agrupa junto con el caracter que escapa en un solo token
    (por ejemplo "/(" queda como un solo token de dos caracteres, distinto
    del token "(" ). Asi cualquier simbolo reservado (parentesis, |, *, +,
    ?, o incluso 'ε') se puede pedir como caracter literal del alfabeto sin
    que se confunda con su significado especial; para un '/' literal se
    escapa a si mismo: "//".

    '^' seguido de digitos (elevacion/repeticion exacta, ej. "a^12") se
    agrupa en un solo token ("^12"), igual que un escape: asi el resto del
    algoritmo lo trata como un unico operador unario, con el numero incluido.

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

        if caracter == "/" and i + 1 < len(expresion):
            tokens.append(expresion[i:i + 2])
            i += 2
        elif caracter == "^":
            fin = i + 1
            while fin < len(expresion) and expresion[fin].isdigit():
                fin += 1
            tokens.append(expresion[i:fin])
            i = fin
        else:
            tokens.append(caracter)
            i += 1

    return tokens
