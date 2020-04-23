import config
import pymysql
import const
import datetime
import cryptographer
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup


def message(update, context):
    con = pymysql.connect(config.DB_SERVER, config.DB_USER, config.DB_PASSWORD, config.DB_DATABASE)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT `status` FROM `Users` WHERE `telegram_id` = '{update.message.from_user.id}';")
        # берем из обеих веток
        if cur.rowcount == 1:
            print('not OK')
            return
        res = cur.fetchall()
        status = res[0][0]
        if update.message.text.lower() == "шифрование" and status == const.STATUS[0]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[1]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
        elif update.message.text.lower() == "дешифрование" and status == const.STATUS[0]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[6]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
        elif status == const.STATUS[0]:
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Я не понимаю, выбери что делать.", reply_markup=reply_markup)
        elif update.message.text.lower().endswith("изображение") and status == const.STATUS[1]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[2]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            update.message.reply_text(text="Отправь изображение в формате png как документ!", reply_markup=None)
        elif update.message.text.lower().endswith("текст") and status == const.STATUS[1]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[3]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            update.message.reply_text(text="Отправь текст который будет зашифрован", reply_markup=None)
        elif status == const.STATUS[3]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[1]}', `text`='{update.message.text}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
        elif update.message.text.lower().endswith("ключ") and status == const.STATUS[1]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[4]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            update.message.reply_text(text="Отправьте ключ для шифрования", reply_markup=None)
        elif status == const.STATUS[4]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[1]}', `crypto_key`='{update.message.text}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
         elif update.message.text.lower() == "завершить" and status == const.STATUS[1]:
            cur.execute(f"SELECT `image`, `text`, `crypto_key` FROM `Users` WHERE `telegram_id` = '{update.message.from_user.id}';")
            res = cur.fetchall()[0]
            if res[0] is not None and res[1] is not None and res[2] is not None:
                update.message.reply_text(text="Идёт шифрование...", reply_markup=None)
                crypto = cryptographer.Cryptographer(f"photo/encrypt/before/{res[0]}", res[2], res[1])
                image = crypto.encrypt()
                reply_markup = ReplyKeyboardMarkup([['В начало']], resize_keyboard=True, one_time_keyboard=True)
                update.message.reply_text(text="Зашифрованная картинка:", reply_markup=reply_markup)
                context.bot.send_document(chat_id=update.message.from_user.id, document=open(image, 'rb'))
                cur.execute(f"UPDATE `Users` SET `status`='{const.STATUS[5]}' WHERE `telegram_id`='{update.message.from_user.id}';")
        elif update.message.text.lower() == "в начало" and (status == const.STATUS[5] or status == const.STATUS[9]):
            cur.execute(f"UPDATE `Users` SET `name`='{update.message.from_user.first_name}', `status`='{const.STATUS[0]}', `image`=NULL, `text`=NULL, `crypto_key`=NULL WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = ReplyKeyboardMarkup([['Шифрование', 'Дешифрование']], resize_keyboard=True, one_time_keyboard=True)
            update.message.reply_text(text="Приветствую, я CryptoBot, умею шифровать сообщение в картинку.", reply_markup=reply_markup)
        elif update.message.text.lower().endswith("изображение") and status == const.STATUS[6]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[7]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            update.message.reply_text(text="Отправь изображение в формате png как документ!", reply_markup=None)
        elif update.message.text.lower().endswith("ключ") and status == const.STATUS[6]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[8]}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            update.message.reply_text(text="Отправьте ключ для дешифрования", reply_markup=None)
        elif status == const.STATUS[8]:
            cur.execute(f"UPDATE `Users` set `status`='{const.STATUS[6]}', `crypto_key`='{update.message.text}' WHERE `telegram_id`='{update.message.from_user.id}';")
            con.commit()
            reply_markup = get_keyboard(update.message.from_user.id, cur)
            update.message.reply_text(text="Выбери, что установить.", reply_markup=reply_markup)
        elif update.message.text.lower() == "завершить" and status == const.STATUS[6]:
            cur.execute(f"SELECT `image`, `crypto_key` FROM `Users` WHERE `telegram_id` = '{update.message.from_user.id}';")
            res = cur.fetchall()[0]
            if res[0] is not None and res[1] is not None:
                update.message.reply_text(text="Идёт дешифрование...", reply_markup=None)
                crypto = cryptographer.Cryptographer(f"photo/decrypt/before/{res[0]}", res[1])
                text = crypto.decrypt()
                reply_markup = ReplyKeyboardMarkup([['В начало']], resize_keyboard=True, one_time_keyboard=True)
                update.message.reply_text(text="Расшифрованный текст:", reply_markup=None)
                update.message.reply_text(text=text, reply_markup=reply_markup)
                cur.execute(f"UPDATE `Users` SET `status`='{const.STATUS[9]}' WHERE `telegram_id`='{update.message.from_user.id}';")



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
    
# берем из feature
def test(test):
    print(test)
    
    
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
    # берем из master
    print('OK')
