"""
Módulo para automatizar la aceptación de facturas en el SII - VERSION MEJORADA PARA PESTAÑAS DINÁMICAS
"""
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.common.keys import Keys
import re
import os
import shutil
from datetime import datetime, timedelta

def get_project_root():
    """Obtener el directorio raíz del proyecto (donde se guardan logs y reportes)"""
    if getattr(sys, 'frozen', False):
        # En modo ejecutable, el directorio raíz es donde está el .exe
        return os.path.dirname(sys.executable)
    else:
        # En desarrollo, es el directorio de trabajo actual o el padre de src
        cwd = os.getcwd()
        # Si estamos ejecutando desde src/, subir un nivel
        if os.path.basename(cwd) == 'src':
            return os.path.dirname(cwd)
        return cwd


# ================= CONFIGURACIÓN ACTUALIZADA DEL SII =================
SII_URLS = {
    'portal': 'https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'login': 'https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'servicios_online': 'https://www.sii.cl/servicios_online/1042-.html',
    'factura_electronica': 'https://www.sii.cl/servicios_online/1039-3256.html',
    'registro_compras': 'https://www.sii.cl/servicios_online/1042-3253.html',
    'facturas': 'https://www4.sii.cl/consdcvinternetui/#/index',
}

SII_SELECTORS = {
    'campo_rut': [
        (By.ID, "rutcntr"),
        (By.NAME, "rutcntr"),
        (By.ID, "rut"),
        (By.NAME, "rut"),
    ],
    'campo_clave': [
        (By.ID, "clave"),
        (By.NAME, "clave"),
        (By.XPATH, "//input[@type='password']"),
    ],
    'campo_dv': [
        (By.ID, "dvcntr"),
        (By.NAME, "dvcntr"),
        (By.ID, "dv"),
        (By.NAME, "dv"),
    ],
    'boton_login': [
        (By.ID, "bt_ingresar"),
        (By.NAME, "bt_ingresar"),
        (By.XPATH, "//button[@type='submit']"),
    ],
    'menu_servicios': [
        (By.XPATH, "//a[contains(., 'Servicios Online')]"),
        (By.XPATH, "//a[contains(@href, 'servicios_online')]"),
        (By.XPATH, "//li[contains(., 'Servicios Online')]/a"),
    ],
    'factura_electronica': [
        (By.XPATH, "//a[contains(., 'Factura Electrónica')]"),
        (By.XPATH, "//a[contains(@href, '1039-3256')]"),
    ],
    'registro_compras_ventas': [
        (By.XPATH, "//a[contains(., 'Registro de Compras y Ventas')]"),
        (By.XPATH, "//a[contains(@href, '1042-3253')]"),
    ],
    'ingresar_registro': [
        (By.XPATH, "//a[contains(., 'Ingresar') and contains(@href, 'consdcvinternetui')]"),
        (By.XPATH, "//button[contains(., 'Ingresar al Registro')]"),
        (By.XPATH, "//a[contains(@href, 'consdcvinternetui')]"),
    ],
    'tab_compra': [
        "//button[contains(., 'COMPRA')]",
        "//a[contains(., 'COMPRA')]",
        "//li[contains(., 'COMPRA')]",
        "//button[contains(@class, 'tab') and contains(., 'COMPRA')]",
    ],
    'tab_venta': [
        "//button[contains(., 'VENTA')]",
        "//a[contains(., 'VENTA')]",
        "//li[contains(., 'VENTA')]",
    ],
    # NUEVOS SELECTORES ESPECÍFICOS PARA PESTAÑAS DINÁMICAS
    'tabs_principales': [
        "//button[contains(., 'Pendientes') and not(contains(., 'Registro'))]",
        "//a[contains(., 'Pendientes') and not(contains(., 'Registro'))]",
        "//li[contains(., 'Pendientes') and not(contains(., 'Registro'))]",
        "//span[contains(., 'Pendientes') and not(contains(., 'Registro'))]",
        "//div[contains(@class, 'tab') and contains(., 'Pendientes')]",
        "//button[text()='Pendientes' or text()=' PENDIENTES ']",
    ],
    'contenido_pendientes': [
        "//div[contains(@class, 'pendientes') and contains(@class, 'active')]",
        "//div[contains(@class, 'content') and contains(@class, 'pendientes')]",
        "//div[contains(@id, 'pendientes') and contains(@class, 'show')]",
        "//div[contains(@class, 'tab-content') and contains(., 'pendientes')]",
        "//div[contains(@class, 'tabla') and contains(., 'pendientes')]",
    ],
    'boton_aceptar': [
        "//button[contains(., 'Aceptar')]",
        "//button[contains(., 'aceptar')]",
        "//a[contains(., 'Aceptar')]",
    ],
    'select_periodo': [
        (By.ID, "periodo"),
        (By.NAME, "periodo"),
        (By.XPATH, "//select[contains(@id, 'periodo')]"),
        (By.XPATH, "//select[contains(@name, 'ano')]"),
    ],
    'select_mes': [
        (By.ID, "mes"),
        (By.NAME, "mes"),
        (By.XPATH, "//select[contains(@id, 'mes')]"),
        (By.XPATH, "//select[contains(@name, 'mes')]"),
    ],
    'boton_consultar': [
        "//button[contains(., 'Consultar')]",
        "//input[@value='Consultar']",
        "//button[contains(., 'Buscar')]",
    ],
    # NUEVOS SELECTORES PARA ACEPTACIÓN MASIVA
    'checkbox_seleccionar_todo': [
        "//input[@type='checkbox' and contains(@id, 'selectAll')]",
        "//input[@type='checkbox' and contains(@name, 'selectAll')]",
        "//input[@type='checkbox' and contains(@class, 'select-all')]",
        "//th[contains(., 'Seleccionar')]//input[@type='checkbox']",
        "//input[@type='checkbox' and contains(@id, 'checkall')]",
        "//input[@type='checkbox' and contains(@name, 'checkall')]",
        "//input[@type='checkbox' and contains(@class, 'check-all')]",
    ],
    'checkbox_factura_individual': [
        "//input[@type='checkbox' and contains(@name, 'select')]",
        "//input[@type='checkbox' and contains(@id, 'select')]",
        "//input[@type='checkbox' and @value]",
        "//td[contains(@class, 'selection')]//input[@type='checkbox']",
        "//tr[contains(@class, 'row')]//input[@type='checkbox']",
        "//tbody//input[@type='checkbox']",
        "//input[@type='checkbox' and contains(@class, 'chk')]",
    ],
    'boton_aceptar_masivo': [
        "//button[contains(., 'Aceptar Seleccionados')]",
        "//button[contains(., 'Aceptar Masivo')]",
        "//button[contains(., 'Aceptar Todas')]",
        "//button[contains(., 'Acuso Recibo Masivo')]",
        "//button[contains(., 'Procesar Seleccionados')]",
        "//button[contains(., 'Aceptar Documentos')]",
        "//button[contains(., 'Acusar Recibido')]",
        "//button[contains(., 'Acuso Recibo')]",
    ],
    'confirmacion_aceptar_masivo': [
        "//button[contains(., 'Sí, aceptar')]",
        "//button[contains(., 'Confirmar')]",
        "//button[contains(., 'Aceptar') and contains(@class, 'btn-primary')]",
        "//button[contains(., 'Aceptar') and contains(@class, 'primary')]",
        "//button[contains(., 'Continuar')]",
        "//button[contains(., 'Cerrar')]",
    ],
    # NUEVOS SELECTORES PARA ENLACES DE TIPO DE DOCUMENTO
    'enlace_tipo_documento': [
        "//div[contains(@id, 'pendientes')]//a[contains(., '33')]",
        "//div[contains(@id, 'pendientes')]//a[contains(., '34')]",
        "//div[contains(@class, 'active')]//a[contains(., '33')]",
        "//div[contains(@class, 'active')]//a[contains(., '34')]",
        "//table[contains(., 'Resumen')]//a[contains(., '33') or contains(., '34')]",
        "//a[contains(., '33') and not(contains(@href, 'registro'))]",
        "//a[contains(., '34') and not(contains(@href, 'registro'))]",
    ],
    'modal_actualizar_datos': [
        "//div[contains(., 'actualizar') or contains(., 'Actualizar')]",
        "//div[@class='modal' and contains(., 'datos')]",
        "//div[contains(@class, 'modal') and contains(., 'más tarde')]",
    ],
    'boton_actualizar_mas_tarde': [
        "//button[contains(., 'más tarde')]",
        "//button[contains(., 'Más tarde')]",
        "//button[contains(., 'Ahora no')]",
        "//a[contains(., 'más tarde')]",
    ],
    # NUEVO: Selectores para verificar si hay pendientes
    'contador_pendientes': [
        "//span[contains(@class, 'contador') and contains(., 'Pendientes')]",
        "//div[contains(@class, 'contador') and contains(., 'Pendientes')]",
        "//span[contains(., 'Pendientes') and contains(@class, 'badge')]",
        "//span[contains(., 'Pendientes') and contains(@class, 'label')]",
    ],
    'tabla_facturas': [
        "//table[contains(@class, 'facturas')]",
        "//div[contains(@class, 'tabla-facturas')]",
        "//table[contains(@id, 'facturas')]",
        "//div[contains(@class, 'table-container')]",
        "//div[contains(@class, 'grid') and contains(., 'factura')]",
    ],
    'fila_factura': [
        "//tr[contains(@class, 'factura')]",
        "//tr[contains(@data-id, 'factura')]",
        "//tbody/tr",
        "//div[contains(@class, 'row') and contains(@class, 'factura')]",
    ],
    # SELECTORES PARA IDENTIFICAR PESTAÑA ACTIVA
    'tab_pendientes_activo': [
        "//button[contains(., 'Pendientes') and contains(@class, 'active')]",
        "//button[contains(., 'Pendientes') and contains(@class, 'selected')]",
        "//button[contains(., 'Pendientes') and contains(@class, 'current')]",
        "//button[contains(., 'Pendientes') and @aria-selected='true']",
        "//li[contains(., 'Pendientes') and contains(@class, 'active')]",
        "//a[contains(., 'Pendientes') and contains(@class, 'active')]",
        "//button[contains(@class, 'active') and contains(., 'Pendientes')]",
        "//button[contains(@class, 'tab-active') and contains(., 'Pendientes')]",
        "//li[contains(@class, 'active') and contains(., 'Pendientes')]",
        "//div[contains(@class, 'active') and contains(., 'Pendientes')]",
    ],
    'loading_indicator': [
        "//div[contains(@class, 'spinner')]",
        "//div[contains(@class, 'loading')]",
        "//div[contains(@id, 'loading')]",
        "//div[@class='modal-backdrop']",
        "//div[contains(@class, 'overlay')]",
    ],
}

