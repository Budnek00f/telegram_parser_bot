# src/utils/ocr_processor.py
import easyocr
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        # Инициализируем EasyOCR с русским и английским языками
        try:
            self.reader = easyocr.Reader(
                ['ru', 'en'], 
                gpu=False,  # На CPU для совместимости
                download_enabled=True
            )
            logger.info("✅ EasyOCR инициализирован с русским языком")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации EasyOCR: {e}")
            self.reader = None

    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Извлекает текст из изображения с улучшенными настройками"""
        if not self.reader:
            return "Ошибка: OCR не инициализирован"
        
        try:
            # Используем улучшенные параметры для паспортов
            results = self.reader.readtext(
                image_path,
                detail=0,  # Только текст, без деталей
                paragraph=True,  # Группируем в параграфы
                contrast_ths=0.3,  # Улучшаем контраст
                adjust_contrast=0.7,  # Настройка контраста
                text_threshold=0.5,  # Порог для текста
                mag_ratio=2.0  # Увеличение для лучшего распознавания
            )
            
            # Объединяем все результаты
            full_text = '\n'.join(results)
            logger.info(f"📝 EasyOCR распознал текст: {len(full_text)} символов")
            logger.debug(f"Текст: {full_text}")
            
            return full_text if full_text else "Текст не распознан"
            
        except Exception as e:
            logger.error(f"❌ Ошибка OCR: {e}")
            return f"Ошибка распознавания: {e}"