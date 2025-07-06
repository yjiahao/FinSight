from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Investing Chat Bot"
    env: str = "dev"
    redis_url: str = "redis://localhost:6379/0"

    groq_api_key: str
    google_api_key: str
    tavily_api_key: str

    # for password hashing and JWT
    jwt_secret_key: str
    algorithm: str = "HS256"

settings = Settings()