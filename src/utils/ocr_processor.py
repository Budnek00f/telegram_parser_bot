# src/utils/ocr_processor.py
import logging
import sys

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        self.ocr_type = "Tesseract"
        
        try:
            import pytesseract
            from PIL import Image, ImageEnhance, ImageFilter
            self.pytesseract = pytesseract
            self.Image = Image
            self.ImageEnhance = ImageEnhance
            self.ImageFilter = ImageFilter
            logger.info("✅ Tesseract инициализирован")
        except ImportError as e:
            logger.error(f"❌ Tesseract не установлен: {e}")
            self.ocr_type = "None"

    def _preprocess_image(self, image_path: str):
        """Улучшает изображение для лучшего распознавания"""
        try:
            # Открываем изображение
            image = self.Image.open(image_path)
            
            # Конвертируем в grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Увеличиваем контраст
            enhancer = self.ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # Увеличиваем контраст
            
            # Увеличиваем резкость
            enhancer = self.ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Применяем легкое размытие для уменьшения шума
            image = image.filter(self.ImageFilter.MedianFilter())
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки изображения: {e}")
            # Возвращаем оригинальное изображение если обработка не удалась
            return self.Image.open(image_path)

    def extract_text_from_image(self, image_path: str):
        if self.ocr_type == "None":
            return "Ошибка: Tesseract не установлен. Установите: pip install pytesseract pillow && brew install tesseract tesseract-lang"
        
        try:
            # Обрабатываем изображение
            processed_image = self._preprocess_image(image_path)
            
            # Настройки для лучшего распознавания русских паспортов
            custom_config = r'--oem 3 --psm 6 -l rus+eng'
            
            # Извлекаем текст
            text = self.pytesseract.image_to_string(processed_image, config=custom_config)
            
            logger.info(f"📝 Tesseract распознал текст: {len(text)} символов")
            
            if text and len(text.strip()) > 10:
                logger.info(f"Распознанный текст:\n{text}")
                return text
            else:
                return "Текст не распознан или слишком короткий"
                
        except Exception as e:
            logger.error(f"❌ Ошибка Tesseract: {e}")
            return f"Ошибка распознавания: {e}"