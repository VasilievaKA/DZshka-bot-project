"""! @brief Connection to database and making requests"""
# @file database.py
#
# @brief File with functions working with database.
#
# @section description_sensors Description
# Defines the base and end user classes.
# - Student
# - Teacher
# - Parent
# - Lesson
# - Topic
# @section author_doxygen_example Author(s)
# - Created by MIREA Team on 02/04/2023.
#
# Copyright (c) 2023 MIREA Team.  All rights reserved.
# Imports
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
# Global Constants
engine = create_engine(os.getenv("URL"), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
DataBase = declarative_base()


class Student(DataBase):
    """! Class for information about students.
    Defines attributes which are using in project.
    """
    __tablename__ = "students"
    idstudent = Column(Integer, primary_key=True, unique=True)
    name = Column(String(10))
    fam_name = Column(String(20))
    semestr = Column(Integer)
    id = Column(String(20), unique=True)
    teacher = Column(Integer, ForeignKey('teachers.idteacher'))
    parent = Column(Integer, ForeignKey('parents.idparent'))


class Teacher(DataBase):
    """! Class for information about teachers.
    Defines teachers' name and last name, telegram id.
    """
    __tablename__ = "teachers"
    idteacher = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45))
    fname = Column(String(45))
    t_id = Column(String(20), unique=True)


class Parent(DataBase):
    """! Class for information about parents.
    Defines parent name and last name, telegram id.
    """
    __tablename__ = "parents"
    idparent = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45))
    fname = Column(String(45))
    t_id = Column(String(20), unique=True)


class Topic(DataBase):
    """! Class for information about topics of lessons.
    Defines topic name, long description, short summary and homework.
    """
    __tablename__ = "topics"
    idtopic = Column(Integer, primary_key=True, unique=True)
    name = Column(String(200))
    description = Column(Text)
    summary = Column(Text)
    homework = Column(String(1000))


class Lesson(DataBase):
    """! Class for information about lessons.
    Defines student that took this lesson, topic of the lesson with homework and lesson number.
    """
    __tablename__ = "lessons"
    idlesson = Column(Integer, primary_key=True)
    student = Column(Integer, ForeignKey('students.idstudent'))
    lesson = Column(Integer, ForeignKey('topics.idtopic'))
    lesson_num = Column(Integer)


DataBase.metadata.create_all(engine)


def get_id(name, fname):
    """! Find student in database by his name and last name and return his id.
    @param name   Students' name.
    @param fname   Students' last name.
    """
    for i in SessionLocal().query(Student).filter(Student.name == name, Student.fam_name == fname):
        return i.idstudent


def get_student(t_id):
    """! Find student in database by his telegram id and return his id.
    @param t_id   Students' telegram id.
    """
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.idstudent


def get_student_name(t_id):
    """! Find student in database by his telegram id and return his name and last name.
    @param t_id   Students' telegram id.
    """
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.name, i.fam_name


def get_topic(id_topic):
    """! Find topic in database by its id and return its name, description and summary.
    @param id_topic   Topics' id.
    """
    for i in SessionLocal().query(Topic).filter(Topic.idtopic == id_topic):
        return {'название': i.name, 'описание': i.description, 'функции': i.summary}


def get_homework(id_homework):
    """! Find topic in database by its id and return homework.
    @param id_homework   Topics' id.
    """
    for i in SessionLocal().query(Topic).filter(Topic.idtopic == id_homework):
        return {'описание': i.homework}


def get_lesson(n, t_id=None, user=None):
    """! Find description of the lesson in database by its number and user id and return its id.
    @param n   Number of the lesson.
    @param t_id   Teachers' telegram id.
    @param user   Students' telegram id.
    """
    if t_id is not None:
        id_user = get_student(t_id)
    else:
        id_user = user
    q = SessionLocal().query(Lesson.lesson).filter(Lesson.lesson_num == n, Lesson.student == id_user)
    n = SessionLocal().query(Topic).filter(Topic.idtopic == q)
    for i in n:
        return {'тема': i.idtopic, 'домашнее задание': i.idtopic}


def get_lessons(t_id=None, student_id=None):
    """! Find all number of lessons in database by students' or teachers' telegram id.
    @param t_id   Teachers' telegram id.
    @param student_id   Students' telegram id.
    """
    if t_id is not None:
        id_user = get_student(t_id)
    else:
        id_user = student_id
    return SessionLocal().query(Lesson.lesson_num).filter(Lesson.student == id_user).all()


