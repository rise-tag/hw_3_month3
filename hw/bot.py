import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import TOKEN
import database

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатуры
buttons = [
    [KeyboardButton(text='Добавить задачу')],
    [KeyboardButton(text='Посмотреть задачи')],
    [KeyboardButton(text='Удалить задачу')]
]

keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Команда /start
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.reply("Привет! Я бот для управления задачами. Используй команду /add, чтобы добавить задачу, /view — чтобы посмотреть все задачи, и /delete — чтобы удалить задачу.", reply_markup=keyboard)

# Команда /add
@dp.message(Command('add'))
async def add(message: types.Message):
    await message.reply("Введите текст задачи.")

@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введите текст задачи.")
async def process_task(message: types.Message):
    user_id = message.from_user.id
    task_text = message.text
    database.add_task(user_id, task_text)
    await message.reply("Задача добавлена!")

# Команда /view
@dp.message(Command('view'))
async def view(message: types.Message):
    user_id = message.from_user.id
    tasks = database.get_tasks(user_id)
    
    if tasks:
        response = "Ваши задачи:\n"
        for task in tasks:
            response += f"{task[0]}. {task[1]}\n"
    else:
        response = "У вас нет задач."
    
    await message.reply(response)

# Команда /delete
@dp.message(Command('delete'))
async def delete(message: types.Message):
    user_id = message.from_user.id
    tasks = database.get_tasks(user_id)
    
    if tasks:
        response = "Выберите номер задачи для удаления:\n"
        for task in tasks:
            response += f"{task[0]}. {task[1]}\n"
        await message.reply(response)
        await message.reply("Введите номер задачи для удаления.")
    else:
        await message.reply("У вас нет задач для удаления.")

@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text.startswith("Выберите номер задачи"))
async def process_delete(message: types.Message):
    user_id = message.from_user.id
    try:
        task_id = int(message.text)
        database.delete_task(user_id, task_id)
        await message.reply("Задача удалена!")
    except ValueError:
        await message.reply("Некорректный номер задачи. Попробуйте снова.")

async def main():
    database.create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
