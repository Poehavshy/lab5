import config
import pymysql
import const
import datetime
import cryptographer
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup


def get_keyboard(user_id, cur):
    cur.execute(f"SELECT `status`, `image`, `text`, `crypto_key` FROM `Users` WHERE `telegram_id` = '{user_id}';")
    res = cur.fetchall()[0]
    keyboard = [[]]
    reply_markup = None
    if res[0] == const.STATUS[1]:
        keyboard[0].append(('' if res[1] is None else u'\U00002705') + "Изображение")
        keyboard[0].append(('' if res[2] is None else u'\U00002705') + "Текст")
        keyboard[0].append(('' if res[3] is None else u'\U00002705') + "Ключ")
        if res[1] is not None and res[2] is not None and res[3] is not None:
            keyboard.append([])
            keyboard[1].append("Завершить")
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    if res[0] == const.STATUS[6]:
        keyboard[0].append(('' if res[1] is None else u'\U00002705') + "Изображение")
        keyboard[0].append(('' if res[3] is None else u'\U00002705') + "Ключ")
        if res[1] is not None and res[3] is not None:
            keyboard.append([])
            keyboard[1].append("Завершить")
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    return reply_markup



def main():
    updater = Updater(token=config.TOKEN, use_context=True, request_kwargs=config.REQUEST_KWARGS)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, message))
    dp.add_handler(MessageHandler(Filters.document, photo))

    dp.add_error_handler(error)

    updater.start_polling(timeout=123)

    updater.idle()
    
    
def error(update, context):
    print("ERROR: ", context.error)
    
    
def photo(update, context):
    con = pymysql.connect(config.DB_SERVER, config.DB_USER, config.DB_PASSWORD, config.DB_DATABASE)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT `status` FROM `Users` WHERE `telegram_id` = '{update.message.from_user.id}';")
        if cur.rowcount == 0:
            return
        res = cur.fetchall()
        status = res[0][0]
        if status == const.STATUS[2] or status == const.STATUS[7]:
            update.message.reply_text(text="Загружаю изображение...", reply_markup=None)
            file_id = update.message.document.file_id
            file = context.bot.getFile(file_id)
            file_name = f"{update.message.from_user.id}_{datetime.datetime.now()}.png"

        if status == const.STATUS[2]:
            file.download(f"photo/encrypt/before/{file_name}")
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[1]}', `image`='{file_name}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
        if status == const.STATUS[7]:
            file.download(f"photo/decrypt/before/{file_name}")
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[6]}', `image`='{file_name}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)


if __name__ == "__main__":
    main()
