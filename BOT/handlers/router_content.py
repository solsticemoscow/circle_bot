import os
import shutil
from typing import NoReturn

from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydub import AudioSegment
from sqlalchemy import update, select, insert

from BOT.config import DATA_INPUT, ROOT_DIR
from BOT.db.db import DB_SESSION
from BOT.db.tables import Users, Tasks
from BOT.handlers.fsm_states import FSMSTATES


router = Router()


@router.callback_query(FSMSTATES.STEP_TASK_MUSIC)
async def step_task_music(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    USER_ID: int = call.message.chat.id
    DATA: str = call.data

    DATA_STATE = await state.get_data()

    if DATA == 'yes':
        await state.set_data(
            {"video_note_time": DATA_STATE["video_note_time"],
             "round": DATA_STATE["round"]
             }
        )
        await bot.edit_message_text(
            chat_id=USER_ID,
            message_id=call.message.message_id,
            text='⏳ Пришлите аудио:'
        )
        await state.set_state(FSMSTATES.STEP_TASK_MUSIC_GET)
    if DATA == 'no':

        stmt = select(Tasks)
        result = await DB_SESSION.execute(statement=stmt)
        TASKS = result.all()
        await DB_SESSION.close()

        if TASKS:
            LEN: int = len(TASKS)
            print(f'Длина очереди: {LEN}')
            if LEN >= 1:
                await bot.send_message(chat_id=USER_ID, text=f'⌚ Ваша задача в очереди: {LEN + 1}\n\n'
                                                             f'Ожидайте...')

        DATA_STATE = await state.get_data()

        if DATA_STATE['round'] is True:

            stmt = insert(Tasks).values(
                video_note_time=int(DATA_STATE["video_note_time"]),
                user_id=USER_ID,
                task_type='1'
            )
            await DB_SESSION.execute(statement=stmt)
            await DB_SESSION.commit()
            await DB_SESSION.close()

        else:
            stmt = insert(Tasks).values(
                video_note_time=int(DATA_STATE["video_note_time"]),
                user_id=USER_ID,
                task_type='2'
            )
            await DB_SESSION.execute(statement=stmt)
            await DB_SESSION.commit()
            await DB_SESSION.close()

        await state.clear()

@router.message(FSMSTATES.STEP_TASK_MUSIC_GET)
async def get_music(message: types.Message, bot: Bot, state: FSMContext) -> NoReturn:
    USER_ID: int = message.from_user.id

    if message.audio:
        try:
            file = await bot.get_file(message.audio.file_id)
        except Exception:
            await message.answer(
                "❌ я не могу работать с этим файлом. Я могу скачать файл до 20 мегабайт, а этот файл весит больше")
            return
        try:
            await bot.download_file(file_path=file.file_path,
                                    destination=DATA_INPUT + str(USER_ID) + '/' + message.audio.file_name)
            AudioSegment.from_file(DATA_INPUT + str(USER_ID) + '/' + message.audio.file_name).export(
                out_f=DATA_INPUT + str(USER_ID) + '/music.mp3',
                bitrate="256k",
                format="mp3")
        except Exception as e:
            print(e)

        await bot.send_message(chat_id=USER_ID, text='✅ Получил вашу аудиодорожку.')

        stmt = select(Tasks)
        result = await DB_SESSION.execute(statement=stmt)
        TASKS = result.all()
        await DB_SESSION.close()

        if TASKS:
            LEN: int = len(TASKS)
            print(f'Длина очереди: {LEN}')
            if LEN >= 1:
                await bot.send_message(chat_id=USER_ID, text=f'⌚ Ваша задача в очереди: {LEN + 1}\n\n'
                                                             f'Ожидайте...')
        DATA_STATE = await state.get_data()

        if DATA_STATE["round"] is True:
            stmt = insert(Tasks).values(
                video_note_time=int(DATA_STATE["video_note_time"]),
                user_id=USER_ID,
                task_type='3'
            )
            await DB_SESSION.execute(statement=stmt)
            await DB_SESSION.commit()
            await DB_SESSION.close()

        else:
            stmt = insert(Tasks).values(
                video_note_time=int(DATA_STATE["video_note_time"]),
                user_id=USER_ID,
                task_type='4'
            )
            await DB_SESSION.execute(statement=stmt)
            await DB_SESSION.commit()
            await DB_SESSION.close()

        await state.clear()

    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="⚠ Вы прислали не аудио файл! Попробуйте заново:"
        )
        await state.set_state(FSMSTATES.STEP_TASK_MUSIC_GET)


