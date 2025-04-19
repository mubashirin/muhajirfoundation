import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    API_V1_STR: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str | None = None
    POOL_SIZE: int
    MAX_OVERFLOW: int

    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: str

    # CORS
    CORS_ORIGINS: list[str]
    CORS_METHODS: list[str]
    CORS_HEADERS: list[str]

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
    ) 