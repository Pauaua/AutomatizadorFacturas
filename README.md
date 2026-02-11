# 🚀 Automatizador de Facturas SII

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-orange.svg)
![Selenium](https://img.shields.io/badge/Automation-Selenium-green.svg)
![Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

Este proyecto es una herramienta de automatización avanzada diseñada para gestionar la **aceptación de facturas** en el portal del SII (Servicio de Impuestos Internos) de Chile. Permite procesar empresas de forma individual o masiva mediante planillas Excel, optimizando el tiempo y reduciendo errores manuales.

## ✨ Características Principales

- **👤 Procesamiento Individual**: Interfaz intuitiva para procesar una empresa ingresando RUT y Clave de forma manual.
- **📊 Procesamiento Masivo**: Carga de archivos Excel (`.xlsx`, `.xls`, `.csv`) para procesar múltiples empresas de forma secuencial y automática.
- **🔄 Procesamiento Concurrente**: Hasta 3 procesos simultáneos para optimizar el tiempo de ejecución en modo masivo.
- **🌐 Modo Headless**: Opción para ejecutar el navegador en segundo plano, permitiendo trabajar en otras tareas mientras el proceso ocurre.
- **👁️ Monitoreo en Tiempo Real**: Visualización de logs detallados y barra de progreso durante la ejecución.
- **📊 Reportes Automáticos**: Generación de un resumen en Excel al finalizar el proceso masivo, con el detalle de éxito o error por cada empresa.
- **🎨 Interfaz Premium**: Diseño moderno con tema personalizado, colores armoniosos y experiencia de usuario optimizada.
- **📦 Instalador Incluido**: Instalador profesional con Inno Setup para distribución fácil y profesional.

## 🛠️ Requisitos del Sistema

### Para Usuarios Finales (Instalador)

- **Windows 10/11** (64-bit)
- **Google Chrome** (última versión estable)
- **Espacio en disco**: ~500 MB

### Para Desarrolladores

- **Python 3.8+**
- **Google Chrome** (última versión estable)
- **Tesseract OCR** (opcional, para funcionalidades de lectura de imágenes)

## 📦 Instalación para Usuarios 

### Opción 1: Instalador (Recomendado)

La aplicación incluye un **instalador profesional** que facilita la instalación y configuración:

1. **Obtén el Instalador**:
   - Descarga el archivo `AutomatizadorAV_Installer.exe` desde los releases del repositorio.

2. **Ejecuta el Instalador**:
   - Haz doble clic sobre `AutomatizadorAV_Installer.exe`.
   - > [!NOTE]
     > **¿Windows protegió su PC?**
     > Es posible que aparezca una ventana azul de "Windows protegió su PC" porque el programa no tiene una firma digital costosa. Esto es normal en software interno.
     > - Haz clic en **"Más información"**.
     > - Luego presiona el botón **"Ejecutar de todas formas"**.

3. **Asistente de Instalación**:
   - Se abrirá una ventana de bienvenida. Haz clic en **Siguiente** (*Next*).
   - Selecciona la ubicación de instalación (por defecto: `C:\Program Files\AutomatizadorAV`).
   - Selecciona si deseas crear un **icono en el escritorio** (recomendado).
   - Haz clic en **Instalar** (*Install*).

4. **Finalizar**:
   - Una vez complete la barra de progreso, verás una pantalla de confirmación.
   - Puedes dejar marcada la casilla para abrir el programa inmediatamente.
   - Haz clic en **Finalizar** (*Finish*).

5. **¡Listo!**
   - Ahora verás el icono de **AutomatizadorAV** (el logo del programa) en tu escritorio o menú de inicio.
   - Haz doble clic para abrirlo y comenzar a trabajar.

### Opción 2: Ejecutable Directo

Si prefieres no usar el instalador, puedes ejecutar directamente el archivo `.exe`:

1. Descarga la carpeta completa `AutomatizadorAV` desde los releases.
2. Navega a la carpeta y ejecuta `AutomatizadorAV.exe`.
3. La aplicación se ejecutará sin necesidad de instalación.

## 🔧 Instalación para Desarrolladores

Si deseas modificar o contribuir al proyecto:

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd APPFACTURAS
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv_facturas
   # En Windows:
   .\venv_facturas\Scripts\activate
   # En Linux/Mac:
   source venv_facturas/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar en modo desarrollo**:
   ```bash
   python src/main.py
   ```

## 📂 Estructura del Proyecto

```text
APPFACTURAS/
├── src/
│   ├── main.py              # Punto de entrada de la aplicación (GUI)
│   ├── core/
│   │   ├── sii_automator.py # Lógica central de automatización con Selenium
│   │   ├── ocr_engine.py   # Procesamiento de imágenes (opcional)
│   │   └── document_processor.py
│   ├── ui/                  # Componentes adicionales de la interfaz
│   ├── assets/              # Logos e iconos del sistema
│   ├── config/              # Archivos de configuración
│   └── utils/               # Funciones auxiliares y helpers
├── installer/
│   └── setup.iss            # Script de Inno Setup para el instalador
├── dist/                    # Ejecutables generados (no versionar)
├── build/                   # Archivos temporales de build (no versionar)
├── reports/                 # Reportes generados por la aplicación
├── build_exe.py            # Script para generar el ejecutable
├── AutomatizadorAV.spec    # Configuración de PyInstaller
├── requirements.txt        # Lista de librerías necesarias
└── README.md               # Este archivo
```

## 📖 Uso

### Procesamiento Individual

1. Abre la aplicación **AutomatizadorAV**.
2. Ve a la pestaña **"👤 Procesamiento Individual"**.
3. Ingresa el **RUT** (formato: 76.123.456-7) y **Clave SII**.
4. Opcionalmente, activa **"Modo sin interfaz (Headless)"** para ejecutar en segundo plano.
5. Haz clic en **"🚀 Iniciar Proceso"**.
6. Observa el progreso en tiempo real en el panel de logs.

### Procesamiento Masivo

1. Prepara un archivo Excel con las siguientes columnas:
   - `RUT` o `RUT_EMPRESA` o `RUT_USUARIO`: RUT de la empresa/usuario
   - `CLAVE` o `CLAVE_SII`: Clave de acceso al SII
   
   Ejemplo:
   | RUT | CLAVE |
   |-----|-------|
   | 76.123.456-7 | mi_clave_123 |
   | 77.234.567-8 | otra_clave_456 |

2. Abre la aplicación y ve a la pestaña **"📊 Procesamiento Masivo (Excel)"**.
3. Haz clic en **"📁 Cargar Excel"** y selecciona tu archivo.
4. Revisa los datos cargados en la tabla.
5. Opcionalmente, activa **"Modo sin interfaz (Headless)"** (recomendado para procesamiento masivo).
6. Haz clic en **"🚀 Iniciar Todo el Excel"**.
7. El sistema procesará hasta 3 empresas simultáneamente.
8. Al finalizar, se generará automáticamente un reporte Excel con los resultados en la carpeta `reports/`.

## 🔍 Características Técnicas

- **Framework GUI**: PyQt5
- **Automatización Web**: Selenium WebDriver
- **Gestión de Drivers**: webdriver-manager (descarga automática de ChromeDriver)
- **Procesamiento de Datos**: Pandas para manejo de archivos Excel
- **Empaquetado**: PyInstaller para generar ejecutables standalone
- **Instalador**: Inno Setup para distribución profesional
- **Manejo de Rutas**: Sistema robusto que funciona tanto en desarrollo como en ejecutable congelado
- **Manejo de Errores**: Sistema completo de logging y mensajes de error amigables

## 🛡️ Seguridad

> [!IMPORTANT]
> Las credenciales ingresadas se utilizan exclusivamente para la autenticación en el sitio oficial del SII. El software no almacena ni envía estas claves a servidores externos. Sin embargo, se recomienda manejar los archivos Excel con precaución y mantenerlos seguros.

### Buenas Prácticas

- No compartas archivos Excel con credenciales.
- Mantén actualizado Google Chrome para mayor seguridad.
- Usa el modo headless solo cuando sea necesario para evitar problemas de visualización.

## 🐛 Solución de Problemas

### La aplicación no se abre después de instalar

1. Verifica que Google Chrome esté instalado y actualizado.
2. Revisa si hay mensajes de error en `error_log.txt` en el directorio de instalación.
3. Intenta ejecutar el ejecutable directamente desde `C:\Program Files\AutomatizadorAV\AutomatizadorAV.exe`.

### Error al procesar empresas

1. Verifica que las credenciales sean correctas.
2. Asegúrate de tener conexión a internet estable.
3. Revisa los logs en la aplicación para ver detalles del error.
4. Intenta con el modo headless desactivado para ver qué está pasando.

### El instalador muestra advertencia de Windows

Esto es normal para software sin firma digital. El código es seguro y puedes ejecutarlo haciendo clic en "Más información" y luego "Ejecutar de todas formas".

## 📝 Notas de Versión

### Versión 1.0

- ✅ Procesamiento individual y masivo
- ✅ Interfaz gráfica completa con PyQt5
- ✅ Modo headless para ejecución en segundo plano
- ✅ Generación automática de reportes Excel
- ✅ Instalador profesional con Inno Setup
- ✅ Manejo robusto de errores y logging
- ✅ Procesamiento concurrente (hasta 3 procesos simultáneos)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

---

*Développé par une unicornia muy competente © 2026*
