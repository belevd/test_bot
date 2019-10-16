from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

TOKEN = '893005100:AAE-jeed2SLHp75uud6oPJZZWv4Yt7M8m-Y'
PROXY = {'proxy_url' : 'socks5://115.178.103.78:23500',
        #  'urllib3_proxy_kwargs' : {
        #      'username' : 'learn', 
        #      'password' : 'python'}
        }

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    filename='bot.log'
                    )

def main():
    mybot = Updater(token=TOKEN, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()

def greet_user(bot, update):
    text = 'Вызван /start'
    print(text)
    update.message.reply_text(text)

def talk_to_me(bot, update):
    user_text = update.message.reply_text
    print(user_text)
    update.message.reply_text(user_text)

main()