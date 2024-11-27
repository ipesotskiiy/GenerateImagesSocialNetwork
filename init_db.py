import asyncio
from settings import engine, Base
from posts.models import Post
from auth.models import User

async def init_db():
    async with engine.begin() as conn:
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы успешно созданы.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
    try:
        loop.run_until_complete(init_db())  # Запускаем асинхронную функцию
    finally:
        loop.close()