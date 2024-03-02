import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import sqlite3
from config import token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        balance REAL DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS transfers (
        transfer_id INTEGER PRIMARY KEY,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(sender_id) REFERENCES users(user_id),
        FOREIGN KEY(receiver_id) REFERENCES users(user_id)
    )
''')

conn.commit()

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для управления банковским счетом. Используй /balance, /transfer и другие команды.")


@dp.message_handler(commands=['balance'])
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
        await message.answer(f"Ваш текущий баланс: {balance} рублей.")
    else:
        await message.answer("У вас нет счета. Используйте /start для регистрации.")


@dp.message_handler(commands=['transfer'])
async def cmd_transfer(message: types.Message):
    await message.answer("Введите сумму перевода:")
    await RegisterUserStates.waiting_for_amount.set()


@dp.message_handler(state=RegisterUserStates.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("Введите ID получателя:")
        await RegisterUserStates.waiting_for_receiver.set()
    except ValueError:
        await message.answer("Некорректная сумма. Пожалуйста, введите число.")


@dp.message_handler(state=RegisterUserStates.waiting_for_receiver)
async def process_receiver(message: types.Message, state: FSMContext):
    receiver_id = int(message.text)
    sender_id = message.from_user.id
    amount = (await state.get_data()).get('amount')

    cursor.execute('INSERT INTO transfers (sender_id, receiver_id, amount) VALUES (?, ?, ?)', (sender_id, receiver_id, amount))
    cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, sender_id))
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, receiver_id))
    conn.commit()

    await message.answer(f"Перевод успешно выполнен. Сумма: {amount} рублей. Получатель: {receiver_id}")


    await state.finish()


if __name__ == '__main__':
    from aiogram import executor
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    from aiogram.dispatcher import FSMContext
    from aiogram.dispatcher.filters.state import State, StatesGroup

    class RegisterUserStates(StatesGroup):
        waiting_for_amount = State()
        waiting_for_receiver = State()

    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, skip_updates=True)
