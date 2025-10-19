import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PassportParser:
    def parse(self, text: str) -> dict:
        """
        Универсальный парсер паспортных данных
        """
        try:
            # Очищаем текст
            text = re.sub(r'\s+', ' ', text).upper().strip()
            logger.info(f"Текст для парсинга:\n{text}")
            
            # Извлекаем данные
            result = {
                'full_name': self._extract_name_universal(text),
                'birth_date': self._extract_birth_date_universal(text),
                'passport_series': self._extract_series_universal(text),
                'passport_number': self._extract_number_universal(text),
                'passport_code': self._extract_code_universal(text),
                'issue_date': self._extract_issue_date_universal(text),
                'authority': self._extract_authority_universal(text),
                'birth_place': self._extract_birth_place_universal(text),
            }
            
            logger.info(f"Результат парсинга: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            return {'error': str(e)}
    
    def _extract_name_universal(self, text: str) -> str:
        """Универсальное извлечение ФИО"""
        try:
            # СПОСОБ 1: Ищем три слова подряд в формате "Фамилия Имя Отчество"
            pattern = r'\b([А-ЯЁ]{2,}(?:ОВ|ЕВ|ИН|ЫХ|ИЙ|АЯ|ОВА|ЕВА|ИНА|ЫХ|АЯ))\s+([А-ЯЁ]{2,})\s+([А-ЯЁ]{2,}(?:ОВИЧ|ЕВИЧ|ОВНА|ЕВНА|ИЧ|ИНИЧНА))\b'
            match = re.search(pattern, text)
            if match:
                surname, name, patronymic = match.groups()
                if (self._is_valid_surname(surname) and 
                    self._is_valid_name(name) and 
                    self._is_valid_patronymic(patronymic)):
                    return f"{surname} {name} {patronymic}"
            
            # СПОСОБ 2: Ищем по строкам (Фамилия на одной строке, Имя Отчество на следующей)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i in range(len(lines)-2):
                current_line = lines[i]
                next_line = lines[i+1]
                
                # Проверяем, что текущая строка - одна фамилия, а следующая - имя и отчество
                if (len(current_line.split()) == 1 and 
                    len(next_line.split()) == 2 and
                    self._is_valid_surname(current_line) and
                    self._is_valid_name(next_line.split()[0]) and
                    self._is_valid_patronymic(next_line.split()[1])):
                    return f"{current_line} {next_line}"
            
            # СПОСОБ 3: Ищем любые три слова подряд
            matches = re.findall(r'\b([А-ЯЁ]{3,})\s+([А-ЯЁ]{3,})\s+([А-ЯЁ]{3,})\b', text)
            for surname, name, patronymic in matches:
                if (self._is_valid_surname(surname) and 
                    self._is_valid_name(name) and 
                    self._is_valid_patronymic(patronymic)):
                    return f"{surname} {name} {patronymic}"
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения ФИО: {e}")
            return "не распознано"
    
    def _extract_birth_date_universal(self, text: str) -> str:
        """Извлекает дату рождения"""
        try:
            dates = self._extract_all_dates(text)
            
            if len(dates) >= 2:
                # Дата рождения обычно вторая по порядку или идет сразу после ФИО
                return dates[1]  # Вторая дата чаще всего дата рождения
            
            return dates[0] if dates else "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения даты рождения: {e}")
            return "не распознано"
    
    def _extract_series_universal(self, text: str) -> str:
        """Извлекает серию паспорта"""
        try:
            # СПОСОБ 1: Из MRZ строки
            mrz_match = re.search(r'P[NRUS]{2}[A-Z<]*?(\d{2})(\d{2})', text)
            if mrz_match:
                return f"{mrz_match.group(1)} {mrz_match.group(2)}"
            
            # СПОСОБ 2: Ищем паттерн "XX XX" (серия паспорта)
            series_match = re.search(r'\b(\d{2})\s*(\d{2})\b', text)
            if series_match:
                part1, part2 = series_match.groups()
                # Проверяем, что это не часть даты
                if not self._is_part_of_date(part1 + part2, text):
                    return f"{part1} {part2}"
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения серии: {e}")
            return "не распознано"
    
    def _extract_number_universal(self, text: str) -> str:
        """Извлекает номер паспорта"""
        try:
            # СПОСОБ 1: Из MRZ строки
            mrz_match = re.search(r'P[NRUS]{2}[A-Z<]*?\d{4}(\d{6})', text)
            if mrz_match:
                return mrz_match.group(1)
            
            # СПОСОБ 2: Ищем 6 цифр подряд
            numbers = re.findall(r'\b(\d{6})\b', text)
            for number in numbers:
                if not self._is_part_of_date(number, text):
                    return number
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения номера: {e}")
            return "не распознано"
    
    def _extract_code_universal(self, text: str) -> str:
        """Извлекает код подразделения"""
        try:
            # Ищем паттерн "XXX-XXX" или "XXX XXX"
            match = re.search(r'\b(\d{3}[\s-]\d{3})\b', text)
            if match:
                return match.group(1).replace(' ', '-')
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения кода: {e}")
            return "не распознано"
    
    def _extract_issue_date_universal(self, text: str) -> str:
        """Извлекает дату выдачи"""
        try:
            dates = self._extract_all_dates(text)
            
            if len(dates) >= 2:
                # Дата выдачи обычно первая в документе
                return dates[0]
            
            return dates[0] if dates else "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения даты выдачи: {e}")
            return "не распознано"
    
    def _extract_authority_universal(self, text: str) -> str:
        """Извлекает орган выдачи"""
        try:
            # Ключевые слова для поиска органа выдачи
            start_keywords = ['ОТДЕЛ', 'УФМС', 'УФИС', 'МВД', 'ГУВД', 'ОВД']
            end_keywords = ['РАЙОНЕ', 'ОКРУГЕ', 'ГОРОДЕ', 'ОБЛАСТИ', 'КРАЕ']
            
            for start_word in start_keywords:
                if start_word in text:
                    start_idx = text.find(start_word)
                    # Ищем конец
                    substring = text[start_idx:start_idx + 200]
                    
                    # Обрезаем до следующего ключевого слова или даты
                    for end_word in end_keywords:
                        if end_word in substring:
                            end_idx = substring.find(end_word) + len(end_word)
                            return substring[:end_idx].strip()
                    
                    # Если не нашли конец, обрезаем до даты или берем 100 символов
                    date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', substring)
                    if date_match:
                        end_idx = date_match.start()
                        return substring[:end_idx].strip()
                    
                    return substring[:100].strip()
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения органа: {e}")
            return "не распознано"
    
    def _extract_birth_place_universal(self, text: str) -> str:
        """Универсальное извлечение места рождения"""
        try:
            # Убираем MRZ и технические данные
            clean_text = re.sub(r'P<[A-Z<]*\d+[A-Z<]*', '', text)
            clean_text = re.sub(r'\d{4}[A-Z]+\w*', '', clean_text)
            
            # Ищем место рождения после даты рождения
            birth_date = self._extract_birth_date_universal(clean_text)
            if birth_date != "не распознано":
                date_idx = clean_text.find(birth_date)
                if date_idx != -1:
                    text_after_date = clean_text[date_idx + len(birth_date):]
                    
                    # Ищем до следующей даты или ключевых слов
                    stop_markers = ['Код подразделения', 'Выдан', 'Дата выдачи', 'Паспорт', 'Серия']
                    end_idx = len(text_after_date)
                    
                    for marker in stop_markers:
                        marker_idx = text_after_date.find(marker.upper())
                        if marker_idx != -1 and marker_idx < end_idx:
                            end_idx = marker_idx
                    
                    birth_place = text_after_date[:end_idx].strip()
                    birth_place = self._clean_birth_place_universal(birth_place)
                    
                    if birth_place and len(birth_place) > 5:
                        return birth_place
            
            # Поиск по географическим указателям
            geo_indicators = ['ГОР.', 'С.', 'Д.', 'ПОС.', 'РЕСП.', 'КРАЙ', 'ОБЛ.', 'Г.', 'ДЕРЕВНЯ', 'СЕЛО']
            for indicator in geo_indicators:
                if indicator in clean_text:
                    indicator_idx = clean_text.find(indicator)
                    # Берем текст после индикатора
                    place_text = clean_text[indicator_idx:indicator_idx + 150]
                    place_text = self._clean_birth_place_universal(place_text)
                    if place_text and len(place_text) > 5:
                        return place_text
            
            return "не распознано"
            
        except Exception as e:
            logger.error(f"Ошибка извлечения места рождения: {e}")
            return "не распознано"
    
    def _clean_birth_place_universal(self, text: str) -> str:
        """Очищает место рождения от лишних слов и символов"""
        # Убираем технические слова
        unwanted_words = [
            'РОЖДЕНИЯ', 'КОД', 'ПОДРАЗДЕЛЕНИЯ', 'ВЫДАЧИ', 'ДАТА', 
            'МЕСТО', 'ПАСПОРТ', 'СЕРИЯ', 'НОМЕР', 'ВЫДАН'
        ]
        
        for word in unwanted_words:
            text = text.replace(word, '')
        
        # Убираем специальные символы и мусор
        text = re.sub(r'[<>{}\[\]\\]', '', text)
        text = re.sub(r'\d{4,}[A-Za-z]*', '', text)  # Убираем длинные цифробуквенные последовательности
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Обрезаем до разумной длины
        if len(text) > 100:
            text = text[:100] + '...'
        
        return text
    
    def _extract_all_dates(self, text: str) -> list:
        """Извлекает все валидные даты из текста"""
        dates = []
        matches = re.findall(r'\b(\d{2}\.\d{2}\.\d{4})\b', text)
        
        for date_str in matches:
            try:
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                # Проверяем реалистичные границы дат для паспорта
                if 1930 <= date_obj.year <= datetime.now().year:
                    dates.append(date_str)
            except ValueError:
                continue
        
        return dates
    
    def _is_valid_surname(self, word: str) -> bool:
        """Проверяет валидность фамилии"""
        invalid_words = ['РОССИЙСКАЯ', 'ФЕДЕРАЦИЯ', 'ПАСПОРТ', 'ОТДЕЛ', 'УФМС', 
                        'УФИС', 'РОССИИ', 'ДАТА', 'ВЫДАЧИ', 'КОД', 'ПОДРАЗДЕЛЕНИЯ',
                        'МВД', 'РЕСПУБЛИКА', 'ОБЛАСТЬ', 'КРАЙ']
        return (word.isalpha() and len(word) >= 2 and word not in invalid_words)
    
    def _is_valid_name(self, word: str) -> bool:
        """Проверяет валидность имени"""
        common_names = [
            'АЛЕКСАНДР', 'СЕРГЕЙ', 'ВЛАДИМИР', 'ДМИТРИЙ', 'АНДРЕЙ', 
            'АЛЕКСЕЙ', 'ЕВГЕНИЙ', 'МИХАИЛ', 'ИВАН', 'НИКОЛАЙ',
            'ТАТЬЯНА', 'ЕЛЕНА', 'ОЛЬГА', 'АННА', 'ИРИНА', 
            'СВЕТЛАНА', 'МАРИЯ', 'НАДЕЖДА', 'ЮЛИЯ', 'ЕКАТЕРИНА'
        ]
        return word in common_names
    
    def _is_valid_patronymic(self, word: str) -> bool:
        """Проверяет валидность отчества"""
        return (word.endswith(('ОВИЧ', 'ЕВИЧ', 'ИЧ', 'ОВНА', 'ЕВНА', 'ИЧНА', 'ИНИЧНА')))
    
    def _is_part_of_date(self, number: str, text: str) -> bool:
        """Проверяет, является ли число частью даты"""
        idx = text.find(number)
        if idx == -1:
            return False
        context = text[max(0, idx-5):min(len(text), idx+11)]
        return bool(re.search(r'\d{2}\.\d{2}\.\d{4}', context))