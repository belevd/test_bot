from glob import glob
import locale
import logging
from random import choice
import time

from emoji import emojize
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem

import settings, cities

locale.setlocale(locale.LC_ALL, "russian")

# Initiate logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    filename='bot.log'
                    )

logger = logging.getLogger(__name__)

# function /start
def greet_user(update, context):
    emo = get_user_emo(update, context)
    text = 'Привет, {}{}!\nЧтобы узнать, что я умею, напиши команду /help'.format(update.message.chat.first_name, emo)
    update.message.reply_text(text, reply_markup=get_keyboard())

# Check generation of personal emoji for current user
# Проверяет, создан ли смайл для пользователя
def get_user_emo(update, context):
    if 'emo' in context.user_data:
        return context.user_data['emo']
    else:
        context.user_data['emo'] = emojize(choice(settings.LIST_OF_EMOJI), use_aliases=True)
        return context.user_data['emo']

# Change user personal emoji
# Меняет смайл пользователя
def change_emo(update, context):
    if 'emo' in context.user_data:
        del context.user_data['emo']
    context.user_data['emo'] = emojize(choice(settings.LIST_OF_EMOJI), use_aliases=True)
    update.message.reply_text('Готово! Вот твой новый смайлик - {}'.format(context.user_data['emo']), reply_markup=get_keyboard())

# /help
# Справочник по командам (заполнять ручками)
def help(update, context):
    update.message.reply_text('Напиши /planet *название_планеты_на_английском* и я расскажу тебе, в каком она сейчас созвездии.\
    \n\nНапиши /wordcount *свой_текст* и я посчитаю количество слов в твоем тексте.\
    \n\nНапиши /next_full_moon *дата в формате год-месяц-день* и я скажу, когда следующее полнолуние от твоей даты. Если не указывать дату, то скажу когда будет ближайшее.\
    \n\nЕще я умею повторять за тобой сообщения.\nПопробуй написать мне любой текст (кроме команд)', reply_markup=get_keyboard())

# Echo
# Повторялка
def talk_to_me(update, context):
    get_user_emo(update, context)
    user_text = update.message.text
    logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username, update.message.chat.id, update.message.text)
    update.message.reply_text(user_text + ' ' + context.user_data['emo'], reply_markup=get_keyboard())

# Count words in message
# Считает слова в тексте (ориентируется на пробелы)
# Функция текст ни на какие исключения не проверяет. Можно присылать любые символы
def wordcount(update, context):
    try:
        command_text = update.message.text.split()
        count = len(command_text)
        if (count-1) % 10 in [0, 5, 6, 7, 8, 9]:
            update.message.reply_text('{} слов'.format(count-1))
        elif (count-1) % 10 == 1:
            update.message.reply_text('{} слово'.format(count-1))
        elif (count-1) % 10 in [2, 3, 4]:
            update.message.reply_text('{} слова'.format(count-1))
    except:
        update.message.reply_text('Что-то пошло не так. Повторите попытку')

# Start game "citites" (work in progress)
# Начинает игру "Города" (в процессе)
city_game = {}
def cities_game(update, context):
    user_id = str(update.message.chat.id)
    city_game[user_id] = cities.cities_of_Russia
    # check_letter = update.message.text.split()[-1][0]
    command_text = update.message.text.split()
    user_text = command_text[-1]
    if user_text.capitalize == 'Выход':
        pass
    elif user_text in city_game[user_id]:
        resq_letter = user_text[-1].upper()
        for i in range(len(city_game[user_id])):
            if city_game[user_id][i][0] == resq_letter:
                answer = i
            break
        update.message.reply_text(city_game[user_id][answer])
        # check_letter = answer[-1].upper
        city_game[user_id].remove(user_text)
        city_game[user_id].remove(city_game[user_id][answer])
    else:
        print(len(city_game[user_id]))
        print(user_text)
        print(city_game[user_id])
        update.message.reply_text('Такого города не существует или он уже был')


    # while True:
    #     checker = dp.add_handler(MessageHandler(Filters.text, check_city))
    #     if checker == 'Выход':
    #         break
    #     elif checker == 'error':
    #         update.message.reply_text('Такого города не существует. Повторите попытку')

# Относится к игре "Города"
def check_city(update, context):
    command_text = update.message.text.split()
    user_text = command_text[-1]
    if user_text.capitalize == 'Выход':
        return 'Выход'
    elif user_text in city_game[update.message.chat.id]:
        resq_letter = user_text[-1].upper()
        answer = city_game[update.message.chat.id].index('{}*'.format(resq_letter))
        update.message.reply_text(city_game[update.message.chat.id][answer])
        check_letter = answer[-1].upper
        city_game[update.message.chat.id].remove(user_text)
        city_game[update.message.chat.id].remove(city_game[update.message.chat.id][answer])
    else:
        update.message.reply_text('Такого города не существует. Повторите попытку')

# Send user information about constellation of planet
# Отправляют пользователю информацию о том, в каком созвездии сейчас находится планета
def planet_info(update, context):
    try:
        command_text = update.message.text.split()
        planet = eval('ephem.' + command_text[1] + '(' + time.strftime('%Y/%m/%d') + ')')
        update.message.reply_text('{} находится сейчас в созвездии {}'. format(command_text[1], ephem.constellation(planet)[1]))
    except:
        update.message.reply_text('Название планеты введено неправильно!')

# Send to user date of the next full moon
def next_full_moon(update, context):
    command_text = update.message.text.split()
    if len(command_text) < 2:
        update.message.reply_text(ephem.next_full_moon(time.strftime('%Y/%m/%d')))
    else:
        update.message.reply_text(ephem.next_full_moon(command_text[1]))

# Send to user picture of cat from "img" folder
def send_cat_picture(update, context):
    cat_list = glob('img/cat*.jp*g')
    cat_pic = choice(cat_list)
    update.message.reply_photo(photo=open(cat_pic, 'rb'), reply_markup=get_keyboard())

# Get user's contact
# Получает контакты пользователя
def get_contact(update, context):
    print(update.message.contact)
    update.message.reply_text('Готово {}'.format(get_user_emo(update, context)))

# Get user's location (doesn't work)
# Получает контакты пользователя (не работает)
def get_location(update, context):
    print(update.message.location)
    update.message.reply_text('Готово {}'.format(get_user_emo(update, context)))

# Initiate keyboard
# Инициализирует клавиатуру
def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать локацию', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                        ['ПРИСЛАТЬ КОТИКА!', 'Сменить смайлик'], 
                                        [contact_button, location_button]
                                        ], resize_keyboard=True
                                        )
    return my_keyboard

# bot "body"
def main():
    mybot = Updater(token=settings.TOKEN, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('planet', planet_info))
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(CommandHandler('cities', cities_game))
    dp.add_handler(CommandHandler('cat', send_cat_picture))
    dp.add_handler(MessageHandler(Filters.regex('^(ПРИСЛАТЬ КОТИКА!)$'), send_cat_picture))
    dp.add_handler(MessageHandler(Filters.regex('^(Сменить смайлик)$'), change_emo))
    dp.add_handler(MessageHandler(Filters.contact, get_contact))
    dp.add_handler(MessageHandler(Filters.contact, get_location))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()

if __name__ == '__main__':
    main()