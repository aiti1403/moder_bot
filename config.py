import logging

# Настройки бота
BOT_TOKEN = "7629674183:AAHphaiG4G_Qb7LjoLYv19yto8-hbmQ4bbo"  # Замените на ваш токен от BotFather

# Настройки OpenAI
OPENAI_API_KEY = "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"  # Замените на ваш ключ API
OPENAI_BASE_URL = "https://openrouter.ai/api/v1"

# Настройки логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Список запрещенных слов (базовый, можно расширить)
FORBIDDEN_WORDS = [
    "блять", "хуй", "пизда", "ебать", "сука", 
    "нахуй", "пидор", "пидар", "хуесос", "долбоёб"
]

# Порог уверенности для определения неприемлемого контента
INAPPROPRIATE_THRESHOLD = 0.7
