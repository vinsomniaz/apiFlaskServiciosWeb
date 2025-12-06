import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3307"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "fintech_api")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "Kz9V!mQ2pR7#sL1@xY4nT8uE5cD0hA3bG6jF9wZ2")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "Fintech Alertas <no-reply@localhost>")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
        )

settings = Settings()