@router.callback_query(FSMSTATES.STEP_TASK_DURATION)
async def get_duration(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    USER_ID: int = call.message.chat.id

    video_note_time = call.data
    await state.set_data({"video_note_time": video_note_time})

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Да", callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="➖ Нет", callback_data="no"))
    keyboard.adjust(1)

    await bot.edit_message_text(
        chat_id=USER_ID,
        message_id=call.message.message_id,
        text="💡 Хотите наложить обводку на ваш кружочек?",
        reply_markup=keyboard.as_markup())

    await state.set_state(FSMSTATES.STEP_TASK_ROUND)


@router.callback_query(FSMSTATES.STEP_TASK_ROUND)
async def get_duration(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    USER_ID: int = call.message.chat.id
    DATA = call.data

    DATA_STATE = await state.get_data()


    if DATA == 'yes':
        await state.set_data(
            {"video_note_time": DATA_STATE["video_note_time"],
             "round": True
             }
        )

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Встроенные обводки", callback_data="builtin"))
        keyboard.add(InlineKeyboardButton(text="Свой дизайн 🆒", callback_data="own"))
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
        keyboard.adjust(1)

        await bot.edit_message_text(
            chat_id=USER_ID,
            message_id=call.message.message_id,
            text="💡 Вы хотите использовать встроенные в бота шаблоны обводок или прислать свой дизайн?",
            reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_ROUND_QA)

    if DATA == 'no':
        await state.set_data(
            {"video_note_time": DATA_STATE["video_note_time"],
             "round": False
             }
        )

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Добавить музыку", callback_data="yes"))
        keyboard.add(InlineKeyboardButton(text="➖ Не добавлять", callback_data="no"))
        keyboard.adjust(1)

        await bot.send_message(chat_id=USER_ID,
                               text="💡 Вы хотите наложить музыку?\n<i>(бот принимает только файлы, которые отображаются в тг как "
                                    "аудиофайл, например mp3 и другие)</i>",
                               reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_MUSIC)


@router.callback_query(FSMSTATES.STEP_TASK_ROUND_QA)
async def get_duration(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    USER_ID: int = call.message.chat.id
    DATA = call.data

    DATA_STATE = await state.get_data()
    await state.set_data(
        {"video_note_time": DATA_STATE["video_note_time"],
         "round": DATA_STATE["round"]
         }
    )

    if DATA == 'back':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="➕ Да", callback_data="yes"))
        keyboard.add(InlineKeyboardButton(text="➖ Нет", callback_data="no"))
        keyboard.adjust(1)

        await bot.edit_message_text(
            chat_id=USER_ID,
            message_id=call.message.message_id,
            text="💡 Хотите наложить обводку на ваш кружочек?",
            reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_ROUND)
    if DATA == 'own':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))

        gif = FSInputFile(ROOT_DIR + "/data/help_buy_sub.gif")
        await bot.send_video(chat_id=USER_ID,
                             caption="🆒 Добавление своих обводок и элементов доступно для пользователей с оформленной подпиской.\n\n"
                                     "Для оплаты премиум функции — напишите @oksankazhu\n\n"
                                     "Или нажмите на кнопку в нижней панели «оформить подписку», чтобы узнать подробности",
                             video=gif,
                             reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_TEXTURE)
    if DATA == 'builtin':
        keyboard = InlineKeyboardBuilder()
        for i in range(1, 6):
            keyboard.add(InlineKeyboardButton(text=str(i), callback_data=str(i)))
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
        keyboard.adjust(5, 1)

        photo = FSInputFile(ROOT_DIR + "/data/textures_choose.PNG")
        await bot.send_photo(chat_id=USER_ID, caption="💡 Выберите обводку:", photo=photo,
                             reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_TEXTURE)


