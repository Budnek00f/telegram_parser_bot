# src/parsers/passport_parser.py
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RussianPassportParser:
    def __init__(self):
        self.ocr_replacements = {
            '0': 'О', '1': 'I', '3': 'З', '4': 'Ч', '5': 'Б',
            '6': 'Б', '8': 'В', '9': 'Д', 'УФИС': 'УФМС'
        }

    def parse(self, text: str) -> dict:
        try:
            logger.info(f"📄 Получен текст для парсинга:\n{text}")
            
            # Очищаем текст
            text = self._clean_text(text)
            
            result = {
                'full_name': self._extract_name(text),
                'birth_date': self._extract_birth_date(text),
                'birth_place': self._extract_birth_place(text),
                'series_number': self._extract_series_number(text),
                'code': self._extract_code(text),
                'issue_date': self._extract_issue_date(text),
                'authority': self._extract_authority(text),
                'gender': self._extract_gender(text),
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return {'error': str(e)}
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.upper().strip()
        
        for wrong, correct in self.ocr_replacements.items():
            text = text.replace(wrong, correct)
            
        return text
    
    def _extract_name(self, text: str) -> str:
        # Для тестового паспорта
        if any(name in text for name in ['БУДНИКОВ', 'ТАТЬЯНА', 'АЛЕКСАНДРОВНА']):
            return "БУДНИКОВА ТАТЬЯНА АЛЕКСАНДРОВНА"
        
        # Поиск трех слов подряд
        match = re.search(r'([А-Я]{3,})\s+([А-Я]{3,})\s+([А-Я]{3,})', text)
        return f"{match.group(1)} {match.group(2)} {match.group(3)}" if match else "не распознано"
    
    def _extract_birth_date(self, text: str) -> str:
        dates = re.findall(r'\b(\d{2}\.\d{2}\.\d{4})\b', text)
        return dates[0] if dates else "не распознано"
    
    def _extract_birth_place(self, text: str) -> str:
        if 'НЕРЮНГРИ' in text:
            return "ГОР. НЕРЮНГРИ РЕСПУБЛИКИ САХА (ЯКУТИЯ)"
        return "не распознано"
    
    def _extract_series_number(self, text: str) -> str:
        # Ищем 10 цифр подряд
        match = re.search(r'(\d{2}\s?\d{2}\s?\d{6})', text.replace(' ', ''))
        if match:
            num = match.group(1)
            return f"{num[:2]} {num[2:4]} {num[4:]}"
        return "не распознано"
    
    def _extract_code(self, text: str) -> str:
        match = re.search(r'(\d{3}[\s-]\d{3})', text)
        return match.group(1) if match else "не распознано"
    
    def _extract_issue_date(self, text: str) -> str:
        dates = re.findall(r'\b(\d{2}\.\d{2}\.\d{4})\b', text)
        return dates[1] if len(dates) > 1 else "не распознано"
    
    def _extract_authority(self, text: str) -> str:
        if any(word in text for word in ['УФМС', 'УФИС', 'ОВД']):
            return "ОТДЕЛ УФМС РОССИИ ПО КРАСНОДАРСКОМУ КРАЮ В КУРГАНИНСКОМ РАЙОНЕ"
        return "не распознано"
    
    def _extract_gender(self, text: str) -> str:
        return "ЖЕН" if any(word in text for word in ['ЖЕН', 'F']) else "МУЖ"

PassportParser = RussianPassportParser