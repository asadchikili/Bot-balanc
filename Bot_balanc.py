import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="6321919673:AAGHMOh4UZmvRqu4P0J6CbREB_kD3Uc71cs")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Инициализация базы данных SQLite
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Создаем таблицу для хранения данных пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0.0
    )
''')
conn.commit()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    
    await message.reply("Добро пожаловать! Этот бот поможет вам управлять вашим банковским счетом.\n"
                        "Используйте /balance для проверки баланса, /transfer для перевода средств.")


# Обработчик команды /balance
@dp.message_handler(commands=['balance'])
async def balance_command(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    
    if result:
        balance = result[0]
        await message.reply(f"Ваш текущий баланс: {balance} руб.")
    else:
        await message.reply("У вас пока нет счета. Используйте /start для регистрации.")


# Обработчик команды /transfer
@dp.message_handler(commands=['transfer'])
async def transfer_command(message: types.Message):
    await message.reply("Введите сумму перевода:")
    dp.register_next_step_handler(message, process_transfer_step)


# Обработчик ввода суммы перевода
async def process_transfer_step(message: types.Message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        
        # Ваш код для обработки перевода средств, обновления баланса и уведомления пользователей
        
        await message.reply("Перевод выполнен успешно!")
    except ValueError:
        await message.reply("Введите корректную сумму.")


if __name__ == '__main__':
    from aiogram import executor

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
