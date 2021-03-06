import sys

from flask import Flask,  redirect
from flask.ext import admin
from flask.ext.admin.datastore.sqlalchemy import SQLAlchemyDatastore
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
import wtforms as wtf

Base = declarative_base()


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------
class TestModel(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)


class FileForm(wtf.Form):
    """
    A form with a filefield on it.
    """
    filefield = wtf.fields.FileField()


def create_app(database_uri='sqlite://'):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'not secure'
    engine = create_engine(database_uri, convert_unicode=True)
    app.db_session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False,
        bind=engine))
    datastore = SQLAlchemyDatastore(
        (TestModel,), app.db_session, model_forms={'TestModel': FileForm})
    admin_blueprint = admin.create_admin_blueprint(datastore)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    Base.metadata.create_all(bind=engine)

    @app.route('/')
    def go_to_admin():
        return redirect('/admin')

    return app


if __name__ == '__main__':
    app = create_app('sqlite://')
    app.run(debug=True)
