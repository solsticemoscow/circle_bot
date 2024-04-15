import os

from sqlalchemy import select

from BOT.config import DATA_INPUT
from BOT.db.db import DB_SESSION
from BOT.handlers.fsm_states import FSMSTATES

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from BOT.db.tables import Data, Buttons, Channels
from BOT.config import ROOT_DIR
from BOT.utils.func_write_to_excel import write_to_excel_whitelist, write_to_excel_all

router = Router()




@router.callback_query()
async def get_admin_command(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    DATA: str = call.data

    print(f'CALL LAST: {DATA}')

    if DATA.startswith('CHANNEL:'):
        CHANNEL_ID = int(DATA.replace('CHANNEL:', ''))
        print(CHANNEL_ID)

        await bot.send_video_note(
            chat_id=CHANNEL_ID,
            video_note=FSInputFile(DATA_INPUT + str(call.from_user.id) + '/video_final.mp4')
        )

        await bot.send_message(
            chat_id=call.from_user.id,
            text=f'✅ Видеокружок успешно переслан в канал: {CHANNEL_ID}')

    if DATA == 'channel_add':
        await call.message.answer(text="Добавьте бота в канал и перешлите cообщение из"
                                                               " канала для изменения привязки.")
        await state.set_state(FSMSTATES.STEP13_USER_CHANNEL)
    if DATA == 'channel_remove':
        await call.message.answer(text="Добавьте бота в канал и перешлите cообщение из"
                                                               " канала для изменения привязки.")
        await state.set_state(FSMSTATES.STEP13_USER_CHANNEL)

    if DATA == 'admin_channel':
        await bot.send_message(chat_id=call.from_user.id, text="Добавьте бота в канал и перешлите cообщение из"
                                                               " канала для изменения привязки.")
        await state.set_state(FSMSTATES.STEP8_ADMIN_CHANNEL)
    if DATA == 'admin_whitelist':

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="admin_whitelist_add"))
        keyboard.add(InlineKeyboardButton(text="➖ Удалить пользователя", callback_data="admin_whitelist_remove"))
        keyboard.adjust(1)

        try:
            WHITELIST = await write_to_excel_whitelist()
            if WHITELIST:
                stat_file = FSInputFile(ROOT_DIR + '/data/statistics/whitelist.xlsx')
                await bot.send_document(chat_id=call.from_user.id, document=stat_file, caption="✅ Текущий whitelist. Выберете действие:", reply_markup=keyboard.as_markup())
                os.remove(ROOT_DIR + f'/data/statistics/whitelist.xlsx')
            else:
                await call.message.answer(
                    text='⚠ whitelist пуст. Выберете действие:',
                    reply_markup=keyboard.as_markup()
                )
        except Exception as e:
            print(e)
    if DATA == 'admin_himsg_add':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='🔸 Введите новое сообщение:',
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP1_EDIT_HIMSG)
    if DATA == 'admin_back':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔸 Белый список", callback_data="admin_whitelist"))
        keyboard.add(InlineKeyboardButton(text="🔸 Приветственное сообщение", callback_data="admin_himsg"))
        keyboard.add(InlineKeyboardButton(text="🔸 Рассылка", callback_data="admin_send"))
        keyboard.add(InlineKeyboardButton(text="🔸 Статистика", callback_data="admin_stat"))
        keyboard.add(InlineKeyboardButton(text="🔸 Изменить канал к которому привязан бот", callback_data="admin_channel"))
        keyboard.add(InlineKeyboardButton(text="🔸 Меню пользователя", callback_data="admin_usermenu"))
        keyboard.adjust(1)

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='🔏 Привет! Добро пожаловать в админ панель :)',
            reply_markup=keyboard.as_markup())

        await state.clear()
    if DATA == 'admin_himsg':
        await call.message.answer(text="Текущее сообщение:")

        stmt = select(Data.hi_message)
        result = await DB_SESSION.execute(statement=stmt)
        TEXT: str = result.scalar_one_or_none()

        if not TEXT:
            TEXT = 'У вас нету приветственного сообщения.'

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Прислать новое сообщение", callback_data="admin_himsg_add"))
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))
        keyboard.adjust(1)

        await call.message.answer(text=TEXT, reply_markup=keyboard.as_markup())
    if DATA == 'admin_stat':
        try:
            await write_to_excel_all()
            stat_file = FSInputFile(ROOT_DIR + '/data/statistics/stat.xlsx')
            await bot.send_document(chat_id=call.from_user.id, document=stat_file, caption="✅ Ваш файл статистики.")
            os.remove(f'./data/statistics/stat.xlsx')
        except Exception as e:
            print(e)
    if DATA == 'admin_whitelist_add':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await call.message.answer(text="💡 Перешлите сообщение от пользователя:", reply_markup=keyboard.as_markup())
        await state.set_state(FSMSTATES.STEP2_ADD_WHITELIST)
    if DATA == 'admin_whitelist_remove':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await call.message.answer(text="💡 Перешлите сообщение от пользователя:", reply_markup=keyboard.as_markup())
        await state.set_state(FSMSTATES.STEP3_REMOVE_WHITELIST)
    if DATA == 'admin_usermenu':
        try:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="➕ Добавить кнопку", callback_data="admin_usermenu_add"))
            keyboard.add(InlineKeyboardButton(text="➖ Удалить кнопку", callback_data="admin_usermenu_remove"))

            stmt = select(Buttons)
            result = await DB_SESSION.execute(statement=stmt)
            DATA = result.all()

            TEXT = '💡 Здесь вы можете добавить три дополнительные кнопки. Текущие кнопки:\n\n'

            if DATA:
                for button in DATA:
                    TEXT += f'<i>Имя</i>: {button[0].button_name}\n'

            keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))
            keyboard.adjust(1)

            await bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text=TEXT,
                reply_markup=keyboard.as_markup()
            )

            await state.set_state(FSMSTATES.STEP9_BUTTONS)

        except Exception as e:
            print(e)
    if DATA == 'admin_send':
        await bot.send_message(chat_id=call.from_user.id, text="💡 Пришлите сообщение для рассылки:")
        await state.set_state(FSMSTATES.STEP4_SENDMSG)


@router.message(F.text)
async def get_all_text_msgs(message: Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id
    await bot.delete_message(chat_id=USER_ID, message_id=message.message_id)

    TEXT = message.text
    print(TEXT)

    if TEXT == "⚡️Постинг на канал":
        stmt = select(Channels).where(Channels.user_id == USER_ID)
        result = await DB_SESSION.execute(statement=stmt)
        channels = result.all()

        TEXT = ('💡 Выберите действие (отобразятся ваши текущие каналы, если они привязаны):\n\n')

        if channels:
            for channel in channels:
                TEXT += f'<i>Имя канала:</i>: {channel[0].channel_name}\n'

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Привязать канал", callback_data="channel_add"))
        keyboard.add(InlineKeyboardButton(text="➖ Отвязать канал", callback_data="channel_remove"))
        keyboard.adjust(1)

        await message.answer(text=TEXT, reply_markup=keyboard.as_markup())

    stmt = select(Buttons)
    result = await DB_SESSION.execute(statement=stmt)
    DATA = result.all()

    if DATA:
        for button in DATA:
            if TEXT == button[0].button_name:
                await message.answer(text=button[0].button_text)



@router.message()
async def get_all(message: Message, bot: Bot):
    print(message)
    await bot.delete_message(message.from_user.id, message.message_id)