@router.callback_query(FSMSTATES.STEP_TASK_TEXTURE)
async def get_duration(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()

    USER_ID: int = call.message.chat.id
    DATA = call.data

    if DATA == 'back':
        await bot.delete_message(chat_id=USER_ID, message_id=call.message.message_id)

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔘 Встроенные обводки", callback_data="builtin"))
        keyboard.add(InlineKeyboardButton(text="🆒 Свой дизайн ", callback_data="own"))
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))
        keyboard.adjust(1)

        await bot.send_message(
            chat_id=USER_ID,
            text="💡 Вы хотите использовать встроенные в бота шаблоны обводок или прислать свой дизайн?",
            reply_markup=keyboard.as_markup())

        await state.set_state(FSMSTATES.STEP_TASK_ROUND_QA)

    else:
        await bot.delete_message(chat_id=USER_ID, message_id=call.message.message_id)

        DATA_STATE = await state.get_data()
        await state.set_data(
            {"video_note_time": DATA_STATE["video_note_time"],
             "round": DATA_STATE["round"]
             }
        )

        shutil.copyfile(ROOT_DIR + f'/data/textures/{DATA}.PNG', ROOT_DIR + f"/data/input/{USER_ID}/texture.png")

        photo = FSInputFile(ROOT_DIR + "/data/texture_help.PNG")
        await bot.send_photo(chat_id=USER_ID,
                             caption="💡 Пришлите квадратную картинку, цвет или дизайн которой применится к выбранной обводке:",
                             photo=photo
                             )

        await state.set_state(FSMSTATES.STEP_TASK_ROUND_IMAGE)


