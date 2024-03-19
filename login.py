from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, Text, Array


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Login(db.Model):
    id = mapped_column(Integer, primary_key=True)
    user = mapped_column(Text, nullable=False)
    password = mapped_column(Text, nullable=False)
    title = mapped_column(Text, nullable=False)
    events = mapped_column(Array, nullable=False)

    def __init__(self, user, password, title, events):
        self.user = user
        self.password = password
        self.title = title
        self.events = events

    def __repr__(self):
        return "<Login {}>".format(self.id)