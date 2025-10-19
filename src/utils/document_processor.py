import logging
from src.utils.vision_processor import YandexVisionProcessor
from src.parsers.passport_parser import PassportParser

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.vision = YandexVisionProcessor()
        self.parser = PassportParser()
    
    async def process_document(self, file_path: str) -> dict:
        """
        Основной метод обработки документа
        """
        try:
            logger.info(f"Начинаем обработку документа: {file_path}")
            
            # Распознаем текст
            extracted_text = self.vision.extract_text(file_path)
            
            if not extracted_text or "❌" in extracted_text:
                return {
                    'error': f'Не удалось распознать текст: {extracted_text}',
                    'raw_text': ''
                }
            
            logger.info(f"Распознано текста: {len(extracted_text)} символов")
            
            # Парсим данные
            parsed_data = self.parser.parse(extracted_text)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Ошибка в process_document: {e}")
            return {'error': f'Системная ошибка: {str(e)}'}