"""Modelo de una alerta de ciberseguridad."""

class Alerta:
    def __init__(
        self, id: int, sistema: str, descripcion: str, riesgo: int, instante: int) -> None:
        if type(id) is not int:
            raise TypeError("El id debe ser un entero")
        if id <= 0:
            raise ValueError("El id debe ser positivo")
        if type(riesgo) is not int:
            raise TypeError("El riesgo debe ser un entero")
        if not 1 <= riesgo <= 10:
            raise ValueError("El riesgo debe estar entre 1 y 10")
        if type(instante) is not int:
            raise TypeError("El instante debe ser un entero")
        if instante < 0:
            raise ValueError("El instante no puede ser negativo")

        self.__id: int = id
        self.__riesgo: int = riesgo
        self.__instante: int = instante
        self.sistema = sistema
        self.descripcion = descripcion
        self.__estado: str = "PENDIENTE"

    @property
    def id(self) -> int:
        return self.__id

    @property
    def riesgo(self) -> int:
        return self.__riesgo

    @property
    def instante(self) -> int:
        return self.__instante

    @property
    def sistema(self) -> str:
        return self.__sistema

    @sistema.setter
    def sistema(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("El sistema debe ser una cadena")
        if not valor.strip():
            raise ValueError("El sistema no puede estar vacio")
        self.__sistema = valor.strip()

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("La descripcion debe ser una cadena")
        if not valor.strip():
            raise ValueError("La descripcion no puede estar vacia")
        self.__descripcion = valor.strip()

    @property
    def estado(self) -> str:
        return self.__estado

    @estado.setter
    def estado(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("El estado debe ser una cadena")
        if valor not in ("PENDIENTE", "ATENDIDA", "CANCELADA"):
            raise ValueError("Estado de alerta no valido")
        if self.__estado != "PENDIENTE":
            raise ValueError("No se puede cambiar una alerta atendida o cancelada")
        self.__estado = valor

    def __str__(self) -> str:
        return (
            f"ID: {self.id} | Sistema: {self.sistema} | "
            f"Descripcion: {self.descripcion} | Riesgo: {self.riesgo} | "
            f"Instante: {self.instante} | Estado: {self.estado}"
        )

