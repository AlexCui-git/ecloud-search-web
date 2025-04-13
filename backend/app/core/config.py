from pydantic import BaseSettings

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    ALLOWED_ORIGINS: list = ["http://localhost:5173"]
    DEBUG: bool = True

settings = Settings()