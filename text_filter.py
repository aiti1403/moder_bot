from openai import OpenAI
import re
from config import OPENAI_API_KEY, OPENAI_BASE_URL, FORBIDDEN_WORDS, INAPPROPRIATE_THRESHOLD

client = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
)

def contains_forbidden_words(text):
    """Проверяет наличие запрещенных слов в тексте"""
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return True
    return False

async def check_text_with_ai(text):
    """Проверяет текст с помощью OpenAI на наличие неприемлемого содержания"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - система модерации контента. Твоя задача - определить, содержит ли текст нецензурную лексику, оскорбления, угрозы или другой неприемлемый контент. Ответь только 'inappropriate' если текст неприемлемый или 'appropriate' если текст приемлемый."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip().lower()
        return "inappropriate" in result
    except Exception as e:
        print(f"Ошибка при проверке текста через OpenAI: {e}")
        # В случае ошибки API используем базовую проверку
        return contains_forbidden_words(text)

async def is_inappropriate_text(text):
    """Комбинированная проверка текста"""
    # Сначала проверяем по базовому списку слов (быстрее)
    if contains_forbidden_words(text):
        return True
    
    # Если базовая проверка не выявила проблем, используем AI
    return await check_text_with_ai(text)
