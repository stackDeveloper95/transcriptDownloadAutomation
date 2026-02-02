import argparse
from typing import Literal

import httpx

from src.config import get_settings


def build_payload(callback_url: str, channel_id: str, mode: Literal["subscribe", "unsubscribe"], hub_secret: str | None) -> dict[str, str]:
    feed_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
    payload = {
        "hub.mode": mode,
        "hub.topic": feed_url,
        "hub.callback": callback_url,
        "hub.verify": "async",
    }
    if hub_secret:
        payload["hub.secret"] = hub_secret
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Subscribe/unsubscribe to a YouTube channel WebSub feed")
    parser.add_argument("--mode", choices=["subscribe", "unsubscribe"], default="subscribe")
    args = parser.parse_args()

    settings = get_settings()
    channel_ids = settings.channel_ids or ([settings.channel_id] if settings.channel_id else [])
    if not channel_ids:
        raise SystemExit("CHANNEL_IDS (comma-separated) or CHANNEL_ID is required")
    if not settings.callback_url:
        raise SystemExit("CALLBACK_URL is required")

    with httpx.Client(timeout=10.0) as client:
        for channel_id in channel_ids:
            payload = build_payload(settings.callback_url, channel_id, args.mode, settings.hub_secret)
            # Cast AnyHttpUrl to str to satisfy httpx
            resp = client.post(str(settings.hub_url), data=payload)
            resp.raise_for_status()
            print(f"{args.mode.title()} request for {channel_id} accepted: {resp.status_code}")


if __name__ == "__main__":
    main()