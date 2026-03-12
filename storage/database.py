from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from bot.config import DATABASE_URL
from models import Base, User

# Поддержка SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL.lower() else {}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(session: AsyncSession, tg_user_id: int):
    stmt = select(User).where(User.tg_user_id == tg_user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def save_or_update_token(session: AsyncSession, tg_user_id: int, diary_token: str):
    user = await get_user(session, tg_user_id)
    if user:
        user.diary_token = diary_token
    else:
        user = User(tg_user_id=tg_user_id, diary_token=diary_token)
        session.add(user)
    await session.commit()

async def get_diary_token(tg_user_id: int) -> str | None:
    async with AsyncSessionLocal() as session:
        user = await get_user(session, tg_user_id)
        return user.diary_token if user else None

async def set_diary_token(tg_user_id: int, diary_token: str):
    async with AsyncSessionLocal() as session:
        await save_or_update_token(session, tg_user_id, diary_token)