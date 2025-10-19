import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN', '7731538447:AAG0pAI5w_kmQce47D-fL_BqUY4i9THwmbw')
    ADMIN_ID = os.getenv('ADMIN_ID', '86458589')
    TEMP_DIR = "temp_files"
    
    # Yandex services
    YANDEX_VISION_API_KEY = os.getenv('YANDEX_VISION_API_KEY', 'test_vision_key')
    YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID', 'b1gtestfolderid123456789')
    
    # Data storage
    DATA_STORAGE_TYPE = os.getenv('DATA_STORAGE_TYPE', 'csv')
    CSV_FILE_PATH = os.getenv('CSV_FILE_PATH', 'passport_data.csv')
    
    # Создаем временные директории если не существуют
    os.makedirs(TEMP_DIR, exist_ok=True)