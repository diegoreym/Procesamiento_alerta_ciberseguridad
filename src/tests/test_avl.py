from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modelos import Alerta
from avl import ArbolAVL

IDS_INICIALES = [90, 45, 135, 22, 67, 112, 157, 11, 5, 1]

class TestArbolAVL(unittest.TestCase):
    def setUp(self) -> None:
        self.arbol = ArbolAVL()

    def cargar(self, ids: list[int]) -> None:
        for id in ids:
            self.arbol.insertar(Alerta(id, "VPN", "Alerta de prueba", 5, id))
            self.assertTrue(self.arbol.validar_balance())

    def claves(self) -> list[int]:
        return [alerta.id for alerta in self.arbol.recorrido_inorden()]

    def test_arbol_vacio(self) -> None:
        self.assertEqual(self.arbol.altura(), -1)
        self.assertIsNone(self.arbol.buscar(1))
        self.assertFalse(self.arbol.eliminar(1))

    def test_carga_inicial_e_inorden(self) -> None:
        self.cargar(IDS_INICIALES)
        self.assertEqual(self.claves(), sorted(IDS_INICIALES))
        self.assertEqual(self.arbol.altura(), 3)

    def test_busquedas(self) -> None:
        self.cargar(IDS_INICIALES)
        for id in (90, 67, 1):
            with self.subTest(id=id):
                self.assertEqual(self.arbol.buscar(id).id, id)
        self.assertIsNone(self.arbol.buscar(999))

    def test_id_duplicado(self) -> None:
        self.cargar(IDS_INICIALES)
        original = self.arbol.buscar(90)
        with self.assertRaises(ValueError):
            self.arbol.insertar(Alerta(90, "Correo", "Duplicada", 10, 0))
        self.assertIs(self.arbol.buscar(90), original)
        self.assertEqual(self.claves(), sorted(IDS_INICIALES))

    def test_cuatro_rotaciones(self) -> None:
        casos = {
            "LL": [30, 20, 10],
            "RR": [10, 20, 30],
            "LR": [30, 10, 20],
            "RL": [10, 30, 20],
        }
        for tipo, secuencia in casos.items():
            with self.subTest(tipo=tipo):
                self.arbol = ArbolAVL()
                self.cargar(secuencia)
                self.assertEqual(self.arbol.raiz.alerta.id, 20)
                self.assertEqual(self.arbol.raiz.izquierdo.alerta.id, 10)
                self.assertEqual(self.arbol.raiz.derecho.alerta.id, 30)
                self.assertEqual(self.arbol.altura(), 1)

    def test_tamanios_exigidos(self) -> None:
        for n in (100, 500, 1000):
            with self.subTest(n=n):
                self.arbol = ArbolAVL()
                self.cargar(list(range(1, n + 1)))
                self.assertEqual(self.claves(), list(range(1, n + 1)))
                self.assertLess(self.arbol.altura(), n - 1)

    def test_eliminacion_y_rebalanceo(self) -> None:
        casos = [
            ("hoja y rebalanceo", [4, 2, 5, 1, 3], 5, [1, 2, 3, 4], 2),
            ("un hijo", [40, 20, 60, 70], 60, [20, 40, 70], 40),
            ("dos hijos", [40, 20, 60, 10, 30, 50, 70], 40,
             [10, 20, 30, 50, 60, 70], 50),
            ("raiz unica", [20], 20, [], None),
        ]
        for caso, secuencia, id, esperado, raiz in casos:
            with self.subTest(caso=caso):
                self.arbol = ArbolAVL()
                self.cargar(secuencia)
                self.assertTrue(self.arbol.eliminar(id))
                self.assertEqual(self.claves(), esperado)
                self.assertTrue(self.arbol.validar_balance())
                if raiz is None:
                    self.assertIsNone(self.arbol.raiz)
                else:
                    self.assertEqual(self.arbol.raiz.alerta.id, raiz)

if __name__ == "__main__":
    unittest.main(verbosity=2)