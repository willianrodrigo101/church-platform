import asyncio
from sqlalchemy import text
from app.core.config.settings import settings
from app.core.database.connection import engine

async def main():
    print(f"Aplicacao: {settings.APP_NAME}")
    print(f"Banco: {settings.POSTGRES_DB}")
    print(f"Host: {settings.POSTGRES_HOST}")

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print(f"Resultado do teste: {result.scalar()}")
            print("CONFIGURACAO OFICIAL FUNCIONANDO!")
    except Exception as error:
        print(f"ERRO: {type(error).__name__}: {error}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
