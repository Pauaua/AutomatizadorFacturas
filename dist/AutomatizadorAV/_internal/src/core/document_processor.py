import re
import json
import datetime
from pathlib import Path

class DocumentProcessor:
    def __init__(self):
        self.patterns = self.load_patterns()
        
    def load_patterns(self):
        """Carga patrones para extraer información de facturas."""
        return {
            'invoice_number': [
                r'Factura\s*[Nn]°?\s*:?\s*([A-Z0-9-]+)',
                r'Factura\s*N\.?\s*:?\s*([A-Z0-9-]+)',
                r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
            ],
            'date': [
                r'Fecha\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'total': [
                r'Total\s*:?\s*\$?\s*(\d+[.,]\d{2})',
                r'Importe\s*Total\s*:?\s*\$?\s*(\d+[.,]\d{2})',
                r'Total\s*Amount\s*:?\s*\$?\s*(\d+[.,]\d{2})',
            ],
            'supplier': [
                r'Proveedor\s*:?\s*(.+?)(?:\n|$)',
                r'Supplier\s*:?\s*(.+?)(?:\n|$)',
                r'Razón\s*Social\s*:?\s*(.+?)(?:\n|$)',
            ]
        }
    
    def extract_invoice_data(self, text):
        """
        Extrae información estructurada de una factura.
        
        Args:
            text: Texto extraído por OCR
            
        Returns:
            Diccionario con datos estructurados
        """
        data = {
            'invoice_number': None,
            'date': None,
            'total': None,
            'supplier': None,
            'confidence_score': 0,
            'extraction_date': datetime.datetime.now().isoformat()
        }
        
        matches_found = 0
        
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[field] = match.group(1).strip()
                    matches_found += 1
                    break
        
        # Calcular puntaje de confianza basado en campos encontrados
        data['confidence_score'] = (matches_found / len(self.patterns)) * 100
        
        return data
    
    def validate_invoice(self, invoice_data, min_confidence=80):
        """
        Valida si una factura cumple con los criterios de aceptación.
        
        Args:
            invoice_data: Datos de la factura
            min_confidence: Confianza mínima requerida
            
        Returns:
            Tupla (es_válida, razones)
        """
        reasons = []
        
        # Verificar confianza
        if invoice_data.get('confidence_score', 0) < min_confidence:
            reasons.append(f"Confianza insuficiente: {invoice_data.get('confidence_score')}%")
        
        # Verificar campos obligatorios
        required_fields = ['invoice_number', 'total']
        for field in required_fields:
            if not invoice_data.get(field):
                reasons.append(f"Campo requerido faltante: {field}")
        
        # Validar formato de número de factura
        invoice_no = invoice_data.get('invoice_number', '')
        if invoice_no and not re.match(r'^[A-Z0-9-]+$', invoice_no):
            reasons.append(f"Formato inválido de número de factura: {invoice_no}")
        
        # Validar monto total
        total = invoice_data.get('total', '0')
        try:
            total_clean = total.replace(',', '.')
            total_value = float(re.search(r'[\d.,]+', total_clean).group())
            if total_value <= 0:
                reasons.append(f"Monto total inválido: {total_value}")
        except:
            reasons.append(f"No se pudo parsear el monto total: {total}")
        
        is_valid = len(reasons) == 0
        
        return is_valid, reasons
    
    def process_document(self, file_path, ocr_engine):
        """
        Procesa un documento completo.
        
        Args:
            file_path: Ruta del archivo
            ocr_engine: Instancia del motor OCR
            
        Returns:
            Resultados del procesamiento
        """
        results = {
            'file_path': str(file_path),
            'file_name': Path(file_path).name,
            'processing_date': datetime.datetime.now().isoformat(),
            'status': 'pending',
            'data': None,
            'validation': None,
            'accepted': False
        }
        
        try:
            # Extraer texto según tipo de archivo
            if str(file_path).lower().endswith('.pdf'):
                ocr_result = ocr_engine.extract_from_pdf(file_path)
            else:
                ocr_result = ocr_engine.extract_text(file_path)
            
            if ocr_result.get('error'):
                results['status'] = 'error'
                results['error'] = ocr_result['error']
                return results
            
            # Extraer datos estructurados
            invoice_data = self.extract_invoice_data(ocr_result['text'])
            invoice_data['ocr_confidence'] = ocr_result.get('confidence', 0)
            
            # Validar factura
            is_valid, reasons = self.validate_invoice(invoice_data)
            
            results['data'] = invoice_data
            results['validation'] = {
                'is_valid': is_valid,
                'reasons': reasons
            }
            results['accepted'] = is_valid
            results['status'] = 'completed'
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results