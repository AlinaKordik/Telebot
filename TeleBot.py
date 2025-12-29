import random
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from main import DB
from models import User

db = DB()
print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = '8565717838:AAGRCVlGsbcwTTUhglcaC4bYVBqSv1PN6qw'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []
user_data = {}


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0

@bot.message_handler(commands=['start_register'])
def start_register(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    msg = bot.reply_to(message, 'Please provide your first_name:')

    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['first_name'] = message.text

        msg = bot.reply_to(message, 'Please provide your age:')

        bot.register_next_step_handler(msg, process_username_step)
    except Exception as e:
        bot.reply_to(message, 'Oops, something went wrong!')

def process_username_step(message):
    try:
        chat_id = message.chat.id
        username = int(message.text)
        first_name = user_data[chat_id]['first_name']
        new_user = User(first_name=first_name, username=username)
        db.add_russian_words(new_user)

        bot.reply_to(message, f'Successfully registered {first_name} who is {username} years old.')
        del user_data[chat_id]

    except ValueError:
        bot.reply_to(message, 'Invalid age. Please enter a number.')

        bot.register_next_step_handler(message, process_username_step)
    except Exception as e:
        db.add_words.rollback()
        bot.reply_to(message, 'An error occurred during database commit.')


@bot.message_handler(commands=['start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, f"Hello, {message.from_user.first_name} let's study English...")
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    random_words = []


    for i in db.get_word():
        target_word = i.english_word  # брать из БД
        translate = i.russian_word # брать из БД
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)

        for word in db.get_random_word():
            if word != i.english_word:
                random_words.append(word.english_word)

        others = random_words  # брать из БД
        other_words_btns = [types.KeyboardButton(word) for word in others]
        buttons.extend(other_words_btns)
        random.shuffle(buttons)
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        buttons.extend([next_btn, add_word_btn, delete_word_btn])

        markup.add(*buttons)

        greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
        bot.send_message(message.chat.id, greeting, reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate
            data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        print(data['target_word'])  # удалить из БД


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid, "Добавьте русское слово")


@bot.message_handler(func=lambda message: userStep.get(message.chat.id) == 1)
def process_word_addition(message):
    cid = message.chat.id
    russian_word = message.text

    userStep[cid] = 2
    bot.send_message(cid, f"Вы добавили '{russian_word}'. Добавьте перевод этого слова на английском.")
    db.add_russian_words(russian_word = russian_word)


@bot.message_handler(func=lambda message: userStep.get(message.chat.id) == 2)
def process_word_addition(message):
    cid = message.chat.id
    english_word = message.text

    userStep[cid] = 3
    bot.send_message(cid, f"{english_word} успешно добавлено")
    db.add_english_words(english_word = english_word)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)



bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)