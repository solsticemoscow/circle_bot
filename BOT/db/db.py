from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DB_POSTGRES

ENGINE = create_async_engine(
    DB_POSTGRES,
    echo=True,
    pool_pre_ping=True
)

async_session = async_sessionmaker(ENGINE, autoflush=False, expire_on_commit=True)

DB_SESSION = async_session()

