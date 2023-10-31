from aiogram import Bot
from aiogram.types import Message, BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Старт.'
        ),
        BotCommand(
            command='help',
            description='Узнай функционал бота.'
        ),
        BotCommand(
            command='write_training',
            description='Запиши треню.'
        ),
        BotCommand(
            command='del_training',
            description='Удали треню, если она отменилась.'
        ),
        BotCommand(
            command='show_all',
            description='Посмотри, какие трени записаны.'
        )
    ]