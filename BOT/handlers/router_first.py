import random, os
import string


from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, KeyboardButton, InlineKeyboardButton, )
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.markdown import hlink
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError

from BOT.config import OWNER, DANIEL, DATA_INPUT


from BOT.db.db import DB_SESSION
from BOT.db.tables import Users, Buttons, Data

from BOT.handlers.router_admin import router as router_admin
from BOT.handlers.router_user import router as router_user
from BOT.handlers.router_last import router as router_last
from BOT.handlers.router_content import router as router_content

from BOT.handlers.fsm_states import FSMSTATES

router = Router()
router.include_router(router_admin)
router.include_router(router_user)
router.include_router(router_content)
router.include_router(router_last)

@router.message(Command(commands=["start"]))
async def get_start(message: Message, bot: Bot, state: FSMContext):
    USERNAME: str = message.from_user.username
    USER_ID: int = message.from_user.id

    try:
        stmt = insert(Users).values(
            id=USER_ID,
            username=USERNAME,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name,
            language_code=message.from_user.language_code,
            time_added=func.now(),
            is_premium=message.from_user.is_premium,
        )
        await DB_SESSION.execute(statement=stmt)
        await DB_SESSION.commit()

    except IntegrityError as e:
        print(e)

    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text='⚡️Постинг на канал'))
    keyboard.adjust(1, 1)

    stmt = select(Buttons)
    result = await DB_SESSION.execute(statement=stmt)
    DATA = result.all()

    if DATA:
        for button in DATA:
            keyboard.row(KeyboardButton(text=button[0].button_name))
            keyboard.adjust(1, 1)

    await message.answer(text='🤖 Вас приветствует бот!', reply_markup=keyboard.as_markup(resize_keyboard=True))
    await message.answer(text='📎 Присылай фото, gif или видео до минуты и жди видеосообщение в ответ.')
    await bot.delete_message(chat_id=USER_ID, message_id=message.message_id)

    await bot.unpin_all_chat_messages(chat_id=message.from_user.id)

    stmt = select(Data.hi_message)
    result = await DB_SESSION.execute(statement=stmt)
    TEXT: str = result.scalar_one_or_none()


    if TEXT is None:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await bot.send_message(
            chat_id=USER_ID,
            text='🔸 Введите новое приветственное сообщение (оно у вас не задано):',
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP1_EDIT_HIMSG)
    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="👉 Инструкция", url="https://t.me/volna_telegram/6"))

        MSG_ID = await message.answer(
            text=TEXT,
            reply_markup=keyboard.as_markup()
        )

        await bot.pin_chat_message(chat_id=message.from_user.id, message_id=MSG_ID.message_id)
        await state.clear()




@router.message(Command(commands=["admin"]))
async def start(message: Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id

    await state.clear()
    await bot.delete_message(chat_id=USER_ID, message_id=message.message_id)

    if message.from_user.id not in [OWNER, DANIEL]:
        await bot.send_message(chat_id=message.from_user.id,
                               text="вы не админ бота, вы не можете использовать админ панель 😊\n"
                                    "Но можете использовать другие функции бота:\n"
                                    "сделать кружочек из фотки или видео и "
                                    "переслать в свой любимый канал (но сначала нужно его привязать и добавить меня "
                                    "туда 😊)")
        return
    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔸 Белый список", callback_data="admin_whitelist"))
        keyboard.add(InlineKeyboardButton(text="🔸 Приветственное сообщение", callback_data="admin_himsg"))
        keyboard.add(InlineKeyboardButton(text="🔸 Рассылка", callback_data="admin_send"))
        keyboard.add(InlineKeyboardButton(text="🔸 Статистика", callback_data="admin_stat"))
        keyboard.add(InlineKeyboardButton(text="🔸 Изменить канал к которому привязан бот", callback_data="admin_channel"))
        keyboard.add(InlineKeyboardButton(text="🔸 Меню пользователя", callback_data="admin_usermenu"))
        keyboard.adjust(1)

        stmt = select(Data)
        result = await DB_SESSION.execute(statement=stmt)
        DATA = result.scalar_one_or_none()
        print(DATA)

        CHANNEL_ID = DATA.channel_id
        CHANNEL_TITLE = DATA.channel_title

        stmt = select(Users)
        result = await DB_SESSION.execute(statement=stmt)
        USERS = result.all()

        await bot.send_message(chat_id=message.from_user.id,
                               reply_markup=keyboard.as_markup(),
                               text='🔏 <i>Привет! Добро пожаловать в админ панель!</i>\n\n'
                                    'Канал бота: ' + hlink(f"{CHANNEL_TITLE}", f"{(await bot.get_chat(CHANNEL_ID)).invite_link}") +
                                    f'\nКоличество пользователей бота: {len(USERS)}',
)


@router.message(Command(commands=["test"]))
async def command_start(message: Message, bot: Bot):
    USER_ID: int = message.from_user.id
    CODE = ''.join(random.choices(string.ascii_letters, k=8))

    try:
        if not os.path.exists(f"{DATA_INPUT}{USER_ID}/"):
            os.makedirs(f"{DATA_INPUT}{USER_ID}/")
    except Exception as e:
        await bot.send_message(
            chat_id=USER_ID,
            text=f'Ошибка: {str(e)}'
        )
