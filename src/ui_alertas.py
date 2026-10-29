
from modelos import Alerta
from gestor import GestorAlerta


class MenuAlertas:
    """Interfaz de consola para gestionar alertas de ciberseguridad."""

    def __init__(self, sistema: GestorAlerta) -> None:
        self.sistema = sistema

    # LECTURA Y VALIDACION DE ENTRADAS
    def leer_entero(self, mensaje: str, minimo: int = 0,
                    maximo: int | None = None) -> int:
        while True:
            try:
                numero = int(input(mensaje).strip())

                if numero < minimo:
                    print(f"ERROR: Ingrese un numero desde {minimo}.")
                elif maximo is not None and numero > maximo:
                    print(f"ERROR: El maximo permitido es {maximo}.")
                else:
                    return numero

            except ValueError:
                print("ERROR: Debe ingresar un numero entero valido.")

    def leer_texto(self, mensaje: str) -> str:
        while True:
            texto = input(mensaje).strip()
            if texto:
                return texto
            print("ERROR: Este campo no puede estar vacio.")

    # 1. REGISTRAR ALERTA
    def registrar_alerta(self) -> None:
        print("\n===== REGISTRAR ALERTA =====")

        id = self.leer_entero("ID: ", 1)
        sistema = self.leer_texto("Sistema afectado: ")
        descripcion = self.leer_texto("Descripcion: ")
        riesgo = self.leer_entero("Riesgo (1-10): ", 1, 10)
        instante = self.leer_entero("Instante de llegada: ", 0)

        alerta = Alerta(id, sistema, descripcion, riesgo, instante)
        self.sistema.registrar(alerta)

        print("\nAlerta registrada correctamente.")
        print(alerta)


    # 2. BUSCAR ALERTA
    def buscar_alerta(self) -> None:
        print("\n===== BUSCAR ALERTA =====")
        id = self.leer_entero("ID a buscar: ", 1)

        alerta = self.sistema.buscar(id)

        if alerta is None:
            print("No existe una alerta con ese ID.")
        else:
            print("\nAlerta encontrada:")
            print(alerta)


    # 3. LISTAR ALERTAS
    def listar_alertas(self) -> None:
        print("\n===== LISTADO DE ALERTAS =====")
        alertas = self.sistema.listar_en_orden()

        if not alertas:
            print("No hay alertas registradas.")
            return

        for alerta in alertas:
            print(alerta)

        print(f"\nTotal de registros: {len(alertas)}")

    # 4. CONSULTAR SIGUIENTE
    def consultar_siguiente(self) -> None:
        print("\n===== SIGUIENTE ALERTA =====")
        alerta = self.sistema.consultar_siguiente()

        print("Alerta con mayor prioridad:")
        print(alerta)
        print("La alerta aun no ha sido atendida.")

    # 5. ATENDER SIGUIENTE
    def atender_siguiente(self) -> None:
        print("\n===== ATENDER ALERTA =====")
        alerta = self.sistema.procesar_alerta()

        print("Alerta atendida correctamente:")
        print(alerta)

    # 6. CANCELAR ALERTA
    def cancelar_alerta(self) -> None:
        print("\n===== CANCELAR ALERTA =====")
        id = self.leer_entero("ID a cancelar: ", 1)

        if self.sistema.cancelar(id):
            print("Alerta cancelada correctamente.")
        else:
            print("No existe una alerta con ese ID.")

    # 7. ACTUALIZAR DATOS
    def actualizar_alerta(self) -> None:
        print("\n===== ACTUALIZAR DATOS =====")
        id = self.leer_entero("ID a actualizar: ", 1)

        alerta = self.sistema.buscar(id)
        if alerta is None:
            print("No existe una alerta con ese ID.")
            return

        print("\nDatos actuales:")
        print(alerta)

        sistema = self.leer_texto("Nuevo sistema: ")
        descripcion = self.leer_texto("Nueva descripcion: ")

        self.sistema.actualizar_datos(alerta, sistema, descripcion)
        print("\nDatos actualizados correctamente.")

    # 8. ESTADISTICAS
    def mostrar_estadisticas(self) -> None:
        print("\n===== ESTADISTICAS =====")
        datos = self.sistema.estadisticas()

        print(f"Total historico : {datos['historicas']}")
        print(f"Pendientes      : {datos['pendientes']}")
        print(f"Atendidas       : {datos['atendidas']}")
        print(f"Canceladas      : {datos['canceladas']}")


    # 9. DEMOSTRACIONES
    def mostrar_demostraciones(self) -> None:
        from demostraciones import ejecutar_demostraciones
        ejecutar_demostraciones()


    # MOSTRAR MENU
    def mostrar_menu(self) -> None:
        print("\n" + "=" * 45)
        print(" SISTEMA DE ALERTAS DE CIBERSEGURIDAD")
        print("=" * 45)
        print(" 1. Registrar alerta")
        print(" 2. Buscar alerta por ID")
        print(" 3. Listar alertas ordenadas")
        print(" 4. Consultar siguiente alerta")
        print(" 5. Atender siguiente alerta")
        print(" 6. Cancelar alerta")
        print(" 7. Actualizar datos")
        print(" 8. Ver estadisticas")
        print(" 9. Demostraciones")
        print(" 0. Salir")
        print("=" * 45)


    # EJECUCION PRINCIPAL
    def ejecutar(self) -> None:
        opciones = {
            "1": self.registrar_alerta,
            "2": self.buscar_alerta,
            "3": self.listar_alertas,
            "4": self.consultar_siguiente,
            "5": self.atender_siguiente,
            "6": self.cancelar_alerta,
            "7": self.actualizar_alerta,
            "8": self.mostrar_estadisticas,
            "9": self.mostrar_demostraciones,
        }

        print("\nBienvenido al sistema de ciberseguridad.")

        while True:
            try:
                self.mostrar_menu()
                opcion = input("Seleccione una opcion: ").strip()

                if opcion == "0":
                    print("\nGracias por utilizar el sistema.")
                    break

                accion = opciones.get(opcion)

                if accion is None:
                    print("\nERROR: Opcion no valida.")
                    continue

                try:
                    accion()
                except (ValueError, TypeError, IndexError) as error:
                    print(f"\nERROR: {error}")

            except (KeyboardInterrupt, EOFError):
                print("\nPrograma finalizado por el usuario.")
                break

