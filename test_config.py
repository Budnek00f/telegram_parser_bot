from config import Config

print("🔧 Проверка конфигурации:")
print(f"BOT_TOKEN: {Config.BOT_TOKEN[:20]}...")
print(f"ADMIN_ID: {Config.ADMIN_ID}")
print(f"YANDEX_VISION_API_KEY: {Config.YANDEX_VISION_API_KEY}")
print(f"YANDEX_FOLDER_ID: {Config.YANDEX_FOLDER_ID}")
print(f"DATA_STORAGE_TYPE: {Config.DATA_STORAGE_TYPE}")
print(f"CSV_FILE_PATH: {Config.CSV_FILE_PATH}")
print("✅ Конфигурация загружена успешно!")