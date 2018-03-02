from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os

from storer import Storer
from user import User
import decoder
from request import request
from helper_classes import myfilters
from helper_classes.date import Date

STORED_FILE = 'users.db'
storer = Storer(STORED_FILE)

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Старт бота, регистрация пользователя
def start(bot, update):
    telegram_user = update.message.from_user

    if not (telegram_user.id in users):
        logger.info("Start for user: %s" % telegram_user)
        users[telegram_user.id] = User(telegram_user.id)
        storer.store('users', users)
        bot.sendMessage(
            update.message.chat_id,
            'Привет, %s!\n'
            'Я помогу Вам следить за расходами на покупки.\n'
            'Чтобы начать вести статистику, пришлите мне фотографию QR-кода на чеке.\n'
            'Чтобы посмотреть список команд, введите /help или "Список команд"' % telegram_user.first_name
        )
        bot.sendMessage(update.message.chat_id, 'Пример:')
        bot.send_photo(update.message.chat_id, open('examples/example.jpg', 'rb'))
    else:
        bot.sendMessage(
            update.message.chat_id,
            'Вы уже зарегистрированы в системе.\n'
            'Чтобы начать вести статистику, пришлите мне фотографию QR-кода на чеке.\n'
            'Чтобы посмотреть список команд, введите /help или "Список команд"'
        )
        bot.sendMessage(update.message.chat_id, 'Пример:')
        bot.send_photo(update.message.chat_id, open('examples/example.jpg', 'rb'))


# Список команд
def commands_list(bot, update):
    bot.sendMessage(
        update.message.chat_id,
        'Список команд:\n'
        '/sum или "Сумма" - показать общую сумму по всем покупкам\n'
        '/today или "Сегодня" - показать сумму за сегодня\n'
        '/month или "Месяц" - показать сумму за текущий месяц\n'
        '/clean - очистить всю статистику\n'
        '/help или "Список команд" - показать список команд\n\n'
        'Чтобы показать сумму за конкретный день, введите дату в формате "ДД.ММ.ГГГГ"'
    )


# Сообщение с фото
def photo(bot, update):
    telegram_user = update.message.from_user

    if not (telegram_user.id in users):
        bot.sendMessage(
            update.message.chat_id,
            'Чтобы начать вести статистику, Вам нужно заоегистрироваться.\n'
            'Для этого введите /start')
        return

    photo_file = bot.get_file(update.message.photo[-1].file_id)
    photo_path = str(telegram_user.id) + ".jpg"
    photo_file.download(photo_path)

    bot.sendMessage(update.message.chat_id, 'Получил фото!\n'
                                            'Ведется обработка...')

    data = decoder.decode(photo_path)

    if data is not None:
        text = request(data)

        if text != '':
            json_path = str(telegram_user.id) + '.txt'
            file_json = open(json_path, 'w')
            file_json.write(request(data))
            file_json.close()

            user = users[telegram_user.id]
            user.add_purchase(json_path)

            storer.store('users', users)

            os.remove(photo_path)
            os.remove(json_path)

            bot.sendMessage(update.message.chat_id, 'Обработка завершена!\n'
                                                    'Чек добавлен.')
        else:
            bot.sendMessage(update.message.chat_id, 'Обработка завершена.\n'
                                                    'Чек отсутствует в базе ФНС. Повторите попытку позже.')
    else:
        bot.sendMessage(update.message.chat_id, 'Обработка не завершена!\n'
                                                'Попробуйте еще раз.')


# Итоговая сумма
def total_sum(bot, update):
    telegram_user = update.message.from_user

    if not (telegram_user.id in users):
        bot.sendMessage(update.message.chat_id, 'Чтобы начать вести статистику, отправь /start')
        return

    user = users[telegram_user.id]
    bot.sendMessage(update.message.chat_id, 'Общая сумма = %s' % user.total_sum)


# Сумма за заданный день
def get_day_sum(bot, update):
    telegram_user = update.message.from_user
    if not (telegram_user.id in users):
        bot.sendMessage(update.message.chat_id, 'Чтобы начать вести статистику, отправь /start')
        return

    date = Date()
    date.from_message(update.message.text)
    if not(date.is_date()):
        bot.sendMessage(update.message.chat_id, 'Такой даты не существует!')
        return

    user = users[telegram_user.id]
    sum = user.get_day_sum(date)
    if not (sum == 0):
        bot.sendMessage(update.message.chat_id, 'Сумма за день %s = %s' % (update.message.text, sum))
    else:
        bot.sendMessage(update.message.chat_id, 'В этот день покупок не зарегистировано.')


