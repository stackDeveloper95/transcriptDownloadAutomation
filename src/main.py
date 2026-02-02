from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import PlainTextResponse

from .config import get_settings
from .storage import get_transcript, init_db, upsert_transcript
from .transcript_service import fetch_transcript
from .websub import parse_video_id, verify_signature

settings = get_settings()
app = FastAPI(title="Transcript Pipeline")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/websub")
def websub_verify(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
    hub_topic: str | None = Query(None, alias="hub.topic"),
) -> PlainTextResponse:
    if hub_mode == "subscribe" and hub_challenge:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=400, detail="Invalid verification request")


def process_video(video_id: str) -> None:
    transcript = fetch_transcript(video_id)
    if not transcript:
        return
    upsert_transcript(video_id=video_id, transcript_text=transcript)


@app.post("/websub", status_code=202)
async def websub_notify(request: Request, background_tasks: BackgroundTasks) -> Response:
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature")

    if not verify_signature(signature, settings.hub_secret, body):
        raise HTTPException(status_code=400, detail="Invalid signature")

    video_id = parse_video_id(body)
    if not video_id:
        raise HTTPException(status_code=202, detail="No video id found")

    background_tasks.add_task(process_video, video_id)
    return Response(status_code=202)


@app.get("/transcripts/{video_id}")
def read_transcript(video_id: str):
    record = get_transcript(video_id)
    if not record:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {
        "video_id": record.get("video_id") or record.get("_id"),
        "channel_id": record.get("channel_id"),
        "transcript": record.get("transcript_text"),
        "updated_at": record.get("updated_at"),
    }