from functools import wraps
import sys

from flask import Flask, g, redirect, render_template, request, session, url_for
from flaskext import themes
from flaskext import admin
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, Float, Time, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from flaskext.wtf import Form, TextField

Base = declarative_base()

# ----------------------------------------------------------------------
# Association tables
# ----------------------------------------------------------------------
course_student_association_table = Table(
    'course_student_association',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student.id')),
    Column('course_id', Integer, ForeignKey('course.id')))


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------
class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)

    teacher = relationship('Teacher', backref='courses')
    students = relationship('Student',
                            secondary=course_student_association_table,
                            backref='courses')
    # teacher = relation()
    # students = relation()

    def __repr__(self):
        return self.subject


class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)

    def __repr__(self):
        return self.name


class Teacher(Base):
    __tablename__ = 'teacher'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)

    def __repr__(self):
        return self.name


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def create_app(database_uri='sqlite://'):
    app = Flask('view_decorator')
    app.config['SECRET_KEY'] = 'not secure'

    app.engine = create_engine(database_uri, convert_unicode=True)
    db_session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=app.engine))

    themes.setup_themes(app)
    admin_mod = admin.Admin(app, (Course, Student, Teacher), db_session,
                            theme='auth',
                            view_decorator=login_required,
                            exclude_pks=True)

    @app.route('/login/', methods=('GET', 'POST'))
    def login():
        if request.form.get('username', None):
            session['user'] = request.form['username']
            return redirect(request.args.get('next', url_for('flaskext.admin.index')))
        else:
            if request.method == 'POST':
                return themes.render_theme_template("auth", "login.html",
                                                    bad_login=True)
            else:
                return themes.render_theme_template("auth", "login.html")

    @app.route('/logout/')
    def logout():
        del session['user']
        return redirect('/')

    app.register_module(admin_mod, url_prefix='/admin')

    @app.route('/')
    def go_to_admin():
        return redirect('/admin/')

    return app


if __name__ == '__main__':
    app = create_app('sqlite:///simple.db')
    Base.metadata.create_all(bind=app.engine)
    app.run(debug=True)