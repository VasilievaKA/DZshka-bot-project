import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('mysql+pymysql://root:12345@127.0.0.1:3306/school', pool_pre_ping=True)
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
    code = Column(String(45), unique=True)
    t_id = Column(String(20), unique=True)

    def update_teacher(self):
        session.add(self)
        session.commit()

    def delete_teacher(self):
        session.delete(self)
        session.commit()


class Topic(DataBase):
    __tablename__ = "topics"
    idtopic = Column(Integer, primary_key=True, unique=True)
    name = Column(String(200))
    description = Column(Text)
    summary = Column(Text)

    def update_topic(self):
        session.add(self)
        session.commit()

    def delete_topic(self):
        session.delete(self)
        session.commit()


class Homework(DataBase):
    __tablename__ = "homeworks"
    idhomework = Column(Integer, primary_key=True, unique=True)
    description = Column(String)

    def update_homework(self):
        session.add(self)
        session.commit()

    def delete_homework(self):
        session.delete(self)
        session.commit()


class Lesson(DataBase):
    __tablename__ = "lessons"
    idlesson = Column(Integer, primary_key=True)
    student = Column(Integer, ForeignKey('students.idstudent'))
    topic = Column(Integer, ForeignKey('topics.idtopic'))
    homework = Column(Integer, ForeignKey('homeworks.idhomework'))
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


def get_id_by_tid(t_id):
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.idstudent


def get_student(t_id):
    for i in SessionLocal().query(Student).filter(Student.id == t_id):
        return i.idstudent


def get_topic(id_topic):
    for i in SessionLocal().query(Topic).filter(Topic.idtopic == id_topic):
        return {'название': i.name, 'описание': i.description, 'функции': i.summary}


def get_homework(id_homework):
    for i in SessionLocal().query(Homework).filter(Homework.idhomework == id_homework):
        return {'описание': i.description}


def get_lesson(n, t_id):
    id_user = get_id_by_tid(t_id)
    q = SessionLocal().query(Lesson).filter(Lesson.lesson_num == n, Lesson.student == id_user)
    for i in q:
        return {'тема': i.topic, 'домашнее задание': i.homework}


def get_lessons(t_id):
    id_user = get_id_by_tid(t_id)
    return SessionLocal().query(Lesson.lesson_num).filter(Lesson.student == id_user).all()


def update_student(name, fname, t_id):
    user = session.query(Student).get(get_id(name, fname))
    user.id = t_id
    session.commit()


def get_teacher(name, fname):
    for i in SessionLocal().query(Teacher).filter(Teacher.name == name, Teacher.fname == fname):
        return i.idteacher


def get_teacher_by_tid(t_id):
    for i in SessionLocal().query(Teacher).filter(Teacher.t_id == t_id):
        return i.idteacher


def update_teacher(name, fname, t_id):
    user = session.query(Teacher).get(get_teacher(name, fname))
    user.t_id = t_id
    session.commit()


def add_student(name, fname, sem):
    session.expire_all()
    id_s = session.query(Student.idstudent).count()
    session.add(Student(idstudent=id_s+1, name=name, fam_name=fname, semestr=sem))
    session.commit()
    if get_id(name, fname) is not None:
        return 0
    else:
        return 1

