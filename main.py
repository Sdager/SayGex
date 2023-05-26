import requests
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "5518007240:AAG5bhuqXZ6OR_P3-mx-lEriV7Xj1W1ql6U"

HELP_COMMAND = """
/help - список команд
/go - Запускает поиск вакансий
/start - запуск бота 
"""


kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton('/go'))
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await  bot.send_message(chat_id=message.from_user.id, text=HELP_COMMAND)
    await message.delete()

@dp.message_handler(commands=['start'])
async def send_kb(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Приветствую тебя, мой дорогой друг! Дай угадаю... Ты очень хочешь найти работу по своему профилю? Ну это логично, если бы это было не так, то ты бы меня не запускал:) Итак, давай познакомимся. Я чат-бот, который помогает найти работу по профилю. Напиши /go чтобы запустить бота')
    await bot.send_sticker(message.from_user.id,
                           sticker="CAACAgIAAxkBAAEJDj9kanDzXnPoDB5nm2eiqAYaPpI-swACmAADe04qEIuj2sf-GJuLLwQ",
                           reply_markup=kb)
    await message.delete()

class UserState(StatesGroup):
    name = State()

@dp.message_handler(commands=['go'])
async def user_register(message: types.Message):
    await message.answer("Введите вакансию")
    await UserState.name.set()

@dp.message_handler(state=UserState.name)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": data['username'],
        "area": 1,
        "per_page": 15
    }
    headers = {
        "User-Agent": "Your User Agent"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        for vacancy in vacancies:
            # Extract relevant information from the vacancy object
            vacancy_id = vacancy.get("id")
            vacancy_title = vacancy.get("name")
            vacancy_url = vacancy.get("alternate_url")
            experience = vacancy.get("experience", {}).get("name")
            company_name = vacancy.get("employer", {}).get("name")
            await message.answer(f"ID: {vacancy_id}\nНазвание: {vacancy_title}\nКомпания: {company_name}\nСсылка: {vacancy_url}\nОпыт: {experience}")
    else:
        await message.answer(f"Request failed with status code: {response.status_code}")

    await message.answer(f"Для повторного ввода снова напишите /go")
    await bot.send_sticker(message.from_user.id,
                            sticker="CAACAgIAAxkBAAEJFzJkbgJ0IyUWkqN4kRp87TFdxMLPJgACtx0AAs3DcUufHIdPsHPh6S8E",
                            reply_markup=kb)

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)