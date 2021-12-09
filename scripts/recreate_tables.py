import asyncio
from sqlalchemy.sql import text

from base import engine
from models import Base


async def main():
    SLEEP_TIME = 2

    create_slee_function_query = text(
        f"""create or replace
function mysleep()
returns trigger
as 
$$
begin 
	perform pg_sleep({SLEEP_TIME});
return null;
end;
$$language PLPGSQL;
"""
    )
    drop_sleep_trigger_query = text(
        """drop trigger if exists insert_with_sleep on users;"""
    )
    create_sleep_trigger_query = text(
        """create trigger delay_insert
after
insert OR UPDATE
	on
	users 
for each row
execute procedure mysleep();"""
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with engine.begin() as conn:
        await conn.execute(create_slee_function_query)
    async with engine.begin() as conn:
        await conn.execute(drop_sleep_trigger_query)
    async with engine.begin() as conn:
        await conn.execute(create_sleep_trigger_query)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
