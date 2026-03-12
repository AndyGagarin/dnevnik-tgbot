import json
from datetime import date
import logging
from pydnevnikruapi import AsyncDiaryAPI

logger = logging.getLogger(__name__)

async def get_schedule(person: int, group: int, target_date: date, dn: AsyncDiaryAPI, tg_user_id: int):
    fr = target_date.strftime("%Y-%m-%d")
    to = fr
    url = f"persons/{person}/groups/{group}/schedules?startDate={fr}&endDate={to}"

    logger.info(f"User {tg_user_id} - API GET request: {url}")
    try:
        response = await dn.get(url)
        logger.info(f"User {tg_user_id} - API response for {url}: {json.dumps(response, ensure_ascii=False)}")

        if not response or "days" not in response or not response["days"]:
            logger.warning(f"User {tg_user_id} - No schedule data")
            return []

        day_data = response["days"][0]
        subjects = {s["id"]: s["name"] for s in day_data.get("subjects", [])}
        teachers = {t["person"]["id"]: t["person"]["shortName"] for t in day_data.get("teachers", [])}

        schedule = []
        for lesson in day_data.get("lessons", []):
            teacher_names = [teachers.get(t_id, f"ID: {t_id}") for t_id in lesson.get("teachers", [])]
            schedule.append({
                "number": lesson["number"],
                "time": lesson.get("hours", ""),
                "subject": subjects.get(lesson["subjectId"], "Неизвестно"),
                "room": lesson.get("place", ""),
                "teacher": ", ".join(teacher_names) if teacher_names else "Не указан"
            })

        logger.info(f"User {tg_user_id} - Parsed schedule: {json.dumps(schedule, ensure_ascii=False)}")
        return sorted(schedule, key=lambda x: x["number"])
    except Exception as e:
        logger.error(f"User {tg_user_id} - Error in get_schedule: {str(e)}")
        return []