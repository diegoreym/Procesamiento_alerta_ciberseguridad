
"""Pruebas automaticas de la interfaz MenuAlertas."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

# Permite importar los archivos ubicados en src.
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from modelos import Alerta
from gestor import GestorAlerta
from ui_alertas import MenuAlertas


class TestMenuAlertas(unittest.TestCase):

    def setUp(self):
        """Cada prueba utiliza un gestor nuevo e independiente."""
        self.gestor = GestorAlerta()
        self.menu = MenuAlertas(self.gestor)

    def crear_alerta(self, id=45, riesgo=10, instante=2):
        return Alerta(id, "ERP", "Acceso sospechoso",
                      riesgo, instante)

    def simular(self, entradas):
        """Ejecuta el menu simulando entradas y captura su salida."""
        salida = StringIO()

        with patch("builtins.input", side_effect=entradas):
            with patch("sys.stdout", new=salida):
                self.menu.ejecutar()

        return salida.getvalue()


    # 1. REGISTRO CORRECTO
    def test_01_registrar_alerta(self):
        salida = self.simular([
            "1", "45", "ERP", "Acceso sospechoso",
            "10", "2", "0"
        ])

        alerta = self.gestor.buscar(45)

        self.assertIsNotNone(alerta)
        self.assertEqual(alerta.riesgo, 10)
        self.assertEqual(alerta.estado, "PENDIENTE")
        self.assertIn("Alerta registrada correctamente", salida)


    # 2. LETRAS EN LUGAR DE NUMEROS
    def test_02_entero_invalido(self):
        with patch("builtins.input", side_effect=["abc", "45"]):
            with patch("sys.stdout", new_callable=StringIO) as salida:
                numero = self.menu.leer_entero("ID: ", 1)

        self.assertEqual(numero, 45)
        self.assertIn("ERROR", salida.getvalue())


    # 3. RIESGO FUERA DE RANGO
    def test_03_riesgo_fuera_de_rango(self):
        with patch("builtins.input", side_effect=["15", "0", "8"]):
            with patch("sys.stdout", new_callable=StringIO) as salida:
                riesgo = self.menu.leer_entero("Riesgo: ", 1, 10)

        self.assertEqual(riesgo, 8)
        self.assertEqual(salida.getvalue().count("ERROR"), 2)

    # 4. TEXTO VACIO
    def test_04_texto_vacio(self):
        with patch("builtins.input", side_effect=["", "   ", "Correo"]):
            with patch("sys.stdout", new_callable=StringIO) as salida:
                texto = self.menu.leer_texto("Sistema: ")

        self.assertEqual(texto, "Correo")
        self.assertEqual(salida.getvalue().count("ERROR"), 2)


    # 5. BUSQUEDA EXISTENTE E INEXISTENTE
    def test_05_buscar_alertas(self):
        self.gestor.registrar(self.crear_alerta())

        salida = self.simular([
            "2", "45",
            "2", "999",
            "0"
        ])

        self.assertIn("Alerta encontrada", salida)
        self.assertIn("No existe una alerta", salida)
        self.assertEqual(len(self.gestor.listar_en_orden()), 1)


    # 6. ID DUPLICADO
    def test_06_id_duplicado(self):
        self.gestor.registrar(self.crear_alerta())

        salida = self.simular([
            "1", "45", "Correo", "Phishing", "5", "1",
            "8",
            "0"
        ])

        self.assertIn("ERROR", salida)
        self.assertIn("Ya existe una alerta", salida)
        self.assertIn("ESTADISTICAS", salida)
        self.assertEqual(len(self.gestor.listar_en_orden()), 1)


    # 7. OPCION FUERA DEL MENU
    def test_07_opcion_invalida(self):
        salida = self.simular(["99", "abc", "0"])

        self.assertEqual(
            salida.count("ERROR: Opcion no valida"), 2
        )
        self.assertIn("Gracias por utilizar", salida)


    # 8. ATENDER COLA VACIA
    def test_08_atender_cola_vacia(self):
        salida = self.simular(["5", "8", "0"])

        self.assertIn("No hay alertas pendientes", salida)
        self.assertIn("ESTADISTICAS", salida)
        self.assertIn("Gracias por utilizar", salida)


    # 9. CANCELAR ALERTA YA ATENDIDA
    def test_09_cancelar_atendida(self):
        self.gestor.registrar(self.crear_alerta())
        self.gestor.procesar_alerta()

        salida = self.simular(["6", "45", "0"])

        self.assertIn("ERROR", salida)
        self.assertEqual(self.gestor.buscar(45).estado, "ATENDIDA")


    # 10. ACTUALIZAR DATOS
    def test_10_actualizar_datos(self):
        self.gestor.registrar(self.crear_alerta())

        salida = self.simular([
            "7", "45", "VPN", "Intentos fallidos", "0"
        ])

        alerta = self.gestor.buscar(45)

        self.assertEqual(alerta.sistema, "VPN")
        self.assertEqual(alerta.descripcion, "Intentos fallidos")
        self.assertEqual(alerta.riesgo, 10)
        self.assertEqual(alerta.instante, 2)
        self.assertIn("Datos actualizados correctamente", salida)


    # 11. ESTADISTICAS
    def test_11_estadisticas(self):
        self.gestor.registrar(self.crear_alerta())
        self.gestor.registrar(
            self.crear_alerta(90, 4, 1)
        )
        self.gestor.procesar_alerta()

        salida = self.simular(["8", "0"])
        datos = self.gestor.estadisticas()

        self.assertEqual(datos["historicas"], 2)
        self.assertEqual(datos["pendientes"], 1)
        self.assertEqual(datos["atendidas"], 1)
        self.assertEqual(datos["canceladas"], 0)
        self.assertIn("ESTADISTICAS", salida)


    # 12. SALIR CORRECTAMENTE
    def test_12_salir(self):
        salida = self.simular(["0"])

        self.assertIn("Gracias por utilizar el sistema", salida)

    # 13. FINALIZACION CON CTRL+C
    def test_13_interrupcion_controlada(self):
        salida = StringIO()

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch("sys.stdout", new=salida):
                self.menu.ejecutar()

        self.assertIn(
            "Programa finalizado por el usuario",
            salida.getvalue()
        )

    # 14. ERROR Y RECUPERACION DEL MENU
    def test_14_recuperacion_despues_de_error(self):
        salida = self.simular([
            "5",                  # Atender cola vacia
            "1", "90", "Correo", "Phishing", "4", "1",
            "4",                  # Consultar siguiente
            "0"
        ])

        self.assertIn("ERROR", salida)
        self.assertIn("Alerta registrada correctamente", salida)
        self.assertIn("Alerta con mayor prioridad", salida)
        self.assertEqual(self.gestor.buscar(90).estado, "PENDIENTE")

    # 15. CONSULTAR NO DEBE ATENDER
    def test_15_consultar_sin_procesar(self):
        self.gestor.registrar(self.crear_alerta())

        salida = self.simular(["4", "0"])

        self.assertIn("Alerta con mayor prioridad", salida)
        self.assertEqual(self.gestor.buscar(45).estado, "PENDIENTE")

    # 16. CANCELAR ID INEXISTENTE
    def test_16_cancelar_inexistente(self):
        salida = self.simular(["6", "999", "0"])

        self.assertIn("No existe una alerta", salida)
        self.assertIn("Gracias por utilizar", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
