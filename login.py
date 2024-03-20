from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, Text


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Login(db.Model):
    id = mapped_column(Integer, primary_key=True)
    user = mapped_column(Text, nullable=False)
    password = mapped_column(Text, nullable=False)
    title = mapped_column(Text, nullable=False)

    def __init__(self, user, password, title):
        self.user = user
        self.password = password
        self.title = title

    def __repr__(self):
        return "<Login {}>".format(self.id)

class Events(db.Model):
    id = mapped_column(Integer, primary_key=True)
    event_user = mapped_column(Text, nullable=False)
    event_title = mapped_column(Text, nullable=False)
    event_date = mapped_column(Text, nullable=False)
    event_staff_count = mapped_column(Integer, nullable=False)

    def __init__(self, event_user, event_title, event_date, event_staff_count):
        self.event_user = event_user
        self.event_title = event_title
        self.event_date = event_date
        self.event_staff_count = event_staff_count

    def __repr__(self):
        return "<Login {}>".format(self.id)
    
class Staff(db.Model):
    id = mapped_column(Integer, primary_key=True)
    event_date = mapped_column(Text, nullable=False)
    event_staff = mapped_column(Text, nullable=False)
    
    def __init__(self, event_date, event_staff):
        self.event_date = event_date
        self.event_staff = event_staff

    def __repr__(self):
        return "<Login {}>".format(self.id)

