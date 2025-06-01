from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Investing Chat Bot"
    env: str = "dev"

    class Config:
        env_file = ".env"

settings = Settings()