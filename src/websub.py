import hashlib
import hmac
from logging import getLogger
from typing import Optional
from xml.etree import ElementTree

logger = getLogger(__name__)


def parse_video_id(payload: bytes) -> Optional[str]:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as err:
        logger.warning("Failed to parse WebSub payload: %s", err)
        return None

    ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}
    video_nodes = root.findall(".//yt:videoId", ns)
    if not video_nodes:
        return None
    return video_nodes[0].text


def verify_signature(signature_header: Optional[str], secret: Optional[str], body: bytes) -> bool:
    if not secret:
        return True
    if not signature_header:
        return False

    try:
        algo, provided = signature_header.split("=")
    except ValueError:
        return False

    if algo.lower() != "sha1":
        return False

    digest = hmac.new(secret.encode(), body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(digest, provided)