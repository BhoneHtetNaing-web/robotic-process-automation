import hashlib

import hmac

import time

from fastapi import HTTPException, Request

from app.core.config import get_settings

async def verify_webhook_signature(request: Request) -> bytes:

    settings = get_settings()

    timestamp = request.headers.get("X-Apexive-Timestamp", "")

    supplied_signature = request.headers.get(

        "X-Apexive-Signature", ""

    )

    if not timestamp or not supplied_signature:

        raise HTTPException(

            status_code=401,

            detail="Missing webhook authentication headers.",

        )

    try:

        timestamp_int = int(timestamp)

    except ValueError:

        raise HTTPException(

            status_code=401,

            detail="Invalid webhook timestamp.",

        )

    if abs(int(time.time()) - timestamp_int) > (

        settings.WEBHOOK_MAX_CLOCK_SKEW_SECONDS

    ):

        raise HTTPException(

            status_code=401,

            detail="Webhook timestamp outside the allowed time window.",

        )

    body = await request.body()

    signed_content = timestamp.encode("utf-8") + b"." + body

    expected_signature = hmac.new(

        settings.WEBHOOK_HMAC_SECRET.encode("utf-8"),

        signed_content,

        hashlib.sha256,

    ).hexdigest()

    received = supplied_signature.removeprefix("sha256=")

    if not hmac.compare_digest(expected_signature, received):

        raise HTTPException(

            status_code=401,

            detail="Invalid webhook signature.",

        )

    return body

def verify_control_token(authorization: str | None) -> None:

    settings = get_settings()

    if not authorization or not authorization.startswith("Bearer "):

        raise HTTPException(

            status_code=401,

            detail="Bearer token required.",

        )

    supplied_token = authorization[7:].strip()

    if not hmac.compare_digest(

        supplied_token,

        settings.CONTROL_API_TOKEN,

    ):

        raise HTTPException(

            status_code=401,

            detail="Invalid control API token.",

        )