TIMEOUTS = {
    'page_load': 12,
    'element_wait': 15,
    'login_wait': 5,
    'action_delay': 1.5,
}

# ================= FUNCIONES DE UTILIDAD =================
def validar_rut(rut_completo):
    """Validar formato de RUT chileno"""
    import re

    rut_pattern = re.compile(r'^(\d{1,3}(?:\.?\d{3}){2})-([\dkK])$')
    match = rut_pattern.match(rut_completo)

    if not match:
        if re.match(r'^\d{7,8}[\dkK]$', rut_completo):
            return True, "RUT aceptado"
        return False, "Formato de RUT inválido. Use: 12.345.678-9"

    return True, "RUT válido"

def limpiar_screenshots_antiguos(dias=7):
    """Borrar archivos de depuración antiguos para ahorrar espacio"""
    try:
        project_root = get_project_root()
        directorio = os.path.join(project_root, "logs", "screenshots")
        if not os.path.exists(directorio):
            return

        limite = datetime.now() - timedelta(days=dias)
        contador = 0

        for archivo in os.listdir(directorio):
            if archivo.startswith("debug_") and archivo.endswith(".png"):
                ruta_completa = os.path.join(directorio, archivo)
                # Verificar fecha de modificación
                mtime = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                if mtime < limite:
                    os.remove(ruta_completa)
                    contador += 1
        
        if contador > 0:
            print(f"🧹 Se han borrado {contador} capturas de pantalla antiguas (> {dias} días)")
    except Exception as e:
        print(f"⚠️ Error limpiando screenshots: {str(e)}")


def guardar_screenshot(driver, nombre):
    """Guardar screenshot con timestamp en carpeta dedicada"""
    try:
        project_root = get_project_root()
        # Asegurar que exista la carpeta
        directorio = os.path.join(project_root, "logs", "screenshots")
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"debug_{nombre}_{timestamp}.png"
        ruta_completa = os.path.join(directorio, nombre_archivo)
        
        driver.save_screenshot(ruta_completa)
        return ruta_completa
    except Exception as e:
        print(f"⚠️ Error guardando screenshot: {str(e)}")
        return ""

