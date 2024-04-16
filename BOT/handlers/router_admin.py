
import datetime
import json

from aiogram import Bot

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hlink
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy import insert, select, update, delete

from BOT.config import OWNER, ROOT_DIR
from BOT.db.db import DB_SESSION
from BOT.db.tables import Users, Buttons, Data
from BOT.handlers.fsm_states import FSMSTATES
from BOT.utils.Message_with_media import MessageWithMedia



router = Router()

@router.message(FSMSTATES.STEP1_EDIT_HIMSG)
async def get_himsg(message: types.Message, state: FSMContext):
    TEXT: str = message.text

    stmt = update(Data).values(hi_message=TEXT)
    await DB_SESSION.execute(statement=stmt)
    await DB_SESSION.commit()


    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔸 Белый список", callback_data="admin_whitelist"))
    keyboard.add(InlineKeyboardButton(text="🔸 Приветственное сообщение", callback_data="admin_himsg"))
    keyboard.add(InlineKeyboardButton(text="🔸 Рассылка", callback_data="admin_send"))
    keyboard.add(InlineKeyboardButton(text="🔸 Статистика", callback_data="admin_stat"))
    keyboard.add(InlineKeyboardButton(text="🔸 Изменить канал к которому привязан бот", callback_data="admin_channel"))
    keyboard.add(InlineKeyboardButton(text="🔸 Меню пользователя", callback_data="admin_usermenu"))
    keyboard.adjust(1)

    await message.answer("✅ Новое приветственное сообщение добавлено!", reply_markup=keyboard.as_markup())

    await state.clear()

@router.message(FSMSTATES.STEP3_REMOVE_WHITELIST)
async def download_audio(message: types.Message, bot: Bot, state: FSMContext):

    stmt = select(Users).where(Users.id == message.forward_from.id)
    result = await DB_SESSION.execute(statement=stmt)
    user = result.scalar_one_or_none()

    if user:
        stmt = update(Users).values(is_whitelist=False).where(Users.id == message.forward_from.id)
        await DB_SESSION.execute(statement=stmt)
        await DB_SESSION.commit()
        await DB_SESSION.close()

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(text='✅ Пользователь удален из whitelist.')

    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(text='⚠ Такого пользователя нет в whitelist.')
    await state.clear()

@router.message(FSMSTATES.STEP2_ADD_WHITELIST)
async def download_audio(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.forward_from.id

    stmt = select(Users).where(Users.id == USER_ID)
    result = await DB_SESSION.execute(statement=stmt)
    user = result.scalar_one_or_none()


    if user:
        if user.is_whitelist:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await message.answer(text='⚠ Такой пользователь уже в whitelist. Попробуйте ещё:')
            await state.set_state(FSMSTATES.STEP2_ADD_WHITELIST)
        else:
            stmt = update(Users).values(is_whitelist=True).where(Users.id == USER_ID)
            await DB_SESSION.execute(statement=stmt)
            await DB_SESSION.commit()
            await DB_SESSION.close()

            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await message.answer(text='✅ Пользователь добавлен в whitelist.')
            await state.clear()
    else:
        stmt = insert(Users).values(
            id=USER_ID,
            username=message.forward_from.username,
            firstname=message.forward_from.first_name,
            lastname=message.forward_from.last_name,
            is_whitelist=True
        )
        await DB_SESSION.execute(statement=stmt)
        await DB_SESSION.commit()
        await DB_SESSION.close()

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(text='✅ Пользователь добавлен в whitelist.')
        await state.clear()

@router.message(FSMSTATES.STEP4_SENDMSG)
async def get_message_to_send(message: types.Message, bot: Bot, state: FSMContext):
    text = message.text

    sending_message = MessageWithMedia(text, None)
    file = open(ROOT_DIR + "/data/temp/message_to_send.json", 'w')
    file.write(json.dumps(sending_message.__dict__))
    file.close()

    a = await bot.send_message(chat_id=message.from_user.id, text='✅ Cообщение сохранено',
                               reply_to_message_id=message.message_id)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Да", callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="Нет", callback_data="no"))

    await a.edit_text("💡 Вы хотите добавить медиа (фото или видео) в рассылку?", reply_markup=keyboard.as_markup())
    await state.set_state(FSMSTATES.STEP5_SENDMSG_MEDIA)

@router.callback_query(FSMSTATES.STEP5_SENDMSG_MEDIA)
async def ask_for_media(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    DATA = call.data

    if DATA == 'yes':
        await call.message.answer(
            "📌 Пришлите одно медиа (видео или фото), я его добавлю и потом спрошу хотите ли добавить еще:")
        await call.message.delete()
        await state.set_state(FSMSTATES.STEP6_SENDMSG_MEDIA2)
    if DATA == 'no':
        await call.message.delete()
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='всем в белом списке', callback_data='send_whitelist'))
        keyboard.add(InlineKeyboardButton(text='все кроме белого списка', callback_data='send_without_whitelist'))
        keyboard.add(InlineKeyboardButton(text='всем пользователям', callback_data='send_all'))
        keyboard.adjust(1)

        await bot.send_message(chat_id=call.from_user.id, text='📌 выберите какой группе пользователей '
                                                               'отослать и я сделаю рассылку:',
                               reply_markup=keyboard.as_markup())
        await state.set_state(FSMSTATES.STEP7_SENDMSG_GROUP)

