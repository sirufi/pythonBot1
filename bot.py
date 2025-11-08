import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# -------------------------------------------------
#  Настройка окружения и логирования
# -------------------------------------------------
load_dotenv()  # .env должен лежать в корне проекта
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Не найден BOT_TOKEN в переменных окружения (.env)")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------------------------------
#  Хэндлеры
# -------------------------------------------------
async def handle_start(message: types.Message) -> None:
    """Стартовое приветствие с кнопкой"""
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="📂 Получить таблицу", callback_data="get_table")
    )
    await message.answer(
        "Привет! Я бот, который выдаёт таблицу после подтверждения оплаты.",
        reply_markup=keyboard
    )

async def handle_get_table(callback: types.CallbackQuery) -> None:
    """Инструкция пользователю после нажатия кнопки"""
    await callback.message.answer(
        "Отправь сюда скриншот оплаты 📸\nПосле этого я пришлю тебе таблицу."
    )
    await callback.answer()  # закрывает «часики» на кнопке

async def handle_payment_screenshot(message: types.Message) -> None:
    """Получает скриншот и отправляет таблицу"""
    file_path = "table.xlsx"
    if not os.path.exists(file_path):
        await message.answer("⚠️ Файл таблицы не найден. Сообщи администратору.")
        return

    await message.answer_document(
        types.InputFile(file_path),
        caption="Спасибо за оплату! Вот твоя таблица 📊"
    )

async def handle_non_photo(message: types.Message) -> None:
    """Если прислали не фото"""
    await message.answer("Пришли, пожалуйста, скриншот оплаты 📷")

# -------------------------------------------------
#  Точка входа
# -------------------------------------------------
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хэндлеров
    dp.message.register(handle_start, CommandStart())
    dp.callback_query.register(handle_get_table, lambda c: c.data == "get_table")
    dp.message.register(
        handle_payment_screenshot,
        lambda message: message.content_type == types.ContentType.PHOTO
    )
    dp.message.register(handle_non_photo)  # fallback

    logging.info("🤖 Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())