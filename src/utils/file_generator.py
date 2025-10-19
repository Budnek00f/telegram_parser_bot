import os
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class FileGenerator:
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
    
    def create_passport_text_file(self, passport_data: dict, user_info: dict) -> str:
        """Создает текстовый файл с данными паспорта"""
        try:
            # Создаем содержимое файла
            content = self._generate_file_content(passport_data, user_info)
            
            # Создаем имя файла
            filename = f"passport_data_{user_info.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.temp_dir, filename)
            
            # Сохраняем файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Текстовый файл создан: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания текстового файла: {e}")
            return ""
    
    def _generate_file_content(self, passport_data: dict, user_info: dict) -> str:
        """Генерирует содержимое текстового файла"""
        content = [
            "=" * 50,
            "ДАННЫЕ ПАСПОРТА ГРАЖДАНИНА РФ",
            "=" * 50,
            "",
            f"ФИО: {passport_data.get('full_name', 'не указано')}",
            f"Дата рождения: {passport_data.get('birth_date', 'не указано')}",
            f"Место рождения: {passport_data.get('birth_place', 'не указано')}",
            f"Серия паспорта: {passport_data.get('passport_series', 'не указано')}",
            f"Номер паспорта: {passport_data.get('passport_number', 'не указано')}",
            f"Код подразделения: {passport_data.get('passport_code', 'не указано')}",
            f"Дата выдачи: {passport_data.get('issue_date', 'не указано')}",
            f"Кем выдан: {passport_data.get('authority', 'не указано')}",
            "",
            "=" * 50,
            "ИНФОРМАЦИЯ О СОХРАНЕНИИ",
            "=" * 50,
            "",
            f"Username: {user_info.get('username', 'не указан')}",
            f"User ID: {user_info.get('user_id', 'не указан')}",
            f"Дата обработки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=" * 50
        ]
        
        return "\n".join(content)
    
    def cleanup_file(self, filepath: str):
        """Удаляет временный файл"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"✅ Файл удален: {filepath}")
        except Exception as e:
            logger.error(f"❌ Ошибка удаления файла: {e}")