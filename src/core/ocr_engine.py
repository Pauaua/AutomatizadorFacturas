import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

class OCREngine:
    def __init__(self, language='spa'):
        """
        Inicializa el motor OCR.
        
        Args:
            language: Idioma para OCR (default: 'spa' - español)
        """
        self.language = language
        self.set_tesseract_path()
        
    def set_tesseract_path(self):
        """Configura la ruta de Tesseract según el sistema operativo."""
        # En Windows, descomenta y ajusta esta línea:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image_path):
        """
        Preprocesa la imagen para mejorar la precisión del OCR.
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Imagen preprocesada
        """
        # Leer imagen
        if isinstance(image_path, str):
            img = cv2.imread(image_path)
        else:
            img = image_path
            
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral adaptativo
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text(self, image_path, preprocess=True):
        """
        Extrae texto de una imagen o documento.
        
        Args:
            image_path: Ruta de la imagen o documento
            preprocess: Si se debe preprocesar la imagen
            
        Returns:
            Texto extraído y datos de confianza
        """
        try:
            if preprocess:
                img = self.preprocess_image(image_path)
                pil_img = Image.fromarray(img)
            else:
                pil_img = Image.open(image_path) if isinstance(image_path, str) else image_path
            
            # Extraer texto con detalles
            data = pytesseract.image_to_data(
                pil_img, 
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Combinar texto
            text = ' '.join([word for word in data['text'] if word.strip()])
            
            # Calcular confianza promedio
            confidences = [int(conf) for conf in data['conf'] if int(conf) >= 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'raw_data': data
            }
            
        except Exception as e:
            print(f"Error en OCR: {e}")
            return {
                'text': '',
                'confidence': 0,
                'error': str(e)
            }
    
    def extract_from_pdf(self, pdf_path):
        """
        Extrae texto de un PDF.
        
        Args:
            pdf_path: Ruta del PDF
            
        Returns:
            Texto extraído
        """
        # Requiere PyPDF2 o pdf2image
        # Esta es una implementación básica
        try:
            # Opción 1: Convertir PDF a imágenes primero
            # from pdf2image import convert_from_path
            # images = convert_from_path(pdf_path)
            # texts = [self.extract_text(img) for img in images]
            # return ' '.join([t['text'] for t in texts])
            
            # Opción 2: Usar PyPDF2 para PDFs basados en texto
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                    
            return {
                'text': text,
                'confidence': 100,  # PDFs de texto tienen confianza alta
                'source': 'pdf_text'
            }
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0,
                'error': str(e)
            }