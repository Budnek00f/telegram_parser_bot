# src/utils/document_processor.py
import logging

# Логгер должен быть определен в самом начале
logger = logging.getLogger(__name__)

# Инициализируем OCR процессор
ocr_processor = None

try:
    from .ocr_processor import OCRProcessor
    ocr_processor = OCRProcessor()
    logger.info("✅ Используем EasyOCR для распознавания")
except Exception as e:
    logger.warning(f"EasyOCR не доступен: {e}")
    try:
        from .tesseract_processor import TesseractOCRProcessor
        ocr_processor = TesseractOCRProcessor()
        logger.info("✅ Используем Tesseract для распознавания")
    except Exception as e:
        logger.error(f"❌ Ни один OCR не доступен: {e}")
        ocr_processor = None

from ..parsers.passport_parser import PassportParser

class DocumentProcessor:
    def __init__(self):
        self.parser = PassportParser()
        
    def process_passport_image(self, image_path: str):
        if not ocr_processor:
            return {'error': 'OCR процессор не инициализирован'}
        
        try:
            text = ocr_processor.extract_text_from_image(image_path)
            logger.info(f"📝 Распознано текста: {len(text)} символов")
            
            if "Ошибка" in text or "Текст не распознан" in text:
                return {'error': text}
            
            result = self.parser.parse(text)
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки документа: {e}")
            return {'error': str(e)}