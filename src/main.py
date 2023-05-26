"""! @brief Main logic of telegram bot work"""
##
# @mainpage Telegram Bot for teachers.
#
# Copyright (c) 2023 MIREA Team.  All rights reserved.
##
# @file main.py
#
# @section author_doxygen_example Author(s)
# - Created by MIREA Team on 02/04/2023.
#
# Copyright (c) 2023 MIREA Team.  All rights reserved.
# Imports
import time
from telebot import types
from dotenv import load_dotenv
import os
import telebot
import database as d

# Global Constants
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))
keyboard = types.InlineKeyboardMarkup()
st_id = 0


@bot.message_handler(commands=['start'])
def start(message):
    """! Send instructions to sender.
    @param message   The input message from chat.
    """
    if d.get_student(message.from_user.id) is None and d.get_teacher_by_tid(message.from_user.id) is None \
            and d.get_parent_by_tid(message.from_user.id) is None:
        bot.send_message(message.from_user.id, "Введи свое имя и фамилию через пробел")
        bot.register_next_step_handler(message, register)
    else:
        if d.get_student(message.from_user.id) is not None or d.get_parent_by_tid(message.from_user.id) is not None:
            bot.send_message(message.from_user.id, "Можешь проверить уроки /check_lesson\n"
                                                   "Для отправки дз просто отправь файл с расширением .py")
        elif d.get_teacher_by_tid(message.from_user.id) is not None:
            bot.send_message(message.from_user.id, "Проверь уроки /admin")


def register(message):
    """! Update telegram id and send instructions to sender.
    @param message   The input message from chat.
    """
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
    """! Make list with lessons' numbers and send keyboard to sender.
    @param message   The input message from chat.
    """
    lis = list()
    if d.get_student(message.from_user.id) is not None:
        lis = list(d.get_lessons(t_id=message.from_user.id))
    elif d.get_parent_by_tid(message.from_user.id) is not None:
        lis = list(d.get_lessons(t_id=d.find_student(message.from_user.id)))
    keyboard = make_keyboard_lessons(lis)
    bot.send_message(message.from_user.id, text='Выбери урок', reply_markup=keyboard)


def lessons_for_teacher(message, info):
    """! Make list with lessons' numbers of a certain student and send keyboard to sender.
    @param message   The input message from chat.
    @param info   Information about sender.
    """
    global st_id
    lis = list(d.get_lessons(student_id=info[5:len(info)]))
    keyboard = make_keyboard_lessons(lis, move=1)
    st_id = info[5:len(info)]
    bot.edit_message_text(text='Выбери урок', chat_id=message.chat.id, message_id=message.message_id,
                          reply_markup=keyboard)


