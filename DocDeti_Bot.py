print ("Hello, world!")
# Импорт необходимых библиотек
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
from aiosqlite import connect  # Для асинхронной работы с SQLite

# Инициализация базы данных
async def init_db():
    """Создаем подключение к БД и таблицу users, если её нет"""
    async with connect('bot_database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с сохранением пользователя в БД"""
    user = update.effective_user  # Получаем информацию о пользователе
    try:
        async with connect('bot_database.db') as db:
            # Добавляем пользователя, если его еще нет в БД
            await db.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user.id, user.username, user.first_name, user.last_name))
            await db.commit()
        
        await update.message.reply_text(f"Привет, {user.first_name}! Я запомнил тебя в базе данных.")
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        await update.message.reply_text("Произошла ошибка при работе с базой данных")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - начало работы\n"
        "/help - помощь\n"
        "/stats - статистика бота"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats для показа статистики"""
    try:
        async with connect('bot_database.db') as db:
            # Получаем общее количество пользователей
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            total_users = await cursor.fetchone()
            
            # Получаем общее количество сообщений
            cursor = await db.execute('SELECT SUM(message_count) FROM users')
            total_messages = await cursor.fetchone()
        
        await update.message.reply_text(
            f"📊 Статистика бота:\n"
            f"👥 Пользователей: {total_users[0]}\n"
            f"✉️ Всего сообщений: {total_messages[0] if total_messages[0] else 0}"
        )
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        await update.message.reply_text("Не удалось получить статистику")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с подсчетом сообщений"""
    user = update.effective_user
    try:
        async with connect('bot_database.db') as db:
            # Увеличиваем счетчик сообщений пользователя
            await db.execute('''
                UPDATE users 
                SET message_count = message_count + 1 
                WHERE user_id = ?
            ''', (user.id,))
            await db.commit()
        
        await update.message.reply_text(f"Вы написали: {update.message.text}")
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        await update.message.reply_text(update.message.text)  # Отправляем эхо без учета в БД

async def main():
    """Основная функция инициализации и запуска бота"""
    await init_db()  # Инициализируем БД перед запуском
    
    # Создаем приложение бота с токеном
    application = Application.builder().token("8111740535:AAEzEBWQI0rFAdR4gjIGS2SghOOe7oN4L1U").build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Добавляем обработчик обычных текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота в режиме опроса
    await application.run_polling()

if __name__ == "__main__":
    # Запускаем асинхронную main функцию
    import asyncio
    asyncio.run(main())