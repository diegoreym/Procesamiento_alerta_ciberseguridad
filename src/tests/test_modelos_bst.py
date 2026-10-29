"""Pruebas de Garrido: modelo Alerta, ArbolBST y datos (carga/generacion)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from random import Random

# Resolver la carpeta src antes de importar (funciona con tests en src/tests
# o en tests/ de la raiz del proyecto).
_AQUI = Path(__file__).resolve().parent
for _carpeta in (_AQUI.parent, _AQUI.parent / "src"):
    if (_carpeta / "modelos.py").exists():
        sys.path.insert(0, str(_carpeta))
        break

from modelos import Alerta
from bst import ArbolBST
from datos import cargar_alertas, generar_alertas, generar_archivos


IDS_INICIALES = [90, 45, 135, 22, 67, 112, 157, 11, 5, 1]
RIESGOS_INICIALES = [4, 10, 2, 8, 6, 10, 7, 3, 9, 5]
ORDEN_INORDEN = [1, 5, 11, 22, 45, 67, 90, 112, 135, 157]
ORDEN_PRIORIDAD = [45, 112, 5, 22, 157, 67, 1, 90, 11, 135]


def crear(id, riesgo=5, instante=None, sistema="Sistema", descripcion="Desc"):
    return Alerta(id, sistema, descripcion, riesgo,
                  id if instante is None else instante)


def arbol_con(ids):
    arbol = ArbolBST()
    for id in ids:
        arbol.insertar(crear(id))
    return arbol


def ids_inorden(arbol):
    return [a.id for a in arbol.recorrido_inorden()]


def cumple_orden_bst(arbol):
    """Comprueba izquierdo < nodo < derecho en todo el arbol (iterativo)."""
    if arbol.raiz is None:
        return True
    pila = [(arbol.raiz, None, None)]
    while pila:
        nodo, minimo, maximo = pila.pop()
        id = nodo.alerta.id
        if minimo is not None and id <= minimo:
            return False
        if maximo is not None and id >= maximo:
            return False
        if nodo.izquierdo is not None:
            pila.append((nodo.izquierdo, minimo, id))
        if nodo.derecho is not None:
            pila.append((nodo.derecho, id, maximo))
    return True


# ---------------------------------------------------------------- ALERTA
class TestAlerta(unittest.TestCase):

    def test_creacion_valida(self):
        a = Alerta(45, "ERP", "Acceso privilegiado anomalo", 10, 2)
        self.assertEqual(a.id, 45)
        self.assertEqual(a.sistema, "ERP")
        self.assertEqual(a.descripcion, "Acceso privilegiado anomalo")
        self.assertEqual(a.riesgo, 10)
        self.assertEqual(a.instante, 2)

    def test_estado_inicial_pendiente(self):
        self.assertEqual(crear(1).estado, "PENDIENTE")

    def test_id_no_positivo(self):
        for id in (0, -1, -100):
            with self.subTest(id=id):
                with self.assertRaises(ValueError):
                    Alerta(id, "S", "D", 5, 1)

    def test_id_tipo_invalido_rechaza_bool(self):
        for id in (True, False, "5", 1.5, None):
            with self.subTest(id=id):
                with self.assertRaises(TypeError):
                    Alerta(id, "S", "D", 5, 1)

    def test_riesgo_fuera_de_rango(self):
        for riesgo in (0, 11, -3, 100):
            with self.subTest(riesgo=riesgo):
                with self.assertRaises(ValueError):
                    Alerta(1, "S", "D", riesgo, 1)

    def test_riesgo_limites_validos(self):
        self.assertEqual(Alerta(1, "S", "D", 1, 1).riesgo, 1)
        self.assertEqual(Alerta(1, "S", "D", 10, 1).riesgo, 10)

    def test_riesgo_tipo_invalido_rechaza_bool(self):
        for riesgo in (True, False, "5", 5.0, None):
            with self.subTest(riesgo=riesgo):
                with self.assertRaises(TypeError):
                    Alerta(1, "S", "D", riesgo, 1)

    def test_instante_negativo(self):
        with self.assertRaises(ValueError):
            Alerta(1, "S", "D", 5, -1)

    def test_instante_cero_valido(self):
        self.assertEqual(Alerta(1, "S", "D", 5, 0).instante, 0)

    def test_instante_tipo_invalido_rechaza_bool(self):
        for instante in (True, False, "1", 1.0, None):
            with self.subTest(instante=instante):
                with self.assertRaises(TypeError):
                    Alerta(1, "S", "D", 5, instante)

    def test_sistema_descripcion_vacios(self):
        for vacio in ("", "   ", "\t\n"):
            with self.subTest(vacio=repr(vacio)):
                with self.assertRaises(ValueError):
                    Alerta(1, vacio, "D", 5, 1)
                with self.assertRaises(ValueError):
                    Alerta(1, "S", vacio, 5, 1)

    def test_sistema_descripcion_tipo_invalido(self):
        with self.assertRaises(TypeError):
            Alerta(1, 123, "D", 5, 1)
        with self.assertRaises(TypeError):
            Alerta(1, "S", None, 5, 1)

    def test_texto_se_limpia_de_espacios(self):
        a = Alerta(1, "  VPN  ", "  Intento  ", 5, 1)
        self.assertEqual(a.sistema, "VPN")
        self.assertEqual(a.descripcion, "Intento")

    def test_id_riesgo_instante_no_se_modifican(self):
        a = crear(7)
        for campo in ("id", "riesgo", "instante"):
            with self.subTest(campo=campo):
                with self.assertRaises(AttributeError):
                    setattr(a, campo, 99)
        self.assertEqual((a.id, a.riesgo, a.instante), (7, 5, 7))

    def test_actualizar_sistema_y_descripcion_mantiene_id(self):
        a = crear(7)
        a.sistema = "DNS"
        a.descripcion = "Dominio raro"
        self.assertEqual(a.sistema, "DNS")
        self.assertEqual(a.descripcion, "Dominio raro")
        self.assertEqual(a.id, 7)

    def test_actualizar_invalido_no_modifica(self):
        a = crear(7, sistema="Web", descripcion="Sondeo")
        with self.assertRaises(ValueError):
            a.sistema = "  "
        with self.assertRaises(ValueError):
            a.descripcion = ""
        self.assertEqual(a.sistema, "Web")
        self.assertEqual(a.descripcion, "Sondeo")

    def test_cambio_de_estado(self):
        a = crear(1)
        a.estado = "ATENDIDA"
        self.assertEqual(a.estado, "ATENDIDA")
        b = crear(2)
        b.estado = "CANCELADA"
        self.assertEqual(b.estado, "CANCELADA")

    def test_estado_invalido(self):
        a = crear(1)
        with self.assertRaises(ValueError):
            a.estado = "OTRO"
        with self.assertRaises(TypeError):
            a.estado = 5
        self.assertEqual(a.estado, "PENDIENTE")

    def test_str_legible(self):
        texto = str(Alerta(45, "ERP", "Acceso anomalo", 10, 2))
        for parte in ("45", "ERP", "Acceso anomalo", "10", "2", "PENDIENTE"):
            self.assertIn(parte, texto)


# ------------------------------------------------------------------- BST
class TestBSTBasico(unittest.TestCase):

    def test_arbol_vacio(self):
        arbol = ArbolBST()
        self.assertTrue(arbol.esta_vacio())
        self.assertEqual(arbol.tamanio(), 0)
        self.assertIsNone(arbol.raiz)
        self.assertEqual(arbol.recorrido_inorden(), [])
        self.assertEqual(arbol.altura(), -1)

    def test_buscar_en_arbol_vacio_retorna_none(self):
        self.assertIsNone(ArbolBST().buscar(1))

    def test_insertar_y_buscar_existente(self):
        arbol = ArbolBST()
        a = crear(10)
        arbol.insertar(a)
        self.assertIs(arbol.buscar(10), a)
        self.assertEqual(arbol.tamanio(), 1)
        self.assertFalse(arbol.esta_vacio())

    def test_buscar_ausente(self):
        arbol = arbol_con([10, 5, 15])
        self.assertIsNone(arbol.buscar(999))
        self.assertIsNone(arbol.buscar(7))

    def test_buscar_id_invalido(self):
        arbol = arbol_con([10])
        with self.assertRaises(TypeError):
            arbol.buscar("10")
        with self.assertRaises(TypeError):
            arbol.buscar(True)
        with self.assertRaises(ValueError):
            arbol.buscar(0)

    def test_insertar_objeto_invalido(self):
        with self.assertRaises(TypeError):
            ArbolBST().insertar("no es alerta")

    def test_id_duplicado_lanza_valueerror_sin_cambios(self):
        arbol = arbol_con([10, 5, 15])
        original = arbol.buscar(5)
        repetida = Alerta(5, "Otro", "Otra descripcion", 9, 99)
        with self.assertRaises(ValueError):
            arbol.insertar(repetida)
        self.assertEqual(arbol.tamanio(), 3)
        self.assertIs(arbol.buscar(5), original)
        self.assertEqual(ids_inorden(arbol), [5, 10, 15])

    def test_duplicado_en_la_raiz(self):
        arbol = arbol_con([10])
        with self.assertRaises(ValueError):
            arbol.insertar(crear(10))
        self.assertEqual(arbol.tamanio(), 1)

    def test_inorden_ordenado_con_insercion_desordenada(self):
        arbol = arbol_con([50, 30, 70, 20, 40, 60, 80])
        self.assertEqual(ids_inorden(arbol), [20, 30, 40, 50, 60, 70, 80])
        self.assertTrue(cumple_orden_bst(arbol))

    def test_inorden_devuelve_las_mismas_instancias(self):
        a, b = crear(2), crear(1)
        arbol = ArbolBST()
        arbol.insertar(a)
        arbol.insertar(b)
        resultado = arbol.recorrido_inorden()
        self.assertIs(resultado[0], b)
        self.assertIs(resultado[1], a)

    def test_visualizar(self):
        self.assertEqual(ArbolBST().visualizar(), "Arbol vacio")
        texto = arbol_con([2, 1, 3]).visualizar()
        self.assertIn("[R] 2", texto)
        self.assertIn("[I] 1", texto)
        self.assertIn("[D] 3", texto)


class TestBSTAltura(unittest.TestCase):

    def test_altura_convencion_aristas(self):
        self.assertEqual(ArbolBST().altura(), -1)
        self.assertEqual(arbol_con([1]).altura(), 0)
        self.assertEqual(arbol_con([2, 1, 3]).altura(), 1)
        self.assertEqual(arbol_con([1, 2]).altura(), 1)

    def test_altura_carga_inicial(self):
        # 90 -> 45 -> 22 -> 11 -> 5 -> 1  = 5 aristas
        self.assertEqual(arbol_con(IDS_INICIALES).altura(), 5)

    def test_cadena_creciente_h_es_n_menos_1(self):
        for n in (100, 500, 1000):
            with self.subTest(n=n):
                arbol = arbol_con(range(1, n + 1))
                self.assertEqual(arbol.altura(), n - 1)
                self.assertEqual(arbol.tamanio(), n)

    def test_cadena_decreciente_1000(self):
        arbol = arbol_con(range(1000, 0, -1))
        self.assertEqual(arbol.altura(), 999)

    def test_cadena_1000_inorden_busqueda_y_visualizar(self):
        arbol = arbol_con(range(1, 1001))
        self.assertEqual(ids_inorden(arbol), list(range(1, 1001)))
        self.assertIsNotNone(arbol.buscar(1000))
        self.assertIsNone(arbol.buscar(1001))
        self.assertEqual(len(arbol.visualizar().splitlines()), 1000)


class TestBSTEliminacion(unittest.TestCase):

    def test_eliminar_en_arbol_vacio(self):
        self.assertFalse(ArbolBST().eliminar(1))

    def test_eliminar_ausente(self):
        arbol = arbol_con([10, 5, 15])
        self.assertFalse(arbol.eliminar(999))
        self.assertEqual(arbol.tamanio(), 3)
        self.assertEqual(ids_inorden(arbol), [5, 10, 15])

    def test_eliminar_id_invalido(self):
        arbol = arbol_con([10])
        with self.assertRaises(TypeError):
            arbol.eliminar("10")
        with self.assertRaises(ValueError):
            arbol.eliminar(-1)

    def test_eliminar_hoja(self):
        arbol = arbol_con([50, 30, 70, 20, 40, 60, 80])
        self.assertTrue(arbol.eliminar(20))
        self.assertIsNone(arbol.buscar(20))
        self.assertEqual(ids_inorden(arbol), [30, 40, 50, 60, 70, 80])
        self.assertEqual(arbol.tamanio(), 6)
        self.assertTrue(cumple_orden_bst(arbol))

    def test_eliminar_nodo_con_hijo_izquierdo(self):
        arbol = arbol_con([50, 30, 70, 20])
        self.assertTrue(arbol.eliminar(30))
        self.assertEqual(ids_inorden(arbol), [20, 50, 70])
        self.assertEqual(arbol.raiz.izquierdo.alerta.id, 20)
        self.assertEqual(arbol.altura(), 1)
        self.assertEqual(arbol.tamanio(), 3)

    def test_eliminar_nodo_con_hijo_derecho(self):
        arbol = arbol_con([50, 30, 70, 40])
        self.assertTrue(arbol.eliminar(30))
        self.assertEqual(ids_inorden(arbol), [40, 50, 70])
        self.assertEqual(arbol.raiz.izquierdo.alerta.id, 40)
        self.assertEqual(arbol.altura(), 1)

    def test_eliminar_nodo_con_dos_hijos(self):
        arbol = arbol_con([50, 30, 70, 20, 40, 60, 80])
        cuarenta = arbol.buscar(40)
        self.assertTrue(arbol.eliminar(30))
        self.assertIsNone(arbol.buscar(30))
        self.assertIs(arbol.buscar(40), cuarenta)
        self.assertEqual(arbol.raiz.izquierdo.alerta.id, 40)  # sucesor
        self.assertEqual(ids_inorden(arbol), [20, 40, 50, 60, 70, 80])
        self.assertEqual(arbol.tamanio(), 6)
        self.assertTrue(cumple_orden_bst(arbol))

    def test_eliminar_raiz_con_dos_hijos(self):
        arbol = arbol_con([50, 30, 70, 20, 40, 60, 80])
        self.assertTrue(arbol.eliminar(50))
        self.assertEqual(arbol.raiz.alerta.id, 60)
        self.assertEqual(ids_inorden(arbol), [20, 30, 40, 60, 70, 80])
        self.assertIsNone(arbol.buscar(50))
        self.assertTrue(cumple_orden_bst(arbol))

    def test_sucesor_con_hijo_derecho(self):
        # El sucesor de 50 es 60, que tiene un hijo derecho (70).
        arbol = arbol_con([50, 30, 80, 60, 70])
        self.assertTrue(arbol.eliminar(50))
        self.assertEqual(arbol.raiz.alerta.id, 60)
        self.assertEqual(arbol.raiz.derecho.alerta.id, 80)
        self.assertEqual(arbol.raiz.derecho.izquierdo.alerta.id, 70)
        self.assertEqual(ids_inorden(arbol), [30, 60, 70, 80])
        self.assertEqual(arbol.tamanio(), 4)

    def test_sucesor_es_hijo_directo(self):
        # El hijo derecho no tiene izquierdo: es el sucesor directo.
        arbol = arbol_con([50, 30, 70, 80])
        self.assertTrue(arbol.eliminar(50))
        self.assertEqual(arbol.raiz.alerta.id, 70)
        self.assertEqual(arbol.raiz.derecho.alerta.id, 80)
        self.assertEqual(ids_inorden(arbol), [30, 70, 80])

    def test_sustituir_conserva_registro_completo(self):
        arbol = ArbolBST()
        arbol.insertar(Alerta(50, "A", "raiz", 1, 1))
        arbol.insertar(Alerta(30, "B", "izq", 2, 2))
        sucesor = Alerta(70, "ERP", "Acceso anomalo", 10, 7)
        sucesor.estado = "CANCELADA"
        arbol.insertar(sucesor)
        self.assertTrue(arbol.eliminar(50))
        nodo = arbol.buscar(70)
        self.assertIs(nodo, sucesor)
        self.assertEqual(
            (nodo.sistema, nodo.descripcion, nodo.riesgo, nodo.instante,
             nodo.estado),
            ("ERP", "Acceso anomalo", 10, 7, "CANCELADA"),
        )

    def test_eliminar_raiz_unica(self):
        arbol = arbol_con([10])
        self.assertTrue(arbol.eliminar(10))
        self.assertTrue(arbol.esta_vacio())
        self.assertEqual(arbol.altura(), -1)
        self.assertEqual(arbol.tamanio(), 0)
        self.assertIsNone(arbol.buscar(10))

    def test_eliminar_raiz_con_un_hijo(self):
        arbol = arbol_con([10, 20])
        self.assertTrue(arbol.eliminar(10))
        self.assertEqual(arbol.raiz.alerta.id, 20)
        self.assertEqual(arbol.altura(), 0)

    def test_eliminar_dos_veces_el_mismo_id(self):
        arbol = arbol_con([10, 5, 15])
        self.assertTrue(arbol.eliminar(5))
        self.assertFalse(arbol.eliminar(5))
        self.assertEqual(arbol.tamanio(), 2)

    def test_reinsertar_id_eliminado(self):
        arbol = arbol_con([10, 5, 15])
        arbol.eliminar(5)
        arbol.insertar(crear(5))
        self.assertEqual(ids_inorden(arbol), [5, 10, 15])
        self.assertEqual(arbol.tamanio(), 3)

    def test_eliminar_en_cadena_de_1000(self):
        arbol = arbol_con(range(1, 1001))
        self.assertTrue(arbol.eliminar(1))      # raiz con un hijo
        self.assertTrue(arbol.eliminar(1000))   # hoja final
        self.assertEqual(arbol.tamanio(), 998)
        self.assertEqual(arbol.altura(), 997)
        self.assertEqual(ids_inorden(arbol), list(range(2, 1000)))

    def test_eliminaciones_aleatorias_contra_referencia(self):
        azar = Random(2026)
        ids = azar.sample(range(1, 1000), 200)
        arbol = arbol_con(ids)
        restantes = set(ids)
        for id in azar.sample(ids, 120):
            self.assertTrue(arbol.eliminar(id))
            restantes.remove(id)
            self.assertEqual(ids_inorden(arbol), sorted(restantes))
            self.assertEqual(arbol.tamanio(), len(restantes))
            self.assertTrue(cumple_orden_bst(arbol))


class TestBSTDatosIniciales(unittest.TestCase):
    """P01, P02 y P09 desde el lado del BST."""

    def setUp(self):
        self.alertas = cargar_alertas()
        self.arbol = ArbolBST()
        for alerta in self.alertas:
            self.arbol.insertar(alerta)

    def test_diez_registros_inorden_esperado(self):
        self.assertEqual(self.arbol.tamanio(), 10)
        self.assertEqual(ids_inorden(self.arbol), ORDEN_INORDEN)

    def test_busquedas_del_enunciado(self):
        por_id = {a.id: a for a in self.alertas}
        for id in (90, 67, 1):  # primero, intermedio y ultimo insertado
            with self.subTest(id=id):
                self.assertIs(self.arbol.buscar(id), por_id[id])
        self.assertIsNone(self.arbol.buscar(999))

    def test_id_repetido_en_datos_iniciales(self):
        with self.assertRaises(ValueError):
            self.arbol.insertar(Alerta(90, "Otro", "Repetida", 3, 99))
        self.assertEqual(self.arbol.tamanio(), 10)
        self.assertEqual(self.arbol.buscar(90).sistema,
                         next(a for a in self.alertas if a.id == 90).sistema)


# ----------------------------------------------------------------- DATOS
class TestCargaAlertas(unittest.TestCase):

    def test_json_inicial(self):
        alertas = cargar_alertas()
        self.assertEqual(len(alertas), 10)
        self.assertEqual([a.id for a in alertas], IDS_INICIALES)
        self.assertEqual([a.riesgo for a in alertas], RIESGOS_INICIALES)
        self.assertEqual([a.instante for a in alertas], list(range(1, 11)))
        self.assertTrue(all(a.estado == "PENDIENTE" for a in alertas))
        self.assertEqual(len({a.id for a in alertas}), 10)

    def test_orden_de_prioridad_esperado(self):
        alertas = cargar_alertas()
        orden = sorted(alertas, key=lambda a: (-a.riesgo, a.instante, a.id))
        self.assertEqual([a.id for a in orden], ORDEN_PRIORIDAD)

    def test_carga_es_reproducible(self):
        a = [(x.id, x.sistema, x.descripcion, x.riesgo, x.instante)
             for x in cargar_alertas()]
        b = [(x.id, x.sistema, x.descripcion, x.riesgo, x.instante)
             for x in cargar_alertas()]
        self.assertEqual(a, b)

    def _escribir(self, carpeta, contenido, nombre="alertas.json"):
        ruta = Path(carpeta) / nombre
        ruta.write_text(
            contenido if isinstance(contenido, str) else json.dumps(contenido),
            encoding="utf-8",
        )
        return ruta

    def _registro(self, base_id=1, **cambios):
        registro = {"id": base_id, "sistema": "Web", "descripcion": "Sondeo",
                    "riesgo": 3, "instante": 1}
        registro.update(cambios)
        return registro

    def test_ruta_como_cadena_o_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._escribir(tmp, [self._registro(1)])
            self.assertEqual(len(cargar_alertas(ruta)), 1)
            self.assertEqual(len(cargar_alertas(str(ruta))), 1)

    def test_archivo_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                cargar_alertas(Path(tmp) / "no_existe.json")

    def test_json_que_no_es_lista(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._escribir(tmp, {"id": 1})
            with self.assertRaises(ValueError):
                cargar_alertas(ruta)

    def test_json_mal_formado(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._escribir(tmp, "{ esto no es json")
            with self.assertRaises(ValueError):
                cargar_alertas(ruta)

    def test_campos_faltantes_o_sobrantes(self):
        faltante = self._registro(1)
        del faltante["riesgo"]
        sobrante = self._registro(1, extra="x")
        for caso in (faltante, sobrante, "texto"):
            with self.subTest(caso=caso):
                with tempfile.TemporaryDirectory() as tmp:
                    ruta = self._escribir(tmp, [caso])
                    with self.assertRaises(ValueError):
                        cargar_alertas(ruta)

    def test_id_repetido_en_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._escribir(tmp, [self._registro(1), self._registro(1)])
            with self.assertRaises(ValueError):
                cargar_alertas(ruta)

    def test_valor_invalido_en_archivo(self):
        for cambio in ({"riesgo": 11}, {"instante": -1}, {"id": 0},
                       {"sistema": " "}):
            with self.subTest(cambio=cambio):
                with tempfile.TemporaryDirectory() as tmp:
                    ruta = self._escribir(tmp, [self._registro(1, **cambio)])
                    with self.assertRaises(ValueError):
                        cargar_alertas(ruta)

    def test_lista_vacia(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._escribir(tmp, [])
            self.assertEqual(cargar_alertas(ruta), [])


def _tupla(alerta):
    return (alerta.id, alerta.sistema, alerta.descripcion,
            alerta.riesgo, alerta.instante)


class TestGenerarAlertas(unittest.TestCase):

    def test_cantidades_y_ids_unicos(self):
        for n in (100, 500, 1000):
            with self.subTest(n=n):
                alertas = generar_alertas(n, 2026)
                self.assertEqual(len(alertas), n)
                self.assertEqual([a.id for a in alertas],
                                 list(range(1, n + 1)))
                self.assertEqual(len({a.id for a in alertas}), n)

    def test_valores_validos(self):
        for alerta in generar_alertas(500, 2026):
            self.assertTrue(1 <= alerta.riesgo <= 10)
            self.assertGreaterEqual(alerta.instante, 0)
            self.assertEqual(alerta.estado, "PENDIENTE")

    def test_misma_semilla_mismos_datos(self):
        a = [_tupla(x) for x in generar_alertas(100, 2026)]
        b = [_tupla(x) for x in generar_alertas(100, 2026)]
        self.assertEqual(a, b)

    def test_semilla_por_defecto(self):
        a = [_tupla(x) for x in generar_alertas(100)]
        b = [_tupla(x) for x in generar_alertas(100, 2026)]
        self.assertEqual(a, b)

    def test_semillas_distintas_difieren(self):
        a = [_tupla(x) for x in generar_alertas(100, 1)]
        b = [_tupla(x) for x in generar_alertas(100, 2)]
        self.assertNotEqual(a, b)

    def test_cero_alertas(self):
        self.assertEqual(generar_alertas(0, 2026), [])

    def test_argumentos_invalidos(self):
        with self.assertRaises(ValueError):
            generar_alertas(-1, 2026)
        for n in ("10", 5.0, True, None):
            with self.subTest(n=n):
                with self.assertRaises(TypeError):
                    generar_alertas(n, 2026)
        for semilla in ("2026", 1.5, None):
            with self.subTest(semilla=semilla):
                with self.assertRaises(TypeError):
                    generar_alertas(10, semilla)

    def test_generadas_se_pueden_insertar_en_bst(self):
        arbol = ArbolBST()
        for alerta in generar_alertas(1000, 2026):
            arbol.insertar(alerta)
        self.assertEqual(arbol.tamanio(), 1000)
        self.assertEqual(arbol.altura(), 999)


class TestGenerarArchivos(unittest.TestCase):

    def test_crea_tres_archivos_cargables_y_reproducibles(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "salida"  # la carpeta aun no existe
            archivos = generar_archivos(2026, destino)
            self.assertEqual([a.name for a in archivos],
                             ["alertas_100.json", "alertas_500.json",
                              "alertas_1000.json"])
            for n, archivo in zip((100, 500, 1000), archivos):
                with self.subTest(n=n):
                    self.assertTrue(archivo.exists())
                    cargadas = [_tupla(a) for a in cargar_alertas(archivo)]
                    esperadas = [_tupla(a) for a in generar_alertas(n, 2026)]
                    self.assertEqual(cargadas, esperadas)

    def test_generar_dos_veces_da_el_mismo_contenido(self):
        with tempfile.TemporaryDirectory() as tmp:
            primera = [p.read_text(encoding="utf-8")
                       for p in generar_archivos(2026, tmp)]
            segunda = [p.read_text(encoding="utf-8")
                       for p in generar_archivos(2026, tmp)]
            self.assertEqual(primera, segunda)


if __name__ == "__main__":
    unittest.main()