import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# ===== Конфигурация =====

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Белый список пользователей
ALLOWED_USERS = set(map(int, os.getenv("WHITELIST", "").split(",")))

# ===== Проверка доступа =====
def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# ===== Обработчики команд =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text(f"⛔ Доступ c userID:{user_id} запрещён.\nОбратитесь к администратору. ")
        return
    await update.message.reply_text(f"✅ Привет, {update.effective_user.first_name}! \nuserID: {update.effective_user.id}")

async def secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text(f"⛔ Доступ c userID:{user_id} запрещён.\nОбратитесь к администратору. ")
        return
    await update.message.reply_text("🤫 Это секретная команда только для избранных!")

# ===== Запуск бота =====
def main():
    if not TOKEN:
        raise ValueError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("secret", secret))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
