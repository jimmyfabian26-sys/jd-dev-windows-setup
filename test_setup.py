"""Pruebas de control de ejecución sin importar ni ejecutar comandos del sistema."""
import ast
from pathlib import Path
from types import SimpleNamespace
import threading
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).with_name('ConfiguracionAutomatica.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
CLASS = next(node for node in TREE.body if isinstance(node, ast.ClassDef))


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.dialogs = SimpleNamespace(askyesno=Mock(return_value=False), showinfo=Mock(), showwarning=Mock())
        self.thread = Mock()
        self.namespace = {'threading': SimpleNamespace(Thread=self.thread), 'messagebox': self.dialogs}
        exec(compile(ast.Module(body=[CLASS], type_ignores=[]), '<J.D DEV class>', 'exec'), self.namespace)
        self.app = self.namespace['JDDevWindowsSetup'].__new__(self.namespace['JDDevWindowsSetup'])
        self.callbacks = []
        self.app.root = SimpleNamespace(after=lambda delay, callback: self.callbacks.append(callback))
        self.app.running = False
        self.app.progress_var = Mock()
        self.app.status_label = Mock()
        self.app.safe_log = Mock()
        self.app.safe_progress = Mock()
        self.app.crear_restauracion = Mock(return_value=True)
        self.app.config_rendimiento = Mock()
        self.app.desactivar_telemetria = Mock()
        self.app.config_apariencia = Mock()
        self.app.restart_explorer_with_delay = Mock()

    def test_cancelar_no_ejecuta_nada(self):
        self.app.config_completa()
        self.thread.assert_not_called()
        self.assertFalse(self.app.running)

    def test_confirmar_inicia_solo_una_ejecucion(self):
        self.dialogs.askyesno.return_value = True
        self.app.config_completa()
        self.assertTrue(self.app.running)
        self.thread.assert_called_once()
        self.app.config_completa()
        self.thread.assert_called_once()
        self.assertEqual(self.dialogs.askyesno.call_count, 1)

    def test_backup_fallido_detiene_cambios(self):
        self.app.crear_restauracion.return_value = False
        self.app.config_completa_thread()
        self.app.config_rendimiento.assert_not_called()
        self.app.config_apariencia.assert_not_called()
        self.app.desactivar_telemetria.assert_not_called()
        self.app.restart_explorer_with_delay.assert_not_called()
        self.callbacks[-1]()
        self.dialogs.showwarning.assert_called_once()

    def test_finalizacion_no_reinicia_windows(self):
        self.app.config_completa_thread()
        self.app.config_rendimiento.assert_called_once_with(silent=True)
        self.app.config_apariencia.assert_called_once_with(silent=True)
        self.app.restart_explorer_with_delay.assert_called_once_with(3)
        self.callbacks[-1]()
        self.assertFalse(self.app.running)
        self.dialogs.showinfo.assert_called_once()
        self.assertNotIn('shutdown', SOURCE.lower())

    def test_ajuste_individual_requiere_confirmacion_y_backup(self):
        action = Mock()
        self.app.advanced_visible = False
        self.app.run_and_collapse(action)
        action.assert_not_called()
        self.dialogs.askyesno.return_value = True
        self.app.crear_restauracion.return_value = False
        self.app.run_and_collapse(action)
        action.assert_not_called()
        self.app.crear_restauracion.return_value = True
        self.app.run_and_collapse(action)
        action.assert_called_once()

    def test_no_hay_cuenta_regresiva_y_marca_completa(self):
        self.assertNotIn('auto_start', SOURCE)
        self.assertNotIn('PCMATIC', SOURCE.upper())
        self.assertNotIn('PC MATIC', SOURCE.upper())
        self.assertIn('text="J.D DEV"', SOURCE)
        self.assertIn('RECOMENDADO DESPUÉS DE REINSTALAR WINDOWS', SOURCE)


if __name__ == '__main__':
    unittest.main()
