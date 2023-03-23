import time

from telebot import types
from dotenv import load_dotenv
import os
import telebot
import database as d

load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

keyboard_lessons = types.InlineKeyboardMarkup()
keyboard = types.InlineKeyboardMarkup()
keyboard_admin = types.InlineKeyboardMarkup()
st_id = 0


@bot.message_handler(commands=['start'])
def start(message):
    if d.get_student(message.from_user.id) is None and d.get_teacher_by_tid(message.from_user.id) is None \
            and d.get_parent_by_tid(message.from_user.id) is None:
        bot.send_message(message.from_user.id, "Введи свое имя и фамилию через пробел")
        bot.register_next_step_handler(message, register)
    else:
        if d.get_student(message.from_user.id) is not None or d.get_parent_by_tid(message.from_user.id) is not None:
            bot.send_message(message.from_user.id, "Проверь уроки /check_lesson")
        elif d.get_teacher_by_tid(message.from_user.id) is not None:
            bot.send_message(message.from_user.id, "Проверь уроки /admin")


def register(message):
    user = message.text.split(' ')
    if d.get_id(user[0], user[1]) is not None:
        d.update_student(user[0], user[1], str(message.chat.id))
        bot.send_message(message.from_user.id, "Регистрация окончена. Проверь уроки /check_lesson")
    elif d.get_teacher(user[0], user[1]) is not None:
        d.update_teacher(user[0], user[1], str(message.chat.id))
        bot.send_message(message.from_user.id, "Регистрация окончена. Проверь уроки /admin")
    elif d.get_parent(user[0], user[1]) is not None:
        d.update_parent(user[0], user[1], str(message.chat.id))
        bot.send_message(message.from_user.id, "Регистрация окончена. Проверь уроки /check_lesson")
    else:
        bot.send_message(message.from_user.id, "Я не нашел тебя в базе")
        start(message)


@bot.message_handler(commands=['check_lesson'])
def lessons(message):
    if d.get_student(message.from_user.id) is not None:
        lis = list(d.get_lessons(t_id=message.from_user.id))
        keyboard_lessons = make_keyboard_lessons(lis)
        bot.send_message(message.from_user.id, text='Выбери урок', reply_markup=keyboard_lessons)
    elif d.get_parent_by_tid(message.from_user.id) is not None:
        lis = list(d.get_lessons(t_id=d.find_student(message.from_user.id)))
        keyboard_lessons = make_keyboard_lessons(lis)
        bot.send_message(message.from_user.id, text='Выбери урок', reply_markup=keyboard_lessons)


def lessons_for_teacher(message, info):
    global st_id
    lis = list(d.get_lessons(student_id=info[5:len(info)]))
    keyboard_lessons = make_keyboard_lessons(lis)
    st_id = info[5:len(info)]
    bot.send_message(message.chat.id, text='Выбери урок', reply_markup=keyboard_lessons)


def make_keyboard_lessons(lis):
    lis.sort()
    keyboard_l = types.InlineKeyboardMarkup()
    for i in lis:
        key = types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'номер {i[0]}')
        keyboard_l.add(key)
    return keyboard_l


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global keyboard
    if call.data[:5] == 'номер':
        keyboard = types.InlineKeyboardMarkup()
        if d.get_student(call.message.chat.id) is not None or d.get_parent_by_tid(call.message.chat.id) is not None:
            lesson = d.get_lesson(n=call.data[6:len(call.data)], t_id=call.message.chat.id)
        else:
            lesson = d.get_lesson(n=call.data[6:len(call.data)], user=st_id)
        for i in lesson:
            key = types.InlineKeyboardButton(text=f'{i}', callback_data=f'{i} {lesson[i]}')
            keyboard.add(key)
        key = types.InlineKeyboardButton(text='<-', callback_data='>')
        keyboard.add(key)
        bot.edit_message_text(text='Информация с урока', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data[:4] == 'тема':
        topic = d.get_topic(call.data[5:len(call.data)])
        bot.edit_message_text(text=f'Название: {topic["название"]}\nОписание: '
                                   f'{topic["описание"]}\nФункции: {topic["функции"]}',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data[:16] == 'домашнее задание':  # исправить для учителя
        topic = d.get_homework(call.data[17:len(call.data)])
        bot.edit_message_text(text=f'Описание: {topic["описание"]}', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data == '>':
        if d.get_student(call.message.chat.id) is not None or d.get_parent_by_tid(call.message.chat.id) is not None:
            lis = list(d.get_lessons(t_id=call.message.chat.id))
        else:
            lis = list(d.get_lessons(student_id=st_id))
        lis.sort()
        bot.edit_message_text(text='Выбери урок', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=make_keyboard_lessons(lis))
    elif call.data[:4] == "урок":
        update_lessons(call.message, call.data[5:len(call.data)])
    elif call.data[:4] == "инфо":
        lessons_for_teacher(call.message, call.data)
    elif int(call.data) in list(d.find_students_by_teacher(call.message.chat.id).keys()):
        keyboard_admin = types.InlineKeyboardMarkup()
        keyboard_admin.add(types.InlineKeyboardButton(text="Добавить информацию об уроке", callback_data=f'урок {int(call.data)}'),
                           types.InlineKeyboardButton(text="Показать информацию об уроках", callback_data=f'инфо {int(call.data)}'))
        bot.edit_message_text(text="Выбери действие", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard_admin)


@bot.message_handler(commands=['admin'])
def send_commands_for_teachers(message):
    lst = d.find_students_by_teacher(message.chat.id)
    bt_lst = []
    keyboard_admin = types.InlineKeyboardMarkup()
    for i in range(1, len(lst) + 1, 3):
        for j in range(i, i + 3):
            try:
                key = types.InlineKeyboardButton(text=lst[j], callback_data=j)
                bt_lst.append(key)
            except:
                break
        try:
            keyboard_admin.row(bt_lst[0], bt_lst[1], bt_lst[2])
        except:
            try:
                keyboard_admin.row(bt_lst[0], bt_lst[1])
            except:
                keyboard_admin.row(bt_lst[0])
        bt_lst.clear()
    bot.send_message(message.chat.id, "Список твоих учеников", reply_markup=keyboard_admin)


def update_lessons(message, student):
    bot.send_message(message.chat.id, "Введи тему урока")
    bot.register_next_step_handler(message, find_topic, student)


def find_topic(message, student):
    if d.get_topic_id(message.text, student) != 0:
        bot.send_message(message.chat.id, f"Такая тема уже есть\nВот ее номер {d.get_topic_id(message.text, student)}")
    else:
        bot.send_message(message.from_user.id, "Введи информацию об уроке \n"
                                               "Тема урока\n"
                                               "Описание урока (что именно прошли)\n"
                                               "Описание пройденных функций, методов и т.д\n"
                                               "Домашнее задание")
        bot.register_next_step_handler(message, add_homework, student)


def add_homework(message, student):
    topic = message.text.split("\n")
    try:
        if d.add_homework(topic, student) != 0:
            bot.send_message(message.chat.id, "Урок успешно добавлен")  # передача id студента, запись в Lesson
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, попробуй еще раз")
        time.sleep(1)
        bot.send_message(message.chat.id, "Введи информацию об уроке \n"
                                          "Тема урока\n"
                                          "Описание урока (что именно прошли)\n"
                                          "Описание пройденных функций, методов и т.д\n"
                                          "Домашнее задание")


bot.polling(non_stop=True)
