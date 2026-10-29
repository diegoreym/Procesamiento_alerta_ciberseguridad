import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelos import Alerta
from gestor import GestorAlerta
from datos import cargar_alertas


class TestGestorAlerta(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorAlerta()

    def cargar(self):
        for alerta in cargar_alertas():
            self.gestor.registrar(alerta)

    def test_gestor_vacio(self):
        self.assertEqual(self.gestor.listar_en_orden(), [])
        self.assertIsNone(self.gestor.buscar(1))
        self.assertFalse(self.gestor.cancelar(1))
        with self.assertRaises(IndexError):
            self.gestor.consultar_siguiente()
        with self.assertRaises(IndexError):
            self.gestor.procesar_alerta()

    def test_registro_duplicado_y_listado(self):
        self.cargar()
        original = self.gestor.buscar(45)
        with self.assertRaises(ValueError):
            self.gestor.registrar(Alerta(45, "VPN", "Duplicada", 1, 0))
        self.assertIs(self.gestor.buscar(45), original)
        self.assertEqual([a.id for a in self.gestor.listar_en_orden()], [1, 5, 11, 22, 45, 67, 90, 112, 135, 157])
        self.assertEqual(self.gestor.estadisticas()["historicas"], 10)

    def test_prioridad_y_no_reproceso(self):
        self.cargar()
        siguiente = self.gestor.consultar_siguiente()
        self.assertEqual(siguiente.id, 45)
        self.assertEqual(siguiente.estado, "PENDIENTE")
        ids = []
        for _ in range(10):
            alerta = self.gestor.procesar_alerta()
            ids.append(alerta.id)
            self.assertEqual(alerta.estado, "ATENDIDA")
            self.assertIs(self.gestor.buscar(alerta.id), alerta)
        self.assertEqual(ids, [45, 112, 5, 22, 157, 67, 1, 90, 11, 135])
        with self.assertRaises(IndexError):
            self.gestor.procesar_alerta()
        self.assertEqual(self.gestor.estadisticas(), {"historicas": 10, "pendientes": 0, "atendidas": 10, "canceladas": 0})

    def test_cancelacion_conserva_historial_y_omite_cola(self):
        self.cargar()
        self.assertTrue(self.gestor.cancelar(45))
        self.assertEqual(self.gestor.buscar(45).estado, "CANCELADA")
        self.assertEqual(self.gestor.consultar_siguiente().id, 112)
        ids = [self.gestor.procesar_alerta().id for _ in range(9)]
        self.assertNotIn(45, ids)
        with self.assertRaises(IndexError):
            self.gestor.procesar_alerta()
        self.assertEqual(self.gestor.estadisticas(), {"historicas": 10, "pendientes": 0, "atendidas": 9, "canceladas": 1})

    def test_no_cancelar_atendida_o_cancelada(self):
        self.cargar()
        self.gestor.procesar_alerta()
        with self.assertRaises(ValueError):
            self.gestor.cancelar(45)
        self.gestor.cancelar(112)
        with self.assertRaises(ValueError):
            self.gestor.cancelar(112)

    def test_actualizar_alerta_encontrada(self):
        self.cargar()
        alerta = self.gestor.buscar(45)
        self.gestor.actualizar_datos(alerta, "Correo", "Nueva descripcion")
        self.assertIs(self.gestor.buscar(45), alerta)
        self.assertEqual((alerta.sistema, alerta.descripcion), ("Correo", "Nueva descripcion"))
        self.assertEqual((alerta.id, alerta.riesgo, alerta.instante), (45, 10, 2))
        self.assertIs(self.gestor.consultar_siguiente(), alerta)
        with self.assertRaises(ValueError):
            self.gestor.actualizar_datos(alerta, "VPN", "")
        self.assertEqual(alerta.sistema, "Correo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
