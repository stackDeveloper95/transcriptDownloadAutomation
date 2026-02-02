from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Transcript(BaseModel):
    video_id: str
    channel_id: Optional[str] = None
    transcript_text: str
    created_at: datetime
    updated_at: datetime
