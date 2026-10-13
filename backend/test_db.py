
import asyncio
import getpass

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    password = getpass.getpass("Senha do PostgreSQL: ")

    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username="postgres",
        password=password,
        host="127.0.0.1",
        port=5432,
        database="church_platform",
    )

    engine = create_async_engine(
        database_url,
        echo=True,
        pool_pre_ping=True,
    )

    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT version()")
            )

            print("\nCONEXÃO SQLALCHEMY OK!")
            print(result.scalar())

    except Exception as error:
        print("\nERRO NA CONEXÃO SQLALCHEMY:")
        print(type(error).__name__)
        print(str(error))

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
