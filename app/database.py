
from tortoise import Tortoise
from app.config import settings
from loguru import logger


TORTOISE_CONFIG = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.models.user", "app.models.role", "app.models.permission"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC"
}


async def init_db():
    logger.info("🔌 Подключение к PostgreSQL...")
    await Tortoise.init(config=TORTOISE_CONFIG)
    if settings.debug:
        await Tortoise.generate_schemas(safe=True)
        logger.success("✅ Таблицы созданы")
    else:
        logger.success("✅ Подключено к БД")


async def close_db():
    await Tortoise.close_connections()
    logger.success("🔌 Соединения закрыты")