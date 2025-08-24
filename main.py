import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# --- загрузка настроек ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WHITELIST = set(map(int, os.getenv("WHITELIST", "").split(",")))

# --- логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- инициализация ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Middleware для проверки доступа ---
class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id

        # если ID найден и он не в whitelist → ответ-заглушка
        if user_id and user_id not in WHITELIST:
            await event.answer("⛔ У вас нет доступа к этому боту.")
            return  # прерываем обработку

        # иначе пропускаем дальше
        return await handler(event, data)


# --- подключаем middleware ---
dp.message.middleware(AccessMiddleware())

# --- хендлеры ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Команды:\n/start\n/help\n/ping")

@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("pong")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Вы сказали: {message.text}")

# --- запуск вебхука ---
async def on_startup(app: web.Application):
    # установка вебхука
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info("Webhook установлен.")

async def on_shutdown(app: web.Application):
    # удаление вебхука при выключении
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Webhook удален.")

def main():
    app = web.Application()
    # подключение aiogram к aiohttp
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # запуск aiohttp
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
