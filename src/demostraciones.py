from modelos import Alerta
from bst import ArbolBST
from avl import ArbolAVL
from heap_prioridad import HeapPrioridad
from gestor import GestorAlerta
from datos import cargar_alertas


IDS = [90, 45, 135, 22, 67, 112, 157, 11, 5, 1]
ORDEN_INORDEN = sorted(IDS)
ORDEN_PRIORIDAD = [45, 112, 5, 22, 157, 67, 1, 90, 11, 135]


def titulo(texto: str) -> None:
    print("\n" + "=" * 55)
    print(texto)
    print("=" * 55)


def obtener_datos() -> list[Alerta]:
    """Carga los 10 registros definidos por el grupo."""
    alertas = cargar_alertas()

    if [a.id for a in alertas] != IDS:
        raise ValueError(
            "El JSON no contiene los IDs iniciales en el orden requerido."
        )

    riesgos = [4, 10, 2, 8, 6, 10, 7, 3, 9, 5]
    if [a.riesgo for a in alertas] != riesgos:
        raise ValueError("Los riesgos del JSON no coinciden con la guia.")

    if [a.id for a in sorted(
        alertas, key=lambda a: (-a.riesgo, a.instante, a.id)
    )] != ORDEN_PRIORIDAD:
        raise ValueError(
            "Los instantes del JSON no generan el orden esperado."
        )

    return alertas



# 1. CARGA DE DATOS INICIALES
def demostrar_carga() -> None:
    titulo("1. CARGA DE LAS 10 ALERTAS INICIALES")

    gestor = GestorAlerta()

    for alerta in obtener_datos():
        gestor.registrar(alerta)
        print(f"Registrada alerta ID {alerta.id} - Riesgo {alerta.riesgo}")

    print("\nREGISTROS ORDENADOS POR ID:")
    for alerta in gestor.listar_en_orden():
        print(alerta)

    print("\nESTADISTICAS:")
    print(gestor.estadisticas())

    ids = [a.id for a in gestor.listar_en_orden()]
    print("\nValidacion de los 10 registros:",
          "CORRECTA" if ids == ORDEN_INORDEN else "FALLIDA")



# 2. COMPARACION BST Y AVL
def demostrar_arboles() -> None:
    titulo("2. COMPARACION BST VS AVL")

    bst = ArbolBST()
    avl = ArbolAVL()

    for alerta in obtener_datos():
        bst.insertar(alerta)
        avl.insertar(alerta)

    print("\nESTRUCTURA BST:")
    print(bst.visualizar())

    print("\nESTRUCTURA AVL:")
    print(avl.visualizar())

    ids_bst = [a.id for a in bst.recorrido_inorden()]
    ids_avl = [a.id for a in avl.recorrido_inorden()]

    print("\nRECORRIDO INORDEN BST:", ids_bst)
    print("RECORRIDO INORDEN AVL:", ids_avl)

    print("\nALTURAS:")
    print("Altura BST:", bst.altura())
    print("Altura AVL:", avl.altura())

    print("\nVALIDACIONES:")
    print("Mismo recorrido ordenado:",
          ids_bst == ids_avl == ORDEN_INORDEN)
    print("AVL balanceado:", avl.validar_balance())

    print("\nBUSQUEDAS DE PRUEBA:")
    for id in (90, 67, 1, 999):
        encontrado_bst = bst.buscar(id)
        encontrado_avl = avl.buscar(id)

        print(
            f"ID {id}: "
            f"BST={'SI' if encontrado_bst else 'NO'} | "
            f"AVL={'SI' if encontrado_avl else 'NO'}"
        )

    print("\nCOMPARACION CON INSERCIONES CRECIENTES:")
    for n in (100, 500, 1000):
        bst_prueba = ArbolBST()
        avl_prueba = ArbolAVL()

        for id in range(1, n + 1):
            alerta = Alerta(id, "Prueba", f"Alerta {id}", 5, id)
            bst_prueba.insertar(alerta)
            avl_prueba.insertar(alerta)

        print(
            f"n={n}: BST={bst_prueba.altura()} | "
            f"AVL={avl_prueba.altura()} | "
            f"Balance correcto={avl_prueba.validar_balance()}"
        )



# 3. ROTACIONES AVL
def demostrar_rotaciones() -> None:
    titulo("3. DEMOSTRACION DE ROTACIONES AVL")

    casos = {
        "LL": [30, 20, 10],
        "RR": [10, 20, 30],
        "LR": [30, 10, 20],
        "RL": [10, 30, 20],
    }

    explicaciones = {
        "LL": "Desequilibrio izquierdo-izquierdo: giro a la derecha.",
        "RR": "Desequilibrio derecho-derecho: giro a la izquierda.",
        "LR": "Giro izquierdo en el hijo y derecho en el ancestro.",
        "RL": "Giro derecho en el hijo y izquierdo en el ancestro.",
    }

    for tipo, secuencia in casos.items():
        print(f"\n{'-' * 50}")
        print(f"ROTACION {tipo}")
        print(f"Secuencia: {secuencia}")
        print(explicaciones[tipo])

        arbol = ArbolAVL()

        # Se insertan dos elementos para mostrar el estado previo.
        for id in secuencia[:2]:
            arbol.insertar(
                Alerta(id, "Prueba", f"Alerta {id}", 5, id)
            )

        print("\nArbol antes de insertar el tercer elemento:")
        print(arbol.visualizar())

        # Esta insercion desencadena el rebalanceo real.
        ultimo = secuencia[2]
        print(f"\nInsertando {ultimo}...")
        arbol.insertar(
            Alerta(ultimo, "Prueba", f"Alerta {ultimo}", 5, ultimo)
        )

        print("\nArbol despues del rebalanceo:")
        print(arbol.visualizar())

        recorrido = [a.id for a in arbol.recorrido_inorden()]
        correcto = (
            arbol.raiz.alerta.id == 20
            and recorrido == [10, 20, 30]
            and arbol.validar_balance()
        )

        print("Recorrido inorden:", recorrido)
        print("Altura:", arbol.altura())
        print("Resultado:", "CORRECTO" if correcto else "FALLIDO")



