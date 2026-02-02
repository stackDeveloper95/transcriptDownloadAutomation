from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "transcript_pipeline"
    mongo_collection: str = "transcripts"
    callback_url: AnyHttpUrl
    channel_ids_raw: Optional[str] = None
    channel_id: Optional[str] = None
    hub_url: AnyHttpUrl = "https://pubsubhubbub.appspot.com/subscribe"
    hub_secret: Optional[str] = None

    @property
    def channel_ids(self) -> list[str]:
        if not self.channel_ids_raw:
            return []
        return [v.strip() for v in str(self.channel_ids_raw).split(",") if v and v.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
