from modelos import Alerta
from heap_prioridad import HeapPrioridad

class ColaPrioridad:
    def __init__(self) -> None:
        self.__heap = HeapPrioridad()

    def agregar(self, alerta: Alerta) -> None:
        self.__heap.insertar(alerta)

    def consultar_siguiente(self) -> Alerta:
        return self.__heap.ver_siguiente()

    def extraer_siguiente(self) -> Alerta:
        return self.__heap.extraer()

    def esta_vacia(self) -> bool:
        return self.__heap.esta_vacia()
