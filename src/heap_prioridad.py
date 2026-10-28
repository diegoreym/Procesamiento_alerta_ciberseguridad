from modelos import Alerta

class HeapPrioridad:
    def __init__(self) -> None:
        self.__arreglo: list[Alerta] = []

    def tamanio(self) -> int:
        return len(self.__arreglo)

    def esta_vacia(self) -> bool:
        return len(self.__arreglo) == 0

    def _padre(self, i: int) -> int:
        return (i - 1) // 2

    def _hijo_izquierdo(self, i: int) -> int:
        return 2 * i + 1

    def _hijo_derecho(self, i: int) -> int:
        return 2 * i + 2

    def _prioridad(self, alerta: Alerta) -> tuple[int, int, int]:
        # Mayor riesgo, luego menor instante (llego antes), luego menor id
        return (alerta.riesgo, -alerta.instante, -alerta.id)

    def _subir(self, indice: int) -> None:
        while indice > 0:
            indice_padre = self._padre(indice)
            
            alerta_actual = self.__arreglo[indice]
            alerta_padre = self.__arreglo[indice_padre]
            
            if self._prioridad(alerta_actual) > self._prioridad(alerta_padre):
                self.__arreglo[indice], self.__arreglo[indice_padre] = self.__arreglo[indice_padre], self.__arreglo[indice]
                indice = indice_padre
            else:
                break

    def _bajar(self, indice: int) -> None:
        n = self.tamanio()
        while True:
            izq = self._hijo_izquierdo(indice)
            der = self._hijo_derecho(indice)
            mayor = indice

            # Comparamos con el hijo izquierdo
            if izq < n and self._prioridad(self.__arreglo[izq]) > self._prioridad(self.__arreglo[mayor]):
                mayor = izq
            
            # Comparamos con el hijo derecho
            if der < n and self._prioridad(self.__arreglo[der]) > self._prioridad(self.__arreglo[mayor]):
                mayor = der
                
            # Si el mayor ya no es el padre original, intercambiamos y seguimos bajando
            if mayor != indice:
                self.__arreglo[indice], self.__arreglo[mayor] = self.__arreglo[mayor], self.__arreglo[indice]
                indice = mayor
            else:
                break

    def insertar(self, alerta: Alerta) -> None:
        self.__arreglo.append(alerta)
        self._subir(self.tamanio() - 1)

    def ver_siguiente(self) -> Alerta:
        if self.esta_vacia():
            raise IndexError("El heap está vacío")
        return self.__arreglo[0]

    def extraer(self) -> Alerta:
        if self.esta_vacia():
            raise IndexError("No se puede extraer de un heap vacío")
        
        if self.tamanio() == 1:
            return self.__arreglo.pop()
            
        alerta_maxima = self.__arreglo[0]
        
        # El último elemento pasa a la raíz y eliminamos el espacio extra al final
        self.__arreglo[0] = self.__arreglo.pop()
        
        # Hacemos que la nueva raíz caiga hasta su posición correcta
        self._bajar(0)
        
        return alerta_maxima
