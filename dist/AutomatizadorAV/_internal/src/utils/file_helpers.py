import os
import shutil
from pathlib import Path
import json

class FileHelpers:
    @staticmethod
    def ensure_directory(path):
        """Asegura que un directorio exista."""
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_extension(file_path):
        """Obtiene la extensión de un archivo."""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def is_supported_file(file_path):
        """Verifica si el archivo es compatible."""
        supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']
        return FileHelpers.get_file_extension(file_path) in supported_extensions
    
    @staticmethod
    def move_file(source, destination):
        """Mueve un archivo a un destino."""
        try:
            shutil.move(source, destination)
            return True, "Archivo movido exitosamente"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def save_results(results, output_path):
        """Guarda los resultados del procesamiento."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando resultados: {e}")
            return False
    
    @staticmethod
    def get_files_from_directory(directory, recursive=False):
        """Obtiene todos los archivos compatibles de un directorio."""
        directory = Path(directory)
        files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and FileHelpers.is_supported_file(file_path):
                files.append(str(file_path))
        
        return files