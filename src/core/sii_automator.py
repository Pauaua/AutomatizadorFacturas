"""
Módulo para automatizar la aceptación de facturas en el SII
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
from datetime import datetime


# ================= CONFIGURACIÓN ACTUALIZADA DEL SII =================
SII_URLS = {
    'portal': 'https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'login': 'https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'facturas': 'https://www4.sii.cl/consdcvinternetui/#/index',
    'compras': 'https://www4.sii.cl/consdcgi/STC/stc0001i',
}

# Selectores actualizados para la nueva página de login
SII_SELECTORS = {
    'boton_ingresar': [
        "//a[contains(text(), 'Ingresar a Mi SII')]",
        "//a[contains(@href, 'AUT2000')]",
        "//button[contains(text(), 'Ingresar')]",
    ],
    'campo_rut': [
        (By.ID, "rutcntr"),
        (By.NAME, "rutcntr"),
        (By.ID, "rut"),
        (By.NAME, "rut"),
        (By.XPATH, "//input[@type='text' and contains(@id, 'rut')]"),
        (By.XPATH, "//input[@type='text' and contains(@name, 'rut')]"),
    ],
    'campo_clave': [
        (By.ID, "clave"),
        (By.NAME, "clave"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//input[contains(@id, 'clave')]"),
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
        (By.XPATH, "//input[@type='submit' and @value='Ingresar']"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//input[@type='submit']"),
    ],
    'facturas_pendientes': [
        "//*[contains(text(), 'Pendientes')]",
        "//*[contains(@class, 'pendiente')]",
        "//*[contains(text(), 'Pendiente')]",
    ],
    'boton_aceptar': [
        "//button[contains(text(), 'Aceptar')]",
        "//button[contains(@class, 'aceptar')]",
        "//a[contains(text(), 'Aceptar')]",
        "//input[@value='Aceptar']",
    ],
    # AGREGAR ESTOS NUEVOS SELECTORES:
    'menu_facturas': [
        "//a[contains(text(), 'Factura Electrónica')]",
        "//a[contains(@href, 'factura')]",
        "//li[contains(text(), 'Factura')]/a",
    ],
    'link_registro_compras': [
        "//a[contains(text(), 'Registro de Compras y Ventas')]",
        "//a[contains(@href, 'consdcvinternetui')]",
    ],
    'elemento_post_login': [
        (By.ID, "user-info"),
        (By.CLASS_NAME, "welcome-user"),
        "//*[contains(text(), 'Bienvenido')]",
    ],
}

TIMEOUTS = {
    'page_load': 15,
    'element_wait': 20,
    'login_wait': 8,
    'action_delay': 3,
}

FACTURA_PATTERNS = {
    'texto': ['factura', 'dte', 'documento', 'comprobante', 'invoice'],
    'estado': ['pendiente', 'por aceptar', 'validar', 'revisar', 'pending'],
    'clases': ['fila-factura', 'item-dte', 'documento-item', 'pending-item'],
}

# ================= FUNCIONES DE UTILIDAD =================
def validar_rut(rut_completo):
    """Validar formato de RUT chileno"""
    import re
    
    # Aceptar varios formatos: 12.345.678-9, 12345678-9, 12345678-K
    rut_pattern = re.compile(r'^(\d{1,3}(?:\.?\d{3}){2})-([\dkK])$')
    match = rut_pattern.match(rut_completo)
    
    if not match:
        # También aceptar sin guión
        if re.match(r'^\d{7,8}[\dkK]$', rut_completo):
            return True, "RUT aceptado"
        return False, "Formato de RUT inválido. Use: 12.345.678-9 o 12345678-9"
    
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

def extraer_texto_elemento(elemento):
    """Extraer texto limpio de un elemento"""
    try:
        texto = elemento.text.strip()
        if texto:
            return texto
        texto = elemento.get_attribute('value') or ''
        return texto.strip()
    except:
        return ""

def buscar_elemento_con_reintentos(driver, lista_selectores, max_intentos=3):
    """Buscar elemento con múltiples intentos y selectores - CORREGIDO"""
    for intento in range(max_intentos):
        for selector_type, selector_value in lista_selectores:
            try:
                elementos = driver.find_elements(selector_type, selector_value)
                for elemento in elementos:
                    try:
                        if elemento.is_displayed() and elemento.is_enabled():
                            return elemento
                    except:
                        continue
            except:
                continue
        time.sleep(2)
    return None


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
        """Ejecuta el proceso de automatización - VERSIÓN SIMPLIFICADA Y CORREGIDA"""
        try:
            self.log_signal.emit("🚀 Iniciando proceso SII...")
            
            # ================= CONFIGURACIÓN DEL NAVEGADOR =================
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless=new")
            else:
                # Para modo visible, maximizar ventana
                chrome_options.add_argument("--start-maximized")
            
            # Configuraciones mínimas para evitar problemas
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # User-agent realista
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.log_signal.emit("⚙️ Configurando navegador...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # ================= PASO 1: IR DIRECTAMENTE AL LOGIN =================
            self.log_signal.emit("🌐 Navegando directamente al login del SII...")
            
            # Usar la URL CORREGIDA
            login_url = SII_URLS['login']
            self.log_signal.emit(f"🔗 URL: {login_url}")
            
            self.driver.get(login_url)
            time.sleep(5)
            
            # Tomar screenshot inicial
            screenshot_1 = guardar_screenshot(self.driver, "01_login_page")
            if screenshot_1:
                self.log_signal.emit(f"📸 Screenshot guardado: {screenshot_1}")
            
            # ================= PASO 2: FORMULARIO DE LOGIN =================
            self.log_signal.emit("🔍 Buscando formulario de login...")
            
            # Validar RUT
            valid, mensaje = validar_rut(self.rut_usuario)
            if not valid:
                self.log_signal.emit(f"❌ {mensaje}")
                raise ValueError(mensaje)
            
            self.log_signal.emit(f"✅ {mensaje}")
            
            # ================= MÉTODO SIMPLIFICADO: BUSCAR TODOS LOS CAMPOS =================
            self.log_signal.emit("🔎 Buscando campos del formulario...")
            
            # Tomar otro screenshot después de cargar
            time.sleep(2)
            guardar_screenshot(self.driver, "02_page_loaded")
            
            # Método 1: Buscar campo RUT específicamente
            rut_field = None
            for selector_type, selector_value in SII_SELECTORS['campo_rut']:
                try:
                    self.log_signal.emit(f"  Probando selector: {selector_value}")
                    elementos = self.driver.find_elements(selector_type, selector_value)
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed():
                                rut_field = elemento
                                self.log_signal.emit(f"✅ Campo RUT encontrado con: {selector_value}")
                                break
                        except:
                            continue
                    if rut_field:
                        break
                except Exception as e:
                    self.log_signal.emit(f"  Error con selector {selector_value}: {str(e)}")
                    continue
            
            # Método 2: Si no se encontró, buscar todos los inputs de texto
            if not rut_field:
                self.log_signal.emit("⚠️ Buscando campo RUT alternativamente...")
                try:
                    inputs_texto = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    self.log_signal.emit(f"  Encontrados {len(inputs_texto)} inputs de texto")
                    
                    for i, input_elem in enumerate(inputs_texto):
                        try:
                            if input_elem.is_displayed():
                                # Verificar si podría ser campo RUT
                                input_id = input_elem.get_attribute("id") or ""
                                input_name = input_elem.get_attribute("name") or ""
                                input_placeholder = input_elem.get_attribute("placeholder") or ""
                                
                                if any(keyword in input_id.lower() for keyword in ['rut', 'usuario', 'user']) or \
                                   any(keyword in input_name.lower() for keyword in ['rut', 'usuario', 'user']) or \
                                   any(keyword in input_placeholder.lower() for keyword in ['rut', 'r.u.t.']):
                                    rut_field = input_elem
                                    self.log_signal.emit(f"✅ Campo RUT identificado (input {i+1})")
                                    break
                        except:
                            continue
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error en búsqueda alternativa: {str(e)}")
            
            # Método 3: Si aún no se encontró, usar el primer input de texto visible
            if not rut_field:
                self.log_signal.emit("⚠️ Usando primer input de texto visible...")
                try:
                    inputs_texto = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    for input_elem in inputs_texto:
                        try:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                rut_field = input_elem
                                self.log_signal.emit("✅ Usando primer input de texto disponible")
                                break
                        except:
                            continue
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error: {str(e)}")
            
            if not rut_field:
                self.log_signal.emit("❌ No se encontró ningún campo para RUT")
                # Guardar HTML para análisis
                with open("debug_login_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source[:5000])  # Primeros 5000 caracteres
                guardar_screenshot(self.driver, "03_no_rut_field")
                raise Exception("No se pudo encontrar el campo RUT")
            
            # Buscar campo Clave
            clave_field = None
            for selector_type, selector_value in SII_SELECTORS['campo_clave']:
                try:
                    elementos = self.driver.find_elements(selector_type, selector_value)
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed():
                                clave_field = elemento
                                self.log_signal.emit(f"✅ Campo clave encontrado con: {selector_value}")
                                break
                        except:
                            continue
                    if clave_field:
                        break
                except:
                    continue
            
            # Si no se encontró campo clave, buscar input de tipo password
            if not clave_field:
                try:
                    password_fields = self.driver.find_elements(By.XPATH, "//input[@type='password']")
                    if password_fields:
                        for field in password_fields:
                            if field.is_displayed():
                                clave_field = field
                                self.log_signal.emit("✅ Campo clave encontrado (tipo password)")
                                break
                except:
                    pass
            
            if not clave_field:
                self.log_signal.emit("❌ No se encontró campo clave")
                guardar_screenshot(self.driver, "04_no_clave_field")
                raise Exception("No se pudo encontrar el campo clave")
            
            # ================= PASO 3: COMPLETAR FORMULARIO =================
            self.log_signal.emit("📝 Completando formulario...")
            
            # Preparar RUT
            rut_limpio = self.rut_usuario.replace('.', '').replace('-', '').upper()
            if len(rut_limpio) > 1:
                rut_numero = rut_limpio[:-1]
                rut_dv = rut_limpio[-1]
            else:
                rut_numero = rut_limpio
                rut_dv = ""
            
            # Escribir RUT
            try:
                rut_field.clear()
                time.sleep(0.5)
                rut_field.send_keys(rut_numero)
                self.log_signal.emit(f"✅ RUT escrito: {rut_numero}")
                time.sleep(1)
                
                # Buscar campo DV separado
                dv_field = None
                for selector_type, selector_value in SII_SELECTORS['campo_dv']:
                    try:
                        elemento = self.driver.find_element(selector_type, selector_value)
                        if elemento.is_displayed():
                            dv_field = elemento
                            break
                    except:
                        continue
                
                if dv_field and rut_dv:
                    dv_field.clear()
                    time.sleep(0.5)
                    dv_field.send_keys(rut_dv)
                    self.log_signal.emit(f"✅ DV escrito: {rut_dv}")
                else:
                    # Intentar escribir guión y DV en el mismo campo
                    rut_field.send_keys("-" + rut_dv)
                    self.log_signal.emit("✅ RUT completo escrito")
                    
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error escribiendo RUT: {str(e)}")
                # Intentar de otra forma
                rut_field.send_keys(self.rut_usuario)
            
            time.sleep(1)
            
            # Escribir clave
            try:
                clave_field.clear()
                time.sleep(0.5)
                
                # Escribir caracter por caracter (más lento pero más realista)
                for char in self.clave:
                    clave_field.send_keys(char)
                    time.sleep(0.05)
                
                self.log_signal.emit("✅ Clave escrita")
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error escribiendo clave: {str(e)}")
                clave_field.send_keys(self.clave)
            
            time.sleep(1)
            
            # Tomar screenshot antes de enviar
            guardar_screenshot(self.driver, "05_antes_login")
            
            # ================= PASO 4: ENVIAR FORMULARIO =================
            self.log_signal.emit("📤 Enviando formulario...")
            
            # Buscar botón de envío
            submit_button = None
            for selector_type, selector_value in SII_SELECTORS['boton_login']:
                try:
                    elemento = self.driver.find_element(selector_type, selector_value)
                    if elemento.is_displayed() and elemento.is_enabled():
                        submit_button = elemento
                        self.log_signal.emit(f"✅ Botón de login encontrado")
                        break
                except:
                    continue
            
            # Si no se encontró botón específico, buscar cualquier botón o input submit
            if not submit_button:
                try:
                    # Buscar botones que contengan "Ingresar"
                    botones = self.driver.find_elements(By.TAG_NAME, "button")
                    for boton in botones:
                        try:
                            if "ingresar" in boton.text.lower() and boton.is_enabled():
                                submit_button = boton
                                break
                        except:
                            continue
                    
                    # Si no, buscar inputs submit
                    if not submit_button:
                        submits = self.driver.find_elements(By.XPATH, "//input[@type='submit']")
                        if submits:
                            submit_button = submits[0]
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error buscando botón: {str(e)}")
            
            if submit_button:
                self.log_signal.emit("🖱️ Haciendo clic en botón de login...")
                try:
                    submit_button.click()
                except:
                    # Si falla el click normal, usar JavaScript
                    self.driver.execute_script("arguments[0].click();", submit_button)
            else:
                self.log_signal.emit("⚠️ No se encontró botón, presionando ENTER...")
                clave_field.send_keys(Keys.RETURN)
            
            self.log_signal.emit("✅ Formulario enviado")
            
            # ================= PASO 5: VERIFICAR LOGIN EXITOSO Y REDIRECCIÓN =================
            self.log_signal.emit("🔄 Esperando respuesta del servidor...")
            time.sleep(TIMEOUTS['login_wait'])
            
            # Tomar screenshot después del login
            guardar_screenshot(self.driver, "06_despues_login")
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            self.log_signal.emit(f"🔗 URL actual: {current_url}")
            self.log_signal.emit(f"📄 Título de página: {page_title}")
            
            # VERIFICAR REDIRECCIÓN - CORREGIDO
            # Caso 1: Ya estamos en la página correcta
            if "consdcvinternetui" in current_url:
                self.log_signal.emit("✅ Login exitoso - Ya en página de facturas")
            
            # Caso 2: Estamos en siihome.cgi (página principal)
            elif "siihome.cgi" in current_url:
                self.log_signal.emit("⚠️ En página principal MISII, redirigiendo...")
                
                # Intentar navegación directa
                try:
                    self.driver.get(SII_URLS['facturas'])
                    time.sleep(5)
                    
                    if "consdcvinternetui" in self.driver.current_url:
                        self.log_signal.emit("✅ Redireccionamiento manual exitoso")
                    else:
                        self.log_signal.emit("❌ No se pudo redirigir")
                        # Intentar alternativa
                        self._navegar_por_menu()
                        
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error redirigiendo: {str(e)}")
                    self._navegar_por_menu()
            
            # Caso 3: URL desconocida
            else:
                self.log_signal.emit(f"⚠️ URL desconocida: {current_url}")
                self.log_signal.emit("Intentando navegación directa...")
                self.driver.get(SII_URLS['facturas'])
                time.sleep(5)
            
            # Verificar indicadores comunes de error
            page_source = self.driver.page_source.lower()
            error_indicators = ['error', 'incorrecto', 'inválido', 'no válido', 'rechazado']
            
            for indicator in error_indicators:
                if indicator in page_source:
                    self.log_signal.emit(f"❌ Error detectado: '{indicator}'")
                    
                    # Guardar página de error
                    with open("debug_error_page.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source[:10000])
                    
                    # Verificar si es error de credenciales
                    if 'incorrect' in indicator or 'inválid' in indicator:
                        raise Exception("Credenciales incorrectas")
                    else:
                        raise Exception(f"Error de login: {indicator}")
            
            # Verificar indicadores de éxito
            success_indicators = ['contribuyente', 'bienvenido', 'menú', 'inicio', 'home']
            login_successful = False
            
            for indicator in success_indicators:
                if indicator in page_source:
                    login_successful = True
                    self.log_signal.emit(f"✅ Login exitoso detectado: '{indicator}'")
                    break
            
            # Verificar por cambio de URL
            if not login_successful:
                login_pages = ['autenticacion', 'login', 'ingreso', 'acceso']
                if not any(page in current_url.lower() for page in login_pages):
                    login_successful = True
                    self.log_signal.emit("✅ Login exitoso (cambio de URL detectado)")
            
            if not login_successful:
                self.log_signal.emit("⚠️ No se pudo verificar login claramente")
                guardar_screenshot(self.driver, "07_login_ambiguo")
                # Continuar de todos modos, podría haber CAPTCHA
            
            self.log_signal.emit("🎉 ¡Login exitoso!")
            time.sleep(2)
            
            # ================= PASO 6: NAVEGAR A FACTURAS PENDIENTES =================
            self.log_signal.emit("📄 Navegando a facturas pendientes...")
            
            # Verificar si ya estamos en la página correcta, si no, ir
            if "consdcvinternetui" not in self.driver.current_url:
                self.driver.get(SII_URLS['facturas'])
                time.sleep(8)
            
            guardar_screenshot(self.driver, "08_facturas_page")
            
            # ================= PASO 7: SELECCIONAR PERIODO ACTUAL =================
            self._seleccionar_periodo_actual()
            
            # ================= PASO 8: BUSCAR PESTAÑA PENDIENTES =================
            self.log_signal.emit("🔍 Buscando pestaña 'Pendientes'...")
            
            encontro_pendientes = False
            for selector in SII_SELECTORS['facturas_pendientes']:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed():
                                self.log_signal.emit(f"✅ Elemento 'Pendientes' encontrado")
                                self.driver.execute_script("arguments[0].click();", elemento)
                                encontro_pendientes = True
                                time.sleep(5)
                                guardar_screenshot(self.driver, "09_pendientes_page")
                                break
                        except:
                            continue
                    if encontro_pendientes:
                        break
                except:
                    continue
            
            if not encontro_pendientes:
                self.log_signal.emit("⚠️ No se encontró pestaña 'Pendientes'")
            
            # ================= PASO 9: BUSCAR Y ACEPTAR FACTURAS =================
            self._buscar_y_aceptar_facturas_simplificado()
            
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
    
    def _seleccionar_periodo_actual(self):
        """Seleccionar automáticamente el mes y año actual"""
        try:
            self.log_signal.emit("📅 Seleccionando periodo actual...")
            
            # Obtener mes y año actual
            ahora = datetime.now()
            mes_actual = ahora.month
            año_actual = ahora.year
            
            self.log_signal.emit(f"📆 Periodo actual: {mes_actual}/{año_actual}")
            
            # Tomar screenshot antes de seleccionar
            guardar_screenshot(self.driver, "11_antes_seleccion_periodo")
            
            # ================= BUSCAR Y SELECCIONAR AÑO =================
            self.log_signal.emit("🔍 Buscando selector de año...")
            
            # Intentar diferentes formas de encontrar el selector de año
            selectores_año = [
                "//select[@id='periodo']/option[contains(text(), '202')]",
                "//select[contains(@name, 'ano')]",
                "//select[contains(@id, 'ano')]",
                "//select[contains(@ng-model, 'ano')]",
                "//select[contains(@data-ng-model, 'ano')]",
                "//*[contains(text(), 'Año')]/following-sibling::select",
                "//select[contains(@class, 'anio')]",
                "//select[contains(@name, 'periodo')]",
                "//select[contains(@id, 'periodo')]",
            ]
            
            selector_año_encontrado = None
            for selector in selectores_año:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    if elementos:
                        # Limpiar el selector si tiene parte de option
                        if "/option" in selector:
                            selector_año_encontrado = selector.split("/option")[0]
                        else:
                            selector_año_encontrado = selector
                        self.log_signal.emit(f"✅ Selector de año encontrado: {selector}")
                        break
                except:
                    continue
            
            # Si encontramos el selector de año, seleccionar el año actual
            if selector_año_encontrado:
                try:
                    select_año = self.driver.find_element(By.XPATH, selector_año_encontrado)
                    select_obj = Select(select_año)
                    
                    # Intentar seleccionar por valor visible
                    año_seleccionado = False
                    for opcion in select_obj.options:
                        texto_opcion = opcion.text.strip()
                        if str(año_actual) in texto_opcion:
                            select_obj.select_by_visible_text(texto_opcion)
                            self.log_signal.emit(f"✅ Año seleccionado: {texto_opcion}")
                            año_seleccionado = True
                            time.sleep(2)
                            break
                    
                    if not año_seleccionado:
                        # Intentar seleccionar la última opción (normalmente el año más reciente)
                        if len(select_obj.options) > 0:
                            ultima_opcion = select_obj.options[-1].text.strip()
                            select_obj.select_by_visible_text(ultima_opcion)
                            self.log_signal.emit(f"✅ Año seleccionado (última opción): {ultima_opcion}")
                            time.sleep(2)
                            
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error seleccionando año: {str(e)}")
            else:
                self.log_signal.emit("⚠️ No se encontró selector de año específico")
            
            # ================= BUSCAR Y SELECCIONAR MES =================
            self.log_signal.emit("🔍 Buscando selector de mes...")
            
            # Intentar diferentes formas de encontrar el selector de mes
            selectores_mes = [
                "//select[contains(@name, 'mes')]",
                "//select[contains(@id, 'mes')]",
                "//select[contains(@ng-model, 'mes')]",
                "//select[contains(@data-ng-model, 'mes')]",
                "//*[contains(text(), 'Mes')]/following-sibling::select",
                "//select[contains(@class, 'mes')]",
                "//select[@id='mes']",
                "//select[contains(@name, 'periodo_mes')]",
            ]
            
            selector_mes_encontrado = None
            for selector in selectores_mes:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    if elementos:
                        selector_mes_encontrado = selector
                        self.log_signal.emit(f"✅ Selector de mes encontrado: {selector}")
                        break
                except:
                    continue
            
            # Si encontramos el selector de mes, seleccionar el mes actual
            if selector_mes_encontrado:
                try:
                    select_mes = self.driver.find_element(By.XPATH, selector_mes_encontrado)
                    select_obj = Select(select_mes)
                    
                    # Mapeo de nombres de meses en español
                    meses_espanol = {
                        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                    }
                    
                    mes_nombre = meses_espanol.get(mes_actual, "Enero")
                    
                    # Intentar seleccionar por valor visible
                    mes_seleccionado = False
                    for opcion in select_obj.options:
                        texto_opcion = opcion.text.strip()
                        if mes_nombre.lower() in texto_opcion.lower():
                            select_obj.select_by_visible_text(texto_opcion)
                            self.log_signal.emit(f"✅ Mes seleccionado: {texto_opcion}")
                            mes_seleccionado = True
                            time.sleep(2)
                            break
                    
                    if not mes_seleccionado:
                        # Buscar por número de mes
                        for opcion in select_obj.options:
                            texto_opcion = opcion.text.strip()
                            if str(mes_actual) in texto_opcion or f"0{mes_actual}" in texto_opcion:
                                select_obj.select_by_visible_text(texto_opcion)
                                self.log_signal.emit(f"✅ Mes seleccionado (por número): {texto_opcion}")
                                time.sleep(2)
                                break
                            
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error seleccionando mes: {str(e)}")
            else:
                self.log_signal.emit("⚠️ No se encontró selector de mes específico")
            
            # ================= BUSCAR BOTÓN CONSULTAR =================
            self.log_signal.emit("🔍 Buscando botón Consultar...")
            
            selectores_consultar = [
                "//button[contains(text(), 'Consultar')]",
                "//input[@value='Consultar']",
                "//button[@type='submit' and contains(text(), 'Consultar')]",
                "//a[contains(text(), 'Consultar')]",
                "//*[contains(@class, 'btn-consultar')]",
                "//input[@type='submit' and contains(@value, 'Consultar')]",
                "//button[contains(@class, 'btn') and contains(text(), 'Consultar')]",
            ]
            
            consultar_encontrado = False
            for selector in selectores_consultar:
                try:
                    botones = self.driver.find_elements(By.XPATH, selector)
                    for boton in botones:
                        if boton.is_displayed():
                            self.log_signal.emit("✅ Botón Consultar encontrado")
                            self.driver.execute_script("arguments[0].click();", boton)
                            self.log_signal.emit("🔄 Consultando periodo seleccionado...")
                            time.sleep(5)
                            
                            # Tomar screenshot después de consultar
                            guardar_screenshot(self.driver, "12_despues_consultar")
                            consultar_encontrado = True
                            break
                    if consultar_encontrado:
                        break
                except:
                    continue
            
            if not consultar_encontrado:
                self.log_signal.emit("⚠️ No se encontró botón Consultar, intentando con ENTER...")
                try:
                    # Intentar presionar ENTER en cualquier campo
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
                    time.sleep(5)
                    guardar_screenshot(self.driver, "13_despues_enter")
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_signal.emit(f"❌ Error seleccionando periodo: {str(e)}")
            guardar_screenshot(self.driver, "error_seleccion_periodo")
            return False
    
    def _navegar_por_menu(self):
        """Intentar navegar por el menú de MISII"""
        try:
            self.log_signal.emit("🔍 Buscando menú de facturas...")
            
            # Intentar encontrar el menú de "Factura Electrónica"
            for selector in SII_SELECTORS.get('menu_facturas', []):
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            self.log_signal.emit("✅ Menú 'Factura Electrónica' encontrado")
                            self.driver.execute_script("arguments[0].click();", elemento)
                            time.sleep(3)
                            
                            # Buscar "Registro de Compras y Ventas"
                            for reg_selector in SII_SELECTORS.get('link_registro_compras', []):
                                try:
                                    links = self.driver.find_elements(By.XPATH, reg_selector)
                                    for link in links:
                                        if link.is_displayed():
                                            self.log_signal.emit("✅ Link 'Registro de Compras' encontrado")
                                            self.driver.execute_script("arguments[0].click();", link)
                                            time.sleep(5)
                                            return True
                                except:
                                    continue
                except:
                    continue
            
            self.log_signal.emit("⚠️ No se pudo navegar por menú")
            return False
            
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error navegando por menú: {str(e)}")
            return False

    def _buscar_y_aceptar_facturas_simplificado(self):
        """Versión simplificada para aceptar facturas"""
        try:
            self.log_signal.emit("🔍 Buscando facturas pendientes...")
            
            # Esperar un poco más para que carguen las facturas
            time.sleep(3)
            
            facturas_aceptadas = 0
            
            # Tomar screenshot inicial
            guardar_screenshot(self.driver, "10_busqueda_inicial")
            
            # Buscar botones de aceptar con más selectores
            selectores_aceptar = [
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'ACEPTAR')]",
                "//a[contains(text(), 'Aceptar')]",
                "//input[@value='Aceptar']",
                "//*[contains(@class, 'btn-aceptar')]",
                "//*[contains(@ng-click, 'aceptar')]",
                "//*[contains(@onclick, 'aceptar')]",
            ]
            
            botones_aceptar = []
            for selector in selectores_aceptar:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    botones_aceptar.extend(elementos)
                except:
                    continue
            
            # Eliminar duplicados
            botones_unicos = []
            ids_vistos = set()
            for boton in botones_aceptar:
                try:
                    boton_id = boton.get_attribute("id") or ""
                    if boton_id not in ids_vistos:
                        ids_vistos.add(boton_id)
                        botones_unicos.append(boton)
                except:
                    botones_unicos.append(boton)
            
            self.log_signal.emit(f"✅ Encontrados {len(botones_unicos)} botones 'Aceptar' únicos")
            
            for i, boton in enumerate(botones_unicos):
                if not self.is_running:
                    break
                    
                try:
                    if boton.is_displayed() and boton.is_enabled():
                        self.log_signal.emit(f"🖱️ Intentando aceptar factura {i+1}...")
                        
                        # Hacer scroll y hacer clic
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
                        time.sleep(1)
                        
                        # Tomar screenshot antes de aceptar
                        guardar_screenshot(self.driver, f"14_antes_aceptar_{i+1}")
                        
                        # Intentar clic con JavaScript
                        self.driver.execute_script("arguments[0].click();", boton)
                        time.sleep(3)
                        
                        # Buscar confirmación
                        confirmado = self._confirmar_aceptacion_simplificado()
                        
                        if confirmado:
                            facturas_aceptadas += 1
                            self.log_signal.emit(f"✅ Factura {facturas_aceptadas} aceptada")
                            # Esperar después de aceptar
                            time.sleep(2)
                        else:
                            self.log_signal.emit(f"⚠️ No se pudo confirmar factura {i+1}")
                        
                        time.sleep(2)
                        
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Error con botón {i+1}: {str(e)}")
                    continue
            
            # Resultado final
            if facturas_aceptadas > 0:
                mensaje = f"🎉 Proceso completado. Se aceptaron {facturas_aceptadas} factura(s)"
                self.log_signal.emit(mensaje)
                self.finished_signal.emit(True, f"{facturas_aceptadas} facturas aceptadas")
            else:
                mensaje = "ℹ️ No se encontraron facturas pendientes para aceptar"
                self.log_signal.emit(mensaje)
                self.finished_signal.emit(True, "No hay facturas pendientes")
                
        except Exception as e:
            self.log_signal.emit(f"❌ Error buscando facturas: {str(e)}")
            self.finished_signal.emit(True, f"Login exitoso pero error buscando facturas: {str(e)}")
    
    def _confirmar_aceptacion_simplificado(self):
        """Confirmar simplificado"""
        try:
            # Esperar breve
            time.sleep(2)
            
            # Buscar botones de confirmación
            confirm_selectors = [
                "//button[contains(text(), 'Confirmar')]",
                "//button[contains(text(), 'Sí')]",
                "//button[contains(text(), 'SI')]",
                "//input[@value='Confirmar']",
                "//input[@value='Sí']",
                "//input[@value='SI']",
                "//*[contains(@class, 'btn-confirmar')]",
                "//*[contains(@ng-click, 'confirmar')]",
            ]
            
            for selector in confirm_selectors:
                try:
                    botones = self.driver.find_elements(By.XPATH, selector)
                    for boton in botones:
                        if boton.is_displayed():
                            self.driver.execute_script("arguments[0].click();", boton)
                            time.sleep(2)
                            return True
                except:
                    continue
            
            # Si no encuentra confirmación, ver si hay diálogo modal
            try:
                # Buscar modales
                modales = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'modal')]")
                for modal in modales:
                    if modal.is_displayed():
                        # Buscar cualquier botón en el modal
                        botones_modal = modal.find_elements(By.TAG_NAME, "button")
                        for boton in botones_modal:
                            if boton.is_displayed() and boton.text.strip():
                                self.driver.execute_script("arguments[0].click();", boton)
                                time.sleep(2)
                                return True
            except:
                pass
            
            return False
            
        except:
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


