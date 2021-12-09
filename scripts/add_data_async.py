import asyncio
import anyio
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

class MyException(Exception):
    pass

async def add_user(session, status = 'active'):
    session.add(User(login=get_new_login(), status=status))
    # if status!='active':
    #     raise MyException('maaaaammaa')

async def main():

    await recreate_tables()
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        async with session.begin():
            # asyncio.create_task(add_user(session))
            # asyncio.create_task(add_user(session, status='inactive'))
            # asyncio.create_task(add_user(session))
            #Todo без слипа не работает
            # logger.info('tasks spawned')
            # await asyncio.sleep(1)
            # try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(add_user, session)
                tg.start_soon(add_user, session, 'inactive')
                tg.start_soon(add_user, session)
            # except MyException as e:
            #     logger.error(e)

    await asyncio.sleep(1)
if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
