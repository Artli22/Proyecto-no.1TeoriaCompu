# Metodologia para tokenizar expresiones con caracteres ^ y /
def tokenizar_basico(expresion):
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
