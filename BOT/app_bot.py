
from typing import NoReturn


from aiogram.types import BotCommandScopeDefault, BotCommand, FSInputFile

import asyncio
from handlers.router_first import router as router_first
from config import TOKEN, DATA_INPUT

from aiogram import Bot, Dispatcher


BOT = Bot(token=TOKEN, parse_mode="HTML")
DP = Dispatcher()
DP.include_router(router_first)



async def main() -> NoReturn:
    print('Bot start!')

    await BOT.set_my_commands([
        BotCommand(command='start', description='✅ Начальное меню, сброс диалога')
    ],
        scope=BotCommandScopeDefault()
    )

    await DP.start_polling(BOT)

async def manager() -> NoReturn:
    print('Bot start!')

    await BOT.set_my_commands([
        BotCommand(command='start', description='✅ Начальное меню, сброс диалога')
    ],
        scope=BotCommandScopeDefault()
    )

    await DP.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())


