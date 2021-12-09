import asyncio
from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.orm import sessionmaker

from base import engine
from models import User
from scripts.recreate_tables import main as recreate_tables

TEST_LOGIN_BLANKS = [f'usr-{i}' for i in range(1_000)]
USED_LOGINS = []

def get_new_login():
    login_blank = TEST_LOGIN_BLANKS.pop()
    login = f"{login_blank}-{datetime.now().time().isoformat()}"
    USED_LOGINS.append(login)
    return login



async def main():

    await recreate_tables()
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:

        async with session.begin():
            logger.info('start adding batch 1')
            session.add_all([
                User(login='user003'),
                User(login='user004'),
            ])
            logger.info('finish adding batch 1')

            savepoint = session.begin_nested()
            await savepoint.start()
            logger.info('start adding batch 2')
            # with session.begin_nested as sp:
            # n =session.begin(subtransactions=True)
            # await n.start()
            session.add_all([
                User(login='inner_user001',  status='inactive'),
                User(login='inner_user002', status='inactive'),
            ])
            # await n.commit()
            logger.info('start committing batch 2')
            await session.flush()
            await savepoint.rollback()
            # await savepoint.commit()

            logger.info('finish committing batch 2')
            await asyncio.sleep(1)
            logger.info('start adding batch 3')
            session.add_all([
                User(login='user005',),
                User(login='user006',),
            ])
            logger.info('finish adding batch 3')
            # logger.info('start rollback main session')
            # raise Exception('mama')
            await session.commit()
            # await session.rollback()
            logger.info('finish rollback main session')

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
