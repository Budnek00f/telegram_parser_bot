# test_easyocr.py
import logging
from src.utils.easyocr_processor import EasyOCRProcessor

logging.basicConfig(level=logging.INFO)

def test_easyocr():
    processor = EasyOCRProcessor()
    
    # Укажите путь к вашему тестовому изображению
    image_path = "test_photo.jpg"
    
    print("🧪 Тестируем EasyOCR...")
    print("=" * 50)
    
    # Тест обычного распознавания
    text = processor.extract_text(image_path)
    print("📄 Обычное распознавание:")
    print(text)
    print()
    
    # Тест с фильтрацией по уверенности
    print("📊 Распознавание с фильтрацией:")
    text_confident = processor.extract_text_with_confidence(image_path, min_confidence=0.6)
    print(text_confident)
    
    print("=" * 50)
    print(f"📊 Сравнение:")
    print(f"Обычное: {len(text)} символов")
    print(f"С фильтром: {len(text_confident)} символов")

if __name__ == "__main__":
    test_easyocr()