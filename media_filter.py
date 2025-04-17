from openai import OpenAI
import base64
import aiohttp
from config import OPENAI_API_KEY, OPENAI_BASE_URL, INAPPROPRIATE_THRESHOLD

client = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
)

async def download_file(file_path):
    """Скачивает файл по URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(file_path) as response:
            if response.status == 200:
                return await response.read()
            return None

async def encode_image_to_base64(image_data):
    """Кодирует изображение в base64"""
    return base64.b64encode(image_data).decode('utf-8')

async def check_image_with_ai(image_data):
    """Проверяет изображение с помощью OpenAI Vision на неприемлемый контент"""
    try:
        if not image_data:
            print("Ошибка: Пустые данные изображения")
            return True  # Блокируем пустые изображения для безопасности
            
        base64_image = await encode_image_to_base64(image_data)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Используем полную модель вместо mini для лучшего распознавания
            messages=[
                {
                    "role": "system", 
                    "content": """Ты - система модерации изображений. Твоя задача - определить, содержит ли изображение неприемлемый контент:
                    1. Порнографию или сексуально откровенный контент
                    2. Насилие, кровь, оружие или жестокость
                    3. Экстремистские символы или пропаганду
                    4. Оскорбительные жесты или действия
                    5. Контент, связанный с наркотиками или их употреблением
                    6. Контент, который может нарушать законодательство
                    
                    Будь очень строгим в оценке. При малейшем подозрении на неприемлемый контент, отмечай как неприемлемый.
                    Ответь только 'inappropriate' если изображение неприемлемое или 'appropriate' если изображение приемлемое."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проверь это изображение на наличие неприемлемого контента."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,  # Снижаем температуру для более консистентных результатов
            max_tokens=50,  # Ограничиваем длину ответа
        )
        
        result = response.choices[0].message.content.strip().lower()
        print(f"Результат проверки изображения: {result}")
        
        # Более строгая проверка результата
        is_inappropriate = "inappropriate" in result or "неприемлем" in result
        
        # Применяем порог из конфигурации, если результат неоднозначный
        if not is_inappropriate and INAPPROPRIATE_THRESHOLD < 1.0:
            # Если есть сомнения, проверяем дополнительно
            if "возможно" in result or "может" in result or "сомнительн" in result:
                is_inappropriate = True
                
        return is_inappropriate
    except Exception as e:
        print(f"Ошибка при проверке изображения через OpenAI: {e}")
        # В случае ошибки блокируем изображение для безопасности
        return True

async def check_video_with_ai(thumbnail_data):
    """Проверяет видео (превью) с помощью OpenAI Vision на неприемлемый контент"""
    try:
        if not thumbnail_data:
            print("Ошибка: Пустые данные превью видео")
            return True  # Блокируем пустые превью для безопасности
            
        base64_image = await encode_image_to_base64(thumbnail_data)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Используем полную модель вместо mini для лучшего распознавания
            messages=[
                {
                    "role": "system", 
                    "content": """Ты - система модерации видеоконтента. Твоя задача - определить, содержит ли видео (по его превью/кадру) неприемлемый контент:
                    1. Порнографию или сексуально откровенный контент
                    2. Насилие, кровь, оружие или жестокость
                    3. Экстремистские символы или пропаганду
                    4. Оскорбительные жесты или действия
                    5. Контент, связанный с наркотиками или их употреблением
                    6. Контент, который может нарушать законодательство
                    
                    Будь очень строгим в оценке. При малейшем подозрении на неприемлемый контент, отмечай как неприемлемый.
                    Даже если ты видишь только один кадр, попытайся определить, к какой категории контента относится видео.
                    Ответь только 'inappropriate' если видео может содержать неприемлемый контент или 'appropriate' если видео выглядит приемлемым."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проверь этот кадр из видео на наличие неприемлемого контента. Даже если это только превью, попытайся определить, может ли видео содержать запрещенный контент."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,  # Снижаем температуру для более консистентных результатов
            max_tokens=50,  # Ограничиваем длину ответа
        )
        
        result = response.choices[0].message.content.strip().lower()
        print(f"Результат проверки видео: {result}")
        
        # Более строгая проверка результата
        is_inappropriate = "inappropriate" in result or "неприемлем" in result
        
        # Применяем порог из конфигурации, если результат неоднозначный
        if not is_inappropriate and INAPPROPRIATE_THRESHOLD < 1.0:
            # Если есть сомнения, проверяем дополнительно
            if "возможно" in result or "может" in result or "сомнительн" in result:
                is_inappropriate = True
                
        return is_inappropriate
    except Exception as e:
        print(f"Ошибка при проверке видео через OpenAI: {e}")
        # В случае ошибки блокируем видео для безопасности
        return True
