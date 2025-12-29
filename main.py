from sqlalchemy import func
import sqlalchemy
from sqlalchemy.orm import Session
from config import DSN
from models import Word, UserNewWords


class DB:
    def __init__(self):
        self.engine = sqlalchemy.create_engine(DSN)

    def session(self) -> Session:
        return Session(self.engine)

    def get_word(self)-> list[Word]:
        with self.session() as s:
            word = s.query(Word).order_by(func.random()).limit(1).all()
            return word

    def get_random_word(self) -> list[Word]:
        with self.session() as s:
            word = s.query(Word).order_by(func.random()).limit(3).all()
            return word

    def add_words(self, russian_word, english_word):
        with self.session() as s:
            new_words= UserNewWords(user_id = cid, russian_word = russian_word, english_word = english_word)
            s.add(new_words)
            s.commit()

            return new_words


    def add_user(self,  telegram_id, first_name, username):
        with self.session() as s:
            new_user = User(telegram_id = telegram_id, first_name=first_name, username=username)
            s.add(new_user)
            s.commit()



# engine = sqlalchemy.create_engine(DSN)
# create_tables(engine)
# #
# #
# Session = sessionmaker(bind=engine)
# session = Session()
# #
# session.close()