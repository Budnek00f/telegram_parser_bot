import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_yandex_vision():
    api_key = os.getenv('YANDEX_VISION_API_KEY')
    folder_id = os.getenv('FOLDER_ID')
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Folder ID: {folder_id}")
    
    if not api_key or not folder_id:
        print("❌ Не настроены API_KEY или FOLDER_ID")
        return
    
    # Создаем простой тестовый запрос
    url = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    # Просто тестовый payload для проверки аутентификации
    payload = {
        "folderId": folder_id,
        "analyzeSpecs": [
            {
                "content": "test",  # Невалидный base64, но проверит аутентификацию
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("❌ Неверный API ключ")
        elif response.status_code == 404:
            print("❌ Неверный URL или ресурс не найден")
        elif response.status_code == 400:
            print("⚠️ Неверные параметры запроса, но аутентификация прошла")
        elif response.status_code == 200:
            print("✅ API работает корректно!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_yandex_vision()