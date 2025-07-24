import asyncio
from aiogram import Bot, Dispatcher

from bot.handlers import router

async def main():
    bot = Bot(token='8007211189:AAHJ0Ae9QufEAgZOlvTdycMjwSzhqLs5rTw', proxy='http://your_proxy:port')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot Stopped. \nMessage - Папочка, я сделала что-то не так? Прости меня!")
    except Exception as e:
        print(f"Обшибка: {e}")