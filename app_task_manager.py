
from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, update
import asyncio

from BOT.db.db import DB_SESSION
from BOT.db.tables import Channels, Users
from BOT.utils.create_videonote import VideoNote
from BOT.config import DATA_INPUT
from app_bot import BOT



TASK = None

async def start():
    print('Task manager start!')
    while True:

        stmt = select(Users).where(Users.task_status == True)
        result = await DB_SESSION.execute(statement=stmt)
        TASK = result.all()
        await DB_SESSION.close()

        if TASK:
            for task in TASK:
                USER_ID = task[0].id
                try:
                    print(f'Новая задача от: {task[0].username}')

                    TYPE = task[0].task['type']

                    VIDEONOTE = VideoNote(telegram_id=USER_ID, video_note_time=task[0].task['video_note_time'])

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
                        await BOT.send_video_note(
                            chat_id=USER_ID,
                            video_note=FSInputFile(DATA_INPUT + str(USER_ID) + '/video_final.mp4')
                        )

                    await BOT.send_message(chat_id=USER_ID,
                                           text='Чтобы убрать водяной знак нужно подписаться на @volna_telegram или оформить премиум подписку 🆒')

                    stmt = update(Users).values(task_status=False, task=None).where(Users.id == USER_ID)
                    await DB_SESSION.execute(statement=stmt)
                    await DB_SESSION.commit()
                    await DB_SESSION.close()

                except Exception as e:
                    print(e)

        print('Очередь пуста.')
        await asyncio.sleep(3)


asyncio.run(start())

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# try:
#     print('Task manager start!')
#     loop.run_until_complete(start())
# finally:
#     loop.run_until_complete(loop.shutdown_asyncgens())
#     loop.close()