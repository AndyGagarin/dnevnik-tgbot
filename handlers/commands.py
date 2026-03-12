from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from datetime import datetime, timedelta, date
from storage.markups import *
import logging

from storage.database import get_diary_token, set_diary_token
from services.diary import get_schedule

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command('set_token'))
async def set_token(message: Message):
    tg_user_id = message.from_user.id
    logger.info(f"User {tg_user_id} - /set_token")

    args = message.text.split()[1:]
    if not args:
        await message.reply("Использование: /set_token <ваш_токен>")
        return

    token = args[0]
    await set_diary_token(tg_user_id, token)
    await message.reply("✅ Токен успешно сохранён в базе!")
    logger.info(f"User {tg_user_id} - Token saved")

@router.message(Command('schedule'))
async def send_schedule(message: Message):
    tg_user_id = message.from_user.id
    logger.info(f"User {tg_user_id} - /schedule")

    diary_token = await get_diary_token(tg_user_id)
    if not diary_token:
        await message.reply("Сначала установите токен: /set_token <токен>", reply_markup=token_kb())
        return

    dn = None
    try:
        import aiohttp
        from pydnevnikruapi import AsyncDiaryAPI
        http_session = aiohttp.ClientSession()
        dn = AsyncDiaryAPI(session=http_session, token=diary_token)

        # Получаем данные пользователя
        user_info = await dn.get("users/me")
        person_id = user_info['personId']

        # Получаем группы
        group_info = await dn.get(f'persons/{person_id}/edu-groups')

        # Ищем группу, у которой есть расписание
        group_id = None
        test_date = datetime.now().date().strftime("%Y-%m-%d")
        for g in group_info:
            g_id = g["id"]
            url = f"persons/{person_id}/groups/{g_id}/schedules?startDate={test_date}&endDate={test_date}"
            try:
                resp = await dn.get(url)
                if resp and "days" in resp and resp["days"]:
                    group_id = g_id
                    logger.info(f"User {tg_user_id} - Используем группу: {g['name']}")
                    break
            except:
                continue

        if not group_id:
            group_id = group_info[0]["id"]

        # Сегодня или завтра?
        args = message.text.split()[1:]
        if args and args[0].lower() == 'today':
            target_date: date = datetime.now().date()
            no_msg = "Нет расписания на сегодня."
        else:
            target_date: date = datetime.now().date() + timedelta(days=1)
            no_msg = "Нет расписания на завтра."

        schedule = await get_schedule(person_id, group_id, target_date, dn, tg_user_id)

        if not schedule:
            await message.reply(no_msg)
            return

        text = f"👤 Группа...\nРАСПИСАНИЕ ({target_date.strftime('%Y.%m.%d')})\n"
        for lesson in schedule:
            time_str = lesson['time'].replace('-', ' - ')
            text += f"<u>{lesson['number']} пара ({time_str})</u>\n"
            text += f"  Дисциплина: {lesson['subject']}\n"
            text += f"  Кабинет: {lesson['room']}\n"
            text += f"  Преподаватель: {lesson['teacher']}\n\n"

        await message.reply(text, parse_mode=ParseMode.HTML)

    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")
        logger.error(f"User {tg_user_id} - Error: {str(e)}")
    finally:
        if dn:
            await dn.close_session()