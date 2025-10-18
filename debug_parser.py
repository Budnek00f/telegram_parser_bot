import logging
from src.parsers.passport_parser import PassportParser

# Настройка детального логирования
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

def test_new_passport():
    parser = PassportParser()
    
    # Текст нового паспорта
    new_passport_text = """РОССИЙСКАЯ ФЕДЕРАЦИЯ

ОТДЕЛ УФИС РОССИИ  
ПО КРАСНОДАРСКОМУ КРАЮ В КУРГАНИНСКОМ РАЙОНЕ  

02.03.2015  
Адрес издания:  
030-040  

---

**ВУДНИКОВА**

**ТАТЬЯНА АЛЕКСАНДРОВНА**  
22.11.1994  
ГОР. НЕРЮНГРИ  
РЕСПУБЛИКИ САХА  
(ЯКУТИЯ)  

---

**Ри Russоимпкоиа<Татэяма<Аекэамокоиа<<<<<<<<**  
0311339404RUS9411221F<<<<<<<5150302230040<90"""

    print("="*60)
    print("ТЕСТ ПАРСЕРА С НОВЫМ ПАСПОРТОМ")
    print("="*60)
    
    result = parser.parse(new_passport_text)
    
    print("РЕЗУЛЬТАТ ПАРСИНГА НОВОГО ПАСПОРТА:")
    print("="*60)
    for key, value in result.items():
        if key != 'raw_text':
            print(f"🔹 {key.upper().replace('_', ' ')}: {value}")
    print("="*60)

if __name__ == "__main__":
    test_new_passport()