import logging
from bot import bot, disp
from handlers import routers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Регистрируем роуты
    for router in routers:
        disp.include_router(router)

    await disp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
