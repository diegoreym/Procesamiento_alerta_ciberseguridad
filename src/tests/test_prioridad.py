import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelos import Alerta
from heap_prioridad import HeapPrioridad
from cola_prioridad import ColaPrioridad

class TestPrioridad(unittest.TestCase):
    def setUp(self):
        self.heap = HeapPrioridad()
        self.cola = ColaPrioridad()

        self.a1 = Alerta(45, "ERP", "Acceso", 10, 2)
        self.a2 = Alerta(112, "Archivos", "Ransomware", 10, 6)
        self.a3 = Alerta(5, "Identidad", "Robo credenciales", 9, 9)
        self.a4 = Alerta(22, "BD", "Consultas sospechosas", 8, 4)
        self.a5 = Alerta(157, "Proxy", "Descarga no autorizada", 7, 7)
        self.a_empate = Alerta(99, "Test", "Test Empate", 10, 2) # Empata en riesgo y en instante con a1

    def test_heap_vacio(self):
        self.assertTrue(self.heap.esta_vacia())
        self.assertEqual(self.heap.tamanio(), 0)
        with self.assertRaises(IndexError):
            self.heap.ver_siguiente()
        with self.assertRaises(IndexError):
            self.heap.extraer()

    def test_heap_insercion_y_orden(self):
        # Insertamos en orden inverso de prioridad para forzar reordenamiento
        self.heap.insertar(self.a5)
        self.heap.insertar(self.a4)
        self.heap.insertar(self.a3)
        self.heap.insertar(self.a2)
        self.heap.insertar(self.a1)
        
        self.assertEqual(self.heap.tamanio(), 5)
        
        # El de mayor riesgo e instante más temprano (a1) debe estar en la cima
        self.assertEqual(self.heap.ver_siguiente().id, 45)

    def test_heap_cinco_extracciones(self):
        alertas = [self.a5, self.a4, self.a3, self.a2, self.a1]
        for a in alertas:
            self.heap.insertar(a)
            
        # P06: Salen 45, 112, 5, 22 y 157
        extracciones_esperadas = [45, 112, 5, 22, 157]
        extracciones_reales = []
        
        while not self.heap.esta_vacia():
            extracciones_reales.append(self.heap.extraer().id)
            
        self.assertEqual(extracciones_reales, extracciones_esperadas)

    def test_heap_empate_total(self):
        # a1 (id=45, riesgo=10, instante=2) vs a_empate (id=99, riesgo=10, instante=2)
        # Gana el menor ID -> a1
        self.heap.insertar(self.a_empate)
        self.heap.insertar(self.a1)
        
        self.assertEqual(self.heap.extraer().id, 45)
        self.assertEqual(self.heap.extraer().id, 99)

    def test_cola_prioridad_delegacion(self):
        self.cola.agregar(self.a1)
        self.cola.agregar(self.a2)
        
        self.assertFalse(self.cola.esta_vacia())
        self.assertEqual(self.cola.consultar_siguiente().id, 45)
        self.assertEqual(self.cola.extraer_siguiente().id, 45)
        self.assertEqual(self.cola.extraer_siguiente().id, 112)
        self.assertTrue(self.cola.esta_vacia())

if __name__ == '__main__':
    unittest.main()
