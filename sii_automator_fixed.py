"""
Módulo para automatizar la aceptación de facturas en el SII - VERSION MEJORADA PARA PESTAÑAS DINÁMICAS
"""
import time
import json
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
from datetime import datetime, timedelta


# ================= CONFIGURACIÓN ACTUALIZADA DEL SII =================
SII_URLS = {
    'portal': 'https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'login': 'https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'servicios_online': 'https://www.sii.cl/servicios_online/1042-.html',
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
    'impuestos_mensuales': [
        (By.XPATH, "//a[contains(., 'Impuestos Mensuales')]"),
        (By.XPATH, "//a[contains(@href, '1042-')]"),
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
    # NUEVOS SELECTORES ESPECÍFICOS PARA PESTAÑAS DINÁMICAS
    'tabs_principales': [
        "//button[contains(@class, 'tab') and contains(., 'Pendientes')]",
        "//button[contains(@class, 'nav-link') and contains(., 'Pendientes')]",
        "//li[contains(@class, 'tab') and contains(., 'Pendientes')]",
        "//a[contains(@class, 'tab') and contains(., 'Pendientes')]",
        "//button[contains(., 'Pendientes') and contains(@class, 'btn')]",
        "//div[contains(@class, 'tab') and contains(., 'Pendientes')]",
        "//span[contains(., 'Pendientes')]",
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
        "//a[contains(., 'Factura Electrónica (33)')]",
        "//a[contains(., 'Factura Electrónica') and contains(., '33')]",
        "//td[contains(., 'Factura Electrónica')]/following-sibling::td//a",
        "//tr[contains(., 'Factura Electrónica')]//a[contains(@href, '#')]",
        "//a[contains(text(), '33') and contains(@class, 'documento')]",
        "//a[contains(text(), 'Factura') and contains(text(), 'Electrónica')]",
        "//a[contains(., '33') and contains(., 'Factura')]",
        "//span[contains(., '33') and contains(., 'Factura')]",
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
    ],
}

TIMEOUTS = {
    'page_load': 15,
    'element_wait': 20,
    'login_wait': 8,
    'action_delay': 3,
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

def guardar_screenshot(driver, nombre):
    """Guardar screenshot con timestamp"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"debug_{nombre}_{timestamp}.png"
        driver.save_screenshot(nombre_archivo)
        return nombre_archivo
    except:
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
        self.wait = None

    def run(self):
        """Ejecuta el proceso de automatización - FLUJO CORREGIDO PARA PESTAÑAS DINÁMICAS"""
        try:
            self.log_signal.emit("🚀 Iniciando proceso SII...")

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
            self.wait = WebDriverWait(self.driver, TIMEOUTS['element_wait'])

            # ================= PASO 1: LOGIN =================
            self.log_signal.emit("🌐 Navegando al login del SII...")
            self.driver.get(SII_URLS['login'])
            time.sleep(5)

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
            time.sleep(8)

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

            # ================= PASO 2: NAVEGAR A SERVICIOS ONLINE =================
            self.log_signal.emit("🔗 Navegando a Servicios Online...")

            # Ir directamente a la URL de servicios online
            self.driver.get(SII_URLS['servicios_online'])
            time.sleep(5)
            guardar_screenshot(self.driver, "04_servicios_online")

            # ================= PASO 3: IMPUESTOS MENSUALES =================
            self.log_signal.emit("📋 Buscando Impuestos Mensuales...")

            # Buscar enlace de Impuestos Mensuales
            impuestos_link = None
            for selector_type, selector_value in SII_SELECTORS['impuestos_mensuales']:
                try:
                    if isinstance(selector_value, str):
                        elementos = self.driver.find_elements(By.XPATH, selector_value)
                    else:
                        elementos = self.driver.find_elements(selector_type, selector_value)

                    for elemento in elementos:
                        if elemento.is_displayed():
                            impuestos_link = elemento
                            break
                    if impuestos_link:
                        break
                except:
                    continue

            if impuestos_link:
                self.log_signal.emit("✅ Enlace de Impuestos Mensuales encontrado")
                impuestos_link.click()
                time.sleep(5)
            else:
                # Si no se encuentra, ir directamente a la URL
                self.log_signal.emit("⚠️ No se encontró enlace, navegando directamente...")
                self.driver.get(SII_URLS['servicios_online'])
                time.sleep(5)

            guardar_screenshot(self.driver, "05_impuestos_mensuales")

            # ================= PASO 4: REGISTRO DE COMPRAS Y VENTAS =================
            self.log_signal.emit("📄 Buscando Registro de Compras y Ventas...")

            registro_link = None
            for selector_type, selector_value in SII_SELECTORS['registro_compras_ventas']:
                try:
                    if isinstance(selector_value, str):
                        elementos = self.driver.find_elements(By.XPATH, selector_value)
                    else:
                        elementos = self.driver.find_elements(selector_type, selector_value)

                    for elemento in elementos:
                        if elemento.is_displayed():
                            registro_link = elemento
                            break
                    if registro_link:
                        break
                except:
                    continue

            if registro_link:
                self.log_signal.emit("✅ Enlace de Registro encontrado")
                registro_link.click()
                time.sleep(5)
            else:
                # Ir directamente
                self.driver.get(SII_URLS['registro_compras'])
                time.sleep(5)

            guardar_screenshot(self.driver, "06_registro_compras")

            # ================= PASO 5: INGRESAR AL REGISTRO =================
            self.log_signal.emit("🚪 Ingresando al Registro...")

            ingresar_link = None
            for selector_type, selector_value in SII_SELECTORS['ingresar_registro']:
                try:
                    if isinstance(selector_value, str):
                        elementos = self.driver.find_elements(By.XPATH, selector_value)
                    else:
                        elementos = self.driver.find_elements(selector_type, selector_value)

                    for elemento in elementos:
                        if elemento.is_displayed():
                            ingresar_link = elemento
                            break
                    if ingresar_link:
                        break
                except:
                    continue

            if ingresar_link:
                self.log_signal.emit("✅ Enlace 'Ingresar' encontrado")
                ingresar_link.click()
                time.sleep(8)
            else:
                # Intentar navegar directamente
                self.driver.get(SII_URLS['facturas'])
                time.sleep(8)

            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            if "consdcvinternetui" not in current_url:
                self.log_signal.emit(f"⚠️ URL actual: {current_url}")
                self.log_signal.emit("Intentando navegación directa...")
                self.driver.get(SII_URLS['facturas'])
                time.sleep(8)

            self.log_signal.emit("✅ En página de registro de facturas")
            guardar_screenshot(self.driver, "07_registro_facturas")

            # ================= PASO 6: ESPERAR A QUE SE CARGUE EL CONTENIDO =================
            self.log_signal.emit("⏳ Esperando carga completa de pestañas...")
            time.sleep(5)
            guardar_screenshot(self.driver, "07b_despues_carga_inicial")

            # ================= PASO 7: BUSCAR Y HACER CLIC EN PESTAÑA PENDIENTES =================
            self.log_signal.emit("🔍 Buscando pestaña 'Pendientes'...")
            
            # Intentar encontrar y hacer clic en la pestaña Pendientes
            pendientes_clicked = False
            for selector in SII_SELECTORS['tabs_principales']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed():
                                self.log_signal.emit("✅ Pestaña 'Pendientes' encontrada")
                                
                                # Tomar screenshot antes de hacer clic
                                guardar_screenshot(self.driver, "08_antes_click_pendientes")
                                
                                # Esperar a que el elemento sea clickeable
                                self.wait.until(EC.element_to_be_clickable(elemento))
                                
                                # Hacer clic
                                self.driver.execute_script("arguments[0].click();", elemento)
                                time.sleep(5)
                                
                                # Verificar si ahora está activa
                                if self._verificar_tab_pendientes_activa():
                                    self.log_signal.emit("✅ Confirmado: pestaña 'Pendientes' está activa")
                                    pendientes_clicked = True
                                    guardar_screenshot(self.driver, "09_pendientes_activa")
                                    break
                                else:
                                    self.log_signal.emit("⚠️ Pestaña no se activó, intentando otro selector...")
                                    time.sleep(2)
                                    
                        except Exception as e:
                            self.log_signal.emit(f"⚠️ Error al hacer clic en pendientes: {str(e)}")
                            continue
                    if pendientes_clicked:
                        break
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error buscando pestaña pendientes: {str(e)}")
                    continue

            if not pendientes_clicked:
                # Si no encontramos con los selectores normales, intentar encontrar una pestaña ya activa
                self.log_signal.emit("🔍 Buscando si ya estamos en la pestaña de pendientes...")
                
                if self._verificar_tab_pendientes_activa():
                    self.log_signal.emit("✅ Ya estamos en la pestaña de pendientes")
                    pendientes_clicked = True
                else:
                    # Último recurso: buscar cualquier elemento que indique que hay facturas pendientes
                    if self._hay_facturas_pendientes_visualmente():
                        self.log_signal.emit("✅ Detectadas facturas pendientes visualmente")
                        pendientes_clicked = True
                    else:
                        self.log_signal.emit("❌ No se pudo encontrar ni activar la pestaña de pendientes")
                        raise Exception("No se encontró la pestaña de facturas pendientes")

            # ================= PASO 8: BUSCAR Y HACER CLIC EN ENLACES DE TIPO DE DOCUMENTO =================
            self.log_signal.emit("📄 Buscando enlaces de tipo de documento (Factura Electrónica (33))...")
            time.sleep(3)

            # Buscar todos los enlaces de tipo de documento
            enlaces_tipo_documento = []
            for selector in SII_SELECTORS['enlace_tipo_documento']:
                try:
                    enlaces = self.driver.find_elements(By.XPATH, selector)
                    for enlace in enlaces:
                        if enlace.is_displayed() and ('factura' in enlace.text.lower() or '33' in enlace.text.lower()):
                            enlaces_tipo_documento.append(enlace)
                except:
                    continue

            if not enlaces_tipo_documento:
                # Si no encontramos enlaces específicos, buscar cualquier enlace que pueda contener tipos de documentos
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        link_text = link.text.lower()
                        if 'factura' in link_text or 'electr' in link_text or '33' in link_text:
                            if link.is_displayed():
                                enlaces_tipo_documento.append(link)
                except:
                    pass

            self.log_signal.emit(f"✅ Encontrados {len(enlaces_tipo_documento)} enlaces de tipo de documento")

            if not enlaces_tipo_documento:
                self.log_signal.emit("⚠️ No se encontraron enlaces específicos de tipo de documento, pero continuando...")
                # Continuar de todas formas, ya que puede haber facturas visibles sin hacer clic en enlaces específicos

            total_facturas_aceptadas = 0

            # Procesar cada enlace encontrado
            for i, enlace in enumerate(enlaces_tipo_documento):
                if not self.is_running:
                    break

                try:
                    tipo_documento = enlace.text.strip()
                    self.log_signal.emit(f"📋 Procesando: {tipo_documento} ({i+1}/{len(enlaces_tipo_documento)})")

                    # Hacer clic en el enlace del tipo de documento
                    self.wait.until(EC.element_to_be_clickable(enlace))
                    self.driver.execute_script("arguments[0].click();", enlace)
                    time.sleep(5)

                    guardar_screenshot(self.driver, f"10_entrando_a_{tipo_documento.replace(' ', '_').replace('(', '').replace(')', '')}")

                    # Ahora estamos dentro de la vista específica del tipo de documento
                    # Aquí es donde debemos seleccionar y aceptar las facturas
                    facturas_aceptadas_en_tipo = self._procesar_facturas_en_tipo_documento(tipo_documento)

                    total_facturas_aceptadas += facturas_aceptadas_en_tipo

                    # Volver atrás para procesar el siguiente tipo de documento
                    if i < len(enlaces_tipo_documento) - 1:
                        self.log_signal.emit("↩️ Volviendo atrás para procesar siguiente tipo de documento...")
                        self.driver.back()
                        time.sleep(5)

                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error procesando enlace {i+1}: {str(e)}")
                    continue

            # Si no hubo enlaces de tipo de documento, procesar directamente en la vista actual
            if not enlaces_tipo_documento:
                self.log_signal.emit("🔍 Procesando facturas en la vista actual...")
                facturas_aceptadas_directo = self._procesar_facturas_en_vista_actual()
                total_facturas_aceptadas += facturas_aceptadas_directo

            # Resultado final
            if total_facturas_aceptadas > 0:
                mensaje = f"🎉 Proceso completado. Se aceptaron {total_facturas_aceptadas} factura(s) en total"
                self.log_signal.emit(mensaje)
                self.finished_signal.emit(True, f"{total_facturas_aceptadas} facturas aceptadas")
            else:
                mensaje = "ℹ️ No se encontraron facturas pendientes para aceptar"
                self.log_signal.emit(mensaje)
                self.finished_signal.emit(True, "No hay facturas pendientes")

        except Exception as e:
            error_msg = f"❌ Error en el proceso: {str(e)}"
            self.log_signal.emit(error_msg)
            self.finished_signal.emit(False, error_msg)

        finally:
            if self.driver:
                self.log_signal.emit("🔒 Cerrando navegador...")
                try:
                    self.driver.quit()
                except:
                    pass

    def _verificar_tab_pendientes_activa(self):
        """Verifica si la pestaña de pendientes está activa"""
        try:
            # Buscar pestañas que estén activas/destacadas
            for selector in SII_SELECTORS['tab_pendientes_activo']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            return True
                except:
                    continue
            
            # También buscar contenido que indique que estamos en pendientes
            for selector in SII_SELECTORS['contenido_pendientes']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            return True
                except:
                    continue
                    
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
                                            self.wait.until(EC.element_to_be_clickable(boton))
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

    def _procesar_facturas_en_tipo_documento(self, tipo_documento):
        """Procesar facturas dentro de un tipo de documento específico"""
        try:
            self.log_signal.emit(f"🔍 Procesando facturas en {tipo_documento}...")
            time.sleep(3)

            facturas_aceptadas = 0

            # Primero verificar si hay facturas pendientes en esta categoría
            if not self._hay_facturas_pendientes_en_categoria():
                self.log_signal.emit(f"ℹ️ No hay facturas pendientes en {tipo_documento}")
                return 0

            # Paso 1: Buscar y marcar todas las facturas pendientes
            checkboxes_marcados = self._marcar_todas_las_facturas_en_vista_actual()

            if checkboxes_marcados > 0:
                self.log_signal.emit(f"✅ Marcadas {checkboxes_marcados} facturas en {tipo_documento}")

                # Paso 2: Buscar botón de acuso de recibo masivo
                boton_acuso_recibo_masivo = self._buscar_boton_acuso_recibo_masivo()

                if boton_acuso_recibo_masivo:
                    self.log_signal.emit(f"✅ Botón de acuso de recibo masivo encontrado en {tipo_documento}")

                    # Paso 3: Hacer clic en acuso de recibo masivo
                    guardar_screenshot(self.driver, f"11_antes_acuso_recibo_masivo_{tipo_documento.replace(' ', '_').replace('(', '').replace(')', '')}")

                    self.wait.until(EC.element_to_be_clickable(boton_acuso_recibo_masivo))
                    self.driver.execute_script("arguments[0].click();", boton_acuso_recibo_masivo)
                    time.sleep(3)

                    # Paso 4: Manejar el modal de confirmación (seleccionar primera opción y confirmar)
                    if self._manejar_modal_confirmacion_acuso_recibo():
                        facturas_aceptadas = checkboxes_marcados
                        self.log_signal.emit(f"✅ {facturas_aceptadas} facturas aceptadas en {tipo_documento}")
                        guardar_screenshot(self.driver, f"12_despues_acuso_recibo_masivo_{tipo_documento.replace(' ', '_').replace('(', '').replace(')', '')}")
                    else:
                        self.log_signal.emit(f"⚠️ No se pudo confirmar el acuso de recibo en {tipo_documento}")
                else:
                    self.log_signal.emit(f"⚠️ No se encontró botón de acuso de recibo masivo en {tipo_documento}")
            else:
                self.log_signal.emit(f"ℹ️ No se encontraron facturas para marcar en {tipo_documento}")

            return facturas_aceptadas

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

                    self.wait.until(EC.element_to_be_clickable(boton_acuso_recibo_masivo))
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
            self.log_signal.emit("🔲 Buscando checkboxes para seleccionar todas las facturas...")

            # Intento 1: Buscar checkbox "Seleccionar todo"
            for selector in SII_SELECTORS['checkbox_seleccionar_todo']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_displayed() and checkbox.is_enabled():
                            self.log_signal.emit("✅ Checkbox 'Seleccionar todo' encontrado")

                            # Esperar a que el elemento sea clickeable
                            self.wait.until(EC.element_to_be_clickable(checkbox))
                            
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
                                self.wait.until(EC.element_to_be_clickable(checkbox))
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

    def _hay_facturas_pendientes_en_categoria(self):
        """Verifica si hay facturas pendientes en la categoría actual"""
        try:
            # Buscar tabla de facturas
            for selector in SII_SELECTORS['tabla_facturas']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            # Buscar filas de facturas
                            for fila_selector in SII_SELECTORS['fila_factura']:
                                try:
                                    filas = elemento.find_elements(By.XPATH, fila_selector)
                                    if len(filas) > 0:
                                        self.log_signal.emit(f"📊 Encontradas {len(filas)} filas de facturas pendientes")
                                        return True
                                except:
                                    continue
                except:
                    continue

            # Si no encontramos nada, intentar contar checkboxes
            for selector in SII_SELECTORS['checkbox_factura_individual']:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    if len(checkboxes) > 0:
                        self.log_signal.emit(f"📊 Encontrados {len(checkboxes)} checkboxes de facturas pendientes")
                        return True
                except:
                    continue

            return False
        except:
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
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal")))
            except:
                # Si no encuentra clase modal, intentar con otros selectores comunes
                try:
                    self.wait.until(lambda driver: driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dialog')]"))
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

                            # Paso 1: Buscar y seleccionar específicamente la opción "acuso recibo de mercaderias y servicios ley 19.983"
                            opcion_encontrada = False

                            # Buscar radio buttons que tengan texto asociado con la opción deseada
                            radios = modal.find_elements(By.XPATH, ".//input[@type='radio' and not(@disabled)]")
                            for radio in radios:
                                try:
                                    # Buscar el label asociado al radio button
                                    label_for = radio.get_attribute("id")
                                    if label_for:
                                        # Buscar label por atributo 'for'
                                        associated_labels = modal.find_elements(By.XPATH, f".//label[@for='{label_for}']")
                                        for label in associated_labels:
                                            label_text = label.text.lower()
                                            if 'acuso recibo de mercaderias y servicios ley 19.983' in label_text or 'ley 19.983' in label_text or 'mercaderias' in label_text or 'servicios' in label_text:
                                                self.log_signal.emit("✅ Opción específica encontrada, seleccionando...")
                                                self.wait.until(EC.element_to_be_clickable(radio))
                                                radio.click()
                                                time.sleep(1)
                                                self.log_signal.emit(f"✅ Opción seleccionada: {label.text[:100]}")
                                                opcion_encontrada = True
                                                break

                                    if opcion_encontrada:
                                        break

                                    # Si no tiene ID o no encontramos por 'for', buscar labels cercanos
                                    parent_element = radio.find_element(By.XPATH, "./..")
                                    parent_text = parent_element.text.lower()
                                    if 'acuso recibo de mercaderias y servicios ley 19.983' in parent_text or 'ley 19.983' in parent_text or 'mercaderias' in parent_text or 'servicios' in parent_text:
                                        self.log_signal.emit("✅ Opción específica encontrada en padre, seleccionando...")
                                        self.wait.until(EC.element_to_be_clickable(radio))
                                        radio.click()
                                        time.sleep(1)
                                        self.log_signal.emit(f"✅ Opción seleccionada en padre: {parent_element.text[:100]}")
                                        opcion_encontrada = True
                                        break

                                except Exception as e:
                                    continue

                                # Si aún no encontramos por el radio button, buscar por texto en elementos cercanos
                                if not opcion_encontrada:
                                    try:
                                        # Buscar spans, divs o labels que contengan el texto deseado
                                        elementos_texto = modal.find_elements(By.XPATH,
                                            ".//span[contains(., 'acuso recibo de mercaderias y servicios ley 19.983') or contains(., 'ley 19.983') or contains(., 'mercaderías') or contains(., 'servicios') or contains(., 'acuso') and contains(., 'recibo')]")
                                        for elemento_texto in elementos_texto:
                                            # Buscar radio button asociado al texto
                                            parent = elemento_texto.find_element(By.XPATH, ".//preceding::input[@type='radio'][1] | .//following::input[@type='radio'][1] | ./preceding-sibling::input[@type='radio'][1] | ./following-sibling::input[@type='radio'][1] | ./../input[@type='radio'][1] | ./../preceding-sibling::input[@type='radio'][1] | ./../following-sibling::input[@type='radio'][1]")
                                            if parent:
                                                self.wait.until(EC.element_to_be_clickable(parent))
                                                parent.click()
                                                time.sleep(1)
                                                self.log_signal.emit(f"✅ Opción seleccionada por texto: {elemento_texto.text[:100]}")
                                                opcion_encontrada = True
                                                break
                                    except:
                                        pass

                                if opcion_encontrada:
                                    break

                            # Si no encontramos la opción específica, seleccionar la primera disponible
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
                                        self.wait.until(EC.element_to_be_clickable(primera_opcion))
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
                                        self.wait.until(EC.element_to_be_clickable(boton))
                                        boton.click()
                                    except:
                                        # Si falla, intentar con JavaScript
                                        self.driver.execute_script("arguments[0].click();", boton)

                                    time.sleep(5)
                                    return True

                            # Si no hay botones en el modal, buscar fuera del modal (caso común en SPAs)
                            botones_fuera_modal = self.driver.find_elements(By.XPATH,
                                "//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar') or contains(., 'Cerrar') or contains(., 'Aceptar Selección') or contains(., 'Acusar Recibo') or contains(., 'Acuso Recibo')] | //input[@type='button' and (@value='Confirmar' or @value='Aceptar' or @value='Sí' or @value='Continuar')]")

                            for boton in botones_fuera_modal:
                                if boton.is_displayed() and boton.is_enabled():
                                    self.log_signal.emit("✅ Haciendo clic en botón de confirmación (fuera del modal)")
                                    try:
                                        self.wait.until(EC.element_to_be_clickable(boton))
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
                            self.wait.until(EC.element_to_be_clickable(boton))
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

            # Buscar el modal de confirmación
            modal_selectors = [
                "//div[contains(@class, 'modal') and contains(., 'confirmación')]",
                "//div[contains(@class, 'modal-dialog')]",
                "//div[@role='dialog']",
                "//div[contains(@class, 'modal-content')]",
                "//div[contains(@class, 'popup')]",
                "//div[contains(@class, 'alert')]",
            ]

            for selector in modal_selectors:
                try:
                    modales = self.driver.find_elements(By.XPATH, selector)
                    for modal in modales:
                        if modal.is_displayed():
                            self.log_signal.emit("✅ Modal de confirmación encontrado")

                            # Paso 1: Seleccionar la primera opción (si hay opciones)
                            opciones_radio = modal.find_elements(By.XPATH, ".//input[@type='radio']")
                            if opciones_radio and len(opciones_radio) > 0:
                                self.log_signal.emit("✅ Seleccionando primera opción del modal")
                                self.wait.until(EC.element_to_be_clickable(opciones_radio[0]))
                                opciones_radio[0].click()
                                time.sleep(1)

                            # Paso 2: Buscar botón de confirmación
                            botones_confirmacion = modal.find_elements(By.XPATH, ".//button[contains(., 'Confirmar') or contains(., 'Aceptar') or contains(., 'Sí') or contains(., 'Continuar')]")
                            for boton in botones_confirmacion:
                                if boton.is_displayed() and boton.is_enabled():
                                    self.log_signal.emit("✅ Haciendo clic en botón de confirmación")
                                    self.wait.until(EC.element_to_be_clickable(boton))
                                    boton.click()
                                    time.sleep(5)
                                    return True
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error buscando modal: {str(e)}")
                    continue

            # Si no se encuentra modal específico, buscar botones directamente
            for selector in SII_SELECTORS['confirmacion_aceptar_masivo']:
                try:
                    botones = self.driver.find_elements(By.XPATH, selector)
                    for boton in botones:
                        if boton.is_displayed() and boton.is_enabled():
                            self.log_signal.emit("✅ Botón de confirmación encontrado (sin modal)")
                            self.wait.until(EC.element_to_be_clickable(boton))
                            boton.click()
                            time.sleep(5)
                            return True
                except:
                    continue

            self.log_signal.emit("ℹ️ No se encontró modal de confirmación, asumiendo éxito...")
            return True

        except Exception as e:
            self.log_signal.emit(f"⚠️ Error manejando confirmación: {str(e)}")
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
        """Iniciar el proceso de automatización"""
        if self.worker and self.worker.isRunning():
            return None

        self.worker = SIIAutomatorWorker(rut_empresa, rut_usuario, clave, headless)
        return self.worker

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