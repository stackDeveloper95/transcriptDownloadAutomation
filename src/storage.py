from datetime import datetime
from typing import Optional

from pymongo import MongoClient, ReturnDocument

from .config import get_settings

settings = get_settings()
client = MongoClient(settings.mongo_url)
db = client[settings.mongo_db]
collection = db[settings.mongo_collection]


def init_db() -> None:
    # _id index is created automatically by MongoDB
    return


def upsert_transcript(video_id: str, transcript_text: str, channel_id: Optional[str] = None) -> None:
    now = datetime.utcnow()
    collection.find_one_and_update(
        {"_id": video_id},
        {
            "$set": {
                "video_id": video_id,
                "channel_id": channel_id,
                "transcript_text": transcript_text,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )


def get_transcript(video_id: str) -> Optional[dict]:
    return collection.find_one({"_id": video_id})