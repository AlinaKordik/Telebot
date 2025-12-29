import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

#Model BD
class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    telegram_id = sq.Column(sq.Integer, unique=True, nullable=False)
    first_name = sq.Column(sq.String(100), nullable=False)
    username = sq.Column(sq.String(100), nullable= False)


class UserNewWords(Base):
    __tablename__ = 'UserNewWords'

    id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String(30))
    english_word = sq.Column(sq.String(40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)

    user = relationship(User, backref='UserNewWords')


class Word(Base):
    __tablename__ = 'TelegramWords'
    id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String(30))
    english_word = sq.Column(sq.String(40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)

    user = relationship(User, backref='TelegramWords')


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

