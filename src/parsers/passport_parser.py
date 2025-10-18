import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PassportParser:
    def parse(self, text: str) -> dict:
        """
        Улучшенный парсер для паспорта РФ с обработкой машиночитаемой зоны
        """
        try:
            # Очищаем и подготавливаем текст
            cleaned_text = self._clean_text(text)
            
            # Логируем очищенный текст для отладки
            logger.info(f"Очищенный текст для парсинга:\n{cleaned_text}")
            
            # Разделяем текст на визуальную и машиночитаемую зоны
            visual_zone, machine_zone = self._split_zones(cleaned_text)
            logger.info(f"Визуальная зона: {visual_zone}")
            logger.info(f"Машиночитаемая зона: {machine_zone}")
            
            # Извлекаем данные из обеих зон
            result = {
                'full_name': self._extract_name_combined(visual_zone, machine_zone),
                'birth_date': self._extract_birth_date_combined(visual_zone, machine_zone),
                'passport_series': self._extract_passport_series_combined(visual_zone, machine_zone),
                'passport_number': self._extract_passport_number_combined(visual_zone, machine_zone),
                'passport_code': self._extract_passport_code_combined(visual_zone, machine_zone),
                'issue_date': self._extract_issue_date_combined(visual_zone, machine_zone),
                'authority': self._extract_authority_combined(visual_zone, machine_zone),
                'birth_place': self._extract_birth_place_combined(visual_zone, machine_zone),
                'raw_text': text[:500] + "..." if len(text) > 500 else text
            }
            
            logger.info(f"Извлечены данные: { {k: v for k, v in result.items() if k != 'raw_text'} }")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка парсинга паспорта: {e}")
            return {'error': f'Ошибка парсинга: {str(e)}'}
    
    def _clean_text(self, text: str) -> str:
        """Очищает текст для парсинга"""
        # Заменяем множественные пробелы и переносы
        text = re.sub(r'\s+', ' ', text)
        # Приводим к верхнему регистру
        text = text.upper().strip()
        return text
    
    def _split_zones(self, text: str) -> tuple:
        """
        Разделяет текст на визуальную и машиночитаемую зоны
        """
        # Машиночитаемая зона обычно содержит много <<<<<<< и имеет специфичный формат
        machine_indicators = ['<<<<<<<', 'RUS', 'F<', 'M<', 'RUS<']
        
        for indicator in machine_indicators:
            if indicator in text:
                parts = text.split(indicator)
                if len(parts) >= 2:
                    visual_zone = parts[0]
                    machine_zone = indicator + parts[1]
                    return visual_zone, machine_zone
        
        # Если не нашли индикаторы, возвращаем весь текст как визуальную зону
        return text, ""
    
    def _extract_name_combined(self, visual_zone: str, machine_zone: str) -> str:
        """
        Извлекает ФИО из обеих зон
        """
        try:
            # Сначала пытаемся из визуальной зоны
            visual_name = self._extract_name_visual(visual_zone)
            if visual_name != "не распознано":
                return visual_name
            
            # Затем из машиночитаемой зоны
            machine_name = self._extract_name_machine(machine_zone)
            if machine_name != "не распознано":
                return machine_name
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения ФИО: {e}")
            return "не распознано"
    
    def _extract_name_visual(self, visual_zone: str) -> str:
        """Извлекает ФИО из визуальной зоны"""
        # Ищем ФИО в формате с ** ** (жирный шрифт в распознавании)
        bold_pattern = r'\*\*([А-Я]+)\*\*\s+\*\*([А-Я]+)\*\*\s+\*\*([А-Я]+)\*\*'
        match = re.search(bold_pattern, visual_zone)
        if match:
            surname, name, patronymic = match.groups()
            return f"{surname} {name} {patronymic}"
        
        # Ищем три слова подряд в верхнем регистре
        name_pattern = r'\b([А-Я]{3,})\s+([А-Я]{3,})\s+([А-Я]{3,})\b'
        matches = re.findall(name_pattern, visual_zone)
        for match in matches:
            surname, name, patronymic = match
            if self._is_valid_name(surname) and self._is_valid_name(name) and self._is_valid_name(patronymic):
                return f"{surname} {name} {patronymic}"
        
        return "не распознано"
    
    def _extract_name_machine(self, machine_zone: str) -> str:
        """Извлекает ФИО из машиночитаемой зоны"""
        # Формат: P<RUSLASTNAME<FIRSTNAME<MIDDLENAME<<<<<...
        if 'P<' in machine_zone:
            parts = machine_zone.split('P<')[1].split('<<')[0].split('<')
            if len(parts) >= 3:
                surname = parts[0].replace('RUS', '')
                name = parts[1]
                patronymic = parts[2]
                return f"{surname} {name} {patronymic}"
        
        return "не распознано"
    
    def _extract_birth_date_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает дату рождения из обеих зон"""
        try:
            # Из визуальной зоны
            visual_date = self._extract_date_visual(visual_zone)
            if visual_date != "не распознано":
                return visual_date
            
            # Из машиночитаемой зоны (формат: YYMMDD)
            machine_date = self._extract_birth_date_machine(machine_zone)
            if machine_date != "не распознано":
                return machine_date
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения даты рождения: {e}")
            return "не распознано"
    
    def _extract_date_visual(self, visual_zone: str) -> str:
        """Извлекает дату из визуальной зоны"""
        dates = re.findall(r'\b(\d{2}\.\d{2}\.\d{4})\b', visual_zone)
        for date in dates:
            try:
                date_obj = datetime.strptime(date, '%d.%m.%Y')
                if 1900 <= date_obj.year <= datetime.now().year:
                    return date
            except ValueError:
                continue
        return "не распознано"
    
    def _extract_birth_date_machine(self, machine_zone: str) -> str:
        """Извлекает дату рождения из машиночитаемой зоны (формат: YYMMDD)"""
        # Ищем паттерн 6 цифр после ФИО (941122 = 94-11-22)
        match = re.search(r'(\d{2})(\d{2})(\d{2})[FM]', machine_zone)
        if match:
            year, month, day = match.groups()
            # Преобразуем год (94 = 1994)
            year = f"19{year}" if int(year) < 50 else f"20{year}"
            return f"{day}.{month}.{year}"
        return "не распознано"
    
    def _extract_passport_series_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает серию паспорта"""
        try:
            # Из машиночитаемой зоны (первые 4 цифры номера паспорта)
            if machine_zone:
                # Ищем 9 цифр подряд (номер паспорта в машиночитаемой зоне)
                match = re.search(r'\b(\d{9})\b', machine_zone)
                if match:
                    full_number = match.group(1)
                    # Первые 4 цифры - серия, последние 6 - номер
                    series = f"{full_number[:2]} {full_number[2:4]}"
                    return series
            
            # Из визуальной зоны
            series_visual = self._extract_series_visual(visual_zone)
            if series_visual != "не распознано":
                return series_visual
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения серии паспорта: {e}")
            return "не распознано"
    
    def _extract_series_visual(self, visual_zone: str) -> str:
        """Извлекает серию из визуальной зоны"""
        # Ищем 4 цифры (серия без пробела)
        match = re.search(r'\b(\d{4})\b', visual_zone)
        if match:
            series = match.group(1)
            return f"{series[:2]} {series[2:]}"
        return "не распознано"
    
    def _extract_passport_number_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает номер паспорта"""
        try:
            # Из машиночитаемой зоны
            if machine_zone:
                match = re.search(r'\b(\d{9})\b', machine_zone)
                if match:
                    full_number = match.group(1)
                    # Последние 6 цифр - номер
                    number = full_number[4:]
                    return number
            
            # Из визуальной зоны
            number_visual = self._extract_number_visual(visual_zone)
            if number_visual != "не распознано":
                return number_visual
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения номера паспорта: {e}")
            return "не распознано"
    
    def _extract_number_visual(self, visual_zone: str) -> str:
        """Извлекает номер из визуальной зоны"""
        # Ищем 6 цифр подряд
        match = re.search(r'\b(\d{6})\b', visual_zone)
        if match:
            return match.group(1)
        return "не распознано"
    
    def _extract_passport_code_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает код подразделения"""
        try:
            # Из визуальной зоны (формат: XXX-XXX)
            code_visual = self._extract_code_visual(visual_zone)
            if code_visual != "не распознано":
                return code_visual
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения кода подразделения: {e}")
            return "не распознано"
    
    def _extract_code_visual(self, visual_zone: str) -> str:
        """Извлекает код подразделения из визуальной зоны"""
        match = re.search(r'\b(\d{3}[\s-]\d{3})\b', visual_zone)
        if match:
            return match.group(1)
        return "не распознано"
    
    def _extract_issue_date_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает дату выдачи"""
        return self._extract_date_visual(visual_zone)
    
    def _extract_authority_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает орган выдачи"""
        try:
            # Ищем в визуальной зоне
            patterns = [
                r'(ОТДЕЛ[^,]{10,80})',
                r'(УФМС[^,]{10,80})',
                r'(УФИС[^,]{10,80})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, visual_zone)
                if match:
                    return match.group(1).strip()
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения органа выдачи: {e}")
            return "не распознано"
    
    def _extract_birth_place_combined(self, visual_zone: str, machine_zone: str) -> str:
        """Извлекает место рождения"""
        try:
            # Ищем место рождения в визуальной зоне
            birth_place_patterns = [
                r'ГОР\.\s*([^0-9]{10,80}?)(?=\d|$)',
                r'(\d{2}\.\d{2}\.\d{4})\s+([^0-9]{10,80}?РЕСПУБЛИКИ[^0-9]{10,80})',
            ]
            
            for pattern in birth_place_patterns:
                match = re.search(pattern, visual_zone)
                if match:
                    if len(match.groups()) == 2:
                        return f"ГОР. {match.group(2).strip()}"
                    else:
                        return f"ГОР. {match.group(1).strip()}"
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения места рождения: {e}")
            return "не распознано"
    
    def _is_valid_name(self, word: str) -> bool:
        """Проверяет, является ли слово валидным именем"""
        invalid_words = ['ФЕДЕРАЦИЯ', 'ОТДЕЛ', 'УФМС', 'УФИС', 'РОССИИ', 'ПО', 'КРАЮ', 'РАЙОНЕ', 'ПАСПОРТ']
        return (len(word) >= 3 and 
                word.isalpha() and 
                word not in invalid_words and
                not any(char.isdigit() for char in word))