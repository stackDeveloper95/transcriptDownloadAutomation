import argparse
from datetime import datetime

from src.config import get_settings
from src.storage import upsert_transcript


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed dummy transcripts into MongoDB")
    parser.add_argument("--count", type=int, default=3, help="Number of dummy transcripts to insert")
    parser.add_argument("--channel-id", default="dummy-channel", help="Channel id to store with each transcript")
    parser.add_argument("--prefix", default="dummy-video-", help="Prefix for dummy video ids")
    args = parser.parse_args()

    settings = get_settings()
    print(
        "Using mongo_url=%s db=%s collection=%s"
        % (settings.mongo_url, settings.mongo_db, settings.mongo_collection)
    )

    for idx in range(1, args.count + 1):
        video_id = f"{args.prefix}{idx}"
        transcript_text = f"Sample transcript {idx} inserted at {datetime.utcnow().isoformat()}Z"
        upsert_transcript(video_id=video_id, transcript_text=transcript_text, channel_id=args.channel_id)
        print(f"Upserted {video_id}")

    print("Done.")


if __name__ == "__main__":
    main()
