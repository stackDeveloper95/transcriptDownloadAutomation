from logging import getLogger
from typing import Optional

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi

logger = getLogger(__name__)


def fetch_transcript(video_id: str) -> Optional[str]:
    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound) as err:
        logger.warning("Transcript unavailable for video %s: %s", video_id, err)
        return None
    except Exception as err:  # pragma: no cover - diagnostic path
        logger.error("Failed to fetch transcript for video %s: %s", video_id, err)
        raise

    lines = [item.get("text", "").strip() for item in entries if item.get("text")]
    transcript = "\n".join(lines).strip()
    return transcript or None