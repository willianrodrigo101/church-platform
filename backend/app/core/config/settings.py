from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    from pydantic import field_validator

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def convert_db_url(cls, v):
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    POSTGRES_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()


