# src/utils/tesseract_processor.py
import logging

logger = logging.getLogger(__name__)

class TesseractOCRProcessor:
    def __init__(self):
        try:
            import pytesseract
            self.pytesseract = pytesseract
            logger.info("✅ Tesseract инициализирован")
        except ImportError:
            logger.error("❌ pytesseract не установлен")
            self.pytesseract = None

    def extract_text_from_image(self, image_path: str):
        if not self.pytesseract:
            return "Ошибка: Tesseract не установлен"
        
        try:
            from PIL import Image
            image = Image.open(image_path)
            text = self.pytesseract.image_to_string(image, lang='rus+eng')
            logger.info(f"📝 Tesseract распознал текст: {len(text)} символов")
            return text if text.strip() else "Текст не распознан"
        except Exception as e:
            logger.error(f"❌ Ошибка Tesseract: {e}")
            return f"Ошибка распознавания: {e}"