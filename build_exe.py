import os
import subprocess
import sys
from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    """Convierte un archivo PNG a ICO para usarlo como icono de la aplicación."""
    if not os.path.exists(ico_path):
        print(f"🎨 Generando icono desde {png_path}...")
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"✅ Icono generado: {ico_path}")

def build():
    """Generar ejecutable (.exe) del programa usando PyInstaller"""
    print("🚀 Iniciando proceso de empaquetado...")
    
    # Asegurar que estamos en el directorio correcto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Comprobar si PyInstaller y Pillow están instalados
    try:
        import PyInstaller
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    try:
        from PIL import Image
    except ImportError:
        print("📦 Instalando Pillow para manejar iconos...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

    # Configuración de rutas e iconos
    entry_point = "src/main.py"
    output_name = "AutomatizadorAV"
    logo_png = os.path.join("src", "assets", "logo.png")
    logo_ico = os.path.join("src", "assets", "logo.ico")

    # Generar icono si existe el PNG
    if os.path.exists(logo_png):
        convert_png_to_ico(logo_png, logo_ico)
    
    # Parámetros de PyInstaller
    # Rutas de datos (activos, config, ui)
    # Formato: --add-data "ruta_origen;ruta_destino"
    data_args = [
        ["--add-data", "src/assets;src/assets"],
        ["--add-data", "src/config;src/config"],
        ["--add-data", "src/ui;src/ui"],
        ["--add-data", "src/utils;src/utils"],
        ["--add-data", "src/core;src/core"],
    ]
    
    # Comando base
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",          # No mostrar consola al abrir
        "--name", output_name,  # Nombre del ejecutable
        "--clean",              # Limpiar cache antes de construir
        "--onedir",             # Carpeta con dependencias (más rápido al abrir)
    ]

    # Añadir icono si se generó exitosamente
    if os.path.exists(logo_ico):
        command.extend(["--icon", logo_ico])
    
    # Añadir argumentos de datos
    for arg_pair in data_args:
        command.extend(arg_pair)
        
    # Añadir entry point
    command.append(entry_point)
    
    print(f"🛠️ Ejecutando empaquetado...")
    
    try:
        subprocess.check_call(command)
        print(f"\n✅ Proceso finalizado con éxito.")
        print(f"📂 El programa ejecutable se encuentra en la carpeta 'dist/{output_name}/{output_name}.exe'")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante el empaquetado: {e}")

if __name__ == "__main__":
    build()
