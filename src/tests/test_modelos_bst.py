import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelos import Alerta
from bst import ArbolBST
from datos import cargar_alertas


class TestAlerta(unittest.TestCase):
    def test_datos_y_estado_inicial(self):
        alerta = Alerta(1, " VPN ", " Acceso sospechoso ", 10, 0)
        self.assertEqual(alerta.sistema, "VPN")
        self.assertEqual(alerta.descripcion, "Acceso sospechoso")
        self.assertEqual(alerta.estado, "PENDIENTE")
        self.assertEqual((alerta.id, alerta.riesgo, alerta.instante), (1, 10, 0))

    def test_datos_invalidos(self):
        casos = [
            ((0, "VPN", "Acceso", 5, 0), ValueError),
            ((True, "VPN", "Acceso", 5, 0), TypeError),
            ((1, "", "Acceso", 5, 0), ValueError),
            ((1, "VPN", "", 5, 0), ValueError),
            ((1, "VPN", "Acceso", 0, 0), ValueError),
            ((1, "VPN", "Acceso", 11, 0), ValueError),
            ((1, "VPN", "Acceso", 5, -1), ValueError),
        ]
        for datos, error in casos:
            with self.subTest(datos=datos), self.assertRaises(error):
                Alerta(*datos)

    def test_claves_solo_lectura_y_estado(self):
        alerta = Alerta(1, "VPN", "Acceso", 5, 0)
        for atributo in ("id", "riesgo", "instante"):
            with self.subTest(atributo=atributo), self.assertRaises(AttributeError):
                setattr(alerta, atributo, 2)
        alerta.estado = "ATENDIDA"
        self.assertEqual(alerta.estado, "ATENDIDA")
        with self.assertRaises(ValueError):
            alerta.estado = "INVALIDO"


    def test_estados_finales_no_permiten_cambios(self):
        for estado_final in ("ATENDIDA", "CANCELADA"):
            with self.subTest(estado_final=estado_final):
                alerta = Alerta(1, "VPN", "Acceso", 5, 0)
                alerta.estado = estado_final
                self.assertEqual(alerta.estado, estado_final)
                for nuevo_estado in ("PENDIENTE", "ATENDIDA", "CANCELADA"):
                    with self.subTest(nuevo_estado=nuevo_estado):
                        with self.assertRaises(ValueError):
                            alerta.estado = nuevo_estado
                        self.assertEqual(alerta.estado, estado_final)


class TestArbolBST(unittest.TestCase):
    def setUp(self):
        self.arbol = ArbolBST()

    def cargar(self, ids):
        for id in ids:
            self.arbol.insertar(Alerta(id, "VPN", "Prueba", 5, id))

    def test_vacio(self):
        self.assertTrue(self.arbol.esta_vacio())
        self.assertEqual(self.arbol.tamanio(), 0)
        self.assertEqual(self.arbol.altura(), -1)
        self.assertIsNone(self.arbol.buscar(1))
        self.assertFalse(self.arbol.eliminar(1))

    def test_datos_iniciales_busqueda_e_inorden(self):
        alertas = cargar_alertas()
        ids = [90, 45, 135, 22, 67, 112, 157, 11, 5, 1]
        self.assertEqual([a.id for a in alertas], ids)
        self.assertEqual([a.riesgo for a in alertas], [4, 10, 2, 8, 6, 10, 7, 3, 9, 5])
        for alerta in alertas:
            self.arbol.insertar(alerta)
        self.assertEqual([a.id for a in self.arbol.recorrido_inorden()], sorted(ids))
        self.assertEqual(self.arbol.altura(), 5)
        self.assertEqual(self.arbol.tamanio(), 10)
        for alerta in alertas:
            self.assertIs(self.arbol.buscar(alerta.id), alerta)
        self.assertIsNone(self.arbol.buscar(999))

    def test_duplicado(self):
        self.cargar([20])
        original = self.arbol.buscar(20)
        with self.assertRaises(ValueError):
            self.cargar([20])
        self.assertIs(self.arbol.buscar(20), original)
        self.assertEqual(self.arbol.tamanio(), 1)

    def test_eliminar_hoja_un_hijo_dos_hijos_y_raiz(self):
        casos = [
            ([40, 20, 60], 20, [40, 60]),
            ([40, 20, 60, 70], 60, [20, 40, 70]),
            ([40, 20, 60, 50, 70], 40, [20, 50, 60, 70]),
            ([20], 20, []),
        ]
        for ids, eliminar, esperado in casos:
            with self.subTest(ids=ids):
                self.arbol = ArbolBST()
                self.cargar(ids)
                self.assertTrue(self.arbol.eliminar(eliminar))
                self.assertIsNone(self.arbol.buscar(eliminar))
                self.assertEqual([a.id for a in self.arbol.recorrido_inorden()], esperado)
                self.assertEqual(self.arbol.tamanio(), len(esperado))
                self.assertFalse(self.arbol.eliminar(999))

    def test_inserciones_crecientes(self):
        for n in (100, 500, 1000):
            with self.subTest(n=n):
                self.arbol = ArbolBST()
                self.cargar(range(1, n + 1))
                self.assertEqual(self.arbol.altura(), n - 1)
                self.assertEqual([a.id for a in self.arbol.recorrido_inorden()], list(range(1, n + 1)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
