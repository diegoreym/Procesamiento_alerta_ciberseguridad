# Procesamiento_alerta_ciberseguridad
Arboles BST, AVL, Heap Priority, min heap max heap.

# Sistema de Procesamiento de Alertas de Ciberseguridad
 
## Descripción

El sistema permite registrar, buscar, organizar y atender alertas de ciberseguridad según su nivel de riesgo. Su objetivo es aplicar estructuras de datos para gestionar incidentes informáticos de manera eficiente, priorizando las alertas más urgentes y evitando que sean procesadas más de una vez.

## Estructuras implementadas

- **BST:** árbol binario de búsqueda utilizado para almacenar registros y comparar su rendimiento.
- **AVL:** árbol binario balanceado que permite buscar alertas por identificador y realiza rotaciones para mantener su  equilibrio.
- **Max-Heap:** estructura encargada de organizar las alertas según su prioridad.
- **Cola de prioridad:** administra la consulta y extracción de alertas urgentes.
- **GestorAlerta:** integra las estructuras y controla el registro, procesamiento, cancelación y actualización de alertas.

## Funcionalidades

El programa cuenta con una interfaz de consola que permite:

- Registrar, buscar y listar alertas.
- Consultar y atender alertas según su prioridad.
- Cancelar alertas y actualizar sus datos.
- Consultar estadísticas de alertas pendientes, atendidas y canceladas.
- Ejecutar demostraciones de BST, AVL, rotaciones y Heap.

## Ejecución

Se requiere **Python 3.10 o superior**.

Desde la carpeta principal del proyecto, ejecutar:

`py -3.13 src/main.py`

## Pruebas

El proyecto utiliza `unittest` para verificar sus componentes.

Para ejecutar las pruebas automáticas:


`py -3.13 -m unittest discover -s src/tests -v`

Las 16 pruebas de la interfaz de consola fueron ejecutadas satisfactoriamente, comprobando el manejo de entradas, operaciones y errores.
