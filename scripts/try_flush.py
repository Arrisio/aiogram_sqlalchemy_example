import asyncio
from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.orm import sessionmaker

from base import engine
from models import User
from scripts.recreate_tables import main as recreate_tables
from sqlalchemy.future import select


async def main():
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )

    async with async_session() as session:
        # async with session.begin():
        session.begin()
        stnm = select(User).where(User.id == 1)
        res = await session.execute(stnm)
        l = list(res.scalars())
        u = l[0]
        print(u.login, u.status, u.email)
        await session.commit()
        pass
        print(u.login, u.status, u.email)




if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
