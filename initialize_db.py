from models import Word
from main import session

word_1 = Word(russian_word = 'Солнце', english_word = 'Sun')
word_2 = Word(russian_word = 'Машина', english_word = 'Car')
word_3 = Word(russian_word = 'Погода', english_word = 'Weather')
word_4 = Word(russian_word = 'Вечер', english_word = 'Evening')
word_5 = Word(russian_word = 'Утро', english_word = 'Morning')
word_6 = Word(russian_word = 'Собака', english_word = 'Dog')
word_7 = Word(russian_word = 'Кровать', english_word = 'Bed')
word_8 = Word(russian_word = 'Стол', english_word = 'Table')
word_9 = Word(russian_word = 'Врач', english_word = 'Doctor')
word_10 = Word(russian_word = 'Таблетка', english_word = 'Pill')

session.add_all([word_1, word_2, word_3, word_4, word_5, word_6, word_7, word_8, word_9, word_10])
session.commit()

session.close()