@router.message(FSMSTATES.STEP_TASK_ROUND_IMAGE)
async def get_shape(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id

    DATA_STATE = await state.get_data()
    await state.set_data(
        {"video_note_time": DATA_STATE["video_note_time"],
         "round": DATA_STATE["round"]
         }
    )
    await bot.delete_message(chat_id=USER_ID, message_id=message.message_id)
    await bot.send_message(chat_id=USER_ID, text='✅ Получил вашу картинку для обводки.')

    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        pass

    try:
        file = await bot.get_file(message.photo[-1].file_id)
    except Exception:
        await message.answer(
            "❌ я не могу работать с этим файлом. Я могу скачать файл до 20 мегабайт, а этот файл весит больше")
        return

    await bot.download_file(file.file_path, DATA_INPUT + str(USER_ID) + '/image_for_texture.jpg')

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Добавить музыку", callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text="➖ Не добавлять", callback_data="no"))
    keyboard.adjust(1)

    await bot.send_message(chat_id=USER_ID,
                           text="💡 Вы хотите наложить музыку?\n<i>(бот принимает только файлы, которые отображаются в тг как "
                                "аудиофайл, например mp3 и другие)</i>",
                           reply_markup=keyboard.as_markup())

    await state.set_state(FSMSTATES.STEP_TASK_MUSIC)


@router.message(F.video)
async def get_video(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id

    stmt = select(Tasks).where(Tasks.user_id == USER_ID)
    result = await DB_SESSION.execute(statement=stmt)
    TASK = result.scalar_one_or_none()


    if TASK:
        await message.answer(
            "⚠ У вас в обработке есть задание. Дождитесь его выполнения и присылайте новые файлы.")
    else:
        try:
            shutil.rmtree(DATA_INPUT + str(USER_ID))
        except Exception as e:
            print(e)

        if not os.path.exists(DATA_INPUT + str(USER_ID)):
            os.makedirs(DATA_INPUT + str(USER_ID))

        if message.video.duration > 60:
            await message.answer(
                text="❌ Я не могу обработать это видео, потому что оно длинее чем одна минута, пожалуйста,"
                     " пришлите видео длительностью до одной минуты")
        else:
            try:
                file = await bot.get_file(message.video.file_id)
                await bot.download_file(file.file_path, DATA_INPUT + str(USER_ID) + '/video.mp4')

                await message.answer(text="✅ Получил видео.")

                keyboard = InlineKeyboardBuilder()
                keyboard.add(InlineKeyboardButton(text="1 сек", callback_data="1"))
                for step in range(0, 60, 5):
                    if step != 0:
                        keyboard.add(InlineKeyboardButton(text=str(step) + ' сек', callback_data=str(step)))
                keyboard.add(InlineKeyboardButton(text="59 сек", callback_data="59"))
                keyboard.adjust(1)

                await bot.send_message(
                    chat_id=USER_ID,
                    text="💡 Выберите длительность видео:",
                    reply_markup=keyboard.as_markup()
                )
                await state.set_state(FSMSTATES.STEP_TASK_DURATION)
            except Exception:
                await message.answer(
                    "❌ я не могу работать с этим файлом. Я могу скачать файл до 20 мегабайт, а этот файл весит больше")


@router.message(F.animation)
async def get_photo(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id

    stmt = select(Tasks).where(Tasks.user_id == USER_ID)
    result = await DB_SESSION.execute(statement=stmt)
    TASK = result.scalar_one_or_none()


    if TASK:
        await message.answer(
            "⚠ У вас в обработке есть задание. Дождитесь его выполнения и присылайте новые файлы.")
    else:
        try:
            shutil.rmtree(DATA_INPUT + str(USER_ID))
        except Exception as e:
            print(e)

        if not os.path.exists(DATA_INPUT + str(USER_ID)):
            os.makedirs(DATA_INPUT + str(USER_ID))

        try:
            file = await bot.get_file(message.animation.file_id)
        except Exception:
            await message.answer(
                "я не могу работать с этим файлом. Я могу скачать файл до 20 мегабайт, а этот файл весит больше")
            return
        await bot.download_file(file.file_path, DATA_INPUT + str(USER_ID) + '/animation.gif')

        await message.answer(text="✅ Получил анимацию.")

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="1 сек", callback_data="1"))
        for step in range(0, 60, 5):
            if step != 0:
                keyboard.add(InlineKeyboardButton(text=str(step) + ' сек', callback_data=str(step)))
        keyboard.add(InlineKeyboardButton(text="59 сек", callback_data="59"))
        keyboard.adjust(1)

        await bot.send_message(
            chat_id=USER_ID,
            text="💡 Выберите длительность видео:",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP_TASK_DURATION)


@router.message(F.photo)
async def get_photo(message: types.Message, bot: Bot, state: FSMContext):
    USER_ID: int = message.from_user.id

    stmt = select(Tasks).where(Tasks.user_id == USER_ID)
    result = await DB_SESSION.execute(statement=stmt)
    TASK = result.scalar_one_or_none()


    if TASK:
        await message.answer(
            "⚠ У вас в обработке есть задание. Дождитесь его выполнения и присылайте новые файлы.")
    else:
        try:
            shutil.rmtree(DATA_INPUT + str(USER_ID))
        except Exception as e:
            print(e)

        if not os.path.exists(DATA_INPUT + str(USER_ID)):
            os.makedirs(DATA_INPUT + str(USER_ID))

        photo = message.photo
        try:
            file = await bot.get_file(photo[len(photo) - 1].file_id)
        except Exception:
            await message.answer(
                "я не могу работать с этим файлом. Я могу скачать файл до 20 мегабайт, а этот файл весит больше")
            return
        await bot.download_file(file.file_path, DATA_INPUT + str(USER_ID) + '/image.jpg')

        await message.answer(text="✅ Получил фото.")

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="1 сек", callback_data="1"))
        for step in range(0, 60, 5):
            if step != 0:
                keyboard.add(InlineKeyboardButton(text=str(step) + ' сек', callback_data=str(step)))
        keyboard.add(InlineKeyboardButton(text="59 сек", callback_data="59"))
        keyboard.adjust(1)

        await bot.send_message(
            chat_id=USER_ID,
            text="💡 Выберите длительность видео:",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(FSMSTATES.STEP_TASK_DURATION)



