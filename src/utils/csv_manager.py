import os
import csv
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class CSVManager:
    def __init__(self):
        self.csv_file = Config.CSV_FILE_PATH
        self._create_file_if_not_exists()
    
    def _create_file_if_not_exists(self):
        """Создает CSV файл с заголовками если его нет"""
        try:
            if not os.path.exists(self.csv_file):
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        'ФИО',
                        'Дата рождения', 
                        'Место рождения',
                        'Серия паспорта',
                        'Номер паспорта',
                        'Код подразделения',
                        'Дата выдачи',
                        'Кем выдан',
                        'Username Telegram',
                        'User ID',
                        'Дата добавления'
                    ])
                logger.info(f"✅ CSV файл создан: {self.csv_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка создания CSV: {e}")
    
    def save_passport_data(self, passport_data: dict, user_info: dict) -> bool:
        """Сохраняет данные паспорта в CSV"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                row_data = [
                    passport_data.get('full_name', ''),
                    passport_data.get('birth_date', ''),
                    passport_data.get('birth_place', ''),
                    passport_data.get('passport_series', ''),
                    passport_data.get('passport_number', ''),
                    passport_data.get('passport_code', ''),
                    passport_data.get('issue_date', ''),
                    passport_data.get('authority', ''),
                    user_info.get('username', ''),
                    str(user_info.get('user_id', '')),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                
                writer.writerow(row_data)
            
            logger.info(f"✅ Данные сохранены в CSV: {passport_data.get('full_name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в CSV: {e}")
            return False
    
    def get_all_data(self) -> list:
        """Возвращает все данные из CSV"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            logger.error(f"❌ Ошибка чтения CSV: {e}")
            return []
    
    def get_csv_file(self) -> str:
        """Возвращает путь к CSV файлу"""
        return self.csv_file if os.path.exists(self.csv_file) else ""