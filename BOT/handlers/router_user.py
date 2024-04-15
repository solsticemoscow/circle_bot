from aiogram import Bot

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import insert, select, delete

from BOT.db.db import DB_SESSION
from BOT.db.tables import Channels
from BOT.handlers.fsm_states import FSMSTATES

router = Router()

@router.message(FSMSTATES.STEP13_USER_CHANNEL)
async def changer(message: types.Message, bot: Bot, state: FSMContext):
    IS_USER_ADMIN = False
    IS_BOT_ADMIN = False

    try:
        CHANNEL = message.forward_from_chat.type
        CHANNEL_ID = message.forward_from_chat.id
    except Exception:
        USER_ID: int = message.chat.id
        await bot.send_message(chat_id=USER_ID, text='❌ Сообщение переслано не из канала.')
    else:
        BOT = await bot.me()
        BOT_ID: int = BOT.id

        try:
            admin_list = await bot.get_chat_administrators(CHANNEL_ID)
            for admin in admin_list:
                if admin.user.id == message.from_user.id:
                    IS_USER_ADMIN = True
        except Exception as e:
            print(e)

        try:
            admin_list = await bot.get_chat_administrators(CHANNEL_ID)
            for admin in admin_list:
                if BOT_ID == admin.user.id:
                    IS_BOT_ADMIN = True
        except Exception as e:
            print(e)

        if IS_BOT_ADMIN and IS_USER_ADMIN:
            if CHANNEL == 'channel':
                USER_ID: int = message.chat.id
                CHANNEL_ID: int = message.forward_from_chat.id

                stmt = select(Channels).where(Channels.user_id == USER_ID, Channels.id == CHANNEL_ID)
                result = await DB_SESSION.execute(statement=stmt)
                CHANNEL = result.scalar_one_or_none()

                if CHANNEL:
                    stmt = delete(Channels).where(Channels.user_id == USER_ID, Channels.id == CHANNEL_ID)
                    await DB_SESSION.execute(statement=stmt)
                    await DB_SESSION.commit()
                    await DB_SESSION.close()
                    await bot.send_message(chat_id=USER_ID, text='✅ Канал успешно удалён!')
                else:
                    stmt = insert(Channels).values(
                        id=CHANNEL_ID,
                        channel_name=message.forward_from_chat.title,
                        user_id=USER_ID)
                    await DB_SESSION.execute(statement=stmt)
                    await DB_SESSION.commit()
                    await DB_SESSION.close()
                    await bot.send_message(chat_id=USER_ID, text='✅ Канал успешно привязан!')
            else:
                USER_ID: int = message.chat.id
                await bot.send_message(chat_id=USER_ID, text='❌ Сообщение переслано не из канала.')
        else:
            USER_ID: int = message.chat.id
            await bot.send_message(chat_id=USER_ID, text='❌ Вы или бот не являетесь администратором канала.')


    await state.clear()




