import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import gspread
import time
import asyncio
import aiohttp
from treelib import Tree, Node
import os

from create_tree import create_tree
from settings import *
from google_drive_provider import drive


RNC_bot = AsyncTeleBot(BOT_TOKEN)
# подключение к google drive
gc = gspread.service_account(filename=SERVICE_ACCOUNT_CREDENTIALS_FILE)
sh = gc.open(GOOGLE_TABLE)


class ContextHolder:
    old_command = {}
    tree = Tree()
    last_upd_time = ''


# init
worksheet = sh.sheet1
ContextHolder.last_upd_time = worksheet.spreadsheet.lastUpdateTime
ContextHolder.tree = create_tree(worksheet)


# Сравнение времени последнего обновления файла
async def tree_refresh():
    while True:
        worksheet = gc.open(GOOGLE_TABLE).sheet1
        last_time = worksheet.spreadsheet.lastUpdateTime
        if ContextHolder.last_upd_time != last_time:
            ContextHolder.last_upd_time = last_time
            ContextHolder.tree = create_tree(worksheet)
        await asyncio.sleep(WORKSHEET_REFRESH_INTERVAL)


def create_buttons(id):
    return list(map(lambda item: KeyboardButton(item),
                       [f'{ContextHolder.tree.get_node(i).tag}' for i in
                        ContextHolder.tree.is_branch(id)]))


# Приветствие
@RNC_bot.message_handler(commands=['start'])
async def welcome(message):
    WelcomeSticker = open('welcome.webp', 'rb')
    await RNC_bot.send_sticker(message.chat.id, WelcomeSticker)
    WelcomeMessage = f"Добро пожаловать, {message.from_user.first_name}! \nЯ <b>ИРИСКА</b>, бот практики <b>RnC</b>.\nО какой <b>индустрии</b> тебе подсказать?"
    ContextHolder.old_command[message.chat.id] = ['root']
    buttons = create_buttons('root')
    await RNC_bot.send_message(message.chat.id, WelcomeMessage, parse_mode='html',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))


# Выбор
@RNC_bot.message_handler(content_types=['text'])
async def data_info(message):
    if message.chat.type == 'private':
        if message.chat.id in ContextHolder.old_command:
            # Заполняем дикт и получаем id очередного узла
            ContextHolder.old_command[message.chat.id].append(message.text)
            print(ContextHolder.old_command)
            nid = '_'.join(ContextHolder.old_command[message.chat.id])
            print(ContextHolder.tree.get_node(nid))
            # Обрабатываем неизвестные команды
            if ContextHolder.tree.contains(nid) == False and message.text != "↩ В начало":
                ContextHolder.old_command[message.chat.id] = ['root']
                buttons = create_buttons('root')
                await RNC_bot.send_message(message.chat.id,
                                           "Прости, такой информации нет, давай вернемся к выбору индустрии!",
                                           parse_mode='html',
                                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
            # Индустрия
            elif nid in [ContextHolder.tree.get_node(i).identifier for i in ContextHolder.tree.is_branch('root')]:
                buttons = create_buttons(nid)
                buttons.append(KeyboardButton("↩ В начало"))
                await RNC_bot.send_message(message.chat.id,
                                           f"Хорошо, поговорим про {message.text}. Какое направление интересно?",
                                           parse_mode='html',
                                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
            # В начало
            elif message.text == "↩ В начало":
                ContextHolder.old_command[message.chat.id] = ['root']
                buttons = create_buttons('root')
                await RNC_bot.send_message(message.chat.id, "Вернемся к выбору индустрии", parse_mode='html',
                                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
            # Направление
            elif ContextHolder.tree.level(nid) == 2:
                buttons = create_buttons(nid)
                buttons.append(KeyboardButton("↩ В начало"))
                await RNC_bot.send_message(message.chat.id, f"Какие кейсы из {message.text} тебя интересуют?",
                                           parse_mode='html',
                                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
            # Кейсы
            elif ContextHolder.tree.level(nid) == 3:
                buttons = create_buttons(nid)
                buttons.append(KeyboardButton("↩ В начало"))
                await RNC_bot.send_message(message.chat.id, f"Что по данным кейса тебе необходимо узнать?",
                                           parse_mode='html',
                                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
            # Все информация о кейсах
            elif ContextHolder.tree.level(nid) == 4:
                ContextHolder.old_command[message.chat.id].pop()
                nid_prev_node = '_'.join(ContextHolder.old_command[message.chat.id])
                print(nid_prev_node)
                buttons = create_buttons(nid_prev_node)
                buttons.append(KeyboardButton("↩ В начало"))
                message_text = ContextHolder.tree.get_node(nid).data
                if ContextHolder.tree.get_node(nid).tag == 'Ссылка на PDF с презентацией':
                    if ContextHolder.tree.get_node(nid).data != 'Ссылка отсутствует':
                        url_id = ContextHolder.tree.get_node(nid).data.split('/')[5]
                        #url_id = url_id.split('/')[5]
                        file6 = drive.CreateFile({'id': url_id})
                        file6.GetContentFile(f'./{ContextHolder.tree.get_node(nid_prev_node).tag}_{message.chat.id}.pdf')
                        Pres = open(f'./{ContextHolder.tree.get_node(nid_prev_node).tag}_{message.chat.id}.pdf', 'rb')
                        await RNC_bot.send_document(message.chat.id, Pres)
                        os.remove(f'./{ContextHolder.tree.get_node(nid_prev_node).tag}_{message.chat.id}.pdf')
                        message_text = 'А вот и презентация!'
                    else:
                        message_text = 'Прости, презентацию пока не добавили('
                await RNC_bot.send_message(message.chat.id, message_text, parse_mode='html',
                                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))
        # Обрабатываем неверные команды
        else:
            ContextHolder.old_command[message.chat.id] = ['root']
            buttons = create_buttons('root')
            await RNC_bot.send_message(message.chat.id, "Начнем сначала и вернемся к выбору индустрии!",
                                       parse_mode='html',
                                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(tree_refresh())
    loop.create_task(RNC_bot.polling(none_stop=True))
    loop.run_forever()
