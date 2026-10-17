import secrets

from functools import lru_cache

from pydantic import Field, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True,

        extra="ignore",

    )

    APP_NAME: str = "ApexiveAI MPT Automation Platform"

    APP_ENV: str = "development"

    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    CONTROL_API_TOKEN: str

    WEBHOOK_HMAC_SECRET: str

    MPT_SOURCE_STATUS: str = "NOT_CONNECTED"

    MPT_API_BASE_URL: str = ""

    MPT_API_TOKEN: str = ""

    WEBHOOK_MAX_CLOCK_SKEW_SECONDS: int = Field(

        default=300,

        ge=30,

        le=900,

    )

    NETWORK_WRITE_ACTIONS_ENABLED: bool = False

    @field_validator("CONTROL_API_TOKEN", "WEBHOOK_HMAC_SECRET")

    @classmethod

    def validate_secret(cls, value: str) -> str:

        value = value.strip()

        if len(value) < 32:

            raise ValueError(

                "Security secrets must contain at least 32 characters."

            )

        forbidden = {

            "REPLACE_WITH_RANDOM_SECRET_AT_LEAST_32_CHARS",

            "REPLACE_WITH_DIFFERENT_RANDOM_SECRET_AT_LEAST_32_CHARS",

            "CHANGE_ME",

        }

        if value in forbidden:

            raise ValueError("Replace the example secret before startup.")

        return value

    @field_validator("MPT_SOURCE_STATUS")

    @classmethod

    def validate_source_status(cls, value: str) -> str:

        allowed = {

            "NOT_CONNECTED",

            "CONFIGURED",

            "CONNECTED",

            "DEGRADED",

        }

        value = value.strip().upper()

        if value not in allowed:

            raise ValueError("Invalid MPT_SOURCE_STATUS.")

        # Configuration alone must not claim a live connection.

        if value == "CONNECTED":

            raise ValueError(

                "CONNECTED must only be reported after a successful "

                "authenticated source health check."

            )

        return value

@lru_cache

def get_settings() -> Settings:

    return Settings()