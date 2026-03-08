import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Secrets
    SECRET_KEY: str
    FINGERPRINT_SALT: str
    IP_HASH_SALT: str

    # Google Gemini — REMOVED. AI scoring has been disabled.
    # GEMINI_API_KEY is no longer required and is ignored if present.
    GEMINI_API_KEY: str = ""

    # Cloudflare Turnstile
    CLOUDFLARE_TURNSTILE_SITE_KEY: str
    CLOUDFLARE_TURNSTILE_SECRET_KEY: str

    # Resend Email
    RESEND_API_KEY: str

    # Admin
    ADMIN_PASSWORD_HASH: str
    ADMIN_SESSION_SECRET: str
    ADMIN_PATH: str = "/manage"
    ADMIN_IP_ALLOWLIST: str = "127.0.0.1,::1"
    ADMIN_ALERT_EMAIL: str

    # Frontend
    NEXT_PUBLIC_API_BASE_URL: str = "http://localhost:8000"
    NEXT_PUBLIC_TURNSTILE_SITE_KEY: str
    NEXT_PUBLIC_ADS_ENABLED: bool = False

    # Scoring constants
    BAYESIAN_M: int = 10  # Minimum vote threshold

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_length(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError("SECRET_KEY must be at least 64 characters")
        return v

    @field_validator("FINGERPRINT_SALT", "IP_HASH_SALT")
    @classmethod
    def salt_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Salts must be at least 32 characters")
        return v

    @field_validator("ADMIN_SESSION_SECRET")
    @classmethod
    def admin_session_secret_length(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError("ADMIN_SESSION_SECRET must be at least 64 characters")
        return v

    def get_admin_ip_allowlist(self) -> List[str]:
        return [ip.strip() for ip in self.ADMIN_IP_ALLOWLIST.split(",") if ip.strip()]


settings = Settings()
