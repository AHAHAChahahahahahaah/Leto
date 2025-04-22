import logging
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from zoneinfo import ZoneInfo  # Используем zoneinfo вместо pytz

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = '7799105036:AAFjUNuNKKcqTZVoYzCW9mLipv8CKZjQ1_U'

# Глобальный список chat_id, куда бот будет отправлять сообщения
active_chats = set()

# Функция для расчета дней до начала лета (1 июня)
def days_until_summer():
    now = datetime.now(ZoneInfo('Asia/Yekaterinburg'))  # Используем ZoneInfo
    summer_start = datetime(now.year, 6, 1, tzinfo=ZoneInfo('Asia/Yekaterinburg'))
    if now > summer_start:
        summer_start = datetime(now.year + 1, 6, 1, tzinfo=ZoneInfo('Asia/Yekaterinburg'))
    return (summer_start - now).days

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    active_chats.add(chat_id)  # Добавляем chat_id в список активных чатов
    await update.message.reply_text('Привет! Я буду сообщать количество дней до начала лета каждый день. Также вы можете использовать команду /days, чтобы узнать количество дней до лета в любое время.')

# Команда /days
async def days(update: Update, context: ContextTypes.DEFAULT_TYPE):
   chat_id = update.message.chat_id
    days = days_until_summer()
    await update.message.reply_text(f'До начала лета осталось {days} дней!')

# Функция для отправки сообщения
async def send_days_remaining(context: ContextTypes.DEFAULT_TYPE):
    days = days_until_summer()
    for chat_id in active_chats:  # Отправляем сообщение во все активные чаты
        try:
            await context.bot.send_message(chat_id=chat_id, text=f'До начала лета осталось {days} дней!')
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик команды /days
    application.add_handler(CommandHandler("days", days))

    # Планирование ежедневного сообщения
    job_queue = application.job_queue
    job_queue.run_daily(send_days_remaining, time=time(0, 0, 0, tzinfo=ZoneInfo('Asia/Yekaterinburg')))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