# 4. HEAP Y PRIORIDADES
def demostrar_heap() -> None:
    titulo("4. DEMOSTRACION DE PRIORIDAD DEL HEAP")

    heap = HeapPrioridad()

    print("\nINSERTANDO LAS 10 ALERTAS:")
    for alerta in obtener_datos():
        heap.insertar(alerta)
        print(
            f"ID {alerta.id:3} | "
            f"Riesgo {alerta.riesgo:2} | "
            f"Instante {alerta.instante:2}"
        )

    print("\nSIGUIENTE ALERTA SIN EXTRAER:")
    siguiente = heap.ver_siguiente()
    print(siguiente)

    print("\nEXTRAYENDO LAS PRIMERAS 5 ALERTAS:")
    extraidas = []

    for numero in range(1, 6):
        alerta = heap.extraer()
        extraidas.append(alerta.id)
        print(
            f"{numero}. ID {alerta.id} | "
            f"Riesgo {alerta.riesgo} | "
            f"Instante {alerta.instante}"
        )

    print("\nOrden obtenido:", extraidas)
    print("Orden esperado:", ORDEN_PRIORIDAD[:5])
    print("Resultado:",
          "CORRECTO" if extraidas == ORDEN_PRIORIDAD[:5]
          else "FALLIDO")

    print("Elementos restantes:", heap.tamanio())

    # Empate completo: gana el menor ID.
    print("\nPRUEBA DE DESEMPATE POR ID:")
    heap_empate = HeapPrioridad()
    heap_empate.insertar(Alerta(99, "Test", "Empate", 10, 2))
    heap_empate.insertar(Alerta(45, "Test", "Empate", 10, 2))
    print("Primer ID:", heap_empate.extraer().id)
    print("Segundo ID:", heap_empate.extraer().id)



# 5. CANCELACION Y NO REPROCESO
def demostrar_cancelacion() -> None:
    titulo("5. CANCELACION Y NO REPROCESO")

    gestor = GestorAlerta()

    for alerta in obtener_datos():
        gestor.registrar(alerta)

    print("\nPRIMERA ALERTA PENDIENTE:")
    print(gestor.consultar_siguiente())

    print("\nATENDIENDO PRIMERA ALERTA:")
    primera = gestor.procesar_alerta()
    print("Atendida:", primera.id)
    print("Estado:", primera.estado)

    print("\nCANCELANDO ALERTA 112:")
    print("Cancelacion exitosa:", gestor.cancelar(112))
    print("Estado de ID 112:", gestor.buscar(112).estado)

    print("\nCONSULTANDO SIGUIENTE ALERTA:")
    siguiente = gestor.consultar_siguiente()
    print("Siguiente ID:", siguiente.id)

    print("\nATENDIENDO LAS RESTANTES:")
    procesadas = [primera.id]

    while True:
        try:
            alerta = gestor.procesar_alerta()
            procesadas.append(alerta.id)
            print(f"Atendida ID {alerta.id}")
        except IndexError:
            break

    print("\nIDs procesados:", procesadas)
    print("ID 112 no fue procesado:", 112 not in procesadas)
    print("Ningun ID se repitio:",
          len(procesadas) == len(set(procesadas)))

    print("\nHISTORIAL DE ID 112:")
    print(gestor.buscar(112))

    print("\nESTADISTICAS FINALES:")
    print(gestor.estadisticas())

    try:
        gestor.procesar_alerta()
    except IndexError as error:
        print("\nCola sin pendientes controlada:", error)



# 6. TODAS LAS DEMOSTRACIONES
def demostrar_todo() -> None:
    demostrar_carga()
    demostrar_arboles()
    demostrar_rotaciones()
    demostrar_heap()
    demostrar_cancelacion()
    titulo("TODAS LAS DEMOSTRACIONES FINALIZADAS")


# SUBMENU INTERACTIVO
def ejecutar_demostraciones() -> None:
    opciones = {
        "1": demostrar_carga,
        "2": demostrar_arboles,
        "3": demostrar_rotaciones,
        "4": demostrar_heap,
        "5": demostrar_cancelacion,
        "6": demostrar_todo,
    }

    while True:
        titulo("MENU DE DEMOSTRACIONES")
        print("1. Cargar las 10 alertas iniciales")
        print("2. Comparar arbol BST y AVL")
        print("3. Demostrar rotaciones AVL")
        print("4. Demostrar prioridad del Heap")
        print("5. Demostrar cancelacion y no reproceso")
        print("6. Ejecutar todas las demostraciones")
        print("0. Volver al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == "0":
            print("\nRegresando al menu principal...")
            return

        accion = opciones.get(opcion)

        if accion is None:
            print("\nERROR: Opcion no valida.")
            continue

        try:
            accion()
        except (ValueError, TypeError, IndexError, OSError) as error:
            print(f"\nERROR EN LA DEMOSTRACION: {error}")

        input("\nPresione ENTER para continuar...")


if __name__ == "__main__":
    try:
        ejecutar_demostraciones()
    except (KeyboardInterrupt, EOFError):
        print("\nDemostraciones finalizadas.")

