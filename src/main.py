"""
Interfaz principal para la automatización del SII - VERSIÓN CORREGIDA
"""
import sys
import os

# ================= CONFIGURACIÓN DE IMPORTS =================
# Obtener el directorio donde está este archivo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

print(f"📁 Directorio del script: {SCRIPT_DIR}")
print(f"📁 Raíz del proyecto: {PROJECT_ROOT}")

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, SCRIPT_DIR)

# Verificar que core existe
CORE_DIR = os.path.join(SCRIPT_DIR, "core")
if not os.path.exists(CORE_DIR):
    print(f"❌ ERROR: No existe la carpeta 'core' en {SCRIPT_DIR}")
    print("Contenido de src/:")
    for item in os.listdir(SCRIPT_DIR):
        print(f"  - {item}")
    sys.exit(1)

# Verificar que sii_automator.py existe
SII_FILE = os.path.join(CORE_DIR, "sii_automator.py")
if not os.path.exists(SII_FILE):
    print(f"❌ ERROR: No existe sii_automator.py en {CORE_DIR}")
    print("Contenido de core/:")
    for item in os.listdir(CORE_DIR):
        print(f"  - {item}")
    sys.exit(1)

# ================= PRIMERO IMPORTAR DEPENDENCIAS =================
print("🔍 Verificando dependencias...")

try:
    import selenium
    print(f"✅ Selenium {selenium.__version__}")
except ImportError:
    print("❌ Selenium no está instalado")
    print("Ejecuta: pip install selenium webdriver-manager PyQt5")
    sys.exit(1)

try:
    import PyQt5
    print(f"✅ PyQt5 instalado")
except ImportError:
    print("❌ PyQt5 no está instalado")
    print("Ejecuta: pip install PyQt5")
    sys.exit(1)

# ================= IMPORTAR SIIAutomator =================
print("🔍 Intentando importar SIIAutomator...")

try:
    # Método más simple: usar importlib
    import importlib.util
    
    # Especificar el módulo
    spec = importlib.util.spec_from_file_location("sii_automator_module", SII_FILE)
    sii_module = importlib.util.module_from_spec(spec)
    
    # Ejecutar el módulo en el contexto actual para que tenga acceso a las dependencias
    sys.modules['sii_automator_module'] = sii_module
    spec.loader.exec_module(sii_module)
    
    # Obtener la clase
    SIIAutomator = getattr(sii_module, 'SIIAutomator', None)
    
    if SIIAutomator:
        print("✅ SIIAutomator importado exitosamente")
    else:
        print("❌ Clase SIIAutomator no encontrada en el módulo")
        print("Funciones/Clases disponibles:")
        for attr_name in dir(sii_module):
            if not attr_name.startswith('_'):
                print(f"  - {attr_name}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error importando SIIAutomator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ================= IMPORTAR PyQt5 COMPONENTES =================
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QCheckBox, QGroupBox, QMessageBox,
                                 QProgressBar, QSplitter, QFrame)
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QPalette, QColor
    print("✅ Componentes PyQt5 importados exitosamente")
except ImportError as e:
    print(f"❌ Error importando componentes PyQt5: {e}")
    sys.exit(1)

# ================= CÓDIGO DE LA INTERFAZ =================
print("🚀 Iniciando interfaz gráfica...")

