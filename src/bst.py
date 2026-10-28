from modelos import Alerta

class NodoBST:
    def __init__(self, alerta: Alerta) -> None:
        self.alerta: Alerta = alerta
        self.izquierdo: NodoBST | None = None
        self.derecho: NodoBST | None = None


class ArbolBST:
    def __init__(self) -> None:
        self.__raiz: NodoBST | None = None
        self.__cantidad: int = 0

    @property
    def raiz(self) -> NodoBST | None:
        return self.__raiz

    def esta_vacio(self) -> bool:
        return self.__raiz is None

    def tamanio(self) -> int:
        return self.__cantidad

    def __validar_id(self, id: int) -> None:
        if type(id) is not int:
            raise TypeError("El id debe ser un entero")
        if id <= 0:
            raise ValueError("El id debe ser positivo")

    def insertar(self, alerta: Alerta) -> None:
        if not isinstance(alerta, Alerta):
            raise TypeError("Debe insertar un objeto Alerta")

        if self.__raiz is None:
            self.__raiz = NodoBST(alerta)
            self.__cantidad += 1
            return

        actual: NodoBST = self.__raiz
        while True:
            if alerta.id == actual.alerta.id:
                raise ValueError("Existe una alerta con ese id")

            if alerta.id < actual.alerta.id:
                if actual.izquierdo is None:
                    actual.izquierdo = NodoBST(alerta)
                    break
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = NodoBST(alerta)
                    break
                actual = actual.derecho

        self.__cantidad += 1

    def buscar(self, id: int) -> Alerta | None:
        self.__validar_id(id)
        actual: NodoBST | None = self.__raiz

        while actual is not None:
            if id == actual.alerta.id:
                return actual.alerta
            if id < actual.alerta.id:
                actual = actual.izquierdo
            else:
                actual = actual.derecho

        return None

    def eliminar(self, id: int) -> bool:
        self.__validar_id(id)
        actual: NodoBST | None = self.__raiz
        anterior: NodoBST | None = None

        while actual is not None and actual.alerta.id != id:
            anterior = actual
            if id < actual.alerta.id:
                actual = actual.izquierdo
            else:
                actual = actual.derecho

        if actual is None:
            return False

        # Con dos hijos, sustituir por el sucesor y retirar su nodo original.
        if actual.izquierdo is not None and actual.derecho is not None:
            padre_sucesor: NodoBST = actual
            sucesor: NodoBST = actual.derecho
            while sucesor.izquierdo is not None:
                padre_sucesor = sucesor
                sucesor = sucesor.izquierdo

            actual.alerta = sucesor.alerta
            anterior = padre_sucesor
            actual = sucesor

        hijo: NodoBST | None = actual.izquierdo
        if hijo is None:
            hijo = actual.derecho

        if anterior is None:
            self.__raiz = hijo
        elif anterior.izquierdo is actual:
            anterior.izquierdo = hijo
        else:
            anterior.derecho = hijo

        self.__cantidad -= 1
        return True

    def recorrido_inorden(self) -> list[Alerta]:
        resultado: list[Alerta] = []
        pila: list[NodoBST] = []
        actual: NodoBST | None = self.__raiz

        while actual is not None or pila:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo

            actual = pila.pop()
            resultado.append(actual.alerta)
            actual = actual.derecho

        return resultado

    def altura(self) -> int:
        if self.__raiz is None:
            return -1

        mayor: int = 0
        pila: list[tuple[NodoBST, int]] = [(self.__raiz, 0)]
        while pila:
            nodo, nivel = pila.pop()
            mayor = max(mayor, nivel)
            if nodo.izquierdo is not None:
                pila.append((nodo.izquierdo, nivel + 1))
            if nodo.derecho is not None:
                pila.append((nodo.derecho, nivel + 1))

        return mayor

    def visualizar(self) -> str:
        if self.__raiz is None:
            return "Arbol vacio"

        lineas: list[str] = []
        pila: list[tuple[NodoBST, int, str]] = [(self.__raiz, 0, "R")]
        while pila:
            nodo, nivel, lado = pila.pop()
            lineas.append(f"{'    ' * nivel}[{lado}] {nodo.alerta.id}")
            if nodo.derecho is not None:
                pila.append((nodo.derecho, nivel + 1, "D"))
            if nodo.izquierdo is not None:
                pila.append((nodo.izquierdo, nivel + 1, "I"))

        return "\n".join(lineas)

