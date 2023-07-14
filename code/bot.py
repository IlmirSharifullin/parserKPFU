import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.types import *
from fnmatch import fnmatch
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from messages import messages
import db
import async_parser

dotenv_path = os.path.abspath(__file__)[:-7] + '/../.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = Bot(os.environ.get('BOT_TOKEN'))
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()


@dp.message_handler(commands='all')
async def all(message: Message):
    uid = message.from_user.id
    if uid == 901977201:
        users = db.get_users()
        q = '\n'.join(list(map(lambda x: x[2], users)))
        await bot.send_message(uid, q)


@dp.message_handler(commands='mailing')
async def mailing(message: Message):
    uid = message.from_user.id
    if uid == 901977201:
        msg = message.text[9:]
        users = db.get_users()
        for user in users:
            tg_id = user[1]
            try:
                await bot.send_message(tg_id, msg)
            except:
                pass


@dp.message_handler(commands='start')
async def start(message: Message):
    uid = message.from_user.id
    await bot.send_message(uid, messages['greeting'])
    await bot.send_message(uid, messages['greeting_2'])


@dp.message_handler(commands='help')
async def start(message: Message):
    uid = message.from_user.id
    user = db.get_user(uid)
    if user:
        msg = messages['help_1'] + '`' + user[2] + '`' + messages['help_2']
    else:
        msg = messages['help_1'] + 'Нет СНИЛСа' + messages['help_2']
    await bot.send_message(uid, msg, parse_mode='markdown')


@dp.message_handler()
async def get_all_messages(message: Message):
    uid = message.from_user.id
    if fnmatch(message.text, '???-???-???-??') or fnmatch(message.text, '???-???-??? ??'):
        # Если отправили СНИЛС
        snils = message.text.strip()
        snils = snils[:11] + '-' + snils[12:]
        res = async_parser.pretty_results(async_parser.get_for_snils(snils))
        if not res:
            return await bot.send_message(uid, messages['snils_not_found'])
        user = db.get_user(uid)
        if user:
            if user[2] != snils:
                db.change_last_snils(uid, snils)
                await bot.send_message(uid, messages['change_snils'])
        else:
            db.add_user(uid, snils)
            await bot.send_message(uid, messages['user_added'])
            count = len(db.get_users())
            await bot.send_message(901977201, str(count))
        await bot.send_message(uid, res, reply_markup=ReplyKeyboardMarkup([[message.text]], resize_keyboard=True))
    else:
        await bot.send_message(uid, 'Неправильный СНИЛС, попробуй еще раз!')


async def send_rating(dp: Dispatcher) -> None:
    """
    Рассылка
    :param dp: диспетчер для отправки сообщений
    :return: None
    """
    bot = dp.bot
    users = db.get_users()
    count = 1
    for user in users:
        uid = user[1]
        snils = user[2]
        res = async_parser.pretty_results(async_parser.get_for_snils(snils))
        if res:
            try:
                await bot.send_message(uid, res)
                count += 1
            except Exception as ex:
                print(ex)
        else:
            print(snils)
    await bot.send_message(901977201, f'Рассылка: Сообщений отправлено {count} пользователям из {len(users)}')


async def update_ratings() -> None:
    """
    Ежечасное обновление рейтингов
    :return: None
    """
    bot = dp.bot
    try:
        await async_parser.gather_data()
    except Exception as ex:
        print(ex)
    await bot.send_message(901977201, 'Рейтинги обновлены')


if __name__ == '__main__':
    # Рассылка
    scheduler.add_job(send_rating, 'cron', hour='8,14,22', args=(dp,))
    # scheduler.add_job(send_rating, 'cron', minute='*', args=(dp,)) # Для проверки рассылки

    # Обновление рейтингов
    scheduler.add_job(update_ratings, 'cron', hour='*', minute=30)
    # scheduler.add_job(update_ratings, 'cron', minute='*')
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
