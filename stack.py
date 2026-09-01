class Stack:
    """Pila LIFO simple, implementada sobre una lista de Python."""

    def __init__(self):
        self._elementos = []

    def push(self, elemento):
        self._elementos.append(elemento)

    def pop(self):
        return self._elementos.pop()

    def peek(self):
        return self._elementos[-1]

    def is_empty(self):
        return len(self._elementos) == 0

    def to_list(self):
        # copia para poder mostrar el estado de la pila sin exponer la lista interna
        return list(self._elementos)

    def __len__(self):
        return len(self._elementos)
