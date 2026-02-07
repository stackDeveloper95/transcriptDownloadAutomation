from logging import getLogger
from typing import Optional

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi

logger = getLogger(__name__)


def fetch_transcript(video_id: str) -> Optional[str]:
    try:
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            entries = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            api = YouTubeTranscriptApi()
            if hasattr(api, "fetch"):
                fetched = api.fetch(video_id)
                entries = (
                    fetched.to_raw_data()
                    if hasattr(fetched, "to_raw_data")
                    else [
                        {"text": snippet.text, "start": snippet.start, "duration": snippet.duration}
                        for snippet in fetched
                    ]
                )
            elif hasattr(api, "list"):
                transcript = api.list(video_id).find_transcript(["en"])
                fetched = transcript.fetch()
                entries = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else fetched
            else:
                raise AttributeError("YouTubeTranscriptApi has no compatible fetch method")
    except (TranscriptsDisabled, NoTranscriptFound) as err:
        logger.warning("Transcript unavailable for video %s: %s", video_id, err)
        return None
    except Exception as err:  # pragma: no cover - diagnostic path
        logger.error("Failed to fetch transcript for video %s: %s", video_id, err)
        raise

    lines = [item.get("text", "").strip() for item in entries if item.get("text")]
    transcript = "\n".join(lines).strip()
    return transcript or None