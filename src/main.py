"""
Interfaz principal para la automatización del SII - VERSIÓN CORREGIDA
"""
import sys
import os

def get_base_path():
    """ Obtener la ruta base correcta, ya sea en desarrollo o en ejecutable congelado """
    if getattr(sys, 'frozen', False):
        # Si estamos en un ejecutable (PyInstaller)
        return sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    else:
        # Si estamos en desarrollo
        return os.path.dirname(os.path.abspath(__file__))

# ================= CONFIGURACIÓN DE IMPORTS =================
# Obtener el directorio base
SCRIPT_DIR = get_base_path()

if getattr(sys, 'frozen', False):
    # En modo ejecutable, la raíz del proyecto es donde está el .exe
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    # En desarrollo, es el padre de src
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

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
print("🔍 Importando SIIAutomator...")

try:
    from core.sii_automator import SIIAutomator
    print("✅ SIIAutomator importado exitosamente")
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
                                 QProgressBar, QSplitter, QFrame, QTabWidget,
                                 QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog)
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
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
        self.active_workers = []  # Para procesamiento paralelo
        self.MAX_CONCURRENT = 3    # Máximo 3 navegadores simultáneos
        self.bulk_results = [] # Lista para almacenar resultados del proceso masivo
        self.init_ui()

    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Automatizador SII - Aceptación de Facturas")
        self.setGeometry(100, 100, 1000, 850) # Un poco más grande para la tabla
        
        # Establecer tema personalizado
        self.set_custom_theme()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # --- CABECERA ---
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # --- CUERPO PRINCIPAL CON TABS ---
        self.tabs = QTabWidget()
        
        # Tab 1: Procesamiento Individual
        self.tab_individual = QWidget()
        self._setup_tab_individual()
        self.tabs.addTab(self.tab_individual, "👤 Procesamiento Individual")
        
        # Tab 2: Procesamiento Masivo (Excel)
        self.tab_masivo = QWidget()
        self._setup_tab_masivo()
        self.tabs.addTab(self.tab_masivo, "📊 Procesamiento Masivo (Excel)")
        
        main_layout.addWidget(self.tabs)
        
        # --- FOOTER ---
        self.status_label = QLabel("✨🦄 <i>Développé par une unicornia muy competente</i> © 2026")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #365ca3; padding: 10px; border-top: 1px solid #a3b4cb;")
        main_layout.addWidget(self.status_label)

    def _create_header(self):
        """Crea el widget de cabecera con logo y título"""
        header = QWidget()
        layout = QVBoxLayout(header)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(SCRIPT_DIR, "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if pixmap.width() > 250:
                pixmap = pixmap.scaledToWidth(250, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.setWindowIcon(QIcon(logo_path))
        layout.addWidget(self.logo_label)

        # Título
        title_label = QLabel("Automatizador SII")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #365ca3; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        return header

    def _setup_tab_individual(self):
        """Configura la interfaz para procesamiento de una sola empresa"""
        layout = QVBoxLayout(self.tab_individual)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel Izquierdo: Configuración
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        cred_group = QGroupBox("🔑 Credenciales de Acceso")
        cred_layout = QVBoxLayout()
        
        # RUT
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 76.123.456-7")
        cred_layout.addWidget(QLabel("RUT:*"))
        cred_layout.addWidget(self.rut_input)
        
        # Clave
        self.clave_input = QLineEdit()
        self.clave_input.setEchoMode(QLineEdit.Password)
        self.clave_input.setPlaceholderText("Tu clave del SII")
        cred_layout.addWidget(QLabel("Clave SII:*"))
        cred_layout.addWidget(self.clave_input)
        
        cred_group.setLayout(cred_layout)
        left_layout.addWidget(cred_group)
        
        # Opciones
        options_group = QGroupBox("⚙️ Opciones")
        options_layout = QVBoxLayout()
        self.headless_check = QCheckBox("Modo sin interfaz (Headless)")
        options_layout.addWidget(self.headless_check)
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # Botones
        self.start_btn = QPushButton("🚀 Iniciar Proceso")
        self.start_btn.clicked.connect(self.iniciar_proceso)
        self.start_btn.setMinimumHeight(50)
        self.stop_btn = QPushButton("⏹️ Detener")
        self.stop_btn.clicked.connect(self.detener_proceso)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.stop_btn)
        left_layout.addStretch()
        
        # Panel Derecho: Logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.progress_bar_ind = QProgressBar()
        right_layout.addWidget(self.progress_bar_ind)
        
        self.log_text_ind = QTextEdit()
        self.log_text_ind.setReadOnly(True)
        right_layout.addWidget(self.log_text_ind)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)
        
    def _setup_tab_masivo(self):
        """Configura la interfaz para procesamiento por Excel"""
        layout = QVBoxLayout(self.tab_masivo)
        
        # Panel Superior: Carga de archivo
        top_group = QGroupBox("📁 Carga de Datos")
        top_layout = QHBoxLayout()
        
        self.excel_path_label = QLabel("No se ha seleccionado archivo")
        self.excel_path_label.setStyleSheet("color: #666; font-style: italic;")
        btn_load = QPushButton("📁 Cargar Excel")
        btn_load.clicked.connect(self._cargar_excel)
        
        top_layout.addWidget(self.excel_path_label, 1)
        top_layout.addWidget(btn_load)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # Tabla de datos
        self.table_masivo = QTableWidget()
        self.table_masivo.setColumnCount(4)
        self.table_masivo.setHorizontalHeaderLabels(["RUT Empresa", "RUT Usuario", "Clave", "Estado"])
        # Opción headless masiva
        self.headless_masivo_check = QCheckBox("Modo sin interfaz (Headless)")
        self.headless_masivo_check.setChecked(True) # Por defecto activado para masividad
        layout.addWidget(self.headless_masivo_check)

        # Botones de ejecución masiva
        btn_layout = QHBoxLayout()
        self.start_masivo_btn = QPushButton("🚀 Iniciar Todo el Excel")
        self.start_masivo_btn.clicked.connect(self._iniciar_proceso_masivo)
        self.start_masivo_btn.setMinimumHeight(50)
        self.start_masivo_btn.setEnabled(False)
        
        self.stop_masivo_btn = QPushButton("⏹️ Detener Proceso")
        self.stop_masivo_btn.clicked.connect(self._detener_proceso_masivo)
        self.stop_masivo_btn.setEnabled(False)
        
        btn_layout.addWidget(self.start_masivo_btn)
        btn_layout.addWidget(self.stop_masivo_btn)
        layout.addLayout(btn_layout)
        
        # Logs masivos
        self.log_text_masivo = QTextEdit()
        self.log_text_masivo.setReadOnly(True)
        self.log_text_masivo.setMaximumHeight(150)
        layout.addWidget(self.log_text_masivo)

    def _cargar_excel(self):
        """Maneja la carga de archivos Excel"""
        try:
            import pandas as pd
        except ImportError:
            QMessageBox.critical(self, "Error", "Pandas no está instalado. Ejecute 'pip install pandas openpyxl'")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Excel", "", "Excel Files (*.xlsx *.xls *.csv)")
        if file_path:
            try:
                self.excel_path_label.setText(file_path)
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Cargar en tabla
                self.table_masivo.setRowCount(len(df))
                for i, row in df.iterrows():
                    # Obtener RUT de cualquiera de las posibles columnas
                    rut_val = row.get('RUT', row.get('RUT_EMPRESA', row.get('RUT_USUARIO', '')))
                    self.table_masivo.setItem(i, 0, QTableWidgetItem(str(rut_val)))
                    self.table_masivo.setItem(i, 1, QTableWidgetItem(str(rut_val)))
                    self.table_masivo.setItem(i, 2, QTableWidgetItem("********")) # Ocultar clave por seguridad
                    # Guardar clave real en un dato oculto o lista interna
                    clave_val = row.get('CLAVE', row.get('CLAVE_SII', ''))
                    self.table_masivo.item(i, 2).setData(Qt.UserRole, str(clave_val))
                    self.table_masivo.setItem(i, 3, QTableWidgetItem("Pendiente"))
                
                self.start_masivo_btn.setEnabled(True)
                self._actualizar_log_masivo(f"✅ Excel cargado con {len(df)} empresas.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo leer el archivo: {str(e)}")

    def _iniciar_proceso_masivo(self):
        """Inicia el orquestador masivo concurrente"""
        self.current_bulk_row = 0
        self.proceso_masivo_detenido = False
        self.active_workers = []
        self.bulk_results = []
        self._actualizar_log_masivo(f"🚀 Iniciando procesamiento masivo (Máx {self.MAX_CONCURRENT} hilos)...")
        self.start_masivo_btn.setEnabled(False)
        self.stop_masivo_btn.setEnabled(True)
        
        # Iniciar los primeros workers
        for _ in range(self.MAX_CONCURRENT):
            self._procesar_siguiente_fila()

        
    def _procesar_siguiente_fila(self):
        """Toma la siguiente empresa disponible y lanza un worker"""
        if self.proceso_masivo_detenido:
            return

        if self.current_bulk_row >= self.table_masivo.rowCount():
            # Si no hay más filas y no hay workers activos, terminamos
            if not self.active_workers:
                self._finalizar_todo_el_proceso()
            return

        # Si ya alcanzamos el máximo de workers, esperar a que uno termine
        if len(self.active_workers) >= self.MAX_CONCURRENT:
            return

        # Obtener datos de la fila actual
        row_idx = self.current_bulk_row
        self.current_bulk_row += 1

        rut_empresa = self.table_masivo.item(row_idx, 0).text()
        rut_usuario = self.table_masivo.item(row_idx, 1).text()
        clave = self.table_masivo.item(row_idx, 2).data(Qt.UserRole)
        headless = self.headless_masivo_check.isChecked()

        # Actualizar UI
        self.table_masivo.setItem(row_idx, 3, QTableWidgetItem("⏳ Procesando..."))
        self._actualizar_log_masivo(f"▶️ Iniciando ({row_idx + 1}/{self.table_masivo.rowCount()}): {rut_empresa}")

        # Iniciar worker
        worker = self.automator.crear_worker_independiente(rut_empresa, rut_usuario, clave, headless)
        self.active_workers.append(worker)
        
        # Conectar señales con el índice de fila para saber cuál terminó
        worker.log_signal.connect(self._actualizar_log_masivo)
        worker.finished_signal.connect(lambda exito, msj, idx=row_idx, w=worker: self._on_bulk_step_finished(exito, msj, idx, w))
        worker.start()

    def _on_bulk_step_finished(self, exito, mensaje, row_idx, worker):
        """Maneja la finalización de UNA empresa en el modo masivo"""
        from datetime import datetime
        
        # Remover de workers activos
        if worker in self.active_workers:
            self.active_workers.remove(worker)

        rut_empresa = self.table_masivo.item(row_idx, 0).text()
        
        # Guardar resultado para el reporte
        self.bulk_results.append({
            'RUT Empresa': rut_empresa,
            'Estado': "Éxito" if exito else "Fallo",
            'Detalle': mensaje,
            'Fecha/Hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        estado = "✅ Éxito" if exito else "❌ Falló"
        self.table_masivo.setItem(row_idx, 3, QTableWidgetItem(estado))
        self._actualizar_log_masivo(f"🏁 Finalizado {rut_empresa}: {mensaje}")

        # Intentar procesar la siguiente fila
        self._procesar_siguiente_fila()

    def _finalizar_todo_el_proceso(self):
        """Llamado cuando termina todo el Excel"""
        self._actualizar_log_masivo("🎉 Fin del procesamiento masivo.")
        self.start_masivo_btn.setEnabled(True)
        self.stop_masivo_btn.setEnabled(False)
        
        if self.bulk_results:
            self._generar_reporte_final()


    def _generar_reporte_final(self):
        """Genera un archivo Excel con el resumen de los resultados"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(PROJECT_ROOT, "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Crear DataFrame y guardar
            df = pd.DataFrame(self.bulk_results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Reporte_Automatizacion_{timestamp}.xlsx"
            filepath = os.path.join(reports_dir, filename)
            
            df.to_excel(filepath, index=False)
            
            self._actualizar_log_masivo(f"📊 Reporte generado: {filename}")
            QMessageBox.information(self, "Reporte Generado", 
                f"Se ha generado un reporte Excel con los resultados en:\n\n{filepath}")
            
            # Intentar abrir la carpeta
            try:
                os.startfile(reports_dir)
            except:
                pass
                
        except Exception as e:
            self._actualizar_log_masivo(f"⚠️ Error al generar reporte: {str(e)}")

    def _detener_proceso_masivo(self):
        """Detiene el orquestador masivo"""
        self.proceso_masivo_detenido = True
        self._actualizar_log_masivo("🛑 Solicitando detención del proceso masivo...")
        
        # Detener todos los workers activos
        for w in self.active_workers:
            w.stop()
        
        self.active_workers = []
        self.start_masivo_btn.setEnabled(True)
        self.stop_masivo_btn.setEnabled(False)


    def _actualizar_log_masivo(self, msj):
        self.log_text_masivo.append(msj)
        
    # --- Métodos de compatibilidad con código anterior ---
    def actualizar_log(self, mensaje):
        self._actualizar_log_individual(mensaje)
        
    def _actualizar_log_individual(self, mensaje):
        self.log_text_ind.append(mensaje)
        cursor = self.log_text_ind.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text_ind.setTextCursor(cursor)

    def actualizar_progreso(self, valor):
        self.progress_bar_ind.setValue(valor)
        
    def set_custom_theme(self):
        """Establecer tema personalizado basado en requerimientos del usuario"""
        # Paleta de colores
        COLOR_FONDO = "#d4dce4"
        COLOR_LETRAS = "#365ca3"
        COLOR_DETALLES = "#a3b4cb"
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLOR_FONDO))
        palette.setColor(QPalette.WindowText, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(COLOR_DETALLES))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.Text, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.Button, QColor(COLOR_DETALLES))
        palette.setColor(QPalette.ButtonText, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.Highlight, QColor(COLOR_LETRAS))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(palette)
        
        # Estilos específicos para widgets mediante CSS
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_FONDO};
            }}
            QGroupBox {{
                border: 2px solid {COLOR_DETALLES};
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                color: {COLOR_LETRAS};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {COLOR_DETALLES};
                border-radius: 4px;
                background-color: white;
                color: {COLOR_LETRAS};
            }}
            QPushButton {{
                background-color: {COLOR_DETALLES};
                color: {COLOR_LETRAS};
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0cedf;
            }}
            QPushButton:pressed {{
                background-color: #90a0b8;
            }}
            QTextEdit {{
                background-color: white;
                color: {COLOR_LETRAS};
                border: 1px solid {COLOR_DETALLES};
                border-radius: 4px;
            }}
            QProgressBar {{
                border: 1px solid {COLOR_DETALLES};
                border-radius: 5px;
                text-align: center;
                background-color: white;
                color: {COLOR_LETRAS};
            }}
            QProgressBar::chunk {{
                background-color: #4CAF50;
                width: 20px;
            }}
            QCheckBox {{
                color: {COLOR_LETRAS};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLOR_DETALLES};
                background: {COLOR_FONDO};
            }}
            QTabBar::tab {{
                background: {COLOR_DETALLES};
                color: {COLOR_LETRAS};
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: white;
                font-weight: bold;
            }}
            QTableWidget {{
                background-color: white;
                gridline-color: {COLOR_DETALLES};
                color: {COLOR_LETRAS};
            }}
            QHeaderView::section {{
                background-color: {COLOR_DETALLES};
                padding: 4px;
                border: 1px solid white;
                font-weight: bold;
                color: {COLOR_LETRAS};
            }}
        """)

    def iniciar_proceso(self):
        """Iniciar el proceso de automatización"""
        # Validar campos
        rut = self.rut_input.text().strip()
        clave = self.clave_input.text().strip()
        
        if not rut:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa el RUT")
            return
            
        if not clave:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa la clave del SII")
            return
        
        # Deshabilitar botón de inicio
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Limpiar logs anteriores
        self.log_text_ind.clear()
        self.status_label.setText("🚀 Iniciando proceso...")
        
        # Obtener parámetros
        headless = self.headless_check.isChecked()
        
        # Crear worker (usamos el mismo RUT para usuario y empresa)
        self.worker = self.automator.iniciar_proceso(
            rut, rut, clave, headless
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
        """Actualizar el área de logs individual (Compatibilidad)"""
        self._actualizar_log_individual(mensaje)
    
    def actualizar_progreso(self, valor):
        """Actualizar la barra de progreso individual (Compatibilidad)"""
        self.progress_bar_ind.setValue(valor)
    
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
        """Limpiar el área de logs individual"""
        self.log_text_ind.clear()
        self._actualizar_log_individual("🗑️ Logs limpiados")
    
    def guardar_logs(self):
        """Guardar logs individuales a archivo"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_sii_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text_ind.toPlainText())
            self._actualizar_log_individual(f"💾 Logs guardados en: {filename}")
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