def make_keyboard_lessons(lis: list, move=None):
    """! Make keyboard for students and their parents.
    @param lis   Numbers of students' lessons.
    @param move   Flag for making keyboard for teacher
    """
    lis.sort()
    keyboard_l = types.InlineKeyboardMarkup(row_width=5)
    for i in lis:
        keyboard_l.add(types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'номер {i[0]}'))
    if move is not None:
        keyboard_l.add(types.InlineKeyboardButton(text=f'<-', callback_data='<'))
    return keyboard_l


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    """! Processing of pushing buttons.
    @param call   Information about sender, message, message data.
    """
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
    elif call.data[:16] == 'домашнее задание':
        topic = d.get_homework(call.data[17:len(call.data)])
        if topic['оценка'] == 0:
            topic['оценка'] = 'не выставлена'
        bot.edit_message_text(text=f'Описание: {topic["описание"]}\nОценка: {topic["оценка"]}',
                              chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data == '>':
        if d.get_student(call.message.chat.id) is not None or d.get_parent_by_tid(call.message.chat.id) is not None:
            lis = list(d.get_lessons(t_id=call.message.chat.id))
            move = None
        else:
            lis = list(d.get_lessons(student_id=st_id))
            move = 1
        lis.sort()
        bot.edit_message_text(text='Выбери урок', chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=make_keyboard_lessons(lis, move))
    elif call.data[:4] == "урок":
        update_lessons(call.message, call.data[5:len(call.data)])
    elif call.data[:4] == "инфо":
        lessons_for_teacher(call.message, call.data)
    elif call.data in list(str(d.find_students_by_teacher(call.message.chat.id).keys())):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text="Добавить информацию об уроке", callback_data=f'урок {int(call.data)}'),
            types.InlineKeyboardButton(text="Показать информацию об уроках", callback_data=f'инфо {int(call.data)}'))
        bot.edit_message_text(text="Выбери действие", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data == "<":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text="Добавить информацию об уроке", callback_data=f'урок {st_id}'),
            types.InlineKeyboardButton(text="Показать информацию об уроках", callback_data=f'инфо {st_id}'))
        bot.edit_message_text(text="Выбери действие", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data[:6] == "оценка":
        d.update_mark(int(call.data[7]), int(call.data[9:]))
        bot.send_message(int(call.data[9:]), f"Твоя оценка за домашнее задание {call.data[7]}.\n"
                                             f"На уроке разберем ее полностью.")
        bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(commands=['admin'])
def send_commands_for_teachers(message):
    """! Make keyboard with students for certain teacher, only for admins.
    @param message   Information about sender and message.
    """
    lst = d.find_students_by_teacher(message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    k = len(lst)
    keys = list(lst.keys())
    for i in range(k // 3 + bool(k % 3)):
        if k - 3 >= 0:
            a = 3
        else:
            a = k % 3
        buttons = []
        for j in range(a):
            k -= 1
            buttons.append(types.InlineKeyboardButton(text=lst[keys[j]], callback_data=keys[j]))
        keyboard.add(*buttons)
        del keys[0:3]
    bot.send_message(message.chat.id, "Список твоих учеников", reply_markup=keyboard)


def update_lessons(message, student):
    """! Send instructions for teacher.
    @param message   Information about sender and message.
    @param student   Students' telegram id.
    """
    bot.send_message(message.chat.id, "Введи тему урока")
    bot.register_next_step_handler(message, find_topic, student)


def find_topic(message, student):
    """! Find certain topic and send instructions, how to update information about lesson.
    @param message   Information about sender and message.
    @param student   Students' telegram id.
    """
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
    """!Update student's information about lesson.
    @param message   Information about sender and message.
    @param student   Students' telegram id.
    """
    topic = message.text.split("\n")
    if d.add_homework(topic, student) != 0:
        bot.send_message(message.chat.id, "Урок успешно добавлен")
        bot.send_message(d.get_student_tid_by_id(int(student)), "Добавлена информация о прошедшем уроке. "
                                                                "Чтобы ее посмотреть нажми /check_lesson")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так, попробуй еще раз")
        time.sleep(1)
        bot.send_message(message.chat.id, "Введи информацию об уроке \n"
                                          "Тема урока\n"
                                          "Описание урока (что именно прошли)\n"
                                          "Описание пройденных функций, методов и т.д\n"
                                          "Домашнее задание")


@bot.message_handler(content_types=['document'])
def send_doc(message):
    """!Get files with python scripts from student and send them to teacher.
    @param message   Information about sender and message.
    """
    id_doc = message.document.file_id
    if ".py" in bot.get_file(id_doc).file_path:
        doc = bot.download_file(bot.get_file(id_doc).file_path)
        with open("homework.py", "wb") as file:
            file.write(doc)
        file = open("homework.py", "rb")
        keyboard_mark = types.InlineKeyboardMarkup(row_width=5)
        buttons_list = []
        for i in range(1, 6):
            buttons_list.append(types.InlineKeyboardButton(text=f"{i}",
                                                           callback_data=f"оценка {i} {message.chat.id}"))
        keyboard_mark.add(*buttons_list)
        bot.send_document(d.get_teacher_by_student(message.chat.id), file,
                          caption=f"Домашка от {d.get_student_name(message.chat.id)[0]} "
                                  f"{d.get_student_name(message.chat.id)[1]}",
                          visible_file_name=f"{d.get_student_name(message.chat.id)[0]} "
                                            f"{d.get_student_name(message.chat.id)[1]}.py",
                          protect_content=True, reply_markup=keyboard_mark)
        file.close()
        os.remove("homework.py")
        msg = bot.send_message(message.chat.id, "Домашка отправлена")
        time.sleep(4)
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        msg = bot.send_message(message.chat.id, "Только скрипты на Python")
        time.sleep(2)
        bot.delete_message(message.chat.id, msg.message_id)


bot.polling(non_stop=True)
