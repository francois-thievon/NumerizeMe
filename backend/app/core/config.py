from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "NumerizeMe"
    PROJECT_VERSION: str = "1.0.0"
    
    # Configuration Base de données
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/numerize_me"
    
    # Configuration JWT
    SECRET_KEY: str = "your-secret-key-here"  # À changer en production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
