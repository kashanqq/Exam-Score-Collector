import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F 
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_subjects_keyboard, get_main_keyboard, AVAILABLE_SUBJECTS
from states import RegState, ScoreState

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# СТАРТ И МЕНЮ (я не стал разделять на файлы роутеров т.к тут не много команд)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Йо! Я бот для баллов ЕГЭ.\nЖми кнопку ниже или /register, если ты тут впервые.",
        reply_markup=get_main_keyboard()
    )


# РЕГИСТРАЦИЯ
@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    await message.answer("Введите Имя и Фамилию через пробел:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegState.waiting_for_name)

@dp.message(RegState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        first, last = message.text.split()
        async with aiohttp.ClientSession() as session:
            payload = {"telegram_id": message.from_user.id, "first_name": first, "last_name": last}
            async with session.post(f"{API_URL}/register/", json=payload) as resp:
                if resp.status == 200:
                    await message.answer("Успешно зарегистрирован!", reply_markup=get_main_keyboard())
                elif resp.status == 400: # Обычно 400 возвращают, если юзер уже есть, но в нашем API пока 200 с msg
                     await message.answer("Ты уже зарегистрирован.", reply_markup=get_main_keyboard())
                else:
                    await message.answer("Ошибка на сервере.", reply_markup=get_main_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("Нужно два слова: Имя Фамилия.")

# ВВОД БАЛЛОВ

# Срабатывает ИЛИ на команду /enter_scores, ИЛИ на кнопку с текстом "📝 Ввести баллы"
@dp.message(Command("enter_scores"))
@dp.message(F.text == "📝 Ввести баллы") 
async def cmd_enter_scores(message: types.Message, state: FSMContext):
    await message.answer(
        "Выбери предмет из списка:", 
        reply_markup=get_subjects_keyboard()
    )
    await state.set_state(ScoreState.waiting_for_subject)

@dp.message(ScoreState.waiting_for_subject)
async def process_subject(message: types.Message, state: FSMContext):
    subject = message.text
    
    # --- ВАЛИДАЦИЯ ---
    if subject not in AVAILABLE_SUBJECTS:
        await message.answer(
            "Пожалуйста, выбери предмет, используя кнопки внизу. Я не знаю такого предмета.",
            reply_markup=get_subjects_keyboard() # Возвращаем кнопки, если не допустимый ввод
        )
        return


    await state.update_data(subject=subject)
 
    await message.answer(
        f"Отлично, {subject}. Теперь введи балл (0-100):", 
        reply_markup=types.ReplyKeyboardRemove() 
    )
    await state.set_state(ScoreState.waiting_for_score)

@dp.message(ScoreState.waiting_for_score)
async def process_score(message: types.Message, state: FSMContext):
    try:
        score = int(message.text)
        if not (0 <= score <= 100):
            await message.answer("Балл должен быть от 0 до 100.")
            return
    except ValueError:
        await message.answer("Нужно ввести число!")
        return

    data = await state.get_data()
    subject = data['subject']
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "telegram_id": message.from_user.id,
            "subject": subject,
            "score": score
        }
        async with session.post(f"{API_URL}/scores/", json=payload) as resp:
            if resp.status == 200:
                # После успеха возвращаем Главное Меню
                await message.answer(f"Записал! {subject}: {score}", reply_markup=get_main_keyboard())
            else:
                await message.answer("Ошибка сохранения :(", reply_markup=get_main_keyboard())
    
    await state.clear()

# ПРОСМОТР БАЛЛОВ
@dp.message(Command("view_scores"))
@dp.message(F.text == "📊 Мои баллы")
async def view_scores(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/scores/{message.from_user.id}") as resp:
            data = await resp.json()
            if not data:
                await message.answer("Баллов пока нет или ты не зареган.", reply_markup=get_main_keyboard())
            else:
                text = "\n".join([f"• {item['subject']}: {item['score']}" for item in data])
                await message.answer(f"Твои результаты:\n{text}", reply_markup=get_main_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())