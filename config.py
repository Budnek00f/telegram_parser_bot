import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_ID = os.getenv('ADMIN_ID')
    TEMP_DIR = "temp_files"
    
    # Yandex Vision
    YANDEX_VISION_API_KEY = os.getenv('YANDEX_VISION_API_KEY')
    FOLDER_ID = os.getenv('FOLDER_ID')
    
    # Создаем временную директорию если не существует
    os.makedirs(TEMP_DIR, exist_ok=True)