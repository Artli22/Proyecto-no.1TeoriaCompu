# Definicon de la pila Filo para shunting yard y arbol de expresiones
class Stack:
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
        return list(self._elementos)

    def __len__(self):
        return len(self._elementos)