# Сумма за сегодня
def get_today_sum(bot, update):
    telegram_user = update.message.from_user
    if not (telegram_user.id in users):
        bot.sendMessage(update.message.chat_id, 'Чтобы начать вести статистику, отправь /start')
        return

    user = users[telegram_user.id]
    sum = user.get_today_sum()
    if not (sum == 0):
        bot.sendMessage(update.message.chat_id, 'Сумма за сегодня = %s' % sum)
    else:
        bot.sendMessage(update.message.chat_id, 'Сегодня покупок не зарегистировано.')


# Сумма за текущий месяц
def get_month_sum(bot, update):
    telegram_user = update.message.from_user
    if not (telegram_user.id in users):
        bot.sendMessage(update.message.chat_id, 'Чтобы начать вести статистику, отправь /start')
        return

    user = users[telegram_user.id]
    sum = user.get_month_sum()
    if not (sum == 0):
        bot.sendMessage(update.message.chat_id, 'Сумма за прошедший месяц = %s' % sum)
    else:
        bot.sendMessage(update.message.chat_id, 'За прошедший месяц покупок не зарегистировано.')


# Очистка статистики
def clean(bot, update):
    telegram_user = update.message.from_user

    if not (telegram_user.id in users):
        bot.sendMessage(update.message.chat_id,
                        'Нет данных для удаления.\n'
                        'Чтобы начать вести статистику, отправь /start')
        return

    keyboard = [[InlineKeyboardButton("Да", callback_data='Да'),
                 InlineKeyboardButton("Нет", callback_data='Нет')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Вы точно хотите удалить всю статистику?',
                    reply_markup=reply_markup)


def confirm_clean(bot, update):
    query = update.callback_query

    if query.data == 'Да':
        user = users[query.message.chat_id]
        user.clear_archive()

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text='Статистика удалена')
    elif query.data == 'Нет':
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text='Вы ответили "Нет"')


# Ручное добавление покупки
def add_purchase(bot, update):
    telegram_user = update.message.from_user
    if not (telegram_user.id in users):
        bot.sendMessage(
            update.message.chat_id,
            'Чтобы начать вести статистику, Вам нужно заоегистрироваться.\n'
            'Для этого введите /start')
        return

    user = users[telegram_user.id]
    error = user.add_custom_purchase(update.message.text)

    if error is False:
        bot.sendMessage(update.message.chat_id, 'Ошибка в данных! Попробуйте еще раз.')
    else:
        storer.store('users', users)
        bot.sendMessage(update.message.chat_id, 'Покупка успешно добавлена!')


def main():
    global users
    users = storer.restore('users')
    if users is None:
        users = {}

    token = open('token.txt').read()

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(confirm_clean))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', commands_list))
    dispatcher.add_handler(CommandHandler('sum', total_sum))
    dispatcher.add_handler(CommandHandler('clean', clean))
    dispatcher.add_handler(CommandHandler('month', get_month_sum))
    dispatcher.add_handler(CommandHandler('today', get_today_sum))

    dispatcher.add_handler(MessageHandler(Filters.photo, photo))

    help_filter = myfilters.HelpFilter()
    sum_filter = myfilters.SumFilter()

    date_filter = myfilters.DateFilter()
    today_filter = myfilters.TodayFilter()
    month_filter = myfilters.MonthFilter()

    add_purchase_filter = myfilters.AddPurchaseFilter()

    dispatcher.add_handler(MessageHandler(help_filter, commands_list))
    dispatcher.add_handler(MessageHandler(sum_filter, total_sum))

    dispatcher.add_handler(MessageHandler(date_filter, get_day_sum))
    dispatcher.add_handler(MessageHandler(today_filter, get_today_sum))
    dispatcher.add_handler(MessageHandler(month_filter, get_month_sum))

    dispatcher.add_handler(MessageHandler(add_purchase_filter, add_purchase))

    updater.start_polling(timeout=60)
    updater.idle()


if __name__ == '__main__':
    main()
