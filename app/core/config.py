from pydantic import EmailStr, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

import secrets

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    API_V1_STR: str = "/api/v1"
    ENV: str
    SECRET_KEY: str = ""
    DATABASE_TYPE: str = "POSTGRES"

    SUPER_ADMIN_EMAIL: EmailStr
    SUPER_ADMIN_NAME: str
    SUPER_ADMIN_USER_NAME: str
    SUPER_ADMIN_PASSWORD: str

    GROQ_MODEL_NAME: str
    GROQ_API_KEY: str

    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, **values):
        super().__init__(**values)
        if self.ENV == "development":
            self.SECRET_KEY = "secret"
        else:
            self.SECRET_KEY = secrets.token_urlsafe(32)
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8


    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        if self.DATABASE_TYPE == "SQLITE":
            return "sqlite:///./test.db"
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
