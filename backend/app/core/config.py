from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Data Analyst API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_host: str = "db"
    mysql_port: int = 3306
    mysql_db: str = "ai_data_analyst"

    upload_dir: str = str(BASE_DIR / "storage" / "uploads")
    model_dir: str = str(BASE_DIR / "storage" / "models")
    report_dir: str = str(BASE_DIR / "storage" / "reports")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
