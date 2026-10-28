
from modelos import Alerta
from avl import ArbolAVL
from cola_prioridad import ColaPrioridad


class GestorAlerta:
    """Administra las alertas usando AVL y cola de prioridad."""

    def __init__(self) -> None:
        self.__arbol = ArbolAVL()
        self.__cola = ColaPrioridad()

    # 1. REGISTRAR ALERTA

    def registrar(self, alerta: Alerta) -> None:
        if not isinstance(alerta, Alerta):
            raise TypeError("Debe registrar un objeto Alerta")

        if alerta.estado != "PENDIENTE":
            raise ValueError("Solo se registran alertas pendientes")

        # Comprobar duplicados antes de modificar las estructuras.
        if self.__arbol.buscar(alerta.id) is not None:
            raise ValueError("Ya existe una alerta con ese ID")

        # Ambas estructuras comparten el mismo objeto Alerta.
        self.__arbol.insertar(alerta)

        try:
            self.__cola.agregar(alerta)
        except Exception:
            # Evitar dejar una alerta registrada solo en el AVL.
            self.__arbol.eliminar(alerta.id)
            raise

    # 2. BUSCAR POR ID
    def buscar(self, id: int) -> Alerta | None:
        return self.__arbol.buscar(id)

    # 3. LISTAR ALERTAS ORDENADAS
    def listar_en_orden(self) -> list[Alerta]:
        return self.__arbol.recorrido_inorden()

    def __limpiar_obsoletas(self) -> None:
        while not self.__cola.esta_vacia():
            alerta = self.__cola.consultar_siguiente()

            if alerta.estado == "PENDIENTE":
                break

            # Descartar alertas atendidas o canceladas.
            self.__cola.extraer_siguiente()

    # 4. CONSULTAR SIGUIENTE ALERTA
    def consultar_siguiente(self) -> Alerta:
        self.__limpiar_obsoletas()

        if self.__cola.esta_vacia():
            raise IndexError("No hay alertas pendientes")

        return self.__cola.consultar_siguiente()


    # 5. PROCESAR SIGUIENTE ALERTA
    def procesar_alerta(self) -> Alerta:
        self.__limpiar_obsoletas()

        if self.__cola.esta_vacia():
            raise IndexError("No hay alertas pendientes para atender")

        alerta = self.__cola.extraer_siguiente()
        alerta.estado = "ATENDIDA"

        return alerta


    # 6. CANCELAR ALERTA
    def cancelar(self, id: int) -> bool:
        alerta = self.__arbol.buscar(id)

        if alerta is None:
            return False

        if alerta.estado != "PENDIENTE":
            raise ValueError("Solo se pueden cancelar alertas pendientes")

        alerta.estado = "CANCELADA"
        return True


    # 7. ACTUALIZAR DATOS DESCRIPTIVOS
    def actualizar_datos(
        self, id: int, sistema: str, descripcion: str
    ) -> None:

        alerta = self.__arbol.buscar(id)

        if alerta is None:
            raise ValueError("No existe una alerta con ese ID")

        # Validar ambos campos antes de modificar cualquiera.
        if not isinstance(sistema, str):
            raise TypeError("El sistema debe ser una cadena")

        if not isinstance(descripcion, str):
            raise TypeError("La descripcion debe ser una cadena")

        sistema = sistema.strip()
        descripcion = descripcion.strip()

        if not sistema:
            raise ValueError("El sistema no puede estar vacio")

        if not descripcion:
            raise ValueError("La descripcion no puede estar vacia")

        alerta.sistema = sistema
        alerta.descripcion = descripcion


    # 8. ESTADISTICAS
    def estadisticas(self) -> dict[str, int]:
        alertas = self.__arbol.recorrido_inorden()

        pendientes = 0
        atendidas = 0
        canceladas = 0

        for alerta in alertas:
            if alerta.estado == "PENDIENTE":
                pendientes += 1
            elif alerta.estado == "ATENDIDA":
                atendidas += 1
            elif alerta.estado == "CANCELADA":
                canceladas += 1

        return {
            "historicas": len(alertas),
            "pendientes": pendientes,
            "atendidas": atendidas,
            "canceladas": canceladas,
        }

