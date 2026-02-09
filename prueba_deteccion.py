"""
Script de prueba para verificar la funcionalidad de detección de pestaña pendientes
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def probar_deteccion_pendientes():
    # Configurar navegador
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("Navegando a la página del SII...")
        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
        time.sleep(10)  # Esperar a que cargue completamente
        
        print("Probando detección de elementos visuales de pendientes...")
        
        # Simular la lógica del método _hay_facturas_pendientes_visualmente
        patterns_to_find = [
            "pendiente",
            "por aceptar", 
            "nueva",
            "recibida",
            "no aceptada"
        ]
        
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        print(f"Texto de la página (primeros 500 caracteres): {page_text[:500]}...")
        
        found_pattern = False
        for pattern in patterns_to_find:
            if pattern in page_text:
                print(f"✓ Encontrado patrón: '{pattern}'")
                found_pattern = True
                
        if not found_pattern:
            print("✗ No se encontraron patrones conocidos de pendientes")
        
        # Buscar tablas
        tablas = driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tablas)}")
        
        # Buscar checkboxes
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        print(f"Checkboxes encontrados: {len(checkboxes)}")
        
        # Buscar botones que podrían ser tabs
        botones = driver.find_elements(By.TAG_NAME, "button")
        print(f"Botones encontrados: {len(botones)}")
        
        for i, boton in enumerate(botones[:10]):  # Mostrar solo los primeros 10
            try:
                texto = boton.text.strip()
                clases = boton.get_attribute("class") or ""
                if "pendiente" in texto.lower() or "pendiente" in clases.lower():
                    print(f"  Botón {i+1}: texto='{texto}', class='{clases}'")
            except:
                continue
        
        print("\nLa página está lista. Puedes interactuar manualmente si deseas.")
        input("Presiona Enter para cerrar el navegador...")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    probar_deteccion_pendientes()