@router.message(FSMSTATES.STEP6_SENDMSG_MEDIA2)
async def save_media(message: types.Message, bot: Bot, state: FSMContext):
    file_id = None
    if message.photo is not None and len(message.photo) != 0:
        file_id = message.photo[-1].file_id
    elif message.video is not None:
        file_id = message.video.file_id
    try:
        await bot.get_file(file_id)
    except Exception as e:
        await message.answer("❌ Я не могу скачать этот файл, он превышает 20 мб, попробуйте снова или нажмите чтобы "
                             "выйти из текущего состояния")
        print(e)
        return

    file = open(ROOT_DIR + "/data/temp/message_to_send.json", 'r')
    sending_message = MessageWithMedia(**json.load(file))
    file.close()
    if sending_message.media is None:
        sending_message.media = []
    sending_message.media.append(file_id)
    file = open(ROOT_DIR + "/data/temp/message_to_send.json", 'w')
    file.write(json.dumps(sending_message.__dict__))
    file.close()
    a = await message.answer("сохранил")
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Да", callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="Нет", callback_data="no"))

    await a.edit_text("💡 Вы хотите добавить медиа (фото или видео) в рассылку?", reply_markup=keyboard.as_markup())
    await state.set_state(FSMSTATES.STEP5_SENDMSG_MEDIA)

@router.callback_query(FSMSTATES.STEP7_SENDMSG_GROUP)
async def sending(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    USER_ID: int = call.from_user.id
    DATA = call.data

    users = None

    if DATA == 'send_whitelist':
        stmt = select(Users).where(Users.is_whitelist is True)
        result = await DB_SESSION.execute(statement=stmt)
        users = result.all()
    if DATA == 'send_without_whitelist':
        stmt = select(Users).where(Users.is_whitelist is False)
        result = await DB_SESSION.execute(statement=stmt)
        users = result.all()
    if DATA == 'send_all':
        stmt = select(Users)
        result = await DB_SESSION.execute(statement=stmt)
        users = result.all()

    await call.message.delete()


    await bot.send_message(chat_id=USER_ID, text='начинаю рассылку')

    file = open(ROOT_DIR + "/data/temp/message_to_send.json", 'r')
    sending_message = MessageWithMedia(**json.load(file))
    file.close()

    status_cnt = 0

    if users:
        for user in users:
            status_cnt += 1
            try:
                if user[0].id != OWNER:
                    if sending_message.media is None:
                        await bot.send_message(chat_id=user[0].id, text=sending_message.text)
                    else:
                        album_builder = MediaGroupBuilder(
                            caption=sending_message.text
                        )

                        if sending_message.media:
                            for media in sending_message.media:
                                file = await bot.get_file(media)
                                if file.file_path.endswith(('.jpg', '.jpeg', '.png')) or "photos" in file.file_path:
                                    album_builder.add_photo(
                                        media=media
                                    )
                                elif file.file_path.endswith(
                                        ('.mp4', '.avi', '.mov', '.mkv')) or "video" in file.file_path:
                                    album_builder.add_video(
                                        media=media
                                    )

                            await bot.send_media_group(chat_id=user[0].id, media=album_builder.build())
            except Exception as e:
                print(e)
                stmt = update(Users).values(blocked=True)
                await DB_SESSION.execute(statement=stmt)
                await DB_SESSION.commit()
                await DB_SESSION.close()

    await bot.send_message(chat_id=call.from_user.id, text="✅ Готово!")
    await state.clear()

@router.message(FSMSTATES.STEP8_ADMIN_CHANNEL)
async def changer(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.chat.id

    await bot.delete_message(chat_id=USER_ID, message_id=message.message_id)

    try:
        print(message.forward_from_chat.type)
    except Exception:
        await bot.send_message(chat_id=USER_ID, text='❌ Сообщение переслано не из канала.')
    else:
        CHANNEL_ID: int = message.forward_from_chat.id
        CHANNEL_TITLE: str = message.forward_from_chat.title
        INVITE_LINK = await bot.get_chat(CHANNEL_ID)
        print(INVITE_LINK.invite_link)

        stmt = update(Data).values(
            channel_id=CHANNEL_ID,
            channel_title=CHANNEL_TITLE
        ).where(Data.id == 1)
        await DB_SESSION.execute(statement=stmt)
        await DB_SESSION.commit()
        await DB_SESSION.close()

        await bot.send_message(chat_id=message.from_user.id,
                               text=f"✅ Теперь я буду просить подписаться на:\n\n" + hlink(f"{message.forward_from_chat.title}", f"{(INVITE_LINK.invite_link)}"))

    await state.clear()

@router.callback_query(FSMSTATES.STEP9_BUTTONS)
async def changer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()

    DATA: str = call.data

    if DATA == "admin_back":
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
    if DATA == 'admin_usermenu_add':
        stmt = select(Buttons)
        result = await DB_SESSION.execute(statement=stmt)
        buttons = result.all()

        if len(buttons) == 3:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="➕ Добавить кнопку", callback_data="admin_usermenu_add"))
            keyboard.add(InlineKeyboardButton(text="➖ Удалить кнопку", callback_data="admin_usermenu_remove"))
            keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))
            keyboard.adjust(1)

            stmt = select(Buttons)
            result = await DB_SESSION.execute(statement=stmt)
            DATA = result.all()
            TEXT = ('💡 Здесь вы можете добавить три дополнительные кнопки. Текущие кнопки:\n\n'
                    f'<i>⚠ У вас уже добавлено три кнопки! {datetime.datetime.now()}\n\n</i>')

            if DATA:
                for button in DATA:
                    TEXT += f'<i>Имя</i>: {button[0].button_name}\n'

            await bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text=TEXT,
                reply_markup=keyboard.as_markup()
            )
            await state.set_state(FSMSTATES.STEP9_BUTTONS)
        else:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

            await bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text='💡 Введите имя кнопки:',
                reply_markup=keyboard.as_markup()
            )
            await state.set_state(FSMSTATES.STEP10_BUTTONS_ADD)
    if DATA == 'admin_usermenu_remove':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='💡 Введите имя кнопки:',
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP11_BUTTONS_REMOVE)

