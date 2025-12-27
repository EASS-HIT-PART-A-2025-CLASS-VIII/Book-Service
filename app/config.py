from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    app_title: str = "Book Service API"
    app_version: str = "1.0.0"
    app_description: str = "A REST API for managing a book collection"
    
    class Config:
        env_file = ".env"


settings = Settings()