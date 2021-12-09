import contextvars
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select


from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import LabeledPrice

from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, BoundFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from models import User
from settings import Settings

db_session = contextvars.ContextVar('db_session')
user_ctx = contextvars.ContextVar('user_ctx')

def setup_middleware(dp: Dispatcher):
    dp.middleware.setup(CommonMiddleware())

class IsUserNotAuthorized(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        logger.debug("start filtering IsUserNotAuthorized", tg_id=message.chat.id)
        session = db_session.get()
        result = await session.execute(select(User).where(User.tg_id==message.from_user.id))

        return result

def setup_filters(dp: Dispatcher):
    # dp.filters_factory.bind(IsUserNotAuthorized)
    pass


class CommonMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        session = async_session()
        db_session.set(session)
        await session.begin()

        result = await session.execute(select(User).where(User.tg_id==message.from_user.id))
        if not (user := result.scalars().first()):
            user = User(
                tg_id=message.from_user.id, user_name=message.from_user.username
            )
            session.add(user)
            await session.commit()

        user_ctx.set(user)
        logger_ = logger.bind(
            user_id=message.from_user.id,
            username=message.from_user.username,
            message_text=message.text,
        )
        logger_.info("income message")

        data["logger"] = logger_
        # data["user"] = user
        # data["session"] = session

    async def on_pre_process_callback_query(
        self, callback_query: types.CallbackQuery, data: dict
    ):
        pass

    async def on_post_process_message(
        self, message: types.Message, results, data: dict
    ):
        session = db_session.get()
        # session = data["session"]
        await session.commit()
        await session.close()
        logger.debug("finish")


settings = Settings()
bot = Bot(settings.TG_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}",
    echo=True,
)


cb_add_to_cart = CallbackData("add_to_cart", "pizza_id")
cb_goto_main_menu = "goto_main_menu"


@dp.message_handler(CommandStart(), IsUserNotAuthorized())
async def handle_start(message: types.Message,
                       # user: User,
                       state: FSMContext):
    await state.finish()
    session = db_session.get()
    user = user_ctx.get()
    user.counter += 1
    await session.commit()


    await message.answer(
        f"{user.user_name} написал {message.text} \n counter: {user.counter}"
    )

@dp.message_handler(CommandStart())
async def handle_start(message: types.Message):
    await message.answer('not authorized -you should never see this message')

@dp.callback_query_handler(text=cb_goto_main_menu)
async def show_pizza_list_cb(call: CallbackQuery, state: FSMContext):
    await call.answer()


@dp.callback_query_handler(cb_add_to_cart.filter())
async def show_pizza_details(
    call: CallbackQuery, callback_data: dict, state: FSMContext
):
    await call.message.answer("a")
    await call.answer()


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery, state: FSMContext
):
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id, ok=True
    )
    await bot.send_message(
        chat_id=pre_checkout_query.from_user.id,
        text="кушайте не обляпайтесь",
    )
    await state.finish()


async def on_startup(dp):
    setup_middleware(dp)
    setup_filters(dp)
    await dp.bot.send_message(settings.TG_BOT_ADMIN_ID, "Бот Запущен и готов к работе!")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
