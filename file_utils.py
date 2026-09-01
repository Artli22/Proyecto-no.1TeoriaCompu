def leer_lineas(ruta):
    """Lee un archivo de texto y devuelve una lista con una expresion por linea.

    Se ignoran las lineas vacias (o que solo tienen espacios).
    """
    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    return [linea.strip() for linea in lineas if linea.strip() != ""]
