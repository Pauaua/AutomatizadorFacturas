"""
Herramienta de diagnóstico para inspeccionar la página del SII
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
        print("1. Iniciando navegador y navegando a la pagina del SII...")
        driver.get("https://www4.sii.cl/consdcvinternetui/#/index")
        time.sleep(10)  # Esperar a que cargue completamente

        print("\n2. Guardando captura de pantalla...")
        driver.save_screenshot("diagnostico_estado_actual.png")

        print("\n3. Guardando HTML completo de la pagina...")
        with open("diagnostico_html_completo.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("\n4. Buscando todos los botones y elementos potenciales...")
        # Buscar todos los botones
        botones = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nBotones encontrados: {len(botones)}")
        for i, boton in enumerate(botones[:20]):  # Solo los primeros 20 para no saturar
            try:
                texto = boton.text.strip()
                clases = boton.get_attribute("class") or ""
                id_attr = boton.get_attribute("id") or ""
                aria_label = boton.get_attribute("aria-label") or ""
                aria_selected = boton.get_attribute("aria-selected") or ""

                if texto or clases or id_attr or aria_label:
                    print(f"  Boton {i+1}: texto='{texto}', class='{clases}', id='{id_attr}', aria-label='{aria_label}', aria-selected='{aria_selected}'")
            except:
                continue

        print("\n5. Buscando todos los enlaces...")
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nEnlaces encontrados: {len(enlaces)}")
        for i, enlace in enumerate(enlaces[:20]):  # Solo los primeros 20 para no saturar
            try:
                texto = enlace.text.strip()
                clases = enlace.get_attribute("class") or ""
                href = enlace.get_attribute("href") or ""

                if texto or clases or href:
                    print(f"  Enlace {i+1}: texto='{texto}', class='{clases}', href='{href}'")
            except:
                continue

        print("\n6. Buscando elementos div con clases comunes de tabs...")
        divs = driver.find_elements(By.TAG_NAME, "div")
        tabs_relacionados = []
        for div in divs:
            try:
                clases = div.get_attribute("class") or ""
                texto = div.text.strip()

                if any(keyword in clases.lower() for keyword in ['tab', 'panel', 'content', 'pendiente', 'aceptada', 'rechazada']) or \
                   any(keyword in texto.lower() for keyword in ['pendiente', 'aceptada', 'rechazada']):
                    tabs_relacionados.append((clases, texto))
            except:
                continue

        print(f"Divs relacionados con tabs encontrados: {len(tabs_relacionados)}")
        for i, (clases, texto) in enumerate(tabs_relacionados[:20]):
            print(f"  Div {i+1}: class='{clases}', texto='{texto[:100]}...'")  # Limitar texto

        print("\n7. Buscando inputs de tipo checkbox...")
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        print(f"Checkboxes encontrados: {len(checkboxes)}")

        print("\n8. Buscando tablas...")
        tablas = driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tablas)}")
        for i, tabla in enumerate(tablas):
            try:
                clases = tabla.get_attribute("class") or ""
                id_attr = tabla.get_attribute("id") or ""
                print(f"  Tabla {i+1}: class='{clases}', id='{id_attr}'")
            except:
                continue

        print("\n9. Informacion de estado actual:")
        print(f"   URL actual: {driver.current_url}")
        print(f"   Titulo: {driver.title}")

        print("\n10. Esperando interaccion manual...")
        print("   Ahora puedes interactuar manualmente con la pagina:")
        print("   - Haz clic en la pestaña 'Pendientes'")
        print("   - Observa como cambian las clases de los elementos")
        print("   - Luego vuelve aqui y presiona Ctrl+C para terminar")

        # Mantener el navegador abierto para interaccion manual
        while True:
            time.sleep(5)
            print("Navegador abierto. Presiona Ctrl+C para terminar.")

    except KeyboardInterrupt:
        print("\n\nInterrupcion recibida. Cerrando navegador...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    diagnosticar_pagina_sii()