class SIIAutomatorGUI(QMainWindow):
    """Interfaz gráfica para el automatizador SII"""
    
    def __init__(self):
        super().__init__()
        self.automator = SIIAutomator()
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Automatizador SII - Aceptación de Facturas")
        self.setGeometry(100, 100, 900, 700)
        
        # Establecer estilo oscuro moderno
        self.set_dark_theme()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel("🔄 Automatizador SII")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4FC3F7; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #555;")
        main_layout.addWidget(separator)
        
        # Splitter para dividir la ventana
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Configuración
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de credenciales
        cred_group = QGroupBox("🔑 Credenciales de Acceso")
        cred_group.setFont(QFont("Arial", 10))
        cred_layout = QVBoxLayout()
        
        # RUT Empresa
        rut_empresa_layout = QHBoxLayout()
        rut_empresa_label = QLabel("RUT Empresa:*")
        rut_empresa_label.setFixedWidth(120)
        self.rut_empresa_input = QLineEdit()
        self.rut_empresa_input.setPlaceholderText("Ej: 12.123.456-7")
        rut_empresa_layout.addWidget(rut_empresa_label)
        rut_empresa_layout.addWidget(self.rut_empresa_input)
        cred_layout.addLayout(rut_empresa_layout)
        
        # RUT Usuario
        rut_usuario_layout = QHBoxLayout()
        rut_usuario_label = QLabel("RUT Usuario:")
        rut_usuario_label.setFixedWidth(120)
        self.rut_usuario_input = QLineEdit()
        self.rut_usuario_input.setPlaceholderText("Opcional - Solo si es diferente al usuario")
        rut_usuario_layout.addWidget(rut_usuario_label)
        rut_usuario_layout.addWidget(self.rut_usuario_input)
        cred_layout.addLayout(rut_usuario_layout)
        
        # Clave
        clave_layout = QHBoxLayout()
        clave_label = QLabel("Clave SII:*")
        clave_label.setFixedWidth(120)
        self.clave_input = QLineEdit()
        self.clave_input.setEchoMode(QLineEdit.Password)
        self.clave_input.setPlaceholderText("Tu clave del SII")
        clave_layout.addWidget(clave_label)
        clave_layout.addWidget(self.clave_input)
        cred_layout.addLayout(clave_layout)
        
        cred_group.setLayout(cred_layout)
        left_layout.addWidget(cred_group)
        
        # Grupo de opciones
        options_group = QGroupBox("⚙️ Opciones de Ejecución")
        options_group.setFont(QFont("Arial", 10))
        options_layout = QVBoxLayout()
        
        # Modo headless
        self.headless_check = QCheckBox("Modo sin interfaz (Headless)")
        self.headless_check.setToolTip("El navegador no se mostrará")
        options_layout.addWidget(self.headless_check)
        
        # Botón de configuración avanzada
        self.advanced_btn = QPushButton("Configuración Avanzada")
        self.advanced_btn.clicked.connect(self.show_advanced_settings)
        options_layout.addWidget(self.advanced_btn)
        
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Iniciar Proceso")
        self.start_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.start_btn.clicked.connect(self.iniciar_proceso)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Detener")
        self.stop_btn.setFont(QFont("Arial", 11))
        self.stop_btn.clicked.connect(self.detener_proceso)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.stop_btn)
        left_layout.addLayout(action_layout)
        
        # Espaciador
        left_layout.addStretch()
        
        # Panel derecho - Logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Área de logs
        log_group = QGroupBox("📋 Logs del Proceso")
        log_group.setFont(QFont("Arial", 10))
        log_layout = QVBoxLayout()
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        log_layout.addWidget(self.progress_bar)
        
        # Área de texto para logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        # Botones de log
        log_buttons_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("🗑️ Limpiar Logs")
        self.clear_log_btn.clicked.connect(self.limpiar_logs)
        self.save_log_btn = QPushButton("💾 Guardar Logs")
        self.save_log_btn.clicked.connect(self.guardar_logs)
        
        log_buttons_layout.addWidget(self.clear_log_btn)
        log_buttons_layout.addWidget(self.save_log_btn)
        log_buttons_layout.addStretch()
        
        log_layout.addLayout(log_buttons_layout)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])
        
        main_layout.addWidget(splitter)
        
        # Estado
        self.status_label = QLabel("👋 Listo para comenzar")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
    def set_dark_theme(self):
        """Establecer tema oscuro"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        
        self.setPalette(dark_palette)
        
    def iniciar_proceso(self):
        """Iniciar el proceso de automatización"""
        # Validar campos
        rut_usuario = self.rut_usuario_input.text().strip()
        clave = self.clave_input.text().strip()
        
        if not rut_usuario:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa el RUT del usuario")
            return
            
        if not clave:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa la clave del SII")
            return
        
        # Deshabilitar botón de inicio
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Limpiar logs anteriores
        self.log_text.clear()
        self.status_label.setText("🚀 Iniciando proceso...")
        
        # Obtener parámetros
        rut_empresa = self.rut_empresa_input.text().strip()
        headless = self.headless_check.isChecked()
        
        # Crear worker
        self.worker = self.automator.iniciar_proceso(
            rut_empresa, rut_usuario, clave, headless
        )
        
        if self.worker:
            # Conectar señales
            self.worker.log_signal.connect(self.actualizar_log)
            self.worker.progress_signal.connect(self.actualizar_progreso)
            self.worker.finished_signal.connect(self.proceso_finalizado)
            
            # Iniciar worker
            self.worker.start()
        else:
            QMessageBox.warning(self, "Advertencia", "Ya hay un proceso en ejecución")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def detener_proceso(self):
        """Detener el proceso en ejecución"""
        if self.worker and self.worker.isRunning():
            if self.automator.detener_proceso():
                self.actualizar_log("🛑 Proceso detenido por el usuario")
                self.status_label.setText("⏹️ Proceso detenido")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo detener el proceso")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def actualizar_log(self, mensaje):
        """Actualizar el área de logs"""
        self.log_text.append(mensaje)
        # Auto-scroll al final
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def actualizar_progreso(self, valor):
        """Actualizar la barra de progreso"""
        self.progress_bar.setValue(valor)
    
    def proceso_finalizado(self, exito, mensaje):
        """Manejar la finalización del proceso"""
        if exito:
            self.actualizar_log(f"✅ {mensaje}")
            self.status_label.setText("🎉 Proceso completado exitosamente")
        else:
            self.actualizar_log(f"❌ {mensaje}")
            self.status_label.setText("❌ Proceso falló")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def limpiar_logs(self):
        """Limpiar el área de logs"""
        self.log_text.clear()
        self.actualizar_log("🗑️ Logs limpiados")
    
    def guardar_logs(self):
        """Guardar logs a archivo"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_sii_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.actualizar_log(f"💾 Logs guardados en: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron guardar los logs: {str(e)}")
    
    def show_advanced_settings(self):
        """Mostrar configuración avanzada"""
        QMessageBox.information(self, "Configuración Avanzada", 
            "Esta funcionalidad está en desarrollo.\n\n"
            "Próximamente podrás:\n"
            "• Configurar tiempos de espera\n"
            "• Seleccionar periodo específico\n"
            "• Configurar notificaciones\n"
            "• Y más...")
    
    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Confirmar salida",
                "Hay un proceso en ejecución. ¿Estás seguro de que quieres salir?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.detener_proceso()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Establecer estilo de aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = SIIAutomatorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()