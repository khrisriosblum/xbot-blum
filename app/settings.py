from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # -------- Core bot config --------
    EXCEL_PATH: str = Field(default="/data/tracks.xlsx")   # si usas Free sin disco: /app/data/tracks.xlsx
    TIMEZONE: str = Field(default="Europe/Madrid")
    POST_TIMES: str = Field(default="12:00,15:00,18:00,21:00,00:00")
    JITTER_MINUTES: int = Field(default=15)
    SLEEP_BEFORE_PUBLISH: int = Field(default=15)
    DEDUP_DAYS: int = Field(default=70)
    RECENT_DAYS: int = Field(default=2)
    SOUND_CLOUD_EVERY_N_DAYS: int = Field(default=3)
    SPOTIFY_TOPS_EVERY_N_DAYS: int = Field(default=10)
    START_DATE: str = Field(default="2025-01-01")

    # -------- X (Twitter) credentials --------
    X_API_KEY: str = Field(default="")
    X_API_SECRET: str = Field(default="")
    X_ACCESS_TOKEN: str = Field(default="")
    X_ACCESS_SECRET: str = Field(default="")
    X_USERNAME: str = Field(default="")  # opcional (para construir URL legible del tweet)

    # -------- Runtime --------
    DRY_RUN: bool = Field(default=True)
    DB_PATH: str = Field(default="/data/bot.db")           # si Free sin disco: /app/bot.db
    PORT: int = Field(default=8000)

    # -------- Email (SMTP/Gmail) --------
    EMAIL_ENABLED: bool = Field(default=True)  # activa envío de emails
    EMAIL_FROM: str = Field(default="blumriosblum@gmail.com")
    EMAIL_TO: str = Field(default="blumriosblum@gmail.com")
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)         # 587 = TLS, 465 = SSL
    SMTP_USER: str = Field(default="blumriosblum@gmail.com")
    SMTP_PASS: str = Field(default="xaey rclm gxan ywyd")  # tu App Password de Gmail (como pediste)
    SMTP_TLS: bool = Field(default=True)
    EMAIL_ON_DRY_RUN: bool = Field(default=False)  # True = también envía email en pruebas
    EMAIL_TEXT_ONLY: bool = Field(default=True)    # True = el email lleva SOLO el texto exacto del post

    # Carga de variables desde .env (si existe)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()

