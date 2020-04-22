import config
import pymysql
import const
import datetime
import cryptographer
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup


def main():
    updater = Updater(token=config.TOKEN, use_context=True, request_kwargs=config.REQUEST_KWARGS)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, message))
    dp.add_handler(MessageHandler(Filters.document, photo))

    dp.add_error_handler(error)

    updater.start_polling(timeout=123)

    updater.idle()


if __name__ == "__main__":
    main()
