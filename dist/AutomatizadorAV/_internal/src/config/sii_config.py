"""
Configuración actualizada para el módulo SII
"""
from selenium.webdriver.common.by import By

# Configuración de URLs del SII (actualizadas 2026)
SII_URLS = {
    'portal': 'https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'login': 'https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi',
    'facturas': 'https://www4.sii.cl/consdcvinternetui/#/index',
    'compras': 'https://www4.sii.cl/consdcgi/STC/stc0001i',
}

# Selectores optimizados para la nueva interfaz del SII
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
    'facturas_pendientes': [
        "//button[contains(., 'Pendientes')]",
        "//a[contains(., 'Pendientes')]",
    ],
    'boton_aceptar': [
        "//button[contains(., 'Aceptar')]",
        "//button[contains(., 'aceptar')]",
    ],
}

# Tiempos de espera optimizados (segundos)
TIMEOUTS = {
    'page_load': 20,
    'element_wait': 30,
    'login_wait': 10,
    'action_delay': 3,
    'between_actions': 2,
}