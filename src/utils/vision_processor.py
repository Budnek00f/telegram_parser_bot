import os
import requests
import base64
import logging
from config import Config

logger = logging.getLogger(__name__)

class YandexVisionProcessor:
    def __init__(self):
        self.api_key = Config.YANDEX_VISION_API_KEY
        self.folder_id = Config.FOLDER_ID
        self.base_url = "https://vision.api.cloud.yandex.net/vision/v1"
    
    def extract_text(self, image_path: str) -> str:
        """
        Основной метод для извлечения текста из изображения
        """
        try:
            # Проверяем наличие API ключа и folder_id
            if not self.api_key:
                return "❌ Не настроен YANDEX_VISION_API_KEY"
            if not self.folder_id:
                return "❌ Не настроен FOLDER_ID"
            
            # Проверяем существование файла
            if not os.path.exists(image_path):
                logger.error(f"Файл не найден: {image_path}")
                return "❌ Файл не найден"
            
            # Кодируем изображение в base64
            with open(image_path, "rb") as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            # ПРАВИЛЬНЫЙ URL и структура запроса для Yandex Vision
            url = f"{self.base_url}/batchAnalyze"
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # ПРАВИЛЬНАЯ структура payload для batchAnalyze
            payload = {
                "folderId": self.folder_id,
                "analyzeSpecs": [
                    {
                        "content": image_content,
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "textDetectionConfig": {
                                    "languageCodes": ["ru", "en"]
                                }
                            }
                        ]
                    }
                ]
            }
            
            logger.info(f"Отправляем запрос к Yandex Vision API...")
            logger.info(f"URL: {url}")
            logger.info(f"Folder ID: {self.folder_id}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                text = self._parse_response(response.json())
                logger.info(f"Успешно распознано {len(text)} символов")
                return text
            else:
                logger.error(f"Ошибка API: {response.status_code}")
                logger.error(f"Текст ошибки: {response.text}")
                return f"❌ Ошибка API {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            logger.error("Таймаут запроса к Yandex Vision")
            return "❌ Таймаут при обработке изображения"
        except Exception as e:
            logger.error(f"Ошибка в extract_text: {e}")
            return f"❌ Ошибка обработки: {str(e)}"
    
    def _parse_response(self, response_data: dict) -> str:
        """
        Парсим ответ от Yandex Vision API и извлекаем текст
        """
        try:
            logger.info(f"Структура ответа: {list(response_data.keys())}")
            
            # Проверяем наличие результатов
            if "results" not in response_data:
                return "❌ Не удалось распознать текст (нет results в ответе)"
            
            results = response_data["results"]
            if not results:
                return "❌ Не удалось распознать текст (пустой results)"
            
            # Извлекаем текст из первого результата
            result = results[0]
            logger.info(f"Структура result: {list(result.keys())}")
            
            if "results" in result:
                text_results = result["results"]
                if text_results and "textDetection" in text_results[0]:
                    text_detection = text_results[0]["textDetection"]
                    
                    # Собираем текст из блоков
                    full_text = ""
                    if "pages" in text_detection:
                        for page in text_detection["pages"]:
                            for block in page.get("blocks", []):
                                for line in block.get("lines", []):
                                    line_text = ""
                                    for word in line.get("words", []):
                                        line_text += word.get("text", "") + " "
                                    full_text += line_text.strip() + "\n"
                    
                    return full_text.strip() if full_text else "❌ Текст не найден в изображении"
            
            return "❌ Не удалось извлечь текст из ответа API"
            
        except Exception as e:
            logger.error(f"Ошибка парсинга ответа: {e}")
            return f"❌ Ошибка при разборе ответа: {str(e)}"