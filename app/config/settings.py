from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rpc_url: str
    chain_name: str = "Unknown"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()