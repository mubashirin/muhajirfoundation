import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Muhajir Foundation API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API для Muhajir Foundation"
    DEBUG: bool
    API_V1_STR: str = "/api/v1"
    API_DOCS_STR: str = "/docs"
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: int
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "muhajirfoundation")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    POOL_SIZE: int
    MAX_OVERFLOW: int

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"

    # CORS
    CORS_ORIGINS: list[str]
    CORS_METHODS: list[str]
    CORS_HEADERS: list[str]

    # Email settings
    MAIL_USERNAME: str = "your-email@gmail.com"
    MAIL_PASSWORD: str = "your-app-password"
    MAIL_FROM: str = "your-email@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # Pinata
    PINATA_API_KEY: str
    PINATA_API_SECRET: str

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


def load_yaml_config() -> dict:
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found")
    
    with open(config_path) as f:
        return yaml.safe_load(f)


@lru_cache()
def get_settings() -> Settings:
    yaml_config = load_yaml_config()
    
    return Settings(
        PROJECT_NAME=yaml_config["app"]["name"],
        VERSION=yaml_config["app"]["version"],
        DEBUG=yaml_config["app"]["debug"],
        API_V1_STR=yaml_config["app"]["api_v1_str"],
        
        SECRET_KEY=yaml_config["security"]["secret_key"],
        ALGORITHM=yaml_config["security"]["algorithm"],
        ACCESS_TOKEN_EXPIRE_MINUTES=yaml_config["security"]["access_token_expire_minutes"],
        
        POSTGRES_SERVER=yaml_config["database"]["host"],
        POSTGRES_PORT=yaml_config["database"]["port"],
        POSTGRES_USER=yaml_config["database"]["user"],
        POSTGRES_PASSWORD=yaml_config["database"]["password"],
        POSTGRES_DB=yaml_config["database"]["name"],
        POOL_SIZE=yaml_config["database"]["pool_size"],
        MAX_OVERFLOW=yaml_config["database"]["max_overflow"],
        
        LOG_LEVEL=yaml_config["logging"]["level"],
        LOG_FORMAT=yaml_config["logging"]["format"],
        LOG_FILE=yaml_config["logging"]["file"],
        
        CORS_ORIGINS=yaml_config["cors"]["origins"],
        CORS_METHODS=yaml_config["cors"]["methods"],
        CORS_HEADERS=yaml_config["cors"]["headers"],
        
        MAIL_USERNAME=yaml_config["email"]["username"],
        MAIL_PASSWORD=yaml_config["email"]["password"],
        MAIL_FROM=yaml_config["email"]["from"],
        MAIL_PORT=yaml_config["email"]["port"],
        MAIL_SERVER=yaml_config["email"]["server"],
        
        PINATA_API_KEY=yaml_config["pinata_api_key"],
        PINATA_API_SECRET=yaml_config["pinata_api_secret"]
    ) 