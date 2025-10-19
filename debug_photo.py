# debug_photo.py
import logging
from src.utils.vision_processor import YandexVisionProcessor
from src.parsers.passport_parser import PassportParser

logging.basicConfig(level=logging.DEBUG)

def debug_photo(image_path: str):
    print("🔍 ДЕБАГ РЕЖИМ")
    print("=" * 50)
    
    # 1. Смотрим что возвращает Vision
    vision = YandexVisionProcessor()
    print("📷 Получаем текст от Vision...")
    text = vision.extract_text(image_path)
    
    print("\n📄 РАСПОЗНАННЫЙ ТЕКСТ:")
    print("=" * 30)
    print(text)
    print("=" * 30)
    print(f"Длина текста: {len(text)} символов")
    
    # 2. Смотрим что парсит парсер
    print("\n🔧 Запускаем парсер...")
    parser = PassportParser()
    result = parser.parse(text)
    
    print("\n📊 РЕЗУЛЬТАТ ПАРСИНГА:")
    print("=" * 30)
    for key, value in result.items():
        print(f"{key}: {value}")
    
    return text, result

if __name__ == "__main__":
    # Укажите путь к вашему тестовому фото
    image_path = "test_photo.jpg"  # или полный путь к файлу
    debug_photo(image_path)