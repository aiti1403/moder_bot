import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
from config import BOT_TOKEN
from filters import is_inappropriate_text, check_image_with_ai, check_video_with_ai, download_file

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"Пользователь {message.from_user.username} запустил бота")
    await message.answer(
        "Привет! Я бот-модератор. Я буду следить за сообщениями в чате и удалять неприемлемый контент."
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    logger.info(f"Пользователь {message.from_user.username} запросил помощь")
    help_text = """
    Я бот-модератор, который помогает поддерживать чистоту в чате.
    
    Что я умею:
    - Удалять сообщения с нецензурной лексикой
    - Фильтровать неприемлемые изображения
    - Проверять видео и GIF-анимации
    - Следить за стикерами
    
    Команды:
    /start - Запустить бота
    /help - Показать это сообщение
    /status - Проверить статус бота
    """
    await message.answer(help_text)

# Обработчик команды /status
@dp.message(Command("status"))
async def cmd_status(message: Message):
    logger.info(f"Пользователь {message.from_user.username} запросил статус")
    await message.answer("Бот активен и работает в режиме модерации.")

# Обработчик текстовых сообщений (не команд)
@dp.message(F.text & ~F.text.startswith('/'))
async def handle_text(message: Message):
    logger.info(f"Получено текстовое сообщение от {message.from_user.username}")
    if await is_inappropriate_text(message.text):
        try:
            # Удаляем неприемлемое сообщение
            await message.delete()
            # Отправляем предупреждение
            await message.answer(
                f"@{message.from_user.username}, ваше сообщение было удалено, так как оно содержит неприемлемый контент."
            )
            logger.info(f"Удалено неприемлемое текстовое сообщение от {message.from_user.username}")
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

# Обработчик изображений
@dp.message(F.photo)
async def handle_photo(message: Message):
    logger.info(f"Получено изображение от {message.from_user.username}")
    if message.photo:
        # Получаем информацию о файле (берем самое большое изображение)
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Формируем URL для скачивания файла
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Скачиваем файл
        image_data = await download_file(file_url)
        
        if image_data and await check_image_with_ai(image_data):
            try:
                # Удаляем неприемлемое изображение
                await message.delete()
                # Отправляем предупреждение
                await message.answer(
                    f"@{message.from_user.username}, ваше изображение было удалено, так как оно содержит неприемлемый контент."
                )
                logger.info(f"Удалено неприемлемое изображение от {message.from_user.username}")
            except Exception as e:
                logger.error(f"Ошибка при удалении изображения: {e}")

# Обработчик видео
@dp.message(F.video)
async def handle_video(message: Message):
    logger.info(f"Получено видео от {message.from_user.username}")
    if message.video.thumbnail:
        file_id = message.video.thumbnail.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Формируем URL для скачивания превью
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Скачиваем превью
        image_data = await download_file(file_url)
        
        if image_data and await check_video_with_ai(image_data):
            try:
                # Удаляем неприемлемое видео
                await message.delete()
                # Отправляем предупреждение
                await message.answer(
                    f"@{message.from_user.username}, ваше видео было удалено, так как оно может содержать неприемлемый контент."
                )
                logger.info(f"Удалено неприемлемое видео от {message.from_user.username}")
            except Exception as e:
                logger.error(f"Ошибка при удалении видео: {e}")

# Обработчик анимаций (GIF)
@dp.message(F.animation)
async def handle_animation(message: Message):
    logger.info(f"Получена анимация от {message.from_user.username}")
    if message.animation.thumbnail:
        file_id = message.animation.thumbnail.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Формируем URL для скачивания превью
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Скачиваем превью
        image_data = await download_file(file_url)
        
        if image_data and await check_video_with_ai(image_data):
            try:
                # Удаляем неприемлемую анимацию
                await message.delete()
                # Отправляем предупреждение
                await message.answer(
                    f"@{message.from_user.username}, ваша GIF-анимация была удалена, так как она может содержать неприемлемый контент."
                )
                logger.info(f"Удалена неприемлемая GIF-анимация от {message.from_user.username}")
            except Exception as e:
                logger.error(f"Ошибка при удалении GIF-анимации: {e}")

# Обработчик стикеров
@dp.message(F.sticker)
async def handle_sticker(message: Message):
    logger.info(f"Получен стикер от {message.from_user.username}")
    if message.sticker.thumbnail:
        file_id = message.sticker.thumbnail.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Формируем URL для скачивания превью
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Скачиваем превью
        image_data = await download_file(file_url)
        
        if image_data and await check_image_with_ai(image_data):
            try:
                # Удаляем неприемлемый стикер
                await message.delete()
                # Отправляем предупреждение
                await message.answer(
                    f"@{message.from_user.username}, ваш стикер был удален, так как он содержит неприемлемый контент."
                )
                logger.info(f"Удален неприемлемый стикер от {message.from_user.username}")
            except Exception as e:
                logger.error(f"Ошибка при удалении стикера: {e}")

# Обработчик для всех остальных типов сообщений
@dp.message()
async def handle_other(message: Message):
    logger.info(f"Получено сообщение другого типа от {message.from_user.username}")
    # Здесь можно добавить дополнительную логику для других типов сообщений

# Функция для установки команд бота
async def set_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="status", description="Проверить статус бота")
    ]
    await bot.set_my_commands(commands)

# Запуск бота
async def main():
    # Устанавливаем команды бота
    await set_commands()
    # Запускаем бота
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
