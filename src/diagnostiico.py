"""
Diagnóstico del flujo del SII
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configurar navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("1. 🚀 Navegando al login...")
    driver.get("https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html")
    time.sleep(5)
    driver.save_screenshot("diagnostico_01_login.png")
    
    print("2. 🔍 Buscando formulario...")
    # Intenta encontrar campos
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"   Encontrados {len(inputs)} inputs")
    for i, inp in enumerate(inputs):
        inp_id = inp.get_attribute("id") or ""
        inp_name = inp.get_attribute("name") or ""
        inp_type = inp.get_attribute("type") or ""
        print(f"   Input {i}: id='{inp_id}', name='{inp_name}', type='{inp_type}'")
    
    print("\n3. 📄 Guardando HTML de login...")
    with open("diagnostico_login_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source[:5000])
    
    print("4. 🔗 Probando URLs de facturación...")
    urls_prueba = [
        "https://www4.sii.cl/consdcvinternetui/#/index",
        "https://misiir.sii.cl/cgi_misii/siihome.cgi",
        "https://www4.sii.cl/facturaelectronica/"
    ]
    
    for url in urls_prueba:
        print(f"   Probando: {url}")
        try:
            driver.get(url)
            time.sleep(3)
            print(f"   ✅ Cargada - Título: {driver.title[:50]}")
            print(f"   🔗 URL final: {driver.current_url}")
            
            # Verificar elementos clave
            if "factura" in driver.page_source.lower():
                print("   📄 Contiene 'factura' en la página")
            if "pendiente" in driver.page_source.lower():
                print("   ⏳ Contiene 'pendiente' en la página")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n🎉 Diagnóstico completado.")
    print("📁 Archivos generados:")
    print("   - diagnostico_01_login.png")
    print("   - diagnostico_login_page.html")
    
finally:
    driver.quit()