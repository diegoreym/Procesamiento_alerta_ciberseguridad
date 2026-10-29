from modelos import Alerta

class NodoAVL:
    def __init__(self, alerta: Alerta) -> None:
        self.alerta: Alerta = alerta
        self.izquierdo: NodoAVL | None = None
        self.derecho: NodoAVL | None = None
        self.altura: int = 0

class ArbolAVL:
    def __init__(self) -> None:
        self.__raiz: NodoAVL | None = None

    @property
    def raiz(self) -> NodoAVL | None:
        return self.__raiz

    def __validar_id(self, id: int) -> None:
        if type(id) is not int:
            raise TypeError("El id debe ser un entero")
        if id <= 0:
            raise ValueError("El id debe ser positivo")

    def __altura_nodo(self, nodo: NodoAVL | None) -> int:
        return -1 if nodo is None else nodo.altura

    def altura(self) -> int:
        return self.__altura_nodo(self.__raiz)

    def __actualizar_altura(self, nodo: NodoAVL) -> None:
        nodo.altura = 1 + max(self.__altura_nodo(nodo.izquierdo),self.__altura_nodo(nodo.derecho),)

    def factor_balance(self, nodo: NodoAVL | None) -> int:
        if nodo is None:
            return 0
        return (self.__altura_nodo(nodo.izquierdo)- self.__altura_nodo(nodo.derecho))

    def rotar_izquierda(self, nodo: NodoAVL | None) -> NodoAVL:
        if nodo is None or nodo.derecho is None:
            raise ValueError("La rotacion izquierda requiere un hijo derecho")
        nueva_raiz = nodo.derecho
        nodo.derecho = nueva_raiz.izquierdo
        nueva_raiz.izquierdo = nodo
        self.__actualizar_altura(nodo)
        self.__actualizar_altura(nueva_raiz)
        return nueva_raiz

    def rotar_derecha(self, nodo: NodoAVL | None) -> NodoAVL:
        if nodo is None or nodo.izquierdo is None:
            raise ValueError("La rotacion derecha requiere un hijo izquierdo")
        nueva_raiz = nodo.izquierdo
        nodo.izquierdo = nueva_raiz.derecho
        nueva_raiz.derecho = nodo
        self.__actualizar_altura(nodo)
        self.__actualizar_altura(nueva_raiz)
        return nueva_raiz

    def __equilibrar(self, nodo: NodoAVL) -> NodoAVL:
        self.__actualizar_altura(nodo)
        balance = self.factor_balance(nodo)
        # El FB del hijo permite decidir tambien al eliminar, incluso si vale 0.
        if balance > 1:
            if self.factor_balance(nodo.izquierdo) < 0:
                nodo.izquierdo = self.rotar_izquierda(nodo.izquierdo)
            return self.rotar_derecha(nodo)
        if balance < -1:
            if self.factor_balance(nodo.derecho) > 0:
                nodo.derecho = self.rotar_derecha(nodo.derecho)
            return self.rotar_izquierda(nodo)
        return nodo

    def insertar(self, alerta: Alerta) -> None:
        if not isinstance(alerta, Alerta):
            raise TypeError("Debe insertar un objeto Alerta")
        self.__raiz = self.__insertar(self.__raiz, alerta)

    def __insertar(self, nodo: NodoAVL | None, alerta: Alerta) -> NodoAVL:
        if nodo is None:
            return NodoAVL(alerta)
        if alerta.id < nodo.alerta.id:
            nodo.izquierdo = self.__insertar(nodo.izquierdo, alerta)
        elif alerta.id > nodo.alerta.id:
            nodo.derecho = self.__insertar(nodo.derecho, alerta)
        else:
            raise ValueError("Existe una alerta con ese id")
        return self.__equilibrar(nodo)

    def buscar(self, id: int) -> Alerta | None:
        self.__validar_id(id)
        actual: NodoAVL | None = self.__raiz
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
        self.__raiz, eliminado = self.__eliminar(self.__raiz, id)
        return eliminado

    def __eliminar(self, nodo: NodoAVL | None, id: int) -> tuple[NodoAVL | None, bool]:
        if nodo is None:
            return None, False
        if id < nodo.alerta.id:
            nodo.izquierdo, eliminado = self.__eliminar(nodo.izquierdo, id)
        elif id > nodo.alerta.id:
            nodo.derecho, eliminado = self.__eliminar(nodo.derecho, id)
        else:
            if nodo.izquierdo is None:
                return nodo.derecho, True
            if nodo.derecho is None:
                return nodo.izquierdo, True

            sucesor = nodo.derecho
            while sucesor.izquierdo is not None:
                sucesor = sucesor.izquierdo
            nodo.alerta = sucesor.alerta
            nodo.derecho, _ = self.__eliminar(nodo.derecho, sucesor.alerta.id)
            eliminado = True

        if not eliminado:
            return nodo, False
        return self.__equilibrar(nodo), True

    def recorrido_inorden(self) -> list[Alerta]:
        resultado: list[Alerta] = []
        self.__recorrer(self.__raiz, resultado)
        return resultado

    def __recorrer(self,nodo: NodoAVL | None,resultado: list[Alerta]) -> None:
        if nodo is None:
            return
        self.__recorrer(nodo.izquierdo, resultado)
        resultado.append(nodo.alerta)
        self.__recorrer(nodo.derecho, resultado)

    def validar_balance(self) -> bool:
        valido, _ = self.__revisar(self.__raiz, None, None)
        return valido

    def __revisar(self,nodo: NodoAVL | None, minimo: int | None, maximo: int | None) -> tuple[bool, int]:
        if nodo is None:
            return True, -1
        id = nodo.alerta.id
        if minimo is not None and id <= minimo:
            return False, 0
        if maximo is not None and id >= maximo:
            return False, 0
        valida_i, altura_i = self.__revisar(nodo.izquierdo, minimo, id)
        valida_d, altura_d = self.__revisar(nodo.derecho, id, maximo)
        altura_real = 1 + max(altura_i, altura_d)
        valido = (valida_i and valida_d and abs(altura_i - altura_d) <= 1 and nodo.altura == altura_real)

        return valido, altura_real

    def visualizar(self) -> str:
        if self.__raiz is None:
            return "Arbol vacio"
        lineas: list[str] = []

        def recorrer(nodo: NodoAVL, nivel: int, lado: str) -> None:
            lineas.append(f"{'|   ' * nivel}|- [{lado}] {nodo.alerta.id}")
            if nodo.izquierdo is not None:
                recorrer(nodo.izquierdo, nivel + 1, "I")
            if nodo.derecho is not None:
                recorrer(nodo.derecho, nivel + 1, "D")
                
        recorrer(self.__raiz, 0, "R")
        return "\n".join(lineas)