class SIIAutomatorWorker(QThread):
    """Worker para ejecutar la automatización SII en segundo plano"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, rut_empresa, rut_usuario, clave, headless=False):
        super().__init__()
        self.rut_empresa = rut_empresa
        self.rut_usuario = rut_usuario
        self.clave = clave
        self.headless = headless
        self.driver = None
        self.is_running = True
        self.driver_wait = None

    def _ingresar_rut_empresa(self):
        """Ingresa el RUT de la empresa si el campo está presente (maneja Input y Select)"""
        try:
            self.log_signal.emit("🏢 Verificando campo de RUT Empresa...")
            rut_field = None
            for selector_type, selector_value in SII_SELECTORS['campo_rut']:
                try:
                    elementos = self.driver.find_elements(selector_type, selector_value)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            rut_field = elemento
                            break
                    if rut_field: break
                except: continue
            
            if rut_field:
                tag_name = rut_field.tag_name.lower()
                self.log_signal.emit(f"📝 Detectado campo RUT ({tag_name}). Ingresando: {self.rut_empresa}")
                
                if tag_name == "select":
                    # Si es un desplegable, buscar por valor o texto
                    select = Select(rut_field)
                    try:
                        # Limpiar RUT de puntos y guion para comparar valores
                        rut_clean = self.rut_empresa.replace(".", "").replace("-", "")
                        encontrado = False
                        for opt in select.options:
                            opt_val = opt.get_attribute("value").replace(".", "").replace("-", "")
                            if rut_clean in opt_val:
                                select.select_by_value(opt.get_attribute("value"))
                                encontrado = True
                                break
                        if not encontrado:
                            select.select_by_visible_text(self.rut_empresa)
                    except:
                        # Respaldo: intentar coincidencia parcial en el texto
                        for opt in select.options:
                            if self.rut_empresa in opt.text:
                                select.select_by_visible_text(opt.text)
                                break
                else:
                    # Si es un input normal
                    rut_field.clear()
                    rut_field.send_keys(self.rut_empresa)
                    rut_field.send_keys(Keys.RETURN)
                
                time.sleep(1.5)
                return True
            return False
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error al ingresar RUT Empresa: {str(e)}")
            return False

    def _seleccionar_periodo_actual(self):
        """Selecciona el año y mes actuales según el sistema (con soporte para nombres en español)"""
        try:
            now = datetime.now()
            anio_actual = str(now.year)
            mes_actual_num = now.month
            
            meses_es = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            nombre_mes = meses_es.get(mes_actual_num, "")
            
            self.log_signal.emit(f"📅 Seleccionando periodo actual: {nombre_mes} {anio_actual}...")
            
            # Paso 1: Seleccionar año
            año_select_elem = None
            for selector in SII_SELECTORS['select_periodo']:
                try:
                    elemento = self.driver.find_element(*selector)
                    if elemento.is_displayed():
                        año_select_elem = elemento
                        break
                except: continue
            
            if año_select_elem:
                select = Select(año_select_elem)
                try:
                    select.select_by_visible_text(anio_actual)
                except:
                    try: select.select_by_value(anio_actual)
                    except: pass
                time.sleep(1)

            # Paso 2: Seleccionar mes
            mes_select_elem = None
            for selector in SII_SELECTORS['select_mes']:
                try:
                    elemento = self.driver.find_element(*selector)
                    if elemento.is_displayed():
                        mes_select_elem = elemento
                        break
                except: continue
            
            if mes_select_elem:
                select = Select(mes_select_elem)
                mes_seleccionado = False
                
                # Intentar por varias formas
                metodos = [
                    lambda: select.select_by_visible_text(nombre_mes),
                    lambda: select.select_by_value(str(mes_actual_num)),
                    lambda: select.select_by_value(str(mes_actual_num).zfill(2)),
                    lambda: select.select_by_index(mes_actual_num) # Asumiendo 1=Enero si hay "Seleccione"
                ]
                
                for metodo in metodos:
                    try:
                        metodo()
                        mes_seleccionado = True
                        break
                    except: continue
                
                if mes_seleccionado:
                    self.log_signal.emit(f"✅ Mes seleccionado: {nombre_mes}")
                else:
                    self.log_signal.emit("⚠️ No se pudo seleccionar el mes exacto, intentando el más reciente disponible.")
                    opciones = [i for i, opt in enumerate(select.options) if opt.get_attribute("value")]
                    if opciones:
                        select.select_by_index(opciones[-1]) # Fallback al último (que suele ser el actual si el SII está al día)

            # Paso 3: Clic en Consultar
            for selector in SII_SELECTORS['boton_consultar']:
                try:
                    botones = self.driver.find_elements(By.XPATH, selector)
                    for boton in botones:
                        if boton.is_displayed():
                            self.log_signal.emit("🔍 Haciendo clic en Consultar...")
                            self.driver.execute_script("arguments[0].click();", boton)
                            time.sleep(5)
                            return True
                except: continue
            
            return False
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error grave al seleccionar periodo: {str(e)}")
            return False

    def run(self):
        """Ejecuta el proceso de automatización - FLUJO CORREGIDO PARA PESTAÑAS DINÁMICAS"""
        exito = False
        mensaje_final = "Proceso interrumpido"
        
        try:
            self.is_running = True
            self.log_signal.emit("🚀 Iniciando proceso de automatización...")
            
            # LIMPIEZA: Borrar capturas antiguas antes de empezar
            limpiar_screenshots_antiguos(dias=7)

            # ================= CONFIGURACIÓN DEL NAVEGADOR =================
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless=new")
            else:
                chrome_options.add_argument("--start-maximized")

            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            self.log_signal.emit("⚙️ Configurando navegador...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver_wait = WebDriverWait(self.driver, TIMEOUTS['element_wait'])

            # ================= PASO 1: LOGIN =================
            self.log_signal.emit("🌐 Navegando al login del SII...")
            self.driver.get(SII_URLS['login'])
            time.sleep(3)

            # Manejar posible modal de actualizar datos
            self._manejar_modal_actualizar_datos()

            guardar_screenshot(self.driver, "01_login_page")

            # Buscar campos del formulario
            rut_field = None
            clave_field = None

            # Buscar campo RUT
            for selector_type, selector_value in SII_SELECTORS['campo_rut']:
                try:
                    elementos = self.driver.find_elements(selector_type, selector_value)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            rut_field = elemento
                            break
                    if rut_field:
                        break
                except:
                    continue

            # Buscar campo clave
            for selector_type, selector_value in SII_SELECTORS['campo_clave']:
                try:
                    elementos = self.driver.find_elements(selector_type, selector_value)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            clave_field = elemento
                            break
                    if clave_field:
                        break
                except:
                    continue

            if not rut_field or not clave_field:
                # Buscar alternativamente
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        inp_type = inp.get_attribute("type") or ""
                        inp_name = inp.get_attribute("name") or ""
                        if "rut" in inp_name.lower() and not rut_field:
                            rut_field = inp
                        elif inp_type == "password" and not clave_field:
                            clave_field = inp
                except:
                    pass

            if not rut_field or not clave_field:
                raise Exception("No se pudieron encontrar los campos de login")

            # Escribir credenciales
            rut_field.clear()
            rut_field.send_keys(self.rut_usuario)
            time.sleep(1)

            clave_field.clear()
            # Escribir caracter por caracter
            for char in self.clave:
                clave_field.send_keys(char)
                time.sleep(0.05)

            guardar_screenshot(self.driver, "02_credenciales_ingresadas")

            # Buscar y hacer clic en botón de login
            submit_button = None
            for selector_type, selector_value in SII_SELECTORS['boton_login']:
                try:
                    elemento = self.driver.find_element(selector_type, selector_value)
                    if elemento.is_displayed():
                        submit_button = elemento
                        break
                except:
                    continue

            if submit_button:
                submit_button.click()
            else:
                clave_field.send_keys(Keys.RETURN)

            self.log_signal.emit("✅ Formulario enviado, esperando login...")
            time.sleep(5)

            # Verificar login exitoso
            current_url = self.driver.current_url
            if "siihome.cgi" not in current_url:
                # Verificar errores
                page_source = self.driver.page_source.lower()
                error_indicators = ['incorrecto', 'inválido', 'error de autenticación', 'acceso denegado']
                for error in error_indicators:
                    if error in page_source:
                        raise Exception(f"Error de login: {error}")

            self.log_signal.emit("🎉 Login exitoso")
            guardar_screenshot(self.driver, "03_login_exitoso")

            # ================= PASO 2: NAVEGAR DIRECTO AL REGISTRO =================
            self.log_signal.emit("🚀 Navegando directamente al Registro de Compras y Ventas...")
            self.driver.get(SII_URLS['facturas'])
            time.sleep(4)

            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            if "consdcvinternetui" not in current_url:
                self.log_signal.emit(f"⚠️ URL actual: {current_url}. Reintentando navegación directa...")
                self.driver.get(SII_URLS['facturas'])
                time.sleep(4)

            self.log_signal.emit("✅ En página de registro de facturas")
            guardar_screenshot(self.driver, "07_registro_facturas")

            # Manejar posible modal de actualizar datos o mensajes informativos
            self._manejar_modal_actualizar_datos()
            self._cerrar_modales_inesperados()

            # ================= PASO 3: INGRESAR RUT Y SELECCIONAR FECHA =================
            self._ingresar_rut_empresa()
            self._seleccionar_periodo_actual()
            time.sleep(2)

            # ================= PASO 6: ASEGURAR PESTAÑA COMPRA =================
            self.log_signal.emit("🛒 Asegurando pestaña 'COMPRA'...")
            compra_clicked = False
            for selector in SII_SELECTORS['tab_compra']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            self.log_signal.emit("✅ Pestaña 'COMPRA' encontrada, seleccionando...")
                            self.driver.execute_script("arguments[0].click();", elemento)
                            compra_clicked = True
                            time.sleep(2) # Aumentar espera para carga de sub-pestañas
                            break
                    if compra_clicked: break
                except: continue

            if not compra_clicked:
                self.log_signal.emit("⚠️ No se encontró pestaña 'COMPRA' explícita, buscando texto en la página...")
                if "COMPRA" in self.driver.page_source:
                    self.log_signal.emit("✅ Texto 'COMPRA' detectado, procediendo con sub-pestañas")
                    compra_clicked = True

            # ================= PASO 7: ASEGURAR QUE ESTAMOS EN PESTAÑA PENDIENTES =================
            if not self._navegar_a_pendientes():
                self.log_signal.emit("ℹ️ No se detectaron facturas pendientes")
                exito = True
                mensaje_final = "No hay facturas pendientes"
                return

            # ================= PASO 8: PROCESAR DOCUMENTOS POR TIPO (ESTRICTO) =================
            # Definir tipos a procesar en orden según requerimiento
            codigos_a_procesar = ['(33)', '(34)']
            nombres_mapeo = {
                '(33)': 'Factura Electrónica (33)',
                '(34)': 'Factura no Afecta o Exenta Electrónica (34)'
            }
            
            self.log_signal.emit(f"📄 Iniciando procesamiento de tipos: {', '.join(codigos_a_procesar)}")
            
            total_facturas_aceptadas = 0
            encontrado_al_menos_uno = False

            for codigo in codigos_a_procesar:
                if not self.is_running:
                    break

                try:
                    # Re-encontrar el enlace por su código en cada iteración (con REINTENTOS)
                    enlace_actual = None
                    nombre_completo = nombres_mapeo.get(codigo, codigo)
                    codigo_sin_parentesis = codigo.replace('(', '').replace(')', '')
                    for intento in range(3):
                        self.log_signal.emit(f"🔍 Buscando categoría: {nombre_completo} (intento {intento+1}/3)...")
                        
                        # 1. PRIORIDAD: Buscar con selectores estrictos (dentro del contenedor Pendientes)
                        for selector in SII_SELECTORS['enlace_tipo_documento']:
                            try:
                                matches = self.driver.find_elements(By.XPATH, selector)
                                for m in matches:
                                    if not m.is_displayed(): continue
                                    txt = m.text.strip()
                                    if codigo in txt or (f" {codigo_sin_parentesis} " in f" {txt} "):
                                        enlace_actual = m
                                        break
                                if enlace_actual: break
                            except: continue

                        # 2. SEGUNDA OPCIÓN: Buscar en todos los enlaces solo si falló lo anterior
                        if not enlace_actual:
                            enlaces = self.driver.find_elements(By.TAG_NAME, "a")
                            for e in enlaces:
                                if not e.is_displayed(): continue
                                txt = e.text.strip()
                                # Coincidencia estricta con el código (33/34)
                                if (f"({codigo_sin_parentesis})" in txt) and ("registro" not in txt.lower()):
                                    enlace_actual = e
                                    break
                        
                        if enlace_actual:
                            break
                        
                        self.log_signal.emit(f"⏳ No encontrado aún, esperando 2s... (intento {intento+1}/3)")
                        time.sleep(2)

                    if not enlace_actual:
                        self.log_signal.emit(f"⚠️ Aviso: No se encontraron documentos en la categoría {nombre_completo}")
                        continue

                    encontrado_al_menos_uno = True
                    self.log_signal.emit(f"🚀 Entrando a: {nombre_completo}")

                    # Hacer clic
                    self.driver_wait.until(EC.element_to_be_clickable(enlace_actual))
                    self.driver.execute_script("arguments[0].click();", enlace_actual)
                    time.sleep(2.5)

                    guardar_screenshot(self.driver, f"10_entrando_a_{codigo.replace('(', '').replace(')', '')}")

                    # Procesar facturas dentro
                    aceptadas = self._procesar_facturas_en_tipo_documento(nombre_completo)
                    total_facturas_aceptadas += aceptadas

                    # Volver al resumen para el siguiente tipo
                    self.log_signal.emit(f"↩️ Finalizada categoría {codigo}, regresando al resumen de Pendientes...")
                    self._navegar_a_pendientes()
                    time.sleep(3)

                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error procesando {codigo}: {str(e)}")
                    try:
                        self.driver.back()
                        time.sleep(3)
                    except: pass
                    continue

            # Si no se encontró ningún enlace de los 4 tipos, intentar procesar vista actual por si acaso
            if not encontrado_al_menos_uno:
                self.log_signal.emit("🔍 No se encontraron categorías específicas, revisando vista general...")
                total_facturas_aceptadas += self._procesar_facturas_en_vista_actual()

            # Resultado final
            if total_facturas_aceptadas > 0:
                mensaje = f"🎉 Proceso completado. Se aceptaron {total_facturas_aceptadas} factura(s) en total"
                self.log_signal.emit(mensaje)
                exito = True
                mensaje_final = f"{total_facturas_aceptadas} facturas aceptadas"
            else:
                mensaje = "ℹ️ No hay facturas pendientes"
                self.log_signal.emit(mensaje)
                exito = True
                mensaje_final = "No hay facturas pendientes"

        except Exception as e:
            mensaje_final = f"Error en el proceso: {str(e)}"
            self.log_signal.emit(f"❌ {mensaje_final}")
            exito = False

        finally:
            if self.driver:
                self.log_signal.emit("🔒 Cerrando navegador...")
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            
            # Emitir señal de finalización DESPUÉS de cerrar el navegador
            self.finished_signal.emit(exito, mensaje_final)

    def _navegar_a_pendientes(self):
        """Asegura que la pestaña Pendientes esté activa y el contenido cargado (Refinado)"""
        try:
            # LIMPIEZA: Esperar a que desaparezcan indicadores de carga
            self._esperar_carga_sii()
            
            self.log_signal.emit("🔍 Asegurando navegación a pestaña 'Pendientes'...")
            
            # 1. Verificar si ya estamos ahí realmente
            if self._verificar_tab_pendientes_activa():
                self.log_signal.emit("✅ Confirmado: Ya estamos en la pestaña 'Pendientes'")
                return True
                
            # 2. Intentar hacer clic en los selectores de la pestaña Pendientes
            # Priorizar clics explícitos
            for selector in SII_SELECTORS['tabs_principales']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            self.log_signal.emit(f"👆 Clicando en pestaña 'Pendientes'...")
                            self.driver_wait.until(EC.element_to_be_clickable(elemento))
                            self.driver.execute_script("arguments[0].click();", elemento)
                            time.sleep(5)
                            if self._verificar_tab_pendientes_activa():
                                return True
                except: continue
                
            # 3. Si no funcionó, buscar si estamos atrapados en 'Registro'
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if "registro de compras" in body_text and "resúmenes" not in body_text:
                self.log_signal.emit("⚠️ Detectado en 'Registro', intentando forzar cambio a 'Pendientes'...")
                # Buscar botones que digan exactamente 'Pendientes'
                try:
                    btn_pend = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Pendientes')]")
                    self.driver.execute_script("arguments[0].click();", btn_pend)
                    time.sleep(5)
                except: pass

            # 4. Verificar de nuevo
            if self._verificar_tab_pendientes_activa():
                return True
                
            # Fallback final: revisar si el contenido de la tabla está ahí aunque la pestaña no marque activa
            return self._hay_facturas_pendientes_visualmente()
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error navegando a pendientes: {str(e)}")
            return False

    def _verificar_tab_pendientes_activa(self):
        """Verifica si la pestaña de pendientes está activa con alta precisión"""
        try:
            # 1. Buscar pestañas que estén activas/destacadas mediante clases específicas
            clases_activas = ['active', 'selected', 'current', 'tab-active', 'active-tab']
            for selector in SII_SELECTORS.get('tab_pendientes_activo', []):
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            clase = elemento.get_attribute("class")
                            if any(c in clase for c in clases_activas) or elemento.get_attribute("aria-selected") == "true":
                                # Triple check: El texto debe ser Pendientes
                                if "pendientes" in elemento.text.lower():
                                    return True
                except: continue
            
            # 2. Verificar contenido UNICO de Pendientes (La tabla de Resumen)
            try:
                # Si vemos el texto "Resúmenes" o códigos (33/34) sin el detalle del Registro
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                if "resúmenes" in body_text and ("(33)" in body_text or "(34)" in body_text) and "detalle" not in body_text:
                    return True
            except: pass
            
            # 3. También verificar si el contenedor de pendientes es visible
            for selector in SII_SELECTORS.get('contenido_pendientes', []):
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            # Doble check: Asegurarse que no sea el de Registro
                            id_attr = elemento.get_attribute("id").lower()
                            if "registro" not in id_attr and "pendientes" in id_attr:
                                return True
                            # Si no tiene id pero es el contenido visible bajo el tab Pendientes
                            if "pendientes" in elemento.text.lower()[:50]:
                                return True
                except: continue
            
            return False
        except:
            return False

    def _hay_facturas_pendientes_visualmente(self):
        """Verifica visualmente si hay facturas pendientes en la página"""
        try:
            # Buscar elementos visibles que indiquen pendientes
            patterns_to_find = [
                "pendiente",
                "por aceptar",
                "nueva",
                "recibida"
            ]
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            for pattern in patterns_to_find:
                if pattern in page_text:
                    if "no se encuentran" in page_text or "no hay" in page_text:
                        self.log_signal.emit("ℹ️ Se detectó mensaje de 'No hay facturas'")
                        return False
                    self.log_signal.emit(f"✅ Detectado texto '{pattern}' que indica pendientes")
                    return True
            
            # Buscar tablas o listas de facturas
            for selector in SII_SELECTORS['tabla_facturas']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            # Contar filas
                            for fila_selector in SII_SELECTORS['fila_factura']:
                                try:
                                    filas = elemento.find_elements(By.XPATH, fila_selector)
                                    if len(filas) > 0:
                                        self.log_signal.emit(f"📊 Encontradas {len(filas)} filas de posibles facturas pendientes")
                                        return True
                                except:
                                    continue
                except:
                    continue
            
            # Buscar checkboxes de selección
            for selector in SII_SELECTORS['checkbox_factura_individual']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    if len(checkboxes) > 0:
                        self.log_signal.emit(f"📊 Encontrados {len(checkboxes)} checkboxes que podrían ser facturas pendientes")
                        return True
                except:
                    continue
                    
            return False
        except:
            return False

    def _manejar_modal_actualizar_datos(self):
        """Manejar modal de actualización de datos si aparece"""
        try:
            time.sleep(2)
            for selector in SII_SELECTORS['modal_actualizar_datos']:
                try:
                    modales = self.driver.find_elements(By.XPATH, selector)
                    for modal in modales:
                        if modal.is_displayed():
                            self.log_signal.emit("ℹ️ Modal de actualización detectado")

                            # Buscar botón "más tarde"
                            for btn_selector in SII_SELECTORS['boton_actualizar_mas_tarde']:
                                try:
                                    botones = self.driver.find_elements(By.XPATH, btn_selector)
                                    for boton in botones:
                                        if boton.is_displayed():
                                            self.log_signal.emit("✅ Haciendo clic en 'Actualizar más tarde'")
                                            self.driver_wait.until(EC.element_to_be_clickable(boton))
                                            boton.click()
                                            time.sleep(2)
                                            return True
                                except:
                                    continue
                except:
                    continue
            return False
        except:
            return False

    def _cerrar_modales_inesperados(self):
        """Detectar y cerrar modales inesperados que bloquean la interacción (como alert-modal)"""
        try:
            # Selectores de modales conocidos por bloquear clics
            modales_bloqueantes = [
                "//div[@id='alert-modal' and contains(@style, 'display: block')]",
                "//div[contains(@class, 'modal-backdrop')]",
                "//div[contains(@class, 'modal') and contains(@class, 'in')]",
                "//div[@role='dialog' and not(contains(@style, 'display: none'))]"
            ]
            
            for selector in modales_bloqueantes:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elem in elementos:
                        if elem.is_displayed():
                            self.log_signal.emit(f"⚠️ Detectado modal bloqueante: {selector}. Intentando cerrar...")
                            
                            # Intentar encontrar botón de cerrar o aceptar dentro del modal
                            botones_cerrar = elem.find_elements(By.XPATH, ".//button[contains(., 'Aceptar') or contains(., 'Cerrar') or contains(., 'x') or @class='close']")
                            if botones_cerrar:
                                for btn in botones_cerrar:
                                    if btn.is_displayed():
                                        self.driver.execute_script("arguments[0].click();", btn)
                                        self.log_signal.emit("✅ Modal cerrado con botón")
                                        time.sleep(2)
                                        break
                            else:
                                # Fallback: Forzar cierre con JS si el modal tiene ID conocido
                                if "alert-modal" in selector:
                                    self.driver.execute_script("$('#alert-modal').modal('hide');")
                                    self.log_signal.emit("✅ Modal 'alert-modal' forzado a ocultarse con JS")
                                    time.sleep(2)
                except:
                    continue
        except:
            pass

    def _procesar_facturas_en_tipo_documento(self, tipo_documento):
        """Procesar facturas dentro de un tipo de documento específico (Detección continua de lotes)"""
        try:
            self.log_signal.emit(f"🔍 Procesando facturas en {tipo_documento}...")
            total_aceptadas_categoria = 0
            intentos_lote = 0
            max_lotes = 15 # Seguridad: Máximo 150 facturas por categoría
            
            while self.is_running and intentos_lote < max_lotes:
                intentos_lote += 1
                
                # Primero verificar si hay facturas pendientes en esta categoría
                if not self._hay_facturas_pendientes_en_categoria():
                    if intentos_lote == 1:
                        self.log_signal.emit(f"ℹ️ No hay facturas pendientes en {tipo_documento}")
                    else:
                        self.log_signal.emit(f"✅ Todas las facturas de {tipo_documento} han sido procesadas.")
                    break

                if intentos_lote > 1:
                    self.log_signal.emit(f"🔄 Detectadas más facturas en {tipo_documento}, procesando lote {intentos_lote}...")

                # Paso 1: Buscar y marcar todas las facturas pendientes
                checkboxes_marcados = self._marcar_todas_las_facturas_en_vista_actual()

                if checkboxes_marcados > 0:
                    self.log_signal.emit(f"✅ Marcadas {checkboxes_marcados} facturas en {tipo_documento}")

                    # Paso 2: Buscar botón de acuso de recibo masivo
                    boton_acuso_recibo_masivo = self._buscar_boton_acuso_recibo_masivo()

                    if boton_acuso_recibo_masivo:
                        self.log_signal.emit(f"✅ Botón de acuso de recibo masivo encontrado")

                        # Paso 3: Hacer clic en acuso de recibo masivo
                        guardar_screenshot(self.driver, f"11_antes_acuso_recibo_masivo_{tipo_documento.replace(' ', '_').replace('(', '').replace(')', '')}_lote{intentos_lote}")

                        self.driver_wait.until(EC.element_to_be_clickable(boton_acuso_recibo_masivo))
                        self.driver.execute_script("arguments[0].click();", boton_acuso_recibo_masivo)
                        time.sleep(3)

                        # Paso 4: Manejar el modal de confirmación
                        if self._manejar_modal_confirmacion_acuso_recibo():
                            total_aceptadas_categoria += checkboxes_marcados
                            self.log_signal.emit(f"✅ Lote de {checkboxes_marcados} facturas aceptado en {tipo_documento}. Revisando si quedan más...")
                            guardar_screenshot(self.driver, f"12_despues_acuso_recibo_masivo_{tipo_documento.replace(' ', '_').replace('(', '').replace(')', '')}_lote{intentos_lote}")
                            
                            # Esperar a que la página se refresque después de la aceptación masiva
                            time.sleep(5)
                        else:
                            self.log_signal.emit(f"⚠️ No se pudo confirmar el acuso de recibo en el lote {intentos_lote}")
                            break # Detener para evitar bucles infinitos en caso de error de UI
                    else:
                        self.log_signal.emit(f"⚠️ No se encontró botón de acuso de recibo masivo en {tipo_documento}")
                        break
                else:
                    self.log_signal.emit(f"ℹ️ No se encontraron facturas adicionales para marcar en {tipo_documento}")
                    break

            return total_aceptadas_categoria

        except Exception as e:
            self.log_signal.emit(f"⚠️ Error procesando {tipo_documento}: {str(e)}")
            return 0

    def _procesar_facturas_en_vista_actual(self):
        """Procesar facturas en la vista actual sin hacer clic en tipo de documento"""
        try:
            self.log_signal.emit("🔍 Procesando facturas en la vista actual...")
            time.sleep(3)

            facturas_aceptadas = 0

            # Verificar si hay facturas pendientes en la vista actual
            if not self._hay_facturas_pendientes_en_categoria():
                self.log_signal.emit("ℹ️ No hay facturas pendientes en la vista actual")
                return 0

            # Paso 1: Buscar y marcar todas las facturas pendientes
            checkboxes_marcados = self._marcar_todas_las_facturas_en_vista_actual()

            if checkboxes_marcados > 0:
                self.log_signal.emit(f"✅ Marcadas {checkboxes_marcados} facturas en vista actual")

                # Paso 2: Buscar botón de acuso de recibo masivo
                boton_acuso_recibo_masivo = self._buscar_boton_acuso_recibo_masivo()

                if boton_acuso_recibo_masivo:
                    self.log_signal.emit("✅ Botón de acuso de recibo masivo encontrado")

                    # Paso 3: Hacer clic en acuso de recibo masivo
                    guardar_screenshot(self.driver, "11_antes_acuso_recibo_masivo_vista_actual")

                    self.driver_wait.until(EC.element_to_be_clickable(boton_acuso_recibo_masivo))
                    self.driver.execute_script("arguments[0].click();", boton_acuso_recibo_masivo)
                    time.sleep(3)

                    # Paso 4: Manejar el modal de confirmación (seleccionar primera opción y confirmar)
                    if self._manejar_modal_confirmacion_acuso_recibo():
                        facturas_aceptadas = checkboxes_marcados
                        self.log_signal.emit(f"✅ {facturas_aceptadas} facturas aceptadas en vista actual")
                        guardar_screenshot(self.driver, "12_despues_acuso_recibo_masivo_vista_actual")
                    else:
                        self.log_signal.emit("⚠️ No se pudo confirmar el acuso de recibo en vista actual")
                else:
                    self.log_signal.emit("⚠️ No se encontró botón de acuso de recibo masivo en vista actual")
            else:
                self.log_signal.emit("ℹ️ No se encontraron facturas para marcar en vista actual")

            return facturas_aceptadas

        except Exception as e:
            self.log_signal.emit(f"⚠️ Error procesando facturas en vista actual: {str(e)}")
            return 0

    def _marcar_todas_las_facturas_en_vista_actual(self):
        """Marcar todas las facturas en la vista actual del tipo de documento"""
        try:
            # LIMPIEZA PREVIA: Cerrar modales que puedan interceptar el clic
            self._cerrar_modales_inesperados()
            
            self.log_signal.emit("🔲 Buscando checkboxes para seleccionar todas las facturas...")

            # Intento 1: Buscar checkbox "Seleccionar todo"
            for selector in SII_SELECTORS['checkbox_seleccionar_todo']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_displayed() and checkbox.is_enabled():
                            self.log_signal.emit("✅ Checkbox 'Seleccionar todo' encontrado")

                            # Esperar a que el elemento sea clickeable
                            self.driver_wait.until(EC.element_to_be_clickable(checkbox))
                            
                            # Si no está marcado, marcarlo
                            if not checkbox.is_selected():
                                checkbox.click()
                                time.sleep(2)

                            guardar_screenshot(self.driver, "13_checkbox_todo_marcado")
                            return self._contar_checkboxes_marcados_en_vista_actual()
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error con checkbox 'Seleccionar todo': {str(e)}")
                    continue

            # Intento 2: Si no hay checkbox "Seleccionar todo", marcar cada uno individualmente
            self.log_signal.emit("🔍 No se encontró 'Seleccionar todo', marcando individualmente...")
            checkboxes_marcados = 0

            for selector in SII_SELECTORS['checkbox_factura_individual']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_displayed() and checkbox.is_enabled() and not checkbox.is_selected():
                            try:
                                # Esperar a que el elemento sea clickeable
                                self.driver_wait.until(EC.element_to_be_clickable(checkbox))
                                checkbox.click()
                                checkboxes_marcados += 1
                                if checkboxes_marcados % 10 == 0:
                                    self.log_signal.emit(f"📝 Marcadas {checkboxes_marcados} facturas...")
                            except Exception as e:
                                self.log_signal.emit(f"⚠️ Error marcando checkbox individual: {str(e)}")
                                continue
                    if checkboxes_marcados > 0:
                        break
                except:
                    continue

            if checkboxes_marcados > 0:
                self.log_signal.emit(f"✅ Marcadas {checkboxes_marcados} facturas individualmente")
                time.sleep(2)
                guardar_screenshot(self.driver, "14_checkboxes_individuales_marcados")

            return checkboxes_marcados

        except Exception as e:
            self.log_signal.emit(f"⚠️ Error marcando checkboxes: {str(e)}")
            return 0

    def _contar_checkboxes_marcados_en_vista_actual(self):
        """Contar checkboxes marcados en la vista actual"""
        try:
            contador = 0
            for selector in SII_SELECTORS['checkbox_factura_individual']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_selected():
                            contador += 1
                except:
                    continue
            return contador
        except:
            return 0

    def _esperar_carga_sii(self, timeout=10):
        """Esperar a que desaparezcan los indicadores de carga del SII"""
        try:
            time.sleep(1) # Pequeña espera para que el spinner aparezca
            for selector in SII_SELECTORS['loading_indicator']:
                try:
                    # Esperar a que el elemento NO esté presente o sea invisible
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located((By.XPATH, selector))
                    )
                except:
                    continue
        except:
            pass

    def _hay_facturas_pendientes_en_categoria(self):
        """Verifica de forma exhaustiva si hay facturas pendientes, evitando falsos negativos."""
        try:
            self.log_signal.emit("📊 Verificando presencia de facturas...")
            
            # 1. Esperar a que el spinner desaparezca
            self._esperar_carga_sii()
            time.sleep(2)
            
            for intento in range(2): # Dos ciclos de verificación profunda
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # A. BUSQUEDA POR TABLA/FILAS (Máxima precisión)
                for selector in SII_SELECTORS['tabla_facturas']:
                    try:
                        tablas = self.driver.find_elements(By.XPATH, selector)
                        for tabla in tablas:
                            if tabla.is_displayed():
                                # Si hay tabla, buscar filas de datos
                                for fila_selector in SII_SELECTORS['fila_factura']:
                                    filas = tabla.find_elements(By.XPATH, fila_selector)
                                    if len(filas) > 0:
                                        self.log_signal.emit(f"✅ Detectadas {len(filas)} filas de datos en tabla")
                                        return True
                    except: continue

                # B. BUSQUEDA POR CHECKBOXES (Regla de oro)
                for selector in SII_SELECTORS['checkbox_factura_individual']:
                    try:
                        checkboxes = self.driver.find_elements(By.XPATH, selector)
                        if any(cb.is_displayed() for cb in checkboxes):
                            self.log_signal.emit(f"📊 Confirmado: {len(checkboxes)} checkboxes de facturas visibles")
                            return True
                    except: continue

                # C. ANALISIS DE TEXTO NEGATIVO (No se encuentran, etc.)
                no_hay_indicadores = ["no se encuentran", "no hay documentos", "no hay facturas", "0 registros", "sin documentos"]
                confirmado_no_hay = False
                for indicator in no_hay_indicadores:
                    if indicator in page_text:
                        confirmado_no_hay = True
                        break
                
                # REGLA DE SEGURIDAD: Si dice que "no hay", pero es el primer intento, 
                # esperamos un extra por si es un mensaje temporal de carga lenta.
                if confirmado_no_hay:
                    if intento == 0:
                        self.log_signal.emit("⏳ El SII indica 'no hay datos', esperando 5s para re-verificar...")
                        time.sleep(5)
                        # Intentar scroll para forzar refresh visual
                        try:
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        except: pass
                        continue # Reintentar el bucle
                    else:
                        self.log_signal.emit("ℹ️ Confirmado por el SII: No hay facturas pendientes en esta categoría")
                        return False

                # D. PATRONES POSITIVOS (Si nada de lo anterior fue definitivo)
                patterns_to_find = ["pendiente", "por aceptar", "nueva", "recibida"]
                for pattern in patterns_to_find:
                    if pattern in page_text:
                        self.log_signal.emit(f"✅ Detectada palabra clave: '{pattern}'. Posible factura presente.")
                        # Verificación extra: si hay el texto pero no vimos filas/checks, esperamos un poco más
                        time.sleep(2)
                        return True
                
                if intento == 0:
                    self.log_signal.emit("⏳ No se detecta estado definitivo, esperando carga final...")
                    time.sleep(3)
            
            return False
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error en auditoría de detección: {str(e)}")
            return False

    def _buscar_boton_acuso_recibo_masivo(self):
        """Buscar botón de acuso de recibo masivo en la vista actual"""
        # Buscar usando los selectores existentes de aceptación masiva
        for selector in SII_SELECTORS['boton_aceptar_masivo']:
            try:
                botones = self.driver.find_elements(By.XPATH, selector)
                for boton in botones:
                    if boton.is_displayed() and boton.is_enabled():
                        # Verificar que el texto del botón esté relacionado con acuso de recibo
                        boton_text = boton.text.lower()
                        if any(palabra in boton_text for palabra in ['acuso', 'recibo', 'masivo', 'aceptar seleccionados']):
                            return boton
            except:
                continue

        # Buscar variantes específicas de acuso de recibo
        variantes_acuso = [
            "//button[contains(., 'Acuso Recibo Masivo')]",
            "//button[contains(., 'Acuso de Recibo Masivo')]",
            "//button[contains(., 'Acuso Recibo')]",
            "//button[contains(., 'Recibo Masivo')]",
            "//button[contains(., 'Procesar Seleccionados') and contains(., 'Recibo')]",
        ]

        for selector in variantes_acuso:
            try:
                botones = self.driver.find_elements(By.XPATH, selector)
                for boton in botones:
                    if boton.is_displayed() and boton.is_enabled():
                        return boton
            except:
                continue

        return None

    def _manejar_modal_confirmacion_acuso_recibo(self):
        """Manejar el modal de confirmación para acuso de recibo masivo"""
        try:
            self.log_signal.emit("📋 Esperando modal de confirmación de acuso de recibo...")
            time.sleep(3)

            # Esperar explícitamente a que aparezca un modal
            try:
                self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal")))
            except:
                # Si no encuentra clase modal, intentar con otros selectores comunes
                try:
                    self.driver_wait.until(lambda driver: driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dialog')]"))
                except:
                    pass

            # Buscar el modal de confirmación con selectores más amplios
            modal_selectors = [
                "//div[contains(@class, 'modal')]",
                "//div[contains(@class, 'popup') or contains(@class, 'dialog')]",
                "//div[@role='dialog' or @role='alertdialog']",
                "//div[contains(@class, 'modal') and contains(., 'confirm')]",
                "//div[contains(., 'confirm') or contains(., 'Confirm') or contains(., 'recibo') or contains(., 'Recibo')]",
                "//*[contains(@class, 'window') or contains(@class, 'panel')]"
            ]

            for selector in modal_selectors:
                try:
                    modales = self.driver.find_elements(By.XPATH, selector)
                    for modal in modales:
                        if modal.is_displayed():
                            self.log_signal.emit("✅ Modal de confirmación de acuso de recibo encontrado")

                            # Esperar un poco más para que el contenido del modal esté completamente cargado
                            time.sleep(2)

                            # Paso 0: Buscar dropdowns (select)
                            select_elements = modal.find_elements(By.TAG_NAME, "select")
                            for select_elem in select_elements:
                                try:
                                    if select_elem.is_displayed():
                                        self.log_signal.emit("✅ Dropdown de opciones encontrado")
                                        sel = Select(select_elem)
                                        
                                        # Priorizar Opción 2 si se menciona, o Opción 1 como fallback
                                        opcion2_texto = "Recibo de Mercaderías o Servicios Prestados"
                                        opcion1_texto = "Acuse de Recibo de Mercaderías y Servicios Ley 19.983"
                                        
                                        opcion_encontrada = False
                                        
                                        # Intentar Opción 2 primero (Requerimiento actual)
                                        for option in sel.options:
                                            if "Recibo de Mercaderías" in option.text or "Servicios Prestados" in option.text:
                                                sel.select_by_visible_text(option.text)
                                                self.log_signal.emit(f"✅ Seleccionada Opción 2: {option.text}")
                                                opcion_encontrada = True
                                                break
                                        
                                        # Si no, intentar Opción 1
                                        if not opcion_encontrada:
                                            for option in sel.options:
                                                if "19.983" in option.text or "19.883" in option.text:
                                                    sel.select_by_visible_text(option.text)
                                                    self.log_signal.emit(f"✅ Seleccionada Opción 1: {option.text}")
                                                    opcion_encontrada = True
                                                    break
                                        
                                        # Si nada funciona, seleccionar índice 2 (que suele ser la Opción 2)
                                        if not opcion_encontrada and len(sel.options) > 2:
                                            sel.select_by_index(2)
                                            self.log_signal.emit(f"✅ Seleccionada Opción por índice 2: {sel.options[2].text}")
                                            opcion_encontrada = True
                                        elif not opcion_encontrada and len(sel.options) > 1:
                                            sel.select_by_index(1)
                                            self.log_signal.emit(f"✅ Seleccionado primer índice disponible: {sel.options[1].text}")
                                            opcion_encontrada = True
                                        
                                        if opcion_encontrada:
                                            time.sleep(1)
                                            break
                                except Exception as e:
                                    self.log_signal.emit(f"⚠️ Error al manipular dropdown: {str(e)}")
                                    continue

                            # Si no hay dropdown, buscar radio buttons que tengan texto asociado con la opción deseada
                            if not opcion_encontrada:
                                radios = modal.find_elements(By.XPATH, ".//input[@type='radio' and not(@disabled)]")
                                for radio in radios:
                                    try:
                                        # Buscar label asociado
                                        label = ""
                                        try:
                                            # Intentar por ID
                                            radio_id = radio.get_attribute("id")
                                            if radio_id:
                                                label_elem = modal.find_element(By.XPATH, f".//label[@for='{radio_id}']")
                                                label = label_elem.text
                                        except:
                                            # Intentar por parent o sibling
                                            try:
                                                label = self.driver.execute_script("return arguments[0].parentNode.innerText || arguments[0].nextSibling.innerText;", radio)
                                            except: pass
                                        
                                        if "19.983" in label or "19.883" in label:
                                            self.log_signal.emit(f"✅ Seleccionando radio button por texto: {label}")
                                            self.driver_wait.until(EC.element_to_be_clickable(radio))
                                            radio.click()
                                            opcion_encontrada = True
                                            break
                                    except: continue

                            # Si no se encontró la opción específica por texto, seleccionar la primera disponible (Opción 1)
                            if not opcion_encontrada:
                                if radios and len(radios) > 0:
                                    self.log_signal.emit("✅ Seleccionando primera opción del modal (Opción 1)")
                                    self.driver_wait.until(EC.element_to_be_clickable(radios[0]))
                                    # Intentar clic normal
                                    try:
                                        radios[0].click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", radios[0])
                                    
                                    time.sleep(1)
                                    opcion_encontrada = True

                            # Si no hay radio buttons, buscar la primera opción seleccionable en general
                            if not opcion_encontrada:
                                self.log_signal.emit("⚠️ No se encontró la opción específica, seleccionando la primera disponible...")
                                # Buscar cualquier tipo de opción seleccionable con selectores más específicos
                                opciones_seleccionables = []

                                # Buscar radio buttons (más específicos)
                                radios = modal.find_elements(By.XPATH, ".//input[@type='radio' and not(@disabled)]")
                                opciones_seleccionables.extend(radios)

                                # Buscar checkboxes (más específicos)
                                checkboxes = modal.find_elements(By.XPATH, ".//input[@type='checkbox' and not(@disabled)]")
                                opciones_seleccionables.extend(checkboxes)

                                # Buscar labels asociados a inputs seleccionables
                                label_radios = modal.find_elements(By.XPATH, ".//label[input[@type='radio']]")
                                opciones_seleccionables.extend(label_radios)

                                label_checks = modal.find_elements(By.XPATH, ".//label[input[@type='checkbox']]")
                                opciones_seleccionables.extend(label_checks)

                                # Buscar elementos que contengan texto común en opciones de confirmación del SII
                                elementos_texto = modal.find_elements(By.XPATH,
                                    ".//span[contains(text(), 'ley') or contains(text(), 'Ley') or contains(text(), '19') or contains(text(), 'opció') or contains(text(), 'Opció') or contains(text(), 'acepto') or contains(text(), 'Acepto') or contains(text(), 'confirmo') or contains(text(), 'Confirmo') or contains(text(), 'recibo') or contains(text(), 'Recibo')]")
                                opciones_seleccionables.extend(elementos_texto)

                                # Buscar divs o spans que parezcan opciones de selección
                                posibles_opciones = modal.find_elements(By.XPATH,
                                    ".//div[contains(@class, 'option') or contains(@class, 'radio') or contains(@class, 'check') or contains(@class, 'item') or contains(@class, 'choice')] | .//span[contains(@class, 'option') or contains(@class, 'radio') or contains(@class, 'check') or contains(@class, 'item') or contains(@class, 'choice')]")
                                opciones_seleccionables.extend(posibles_opciones)

                                # Seleccionar la primera opción disponible
                                if len(opciones_seleccionables) >= 1:
                                    # Si solo hay una opción, seleccionarla
                                    primera_opcion = opciones_seleccionables[0]
                                    try:
                                        self.driver_wait.until(EC.element_to_be_clickable(primera_opcion))
                                        primera_opcion.click()
                                        time.sleep(1)
                                        self.log_signal.emit(f"✅ Primera opción disponible seleccionada: {primera_opcion.text[:50] if hasattr(primera_opcion, 'text') and primera_opcion.text else 'Elemento sin texto'}")
                                    except:
                                        # Si falla, intentar con JavaScript
                                        try:
                                            self.driver.execute_script("arguments[0].click();", primera_opcion)
                                            time.sleep(1)
                                            self.log_signal.emit(f"✅ Primera opción disponible seleccionada con JavaScript: {getattr(primera_opcion, 'text', 'Elemento sin texto')[:50] if hasattr(primera_opcion, 'text') and primera_opcion.text else 'Elemento sin texto'}")
                                        except:
                                            self.log_signal.emit("⚠️ No se pudo seleccionar la primera opción disponible")
                                else:
                                    self.log_signal.emit("⚠️ No se encontraron opciones disponibles para seleccionar")

                            # Paso 2: Buscar botón de confirmación con selectores más amplios
                            botones_confirmacion = modal.find_elements(By.XPATH,
                                ".//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar') or contains(., 'Cerrar') or contains(., 'Aceptar Selección') or contains(., 'Acusar Recibo') or contains(., 'Acuso Recibo')] | .//input[@type='button' and (@value='Confirmar' or @value='Aceptar' or @value='Sí' or @value='Continuar')] | .//a[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar')]")

                            for boton in botones_confirmacion:
                                if boton.is_displayed() and boton.is_enabled():
                                    self.log_signal.emit("✅ Haciendo clic en botón de confirmación")
                                    try:
                                        self.driver_wait.until(EC.element_to_be_clickable(boton))
                                        boton.click()
                                    except:
                                        # Si falla, intentar con JavaScript
                                        self.driver.execute_script("arguments[0].click();", boton)

                                    time.sleep(3)
                                    
                                    # --- MEJORADO: Manejar posible segundo modal de confirmación ("Está seguro?") ---
                                    try:
                                        self.log_signal.emit("📋 Verificando si aparece un segundo modal de confirmación...")
                                        
                                        # Esperar a que el primer modal desaparezca o aparezca uno nuevo
                                        for _ in range(3): # Reintentar búsqueda de segundo modal
                                            time.sleep(2)
                                            modales_segundos = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') and contains(@style, 'block')] | //div[contains(@class, 'modal-dialog')] | //div[@role='dialog']")
                                            
                                            modal_encontrado = False
                                            for smodal in modales_segundos:
                                                if smodal.is_displayed():
                                                    # Verificar si es el modal de confirmación ("está seguro", "desea continuar", etc)
                                                    texto_modal = smodal.text.lower()
                                                    if any(word in texto_modal for word in ['seguro', 'desea', 'continuar', 'ley', '19.983', '19.883']):
                                                        self.log_signal.emit(f"✅ Segundo modal detectado: '{smodal.text[:30]}...'")
                                                        
                                                        # Buscar botón de confirmación en este modal
                                                        botones_finales = smodal.find_elements(By.XPATH, ".//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar')]")
                                                        for btn_final in botones_finales:
                                                            if btn_final.is_displayed():
                                                                self.log_signal.emit("✅ Haciendo clic en botón final de confirmación")
                                                                self.driver_wait.until(EC.element_to_be_clickable(btn_final))
                                                                self.driver.execute_script("arguments[0].click();", btn_final)
                                                                time.sleep(5)

                                                                # --- NUEVO: Manejar tercer modal de resultado final ("Operación finalizada") ---
                                                                try:
                                                                    self.log_signal.emit("📋 Verificando si aparece un modal de resultado final...")
                                                                    time.sleep(3)
                                                                    modales_finales = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') and contains(@style, 'block')] | //div[contains(@class, 'modal-dialog')] | //div[@role='dialog']")
                                                                    for modal_final in modales_finales:
                                                                        if modal_final.is_displayed():
                                                                            self.log_signal.emit("✅ Modal de éxito detectado, cerrando...")
                                                                            botones_cerrar = modal_final.find_elements(By.XPATH, ".//button[contains(., 'Cerrar') or contains(., 'Aceptar') or contains(., 'Finalizar')]")
                                                                            for btn_cerrar in botones_cerrar:
                                                                                if btn_cerrar.is_displayed():
                                                                                    self.driver_wait.until(EC.element_to_be_clickable(btn_cerrar))
                                                                                    self.driver.execute_script("arguments[0].click();", btn_cerrar)
                                                                                    break
                                                                except: pass

                                                                self.log_signal.emit("🎉 FACTURAS ACEPTADAS EXITOSAMENTE")
                                                                time.sleep(2)
                                                                return True
                                                    modal_encontrado = True
                                            
                                            if not modal_encontrado:
                                                # Si no hay modal visible, quizás ya terminó o el anterior era el único
                                                break
                                    except Exception as e:
                                        self.log_signal.emit(f"ℹ️ No se detectó segundo modal o error al manejararlo: {str(e)}")

                                    return True

                            # Si no hay botones en el modal, buscar fuera del modal (caso común en SPAs)
                            botones_fuera_modal = self.driver.find_elements(By.XPATH,
                                "//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar') or contains(., 'Cerrar') or contains(., 'Aceptar Selección') or contains(., 'Acusar Recibo') or contains(., 'Acuso Recibo')] | //input[@type='button' and (@value='Confirmar' or @value='Aceptar' or @value='Sí' or @value='Continuar')]")

                            for boton in botones_fuera_modal:
                                if boton.is_displayed() and boton.is_enabled():
                                    self.log_signal.emit("✅ Haciendo clic en botón de confirmación (fuera del modal)")
                                    try:
                                        self.driver_wait.until(EC.element_to_be_clickable(boton))
                                        boton.click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", boton)

                                    time.sleep(5)
                                    return True

                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error buscando modal con selector {selector}: {str(e)}")
                    continue

            # Si no se encuentra modal específico, buscar botones directamente
            for selector in SII_SELECTORS['confirmacion_aceptar_masivo']:
                try:
                    botones = self.driver.find_elements(By.XPATH, selector)
                    for boton in botones:
                        if boton.is_displayed() and boton.is_enabled():
                            self.log_signal.emit("✅ Botón de confirmación encontrado (sin modal)")
                            self.driver_wait.until(EC.element_to_be_clickable(boton))
                            boton.click()
                            time.sleep(5)
                            return True
                except:
                    continue

            self.log_signal.emit("ℹ️ No se encontró modal de confirmación, asumiendo éxito...")
            return True

        except Exception as e:
            self.log_signal.emit(f"⚠️ Error manejando confirmación de acuso de recibo: {str(e)}")
            return False

    def _buscar_boton_aceptar_masivo_en_vista_actual(self):
        """Buscar botón de aceptación masiva en la vista actual"""
        for selector in SII_SELECTORS['boton_aceptar_masivo']:
            try:
                botones = self.driver.find_elements(By.XPATH, selector)
                for boton in botones:
                    if boton.is_displayed() and boton.is_enabled():
                        return boton
            except:
                continue

        # Buscar variantes del botón
        variantes_botones = [
            "//button[contains(., 'Acuso Recibo')]",
            "//button[contains(., 'Aceptar Documentos')]",
            "//button[contains(., 'Procesar') and contains(., 'seleccionados')]",
            "//button[contains(., 'Acusar Recibido')]",
            "//button[contains(., 'Recibido')]",
        ]

        for selector in variantes_botones:
            try:
                botones = self.driver.find_elements(By.XPATH, selector)
                for boton in botones:
                    if boton.is_displayed() and boton.is_enabled():
                        return boton
            except:
                continue

        return None

    def _manejar_modal_confirmacion_aceptacion(self):
        """Manejar el modal de confirmación para aceptación masiva"""
        try:
            self.log_signal.emit("📋 Esperando modal de confirmación...")
            time.sleep(3)

            # Buscar el modal
            for selector in [
                "//div[contains(@class, 'modal')]",
                "//div[@role='dialog']",
                "//div[contains(@class, 'popup')]"
            ]:
                try:
                    modales = self.driver.find_elements(By.XPATH, selector)
                    for modal in modales:
                        if modal.is_displayed():
                            self.log_signal.emit("✅ Modal encontrado")
                            
                            # Intentar manejar dropdowns primero
                            opcion_encontrada = False
                            selects = modal.find_elements(By.TAG_NAME, "select")
                            for s in selects:
                                try:
                                    if s.is_displayed():
                                        sel = Select(s)
                                        if len(sel.options) > 1:
                                            # Priorizar Ley 19.983
                                            for opt in sel.options:
                                                if "19.983" in opt.text:
                                                    sel.select_by_visible_text(opt.text)
                                                    opcion_encontrada = True
                                                    break
                                            if not opcion_encontrada:
                                                sel.select_by_index(1)
                                                opcion_encontrada = True
                                        if opcion_encontrada: break
                                except: continue

                            # Si no hay select, buscar radios
                            if not opcion_encontrada:
                                radios = modal.find_elements(By.XPATH, ".//input[@type='radio' and not(@disabled)]")
                                if radios and len(radios) > 0:
                                    self.driver_wait.until(EC.element_to_be_clickable(radios[0]))
                                    radios[0].click()
                                    opcion_encontrada = True

                            # Buscar botón de confirmación
                            botones = modal.find_elements(By.XPATH, ".//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí')]")
                            for boton in botones:
                                if boton.is_displayed() and boton.is_enabled():
                                    self.log_signal.emit("✅ Confirmando modal")
                                    self.driver_wait.until(EC.element_to_be_clickable(boton))
                                    boton.click()
                                    time.sleep(5)
                                    return True
                except: continue
            return True # Asumir éxito si el modal desapareció o no se encontró
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error en modal: {str(e)}")
            return False

    def stop(self):
        """Detener el proceso"""
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


class SIIAutomator:
    """Clase principal para la automatización SII"""

    def __init__(self):
        self.worker = None

    def iniciar_proceso(self, rut_empresa, rut_usuario, clave, headless=False):
        """Iniciar el proceso de automatización individual (monitorea un solo worker)"""
        if self.worker and self.worker.isRunning():
            # Dar un pequeño margen de 1 segundo por si está justo terminando
            if self.worker.wait(1000):
                self.worker = None # Si terminó en la espera, limpiamos
            else:
                return None

        self.worker = SIIAutomatorWorker(rut_empresa, rut_usuario, clave, headless)
        return self.worker

    def crear_worker_independiente(self, rut_empresa, rut_usuario, clave, headless=False):
        """Crea un worker independiente para procesamiento paralelo"""
        return SIIAutomatorWorker(rut_empresa, rut_usuario, clave, headless)

    def detener_proceso(self):
        """Detener el proceso en ejecución"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.quit()
            if not self.worker.wait(3000):
                self.worker.terminate()
                self.worker.wait()
            return True
        return False