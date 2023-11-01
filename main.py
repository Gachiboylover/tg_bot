from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date
import json
import asyncio

import commands
import keyboards
import bot_data

def user_format(training):
    training = training.split()
    date = training[0].split('-')
    d = '%s.%s.%s' % (date[2], date[1], date[0])
    time = training[1].split(':')
    t = '%s:%s' % (time[0], time[1])
    return d+' '+t+' '+training[2]


def check_in(training):
    training = training.split()
    try:
        valid_date = datetime.strptime(training[0], '%d.%m.%Y').date()
        valid_time = datetime.strptime(training[1], '%H:%M').time()
        return (valid_date - date.today()).days >= 0
    except Exception:
        return False
    
    
def right_format(training):
    training = training.split()
    d = str(datetime.strptime(training[0], '%d.%m.%Y').date())
    t = str(datetime.strptime(training[1], '%H:%M').time())
    return d + ' ' + t + ' ' + training[2]


class StepsForm(StatesGroup):
    GET_ANSWER = State()
    GET_FLAG = State()
    GET_DEL_ANSWER = State()
    GET_DEL_FLAG = State()
    
async def start_bot(bot: Bot):
    await bot_data.db_connect()
    await commands.set_commands(bot)
    await bot.send_message(1744005453, f'Бот запущен.')
    
    
async def shutdown_bot(bot: Bot):
    await bot.send_message(1744005453, f'Бот остановлен.')


async def get_start(message: Message, bot: Bot):
    await bot_data.db_write_user(message.from_user.id)
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}.', reply_markup=keyboards.reply_keyboard())


async def show_all(message: Message, bot: Bot):
    trainings = await bot_data.db_show_all(message.from_user.id)
    await bot.send_message(message.from_user.id, '\n'.join(user_format(i[0]) for i in trainings))


async def get_help(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}. Этот бот создан для таго, чтобы ты мог записывать сюда свои трени, а он в свою очередь будет тебе о них напоминать.\n"write-training" - запись трени.\n"del-training" - удалить треню.\n"show_all" - просмотр всех записаных трень.', reply_markup=keyboards.reply_keyboard())


async def get_training(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'{message.from_user.first_name}, введите данные вида: 28.02.2007 01:00 428А.')
    await state.set_state(StepsForm.GET_FLAG)       


async def get_training_flag(message: Message, bot: Bot, state: FSMContext):
    try:
        if check_in(message.text):
            await bot.send_message(message.from_user.id, f'{message.text} Вы уверены?', reply_markup=keyboards.reply_keyboard_answer())
            await state.set_state(StepsForm.GET_ANSWER)
            await state.update_data(name=message.text)
        else:
            await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ')
            await state.clear()   
    except Exception:
        await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ')
        await state.clear()     

async def get_training_answer(message: Message, bot: Bot, state: FSMContext):
    if message.text == 'Да':
        context_data = await state.get_data()
        await bot_data.db_write_training(message.from_user.id, right_format(context_data.get("name")))
        await bot.send_message(message.from_user.id, f'{context_data.get("name")} записана.')
        await state.clear()


async def del_training(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'{message.from_user.first_name}, введите данные вида: 28.02.2007 01:00 428А.')
    await state.set_state(StepsForm.GET_DEL_FLAG)
    
    
async def del_training_flag(message: Message, bot: Bot, state: FSMContext):
    try:
        if check_in(message.text):
            await bot.send_message(message.from_user.id, f'{message.text} Вы уверены?', reply_markup=keyboards.reply_keyboard_answer())
            await state.set_state(StepsForm.GET_DEL_ANSWER)
            await state.update_data(name=message.text)
        else:
            await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ')
            await state.clear()       
    except Exception:
        await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ')
        await state.clear()   

async def del_training_answer(message: Message, bot: Bot, state: FSMContext):
    if message.text == 'Да':
        context_data = await state.get_data()
        await bot_data.db_del_training(message.from_user.id, right_format(context_data.get("name")))
        await bot.send_message(message.from_user.id, f'{context_data.get("name")} удалена.' )
        await state.clear()



async def send_remind_cron(bot: Bot):
    all_id = await bot_data.db_get_all_id()
    for i in all_id:
        trainings = await bot_data.db_show_all(i[0])
        trainings = t[0] for t in trainings if (date.fromisoformat(t[0].split()[0]) - date.today()).days == 0
        await bot.send_message(i[0], '\n'.join(user_format(t[0]) for t in trainings)
        await bot_data.db_del_old(trainings, i[0])
    
    
async def start():
    bot = Bot(token=':)')
    
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(send_remind_cron, trigger='cron', hour = datetime.now().hour, minute = datetime.now().minute + 1, kwargs={'bot': bot})
    scheduler.start()
    
    dp = Dispatcher()
    dp.startup.register(start_bot)
    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(get_help, Command(commands=['help']))
    dp.message.register(get_training, Command(commands=['write_training']))
    dp.message.register(get_training_flag, StepsForm.GET_FLAG)
    dp.message.register(get_training_answer, StepsForm.GET_ANSWER)
    dp.message.register(del_training, Command(commands=['del_training']))
    dp.message.register(del_training_flag, StepsForm.GET_DEL_FLAG)
    dp.message.register(del_training_answer, StepsForm.GET_DEL_ANSWER)
    dp.message.register(show_all, Command(commands=['show_all']))
    dp.shutdown.register(shutdown_bot)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        
if __name__ == '__main__':
    asyncio.run(start())
