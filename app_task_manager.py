import time

from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, update, delete, insert
import asyncio

from BOT.db.db import DB_SESSION
from BOT.db.tables import Channels, Users, Tasks
from BOT.utils.create_videonote import VideoNote
from BOT.config import DATA_INPUT, OWNER
from app_bot import BOT


async def start():
    print('Task manager start!')
    while True:

        stmt = select(Tasks)
        result = await DB_SESSION.execute(statement=stmt)
        TASKS = result.all()
        await DB_SESSION.close()

        if TASKS:

            for task in TASKS:
                ID: int = task[0].id
                USER_ID: int = task[0].user_id
                TYPE: str = task[0].task_type
                VIDEO_NOTE_TIME: int = task[0].video_note_time

                MSG = await BOT.send_message(chat_id=USER_ID, text='⌛ <i>Создаю ваш кружочек...</i>')
                MSG_ID: int = MSG.message_id

                print(f'Новая задача "{ID}" от: {USER_ID}')

                try:

                    VIDEONOTE = VideoNote(telegram_id=USER_ID, video_note_time=VIDEO_NOTE_TIME)

                    if TYPE == '1':
                        await VIDEONOTE.crop()
                        await VIDEONOTE.compose()
                        await VIDEONOTE.add_texture()
                        await VIDEONOTE.add_watermark()
                        await VIDEONOTE.write_to_disk()
                    if TYPE == '2':
                        await VIDEONOTE.crop()
                        await VIDEONOTE.add_watermark()
                        await VIDEONOTE.write_to_disk()

                    if TYPE == '3':
                        await VIDEONOTE.crop()
                        await VIDEONOTE.compose()
                        await VIDEONOTE.add_texture()
                        await VIDEONOTE.add_audio()
                        await VIDEONOTE.add_watermark()
                        await VIDEONOTE.write_to_disk()
                    if TYPE == '4':
                        await VIDEONOTE.crop()
                        await VIDEONOTE.add_audio()
                        await VIDEONOTE.add_watermark()
                        await VIDEONOTE.write_to_disk()

                    stmt = select(Channels).where(Channels.user_id == USER_ID)
                    result = await DB_SESSION.execute(statement=stmt)
                    CHANNELS = result.all()

                    if CHANNELS:
                        keyboard = InlineKeyboardBuilder()
                        for channel in CHANNELS:
                            keyboard.add(InlineKeyboardButton(text=channel[0].channel_name,
                                                              callback_data='CHANNEL:' + str(channel[0].id)))
                        keyboard.adjust(1)
                        await BOT.send_video_note(
                            chat_id=USER_ID,
                            video_note=FSInputFile(DATA_INPUT + str(USER_ID) + '/video_final.mp4'),
                            reply_markup=keyboard.as_markup()
                        )
                    else:
                        keyboard = InlineKeyboardBuilder()
                        keyboard.add(InlineKeyboardButton(text='➕ Привязать канал', callback_data='channel_add'))
                        keyboard.adjust(1)
                        await BOT.send_video_note(
                            chat_id=USER_ID,
                            video_note=FSInputFile(DATA_INPUT + str(USER_ID) + '/video_final.mp4'),
                            reply_markup=keyboard.as_markup()
                        )


                    await BOT.delete_message(chat_id=USER_ID, message_id=MSG_ID)
                    await BOT.send_message(chat_id=USER_ID,
                                           text='<i>Чтобы убрать водяной знак нужно подписаться на @volna_telegram или оформить премиум подписку 🆒</i>')
                    time.sleep(.1)


                    stmt = delete(Tasks).where(Tasks.user_id == USER_ID)
                    await DB_SESSION.execute(statement=stmt)
                    await DB_SESSION.commit()
                    await DB_SESSION.close()

                    time.sleep(.1)

                    print(f'Задача "{ID}" завершена.')

                except Exception as e:
                    await BOT.send_message(chat_id=OWNER,
                                           text=f'<i>⚠ Ошибка обработки задания {ID}:</i> {e}')



asyncio.run(start())

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# try:
#     print('Task manager start!')
#     loop.run_until_complete(start())
# finally:
#     loop.run_until_complete(loop.shutdown_asyncgens())
#     loop.close()