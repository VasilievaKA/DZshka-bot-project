import os
import time

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("URL"), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
DataBase = declarative_base()


class Student(DataBase):
    __tablename__ = "students"
    idstudent = Column(Integer, primary_key=True, unique=True)
    name = Column(String(10))
    fam_name = Column(String(20))
    semestr = Column(Integer)
    id = Column(String(20), unique=True)
    teacher = Column(Integer, ForeignKey('teachers.idteacher'))
    parent = Column(Integer, ForeignKey('parents.idparent'))

    def update_student(self):
        session.add(self)
        session.commit()

    def delete_student(self):
        session.delete(self)
        session.commit()


class Teacher(DataBase):
    __tablename__ = "teachers"
    idteacher = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45))
    fname = Column(String(45))
    t_id = Column(String(20), unique=True)

    def update_teacher(self):
        session.add(self)
        session.commit()

    def delete_teacher(self):
        session.delete(self)
        session.commit()


class Parent(DataBase):
    __tablename__ = "parents"
    idparent = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45))
    fname = Column(String(45))
    t_id = Column(String(20), unique=True)

    def update_parent(self):
        session.add(self)
        session.commit()

    def delete_parent(self):
        session.delete(self)
        session.commit()


class Topic(DataBase):
    __tablename__ = "topics"
    idtopic = Column(Integer, primary_key=True, unique=True)
    name = Column(String(200))
    description = Column(Text)
    summary = Column(Text)
    homework = Column(String(1000))

    def update_topic(self):
        session.add(self)
        session.commit()

    def delete_topic(self):
        session.delete(self)
        session.commit()


class Lesson(DataBase):
    __tablename__ = "lessons"
    idlesson = Column(Integer, primary_key=True)
    student = Column(Integer, ForeignKey('students.idstudent'))
    lesson = Column(Integer, ForeignKey('topics.idtopic'))
    lesson_num = Column(Integer)

    def update_lesson(self):
        session.add(self)
        session.commit()

    def delete_lesson(self):
        session.delete(self)
        session.commit()


DataBase.metadata.create_all(engine)


def get_id(name, fname):
    for i in SessionLocal().query(Student).filter(Student.name == name, Student.fam_name == fname):
        return i.idstudent


def get_student(t_id):
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.idstudent

def get_student_name(t_id):
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.name, i.fam_name


def get_topic(id_topic):
    for i in SessionLocal().query(Topic).filter(Topic.idtopic == id_topic):
        return {'название': i.name, 'описание': i.description, 'функции': i.summary}


def get_homework(id_homework):
    for i in SessionLocal().query(Topic).filter(Topic.idtopic == id_homework):
        return {'описание': i.homework}


def get_lesson(n, t_id=None, user=None):
    if t_id is not None:
        id_user = get_student(t_id)
    else:
        id_user = user
    q = SessionLocal().query(Lesson.lesson).filter(Lesson.lesson_num == n, Lesson.student == id_user)
    n = SessionLocal().query(Topic).filter(Topic.idtopic == q)
    for i in n:
        return {'тема': i.idtopic, 'домашнее задание': i.idtopic}


def get_lessons(t_id=None, student_id=None):
    if t_id is not None:
        id_user = get_student(t_id)
    else:
        id_user = student_id
    return SessionLocal().query(Lesson.lesson_num).filter(Lesson.student == id_user).all()


def update_student(name, fname, t_id):
    user = session.query(Student).get(get_id(name, fname))
    user.id = t_id
    session.commit()


def get_teacher(name, fname):
    for i in SessionLocal().query(Teacher).filter(Teacher.name == name, Teacher.fname == fname):
        return i.idteacher


def get_parent(name, fname):
    for i in SessionLocal().query(Parent).filter(Parent.name == name, Parent.fname == fname):
        return i.idparent


def update_parent(name, fname, t_id):
    user = session.query(Parent).get(get_parent(name, fname))
    user.t_id = t_id
    session.commit()


def get_parent_by_tid(t_id):
    for i in SessionLocal().query(Parent).filter(Parent.t_id == t_id):
        return i.idparent


def get_teacher_by_tid(t_id):
    for i in SessionLocal().query(Teacher).filter(Teacher.t_id == t_id):
        return i.idteacher


def update_teacher(name, fname, t_id):
    user = session.query(Teacher).get(get_teacher(name, fname))
    user.t_id = t_id
    session.commit()


def find_student(t_id):
    for i in session.query(Student).filter(Student.parent == get_parent_by_tid(t_id)):
        return i.id


def find_students_by_teacher(t_id):
    users = {}
    for i in SessionLocal().query(Student).filter(Student.teacher == get_teacher_by_tid(t_id)).all():
        users[i.idstudent] = str(i.name) + ' ' + str(i.fam_name)
    return users


def get_topic_id(name, student_id):
    for i in session.query(Lesson).filter(Lesson.student == student_id):
        for j in session.query(Topic).filter(Topic.idtopic == i.lesson):
            if name == j.name:
                return j.idtopic
    return 0


def get_homework_id(name):
    for i in session.query(Topic).filter(Topic.name == name):
        return i.idtopic


def add_homework(info: list, student_id):
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
    id_t = session.query(Student.teacher).filter(Student.id == t_id)
    for i in session.query(Teacher).filter(Teacher.idteacher == id_t):
        return i.t_id
