from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging, time, ephem, locale
import settings

locale.setlocale(locale.LC_ALL, "russian")

# Initiate logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    filename='bot.log'
                    )

logger = logging.getLogger(__name__)

# function /start
def greet_user(update, context):
    update.message.reply_text('Привет, {}!\nЧтобы узнать, что я умею, напиши команду /help'.format(update.message.chat.first_name))

# function /help
def help(update, context):
    update.message.reply_text('Напиши /planet *название_планеты_на_английском* и я расскажу тебе, в каком она сейчас\
    созвездии.\n\nЕще я умею повторять за тобой сообщения.\nПопробуй написать мне любой текст (кроме команд)')

# function echo
def talk_to_me(update, context):
    user_text = update.message.text
    logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username, update.message.chat.id, update.message.text)
    update.message.reply_text(user_text)

# function /planet
def planet_info(update, context):
    try:
        command_text = update.message.text.split()
        planet = eval('ephem.' + command_text[1] + '(' + time.strftime('%Y/%m/%d') + ')')
        update.message.reply_text('{} находится сейчас в созвездии {}'. format(command_text[1], ephem.constellation(planet)[1]))
    except:
        update.message.reply_text('Название планеты введено неправильно!')

# bot "body"
def main():
    mybot = Updater(token=settings.TOKEN, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('planet', planet_info))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()

if __name__ == '__main__':
    main()