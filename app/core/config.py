from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

import secrets

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = "this is secret key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8


    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return f"postgresql+psycopg://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # return PostgresDsn.build(
        #     scheme="postgresql+psycopg",
        #     username=self.POSTGRES_USER,
        #     password=self.POSTGRES_PASSWORD,
        #     host=self.POSTGRES_SERVER,
        #     port=self.POSTGRES_PORT,
        #     path=f"/{self.POSTGRES_DB}",
        # )


settings = Settings()
