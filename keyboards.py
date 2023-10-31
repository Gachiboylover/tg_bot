from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_keyboard():
    reply_keyboard = ReplyKeyboardBuilder()
    reply_keyboard.button(text='/write_training')
    reply_keyboard.button(text='/del_training')
    reply_keyboard.button(text='/help')
    reply_keyboard.button(text='/show_all')
    reply_keyboard.adjust(2, 1, 1)
    return reply_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

def reply_keyboard_answer():
    reply_keyboard = ReplyKeyboardBuilder()
    reply_keyboard.button(text='Да')
    reply_keyboard.button(text='Нет')
    reply_keyboard.adjust(2)
    return reply_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)