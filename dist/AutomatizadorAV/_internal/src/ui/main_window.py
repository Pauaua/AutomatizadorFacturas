from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFileDialog,
                             QListWidget, QGroupBox, QProgressBar, QTabWidget,
                             QGridLayout, QMessageBox, QSpinBox, QCheckBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import os
import time
from core.document_processor import DocumentProcessor
from core.ocr_engine import OCREngine
from core.sii_automator import SIIAutomator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sii_automator = SIIAutomator()
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("Sistema de Aceptación Automática de Facturas")
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barra de título
        title_label = QLabel("AutoFacturas - Sistema de Procesamiento Automático")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Pestañas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Pestaña 1: Procesamiento de archivos
        self.create_processing_tab()
        
        # Pestaña 2: Automatización SII
        self.create_sii_tab()
        
        # Pestaña 3: Configuración
        self.create_config_tab()
        
        # Barra de estado
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Listo")
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        
    def create_processing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Selección de archivos
        file_group = QGroupBox("Selección de Archivos")
        file_layout = QGridLayout()
        
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list, 0, 0, 1, 3)
        
        self.btn_select_files = QPushButton("Seleccionar Archivos")
        self.btn_select_folder = QPushButton("Seleccionar Carpeta")
        self.btn_clear_list = QPushButton("Limpiar Lista")
        
        file_layout.addWidget(self.btn_select_files, 1, 0)
        file_layout.addWidget(self.btn_select_folder, 1, 1)
        file_layout.addWidget(self.btn_clear_list, 1, 2)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Grupo: Configuración de procesamiento
        process_group = QGroupBox("Configuración de Procesamiento")
        process_layout = QGridLayout()
        
        process_layout.addWidget(QLabel("Umbral de confianza:"), 0, 0)
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(0, 100)
        self.confidence_spin.setValue(80)
        process_layout.addWidget(self.confidence_spin, 0, 1)
        
        self.auto_accept_check = QCheckBox("Aceptar automáticamente")
        self.auto_accept_check.setChecked(True)
        process_layout.addWidget(self.auto_accept_check, 1, 0, 1, 2)
        
        self.save_log_check = QCheckBox("Guardar registro de procesamiento")
        self.save_log_check.setChecked(True)
        process_layout.addWidget(self.save_log_check, 2, 0, 1, 2)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.btn_process = QPushButton("Procesar Facturas")
        self.btn_process.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_process.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.btn_stop = QPushButton("Detener")
        self.btn_stop.setEnabled(False)
        
        action_layout.addWidget(self.btn_process)
        action_layout.addWidget(self.btn_stop)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # Área de log
        log_group = QGroupBox("Registro de Actividad")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Procesamiento")
        
    def create_sii_tab(self):
        """Crear pestaña para automatización SII"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Automatización SII - Aceptación Masiva")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Formulario de credenciales
        cred_group = QGroupBox("Credenciales SII")
        cred_layout = QGridLayout()
        
        # RUT Empresa
        cred_layout.addWidget(QLabel("RUT Empresa:*"), 0, 0)
        self.sii_rut_empresa = QLineEdit()
        self.sii_rut_empresa.setPlaceholderText("Ej: 76123456-K (opcional)")
        cred_layout.addWidget(self.sii_rut_empresa, 1, 1)
        
        # RUT Usuario
        cred_layout.addWidget(QLabel("RUT Usuario:"), 1, 0)
        self.sii_rut_usuario = QLineEdit()
        self.sii_rut_usuario.setPlaceholderText("Ej: 12345678-5")
        cred_layout.addWidget(self.sii_rut_usuario, 0, 1)
        
        # Clave
        cred_layout.addWidget(QLabel("Clave Tributaria:*"), 2, 0)
        self.sii_clave = QLineEdit()
        self.sii_clave.setEchoMode(QLineEdit.Password)
        self.sii_clave.setPlaceholderText("Clave SII")
        cred_layout.addWidget(self.sii_clave, 2, 1)
        
        # Recordar credenciales (no funcional por ahora)
        self.sii_remember = QCheckBox("Recordar credenciales")
        cred_layout.addWidget(self.sii_remember, 3, 0, 1, 2)
        
        # Configuraciones adicionales
        config_group = QGroupBox("Configuración")
        config_layout = QGridLayout()
        
        self.sii_headless = QCheckBox("Modo invisible (sin mostrar navegador)")
        config_layout.addWidget(self.sii_headless, 0, 0)
        
        self.sii_delay = QSpinBox()
        self.sii_delay.setRange(1, 10)
        self.sii_delay.setValue(2)
        self.sii_delay.setSuffix(" seg")
        config_layout.addWidget(QLabel("Delay entre acciones:"), 1, 0)
        config_layout.addWidget(self.sii_delay, 1, 1)
        
        self.sii_max_facturas = QSpinBox()
        self.sii_max_facturas.setRange(1, 100)
        self.sii_max_facturas.setValue(50)
        config_layout.addWidget(QLabel("Máx. facturas:"), 2, 0)
        config_layout.addWidget(self.sii_max_facturas, 2, 1)
        
        config_group.setLayout(config_layout)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        layout.addWidget(config_group)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.sii_btn_iniciar = QPushButton("🚀 INICIAR ACEPTACIÓN MASIVA")
        self.sii_btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.sii_btn_iniciar.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.sii_btn_detener = QPushButton("⏹️ DETENER PROCESO")
        self.sii_btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.sii_btn_detener.setEnabled(False)
        self.sii_btn_detener.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.sii_btn_test = QPushButton("🔧 PROBAR CONEXIÓN")
        self.sii_btn_test.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.sii_btn_test.setFont(QFont("Arial", 11))
        
        button_layout.addWidget(self.sii_btn_iniciar)
        button_layout.addWidget(self.sii_btn_detener)
        button_layout.addWidget(self.sii_btn_test)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Barra de progreso
        self.sii_progress = QProgressBar()
        self.sii_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.sii_progress)
        
        # Área de log
        log_group = QGroupBox("Registro del Proceso")
        log_layout = QVBoxLayout()
        
        self.sii_log = QTextEdit()
        self.sii_log.setReadOnly(True)
        self.sii_log.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: Consolas, Monaco, monospace;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        log_layout.addWidget(self.sii_log)
        
        # Botones de log
        log_buttons = QHBoxLayout()
        self.sii_btn_clear_log = QPushButton("Limpiar Log")
        self.sii_btn_save_log = QPushButton("Guardar Log")
        self.sii_btn_copy_log = QPushButton("Copiar Log")
        
        log_buttons.addWidget(self.sii_btn_clear_log)
        log_buttons.addWidget(self.sii_btn_save_log)
        log_buttons.addWidget(self.sii_btn_copy_log)
        log_buttons.addStretch()
        
        log_layout.addLayout(log_buttons)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Estado
        self.sii_status = QLabel("Listo para iniciar")
        self.sii_status.setAlignment(Qt.AlignCenter)
        self.sii_status.setStyleSheet("padding: 5px; background-color: #34495e; color: white; border-radius: 3px;")
        layout.addWidget(self.sii_status)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Automatización SII")
        
    def create_config_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Configuración de OCR
        ocr_group = QGroupBox("Configuración OCR")
        ocr_layout = QGridLayout()
        
        ocr_layout.addWidget(QLabel("Idioma OCR:"), 0, 0)
        # Aquí podrías añadir un combo box para seleccionar idioma
        ocr_layout.addWidget(QLabel("spa (Español)"), 0, 1)
        
        # Ruta de Tesseract
        ocr_layout.addWidget(QLabel("Ruta Tesseract:"), 1, 0)
        self.tesseract_path = QLineEdit()
        self.tesseract_path.setPlaceholderText("C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        ocr_layout.addWidget(self.tesseract_path, 1, 1)
        
        btn_browse_tesseract = QPushButton("Examinar")
        ocr_layout.addWidget(btn_browse_tesseract, 1, 2)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Configuración de salida
        output_group = QGroupBox("Configuración de Salida")
        output_layout = QGridLayout()
        
        output_layout.addWidget(QLabel("Carpeta de salida:"), 0, 0)
        self.output_path_label = QLabel("data/output/")
        output_layout.addWidget(self.output_path_label, 0, 1)
        
        btn_browse_output = QPushButton("Examinar")
        output_layout.addWidget(btn_browse_output, 0, 2)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Configuración general
        general_group = QGroupBox("Configuración General")
        general_layout = QGridLayout()
        
        self.auto_save = QCheckBox("Guardar automáticamente resultados")
        general_layout.addWidget(self.auto_save, 0, 0)
        
        self.notifications = QCheckBox("Mostrar notificaciones")
        general_layout.addWidget(self.notifications, 1, 0)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Espacio flexible
        layout.addStretch()
        
        # Botones de configuración
        config_buttons = QHBoxLayout()
        btn_save_config = QPushButton("💾 Guardar Configuración")
        btn_load_config = QPushButton("📂 Cargar Configuración")
        btn_reset_config = QPushButton("🔄 Restablecer")
        
        config_buttons.addWidget(btn_save_config)
        config_buttons.addWidget(btn_load_config)
        config_buttons.addWidget(btn_reset_config)
        config_buttons.addStretch()
        
        layout.addLayout(config_buttons)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Configuración")
        
    def setup_connections(self):
        # Conexiones procesamiento de archivos
        self.btn_select_files.clicked.connect(self.select_files)
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_clear_list.clicked.connect(self.clear_file_list)
        self.btn_process.clicked.connect(self.start_processing)
        
        # Conexiones SII
        self.sii_btn_iniciar.clicked.connect(self.iniciar_sii)
        self.sii_btn_detener.clicked.connect(self.detener_sii)
        self.sii_btn_test.clicked.connect(self.probar_conexion_sii)
        self.sii_btn_clear_log.clicked.connect(self.limpiar_log_sii)
        self.sii_btn_save_log.clicked.connect(self.guardar_log_sii)
        self.sii_btn_copy_log.clicked.connect(self.copiar_log_sii)
        
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar facturas",
            "",
            "Documentos (*.pdf *.jpg *.jpeg *.png *.tiff);;Todos los archivos (*.*)"
        )
        
        if files:
            for file in files:
                self.file_list.addItem(file)
            self.log_text.append(f"✓ Se agregaron {len(files)} archivos")
            
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        
        if folder:
            # Buscar archivos de imagen y PDF
            import glob
            extensions = ['*.pdf', '*.jpg', '*.jpeg', '*.png', '*.tiff']
            files = []
            
            for ext in extensions:
                files.extend(glob.glob(os.path.join(folder, ext)))
            
            for file in files:
                self.file_list.addItem(file)
            
            self.log_text.append(f"✓ Se agregaron {len(files)} archivos de la carpeta")
            
    def clear_file_list(self):
        self.file_list.clear()
        self.log_text.append("Lista de archivos limpiada")
        
    def start_processing(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay archivos para procesar")
            return
            
        self.log_text.append("Iniciando procesamiento...")
        # Aquí iniciarías el procesamiento real
        
    # ============ FUNCIONES SII ============
    
    def iniciar_sii(self):
        """Iniciar el proceso de automatización SII"""
        rut_empresa = self.sii_rut_empresa.text().strip()
        rut_usuario = self.sii_rut_usuario.text().strip()
        clave = self.sii_clave.text().strip()
        headless = self.sii_headless.isChecked()
        
        # Validaciones
        if not rut_usuario:
            QMessageBox.warning(self, "Advertencia", "Debe ingresar RUT usuario")
            return
        
        if not clave:
            QMessageBox.warning(self, "Advertencia", "Debe ingresar clave tributaria")
            return
        
        # Validar formato de RUT
        if "-" not in rut_usuario:
            respuesta = QMessageBox.question(
                self,
                "Formato de RUT",
                "El RUT no tiene guión. ¿Desea continuar de todos modos?\n\nFormato recomendado: 12345678-5",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No:
                return
        
        # Deshabilitar botón de inicio
        self.sii_btn_iniciar.setEnabled(False)
        self.sii_btn_detener.setEnabled(True)
        self.sii_btn_test.setEnabled(False)
        
        # Limpiar y preparar interfaz
        self.sii_log.clear()
        self.sii_progress.setValue(0)
        self.sii_status.setText("Procesando...")
        self.sii_status.setStyleSheet("padding: 5px; background-color: #f39c12; color: white; border-radius: 3px;")
        
        # Mostrar información inicial
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ======= INICIANDO PROCESO SII =======")
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] RUT Usuario: {rut_usuario}")
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] Modo: {'Invisible' if headless else 'Visible'}")
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] Máx. facturas: {self.sii_max_facturas.value()}")
        
        # Crear y configurar worker
        worker = self.sii_automator.iniciar_proceso(rut_empresa, rut_usuario, clave, headless)
        
        if worker:
            # Conectar señales
            worker.log_signal.connect(self.actualizar_log_sii)
            worker.progress_signal.connect(self.sii_progress.setValue)
            worker.finished_signal.connect(self.sii_proceso_finalizado)
            
            # Iniciar worker
            worker.start()
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ✅ Proceso iniciado correctamente")
        else:
            QMessageBox.warning(self, "Error", "Ya hay un proceso en ejecución")
            self.sii_btn_iniciar.setEnabled(True)
            self.sii_btn_test.setEnabled(True)
    
    def detener_sii(self):
        """Detener el proceso SII"""
        if self.sii_automator.detener_proceso():
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ⏹️ Proceso detenido por el usuario")
            self.sii_proceso_finalizado(True, "Proceso detenido manualmente")
        else:
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ℹ No hay proceso en ejecución")
    
    def probar_conexion_sii(self):
        """Probar conexión con el SII"""
        rut_usuario = self.sii_rut_usuario.text().strip()
        clave = self.sii_clave.text().strip()
        
        if not rut_usuario or not clave:
            QMessageBox.warning(self, "Advertencia", "Ingrese RUT y clave para probar")
            return
        
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] 🔧 Probando conexión con SII...")
        # Aquí podrías implementar una prueba simple de conexión
        
    def actualizar_log_sii(self, mensaje):
        """Actualizar el log de SII"""
        timestamp = time.strftime('%H:%M:%S')
        # Añadir emoji según el tipo de mensaje
        if mensaje.startswith("✓"):
            formatted = f"[{timestamp}] ✅ {mensaje[1:]}"
        elif mensaje.startswith("✗"):
            formatted = f"[{timestamp}] ❌ {mensaje[1:]}"
        elif mensaje.startswith("⚠"):
            formatted = f"[{timestamp}] ⚠️ {mensaje[1:]}"
        elif mensaje.startswith("ℹ"):
            formatted = f"[{timestamp}] ℹ️ {mensaje[1:]}"
        else:
            formatted = f"[{timestamp}] {mensaje}"
        
        self.sii_log.append(formatted)
        self.sii_log.ensureCursorVisible()
    
    def sii_proceso_finalizado(self, exito, mensaje):
        """Manejar finalización del proceso SII"""
        # Habilitar/deshabilitar botones
        self.sii_btn_iniciar.setEnabled(True)
        self.sii_btn_detener.setEnabled(False)
        self.sii_btn_test.setEnabled(True)
        
        # Actualizar barra de progreso
        self.sii_progress.setValue(100)
        
        # Actualizar estado
        if exito:
            self.sii_status.setText("Completado exitosamente")
            self.sii_status.setStyleSheet("padding: 5px; background-color: #27ae60; color: white; border-radius: 3px;")
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ✅ {mensaje}")
            
            if "aceptadas" in mensaje.lower():
                QMessageBox.information(self, "✅ Proceso Completado", 
                                      f"Proceso finalizado exitosamente.\n\n{mensaje}")
        else:
            self.sii_status.setText("Error en el proceso")
            self.sii_status.setStyleSheet("padding: 5px; background-color: #e74c3c; color: white; border-radius: 3px;")
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ❌ {mensaje}")
            
            QMessageBox.critical(self, "❌ Error en el Proceso", 
                               f"Ocurrió un error durante el proceso:\n\n{mensaje}")
    
    def limpiar_log_sii(self):
        """Limpiar el log de SII"""
        self.sii_log.clear()
        self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] Log limpiado")
    
    def guardar_log_sii(self):
        """Guardar el log en un archivo"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Log",
                f"log_sii_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                "Archivos de texto (*.txt);;Todos los archivos (*.*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.sii_log.toPlainText())
                
                self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ✅ Log guardado en: {file_path}")
        except Exception as e:
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ❌ Error al guardar log: {str(e)}")
    
    def copiar_log_sii(self):
        """Copiar el log al portapapeles"""
        try:
            import pyperclip
            pyperclip.copy(self.sii_log.toPlainText())
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ✅ Log copiado al portapapeles")
        except ImportError:
            # Fallback usando Qt
            clipboard = QApplication.clipboard()
            clipboard.setText(self.sii_log.toPlainText())
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ✅ Log copiado al portapapeles")
        except Exception as e:
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ❌ Error al copiar log: {str(e)}")
    
    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        # Detener cualquier proceso en ejecución
        if self.sii_automator.detener_proceso():
            self.sii_log.append(f"[{time.strftime('%H:%M:%S')}] ⏹️ Proceso SII detenido por cierre de aplicación")
        
        reply = QMessageBox.question(
            self,
            'Confirmar salida',
            '¿Está seguro de que desea salir?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())