import os
import logging
from config import Config

logger = logging.getLogger(__name__)

class YandexVisionProcessor:
    def __init__(self):
        # Оставляем для совместимости
        pass
    
    def extract_text(self, image_path: str) -> str:
        """
        Заглушка - теперь используем EasyOCR
        """
        logger.warning("⚠️ YandexVision устарел, используйте EasyOCR")
        return "❌ Используйте EasyOCR процессор"