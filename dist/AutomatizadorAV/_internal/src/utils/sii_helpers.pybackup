"""
Utilidades para el módulo SII
"""
import time
from datetime import datetime

def log_con_timestamp(mensaje):
    """Agregar timestamp a los mensajes de log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {mensaje}"

def validar_rut(rut_completo):
    """Validar formato de RUT chileno"""
    import re
    
    rut_pattern = re.compile(r'^(\d{1,3}(?:\.?\d{3}){2})-([\dkK])$')
    match = rut_pattern.match(rut_completo)
    
    if not match:
        return False, "Formato de RUT inválido. Use: 12.345.678-9 o 12345678-9"
    
    # Validar dígito verificador
    rut_numero = match.group(1).replace('.', '')
    dv_ingresado = match.group(2).upper()
    
    # Calcular DV
    suma = 0
    multiplo = 2
    
    for i in range(len(rut_numero)-1, -1, -1):
        suma += int(rut_numero[i]) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    dv_calculado = 11 - (suma % 11)
    
    if dv_calculado == 10:
        dv_calculado = 'K'
    elif dv_calculado == 11:
        dv_calculado = '0'
    else:
        dv_calculado = str(dv_calculado)
    
    if dv_calculado == dv_ingresado:
        return True, "RUT válido"
    else:
        return False, f"DV incorrecto. Debería ser: {dv_calculado}"

def guardar_screenshot(driver, nombre):
    """Guardar screenshot con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{nombre}_{timestamp}.png"
    driver.save_screenshot(nombre_archivo)
    return nombre_archivo

def extraer_texto_elemento(elemento):
    """Extraer texto limpio de un elemento"""
    try:
        texto = elemento.text.strip()
        if texto:
            return texto
        # Intentar con atributo value para inputs
        texto = elemento.get_attribute('value') or ''
        return texto.strip()
    except:
        return ""