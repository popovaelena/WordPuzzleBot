from config import TOKEN
import itertools
# import logging
import asyncio
from aiogram.types import Message  # InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

loop = asyncio.get_event_loop()
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, loop=loop, storage=storage)


class States(StatesGroup):
    get_text = State()


class Text:
    def __init__(self, letters):
        self.letters = letters

    # поиск всех возможных комбинаций в зависимости от введённого к-ства букв
    def generate_all_possible_words(self, letters):
        self.letters = letters
        words = []
        for num in range(3, len(letters) + 1):
            words += [''.join(x_set) for x_set in itertools.permutations(letters, num)]
        return words

    # поиск совпадений
    def finding_coincidences(self, letters):
        self.letters = letters
        with open('word_rus1.txt', encoding="utf-8") as inp:
            library = [i.replace('\n', '') for i in inp.readlines()]
            result = list(set(letters) & set(library))
            res = ', '.join(result)
            return res


class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        print(user_id, user_name)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    user = User(message.from_user.id, message.from_user.first_name)
    stick = open('static/welcome.webp', 'rb')
    await bot.send_sticker(message.from_user.id, stick)
    await bot.send_message(message.from_user.id, f'Добро пожаловать, <b>{message.from_user.first_name}</b>. '
                                                 f'Меня зовут <b>WordPuzzleBot</b>. '
                                                 f'Бот, созданный, чтобы помочь тебе взломать эту чёртову игру.')
    await bot.send_message(message.from_user.id, 'Просто напиши мне буквы в любой момент, а я найду все слова за тебя.')
    await States.get_text.set()
#    await bot.send_message(message.from_user.id, 'Вводи свои буквы.')
#    await States.get_text.set()


@dp.message_handler(state=States.get_text)
async def generate_all_possible_words(message: Message):
    letters = message.text.lower()  # перевод в нижний регистр
    let = letters.replace(' ', '')  # убрать пробелы (на выходе str)
    if let.isalpha():
        if (len(let) < 3) or (len(let) > 8):
            await bot.send_message(message.from_user.id, 'Не может быть меньше 3 или больше 8 букв, '
                                                         'проверь и попробуй ещё раз!')
            print('!Некорректное к-ство букв!')
            await States.get_text.set()
        else:
            a = Text(let)

            all_words = a.generate_all_possible_words(let)
            correct_words = a.finding_coincidences(all_words)

            await bot.send_message(message.from_user.id, f'Лови результат:\n{correct_words}')
            await States.get_text.set()

    else:
        await bot.send_message(message.from_user.id, 'Что-то нет так. Возможно, попались цифры или символы. '
                                                     'Проверь и попробуй ещё раз!')
        print('!Некорректный пользовательтский ввод!')
        await States.get_text.set()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    # @dp.callback_query_handler(lambda callback_query: True)
    # async def some_callback_handler(callback_query: types.CallbackQuery)

    # try:
    #     user_id = message.from_user.id
    #     name = message.from_user.first_name
    #     con = sql.connect("WSDB.sqlite")
    #     cursor = con.cursor()
    #     cursor.execute("INSERT OR IGNORE INTO user_id (PersonID, FirstName) VALUES (?,?)", (user_id, name))
    #     con.commit()
    #     con.close()
    #     return input(user_id)
    # except sql.DatabaseError as e:
    #     await bot.send_message(message.from_user.id, 'Ой! Что-то не так. Попробуй ещё раз.')
    #     print(f'Что-то не так! {e}.')
