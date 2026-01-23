import re
import unicodedata

def normalize_for_search(text: str) -> str:
    """
    Первращает строку в "поисковую" форму:
    - нижний регистр
    - убирает знаки препинания и спецсимволы
    - приводит ё -> е
    - оставялет только буквы, цифры и пробелы
    """
    
    if not text:
        return ""

    # 1. Приводим к "нормальной форме" (разделяем буквы и диакритику)
    nfkd = unicodedata.normalize("NFKD", text)
    # 2. Убираем все, что не является буквой или цифрой (включая апострофы, скобки и т.д)
    witchout_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # 3 Переводим в нижний регистр    
    lower = witchout_accents.lower()
    # 4. Заменяем все ё -> е (для русского)  
    lower.replace("ё", "е")
    # 5. Оставляем только буквы, цифры и пробелы
    cleaned = re.sub(r'[^a-zа-я0-9\s]', '', lower)
    # 6. Сжимаем множественные пробелы в один
    normalized = re.sub(r'\s+', ' ', cleaned).strip()
    
    return normalized

def clean_title(title: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+$', '', title)