def update_student(name, fname, t_id):
    """! Find student by his name and last name and update his telegram id .
    @param name   Students' name.
    @param fname   Students' last name.
    @param t_id   Students' telegram id.
    """
    user = session.query(Student).get(get_id(name, fname))
    user.id = t_id
    session.commit()


def get_teacher(name, fname):
    """! Find teacher in database by his name and last name and return his id.
    @param name   Teachers' name.
    @param fname   Teachers' last name.
    """
    for i in SessionLocal().query(Teacher).filter(Teacher.name == name, Teacher.fname == fname):
        return i.idteacher


def get_parent(name, fname):
    """! Find parent in database by his name and last name and return his id.
    @param name   Parents' name.
    @param fname   Parents' last name.
    """
    for i in SessionLocal().query(Parent).filter(Parent.name == name, Parent.fname == fname):
        return i.idparent


def update_parent(name, fname, t_id):
    """! Find parent by his name and last name and update his telegram id .
    @param name   Parents' name.
    @param fname   Parents' last name.
    @param t_id   Parents' telegram id.
    """
    user = session.query(Parent).get(get_parent(name, fname))
    user.t_id = t_id
    session.commit()


def get_parent_by_tid(t_id):
    """! Find parent in database by his telegram id and return his id.
    @param t_id   Parents' telegram id.
    """
    for i in SessionLocal().query(Parent).filter(Parent.t_id == t_id):
        return i.idparent


def get_teacher_by_tid(t_id):
    """! Find teacher in database by his telegram id and return his id.
    @param t_id   Teachers' telegram id.
    """
    for i in SessionLocal().query(Teacher).filter(Teacher.t_id == t_id):
        return i.idteacher


def update_teacher(name, fname, t_id):
    """! Find teacher by his name and last name and update his telegram id .
    @param name   Teachers' name.
    @param fname   Teachers' last name.
    @param t_id   Teachers' telegram id.
    """
    user = session.query(Teacher).get(get_teacher(name, fname))
    user.t_id = t_id
    session.commit()


def find_student(t_id):
    """! Find student in database by his parent id and return his telegram id.
    @param t_id   Parents' telegram id.
    """
    for i in session.query(Student).filter(Student.parent == get_parent_by_tid(t_id)):
        return i.id


def find_students_by_teacher(t_id):
    """! Find student in database by his teacher id and return dictionary of students.
    @param t_id   Teachers' telegram id.
    """
    users = {}
    for i in SessionLocal().query(Student).filter(Student.teacher == get_teacher_by_tid(t_id)).all():
        users[i.idstudent] = str(i.name) + ' ' + str(i.fam_name)
    return users


def get_topic_id(name, student_id):
    """! Find topic for certain student in database by topic name and student telegram id.
    @param name   Topics' name.
    @param student_id     Students' id.
    """
    for i in session.query(Lesson).filter(Lesson.student == student_id):
        for j in session.query(Topic).filter(Topic.idtopic == i.lesson):
            if name == j.name:
                return j.idtopic
    return 0


def get_homework_id(name):
    """! Find topic by topic name and return its id.
    @param name   Topics' name.
    """
    for i in session.query(Topic).filter(Topic.name == name):
        return i.idtopic


def add_homework(info: list, student_id):
    """! Add information about certain lesson.
    @param info   Information about lesson.
    @param student_id   Students' id.
    """
    session.expire_all()
    id_s = session.query(Topic.idtopic).count() + 1
    lessons_id = session.query(Lesson.idlesson).count() + 1
    lesson_num = session.query(Lesson.lesson_num).filter(Lesson.student == student_id). \
                     order_by(Lesson.lesson_num.desc()).first()[0] + 1
    Topic(idtopic=id_s, name=info[0], description=info[1], summary=info[2], homework=info[3]).update_topic()
    Lesson(idlesson=lessons_id, student=student_id, lesson=id_s, lesson_num=lesson_num).update_lesson()
    if get_topic_id(info[0], student_id):
        return get_topic_id(info[0], student_id)
    else:
        return 0


def get_teacher_by_student(t_id):
    """! Find teacher by his student.
    @param t_id   Students' telegram id.
    """
    id_t = session.query(Student.teacher).filter(Student.id == t_id)
    for i in session.query(Teacher).filter(Teacher.idteacher == id_t):
        return i.t_id
