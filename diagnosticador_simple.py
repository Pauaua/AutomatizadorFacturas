"""
Herramienta de diagnóstico simplificado para inspeccionar la página del SII
y encontrar los selectores correctos para las pestañas
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def diagnosticar_pagina_sii():
    # Configurar navegador
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("Iniciando navegador y navegando a la pagina del SII...")
        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
        time.sleep(10)  # Esperar a que cargue completamente
        
        print("Guardando captura de pantalla...")
        driver.save_screenshot("diagnostico_estado_actual.png")
        
        print("Guardando HTML completo de la pagina...")
        with open("diagnostico_html_completo.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        print("\nBuscando todos los elementos potenciales para pestañas...")
        # Buscar elementos que puedan ser pestañas
        posibles_tabs = []
        
        # Buscar por etiquetas comunes de tabs
        tab_selectors = [
            "//button[contains(@class, 'tab')]",
            "//button[contains(@class, 'nav')]",
            "//button[contains(@class, 'btn') and contains(@class, 'tab')]",
            "//li[contains(@class, 'tab')]",
            "//a[contains(@class, 'tab')]",
            "//div[contains(@class, 'tab')]",
            "//button[contains(., 'Pendiente') or contains(., 'pendiente') or contains(., 'Pendientes') or contains(., 'pendientes')]",
            "//button[contains(., 'Aceptadas') or contains(., 'aceptadas') or contains(., 'Rechazadas') or contains(., 'rechazadas')]"
        ]
        
        for selector in tab_selectors:
            try:
                elementos = driver.find_elements(By.XPATH, selector)
                for elem in elementos:
                    try:
                        texto = elem.text.strip()
                        clases = elem.get_attribute("class") or ""
                        id_attr = elem.get_attribute("id") or ""
                        aria_selected = elem.get_attribute("aria-selected") or ""
                        aria_expanded = elem.get_attribute("aria-expanded") or ""
                        
                        posibles_tabs.append({
                            'elemento': elem,
                            'texto': texto,
                            'clases': clases,
                            'id': id_attr,
                            'aria_selected': aria_selected,
                            'aria_expanded': aria_expanded
                        })
                    except:
                        continue
            except:
                continue
        
        print(f"\nPosibles elementos de pestaña encontrados: {len(posibles_tabs)}")
        for i, tab_info in enumerate(posibles_tabs):
            print(f"  {i+1}. texto='{tab_info['texto']}', class='{tab_info['clases']}', id='{tab_info['id']}', aria-selected='{tab_info['aria_selected']}', aria-expanded='{tab_info['aria_expanded']}'")
        
        # Buscar también elementos de contenido de tabs
        print("\nBuscando posibles contenidos de pestañas...")
        contenido_selectors = [
            "//div[contains(@class, 'tab-content')]",
            "//div[contains(@class, 'tab-pane')]",
            "//div[contains(@class, 'content') and contains(@class, 'active')]",
            "//div[contains(@id, 'pendiente') or contains(@id, 'Pendiente')]",
            "//div[contains(@class, 'pendiente') or contains(@class, 'Pendiente')]"
        ]
        
        for selector in contenido_selectors:
            try:
                elementos = driver.find_elements(By.XPATH, selector)
                print(f"\nElementos con selector '{selector}': {len(elementos)}")
                for elem in elementos:
                    try:
                        texto_preview = elem.text[:100]  # Primeros 100 caracteres
                        clases = elem.get_attribute("class") or ""
                        id_attr = elem.get_attribute("id") or ""
                        style = elem.get_attribute("style") or ""
                        
                        print(f"  - class='{clases}', id='{id_attr}', style='{style}', texto='{texto_preview}...'")
                    except:
                        continue
            except:
                continue
        
        print(f"\nInformacion de estado actual:")
        print(f"  URL actual: {driver.current_url}")
        print(f"  Titulo: {driver.title}")
        
        print("\nDiagnostico completado. Revisa los archivos generados:")
        print("- diagnostico_estado_actual.png")
        print("- diagnostico_html_completo.html")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    diagnosticar_pagina_sii()