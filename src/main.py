from telebot import types
from dotenv import load_dotenv
import os
import telebot
import database as d

load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

user = {'name': '', 'fname': ''}
keyboard_lessons = types.InlineKeyboardMarkup()
keyboard = types.InlineKeyboardMarkup()


@bot.message_handler(commands=['start'])
def start(message):
    if d.get_student(message.from_user.id) is None:
        bot.send_message(message.from_user.id, "Введи свое имя")
        bot.register_next_step_handler(message, register)
    else:
        bot.send_message(message.from_user.id, "Проверь уроки /check_lesson")


def register(message):
    user['name'] = message.text
    bot.send_message(message.from_user.id, "Введи свою фамилию")
    bot.register_next_step_handler(message, register_f)


def register_f(message):
    user['fname'] = message.text
    d.update_student(user['name'], user['fname'], str(message.chat.id))
    bot.send_message(message.from_user.id, "Регистрация окончена. Проверь уроки /check_lesson")


@bot.message_handler(commands=['check_lesson'])
def lessons(message):
    lis = list(d.get_lessons(message.from_user.id))
    keyboard_l = make_keyboard_lessons(lis)
    bot.send_message(message.from_user.id, text='Выбери урок', reply_markup=keyboard_l)


def make_keyboard_lessons(lis):
    keyboard_lessons = types.InlineKeyboardMarkup()
    for i in lis:
        key = types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'номер {i[0]}')
        keyboard_lessons.add(key)
    return keyboard_lessons


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global keyboard
    if call.data[:5] == 'номер':
        keyboard = types.InlineKeyboardMarkup()
        lesson = d.get_lesson(call.data[6:len(call.data)], call.message.chat.id)
        for i in lesson:
            key = types.InlineKeyboardButton(text=f'{i}', callback_data=f'{i} {lesson[i]}')
            keyboard.add(key)
        key = types.InlineKeyboardButton(text='назад', callback_data='>')
        keyboard.add(key)
        bot.edit_message_text(text='Информация с урока', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    if call.data[:4] == 'тема':
        topic = d.get_topic(call.data[5:len(call.data)])
        bot.edit_message_text(text=f'Название: {topic["название"]}\nОписание: '
                                   f'{topic["описание"]}\nФункции: {topic["функции"]}',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data[:16] == 'домашнее задание':
        topic = d.get_homework(call.data[17:len(call.data)])
        bot.edit_message_text(text=f'Описание: {topic["описание"]}', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data == '>':
        lis = list(d.get_lessons(call.message.chat.id))
        bot.edit_message_text(text='Выбери урок', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=make_keyboard_lessons(lis))


bot.polling(non_stop=True)
