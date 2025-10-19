import logging
from config import Config
from src.utils.csv_manager import CSVManager

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.storage_type = Config.DATA_STORAGE_TYPE
        self.csv_manager = CSVManager()
    
    def save_passport_data(self, passport_data: dict, user_info: dict) -> bool:
        """Сохраняет данные в выбранное хранилище"""
        try:
            if self.storage_type == 'csv':
                return self.csv_manager.save_passport_data(passport_data, user_info)
            else:
                logger.error(f"❌ Неподдерживаемый тип хранилища: {self.storage_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных: {e}")
            return False
    
    def get_storage_info(self) -> dict:
        """Возвращает информацию о хранилище"""
        if self.storage_type == 'csv':
            data = self.csv_manager.get_all_data()
            return {
                'type': 'csv',
                'file_path': self.csv_manager.get_csv_file(),
                'records_count': len(data),
                'last_records': data[-5:] if data else []
            }
        else:
            return {'type': self.storage_type, 'error': 'Неизвестный тип хранилища'}