# 🚀 Automatizador de Facturas SII

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-orange.svg)
![Selenium](https://img.shields.io/badge/Automation-Selenium-green.svg)

Este proyecto es una herramienta de automatización avanzada diseñada para gestionar la **aceptación de facturas** en el portal del SII (Servicio de Impuestos Internos) de Chile. Permite procesar empresas de forma individual o masiva mediante planillas Excel, optimizando el tiempo y reduciendo errores manuales.

## ✨ Características Principales

- **👤 Procesamiento Individual**: Interfaz intuitiva para procesar una empresa ingresando RUT y Clave de forma manual.
- **📊 Procesamiento Masivo**: Carga de archivos Excel (`.xlsx`, `.xls`, `.csv`) para procesar múltiples empresas de forma secuencial y automática.
- **🌐 Modo Headless**: Opción para ejecutar el navegador en segundo plano, permitiendo trabajar en otras tareas mientras el proceso ocurre.
- **👁️ Monitoreo en Tiempo Real**: Visualización de logs detallados y barra de progreso durante la ejecución.
- **📊 Reportes Automáticos**: Generación de un resumen en Excel al finalizar el proceso masivo, con el detalle de éxito o error por cada empresa.
- **🤖 Motor de Reconocimiento**: Integración con OCR para manejo de desafíos visuales si fuera necesario.
- **🌈 Interfaz Premium**: Diseño moderno con tema personalizado, colores armoniosos y micro-animaciones.

## 🛠️ Requisitos del Sistema

Antes de comenzar, asegúrate de tener instalado:

1.  **Python 3.8+**
2.  **Google Chrome** (última versión estable).
3.  **Tesseract OCR** (opcional, para funcionalidades de lectura de imágenes).

## 🚀 Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone <url-del-repositorio>
    cd APPFACTURAS
    ```

2.  **Crear y activar un entorno virtual**:
    ```bash
    python -m venv venv_facturas
    # En Windows:
    .\venv_facturas\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## 📂 Estructura del Proyecto

```text
APPFACTURAS/
├── src/
│   ├── main.py              # Punto de entrada de la aplicación (GUI)
│   ├── core/
│   │   ├── sii_automator.py # Lógica central de automatización con Selenium
│   │   └── ocr_engine.py    # Procesamiento de imágenes (si aplica)
│   ├── ui/                  # Componentes adicionales de la interfaz
│   ├── assets/              # Logos e iconos del sistema
│   └── utils/               # Funciones auxiliares y helpers
├── data/                    # Directorio para archivos de entrada/salida
└── requirements.txt         # Lista de librerías necesarias
```

## 📖 Uso

### Procesamiento Individual
1. Ejecuta `python src/main.py`.
2. Ingresa el **RUT** y **Clave SII**.
3. Haz clic en **"Iniciar Proceso"**.

### Procesamiento Masivo
1. Prepara un Excel con las columnas: `RUT` y `CLAVE` (también es compatible con `RUT_EMPRESA`, `RUT_USUARIO` y `CLAVE_SII`).
2. En la pestaña **"Procesamiento Masivo"**, carga el archivo.
3. Haz clic en **"Iniciar Todo el Excel"**.

## 🛡️ Seguridad

> [!IMPORTANT]
> Las credenciales ingresadas se utilizan exclusivamente para la autenticación en el sitio oficial del SII. El software no almacena ni envía estas claves a servidores externos. Sin embargo, se recomienda manejar los archivos Excel con precaución.

---



*Développé par une unicornia muy competente © 2026*
