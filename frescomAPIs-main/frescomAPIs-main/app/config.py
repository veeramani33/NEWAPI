from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_service_name: str
    database_provider: str
    database_driver: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
