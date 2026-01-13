from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Список допустимых предметов
AVAILABLE_SUBJECTS = ["Математика", "Русский язык", "Информатика", "Физика", "Английский язык", "Химия"]

def get_subjects_keyboard():
    builder = ReplyKeyboardBuilder()
    for subject in AVAILABLE_SUBJECTS:
        builder.button(text=subject)
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выбери предмет")

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Ввести баллы")
    builder.button(text="📊 Мои баллы")
    
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Что будем делать?")