@router.message(FSMSTATES.STEP10_BUTTONS_ADD)
async def changer(message: types.Message, state: FSMContext):
    TEXT: str = message.text

    await state.set_data({"button_name": TEXT})

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

    await message.answer(
        text='💡 Введите текст кнопки:',
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(FSMSTATES.STEP12_BUTTONS_ADD_TEXT)

@router.message(FSMSTATES.STEP12_BUTTONS_ADD_TEXT)
async def download_audio(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id
    TEXT: str = message.text

    DATA: dict = await state.get_data()

    stmt = insert(Buttons).values(button_name=DATA["button_name"], button_text=TEXT)
    await DB_SESSION.execute(statement=stmt)
    await DB_SESSION.commit()
    await DB_SESSION.close()

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Добавить кнопку", callback_data="admin_usermenu_add"))
    keyboard.add(InlineKeyboardButton(text="➖ Удалить кнопку", callback_data="admin_usermenu_remove"))

    stmt = select(Buttons)
    result = await DB_SESSION.execute(statement=stmt)
    DATA = result.all()
    TEXT = ('💡 Здесь вы можете добавить три дополнительные кнопки. Текущие кнопки:\n\n'
            f'✅ Кнопка успешно добавлена!\n\n')

    if DATA:
        for button in DATA:
            TEXT += f'<i>Имя кнопки</i>: {button[0].button_name}\n'

    keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))
    keyboard.adjust(1)

    await bot.send_message(
        chat_id=USER_ID,
        text=TEXT,
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(FSMSTATES.STEP9_BUTTONS)

@router.message(FSMSTATES.STEP11_BUTTONS_REMOVE)
async def changer(message: types.Message, bot: Bot, state: FSMContext):
    TEXT: str = message.text

    stmt = select(Buttons).where(Buttons.button_name == TEXT)
    result = await DB_SESSION.execute(statement=stmt)
    button = result.scalar_one_or_none()

    if button:
        stmt = delete(Buttons).where(Buttons.button_name == TEXT)
        await DB_SESSION.execute(statement=stmt)
        await DB_SESSION.commit()
        await DB_SESSION.close()

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Добавить кнопку", callback_data="admin_usermenu_add"))
        keyboard.add(InlineKeyboardButton(text="➖ Удалить кнопку", callback_data="admin_usermenu_remove"))

        stmt = select(Buttons)
        result = await DB_SESSION.execute(statement=stmt)
        DATA = result.all()
        TEXT = ('💡 Здесь вы можете добавить три дополнительные кнопки. Текущие кнопки:\n\n'
                f'✅ Кнопка успешно удалена!\n\n')

        if DATA:
            for button in DATA:
                TEXT += f'<i>Имя кнопки</i>: {button[0].button_name}\n'

        keyboard.add(types.InlineKeyboardButton(text="← Назад", callback_data="admin_back"))
        keyboard.adjust(1)

        await bot.send_message(
            chat_id=message.from_user.id,
            text=TEXT,
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP9_BUTTONS)
    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="admin_back"))

        await message.answer(text='❌ Такой кнопки не найдено! Попробуйте ещё:', reply_markup=keyboard.as_markup())
        await state.set_state(FSMSTATES.STEP11_BUTTONS_REMOVE)











