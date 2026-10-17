import json

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from pydantic import BaseModel, ConfigDict, Field, field_validator

from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from app.core.config import get_settings

from app.database import get_db

from app.models import NetworkEvent

from app.security import verify_control_token, verify_webhook_signature

router = APIRouter()

class IncomingEvent(BaseModel):

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1, max_length=100)

    event_id: str = Field(min_length=1, max_length=200)

    event_type: str = Field(min_length=1, max_length=100)

    observed_at: datetime

    payload: dict = Field(default_factory=dict)

    @field_validator("observed_at")

    @classmethod

    def require_timezone(cls, value: datetime) -> datetime:

        if value.tzinfo is None or value.utcoffset() is None:

            raise ValueError("observed_at must include a timezone.")

        return value

def utc_now() -> datetime:

    return datetime.now(timezone.utc)

@router.get("/health")

def health():

    return {

        "service": "apexiveai-mpt-integration",

        "status": "running",

        "network_data": "NOT_CONNECTED",

        "note": "Service health does not prove MPT network connectivity.",

    }

@router.get("/source/status")

def source_status(

    authorization: str | None = Header(default=None),

):

    verify_control_token(authorization)

    settings = get_settings()

    return {

        "source": "MPT",

        "status": settings.MPT_SOURCE_STATUS,

        "live_data_verified": False,

        "endpoint_configured": bool(settings.MPT_API_BASE_URL),

        "message": (

            "Awaiting authorized MPT API documentation and credentials."

        ),

    }

@router.get("/topology")

def topology_status(

    authorization: str | None = Header(default=None),

):

    verify_control_token(authorization)

    return {

        "status": "NOT_CONNECTED",

        "source": "MPT",

        "nodes": [],

        "links": [],

        "last_successful_sync": None,

        "message": (

            "No topology returned: an authorized live source "

            "has not been connected and verified."

        ),

    }

@router.post("/webhooks/events")

async def receive_event(

    request: Request,

    db: Session = Depends(get_db),

):

    raw_body = await verify_webhook_signature(request)

    try:

        data = json.loads(raw_body)

        event = IncomingEvent.model_validate(data)

    except (json.JSONDecodeError, ValueError) as exc:

        raise HTTPException(

            status_code=422,

            detail="Invalid event payload or schema.",

        ) from exc

    # Accept only source names explicitly configured by the operator.

    # Do not trust arbitrary source names sent by webhook clients.

    settings = get_settings()

    if settings.MPT_SOURCE_STATUS == "NOT_CONNECTED":

        raise HTTPException(

            status_code=503,

            detail="MPT event source has not been configured.",

        )

    record = NetworkEvent(

        source=event.source,

        event_id=event.event_id,

        event_type=event.event_type,

        observed_at=event.observed_at,

        received_at=utc_now(),

        payload=event.payload,

    )

    db.add(record)

    try:

        db.commit()

        db.refresh(record)

    except IntegrityError:

        db.rollback()

        existing = db.scalar(

            select(NetworkEvent).where(

                NetworkEvent.source == event.source,

                NetworkEvent.event_id == event.event_id,

            )

        )

        if existing is not None:

            return {

                "accepted": True,

                "duplicate": True,

                "event_id": existing.event_id,

            }

        raise HTTPException(

            status_code=409,

            detail="Event conflict; no record was accepted.",

        )

    return {

        "accepted": True,

        "duplicate": False,

        "event_id": record.event_id,

        "received_at": record.received_at.isoformat(),

    }

@router.get("/events")

def list_events(

    limit: int = 100,

    authorization: str | None = Header(default=None),

    db: Session = Depends(get_db),

):

    verify_control_token(authorization)

    if limit < 1 or limit > 500:

        raise HTTPException(

            status_code=422,

            detail="limit must be between 1 and 500.",

        )

    records = db.scalars(

        select(NetworkEvent)

        .order_by(NetworkEvent.received_at.desc())

        .limit(limit)

    ).all()

    return {

        "items": [

            {

                "source": row.source,

                "event_id": row.event_id,

                "event_type": row.event_type,

                "observed_at": row.observed_at.isoformat(),

                "received_at": row.received_at.isoformat(),

                "payload": row.payload,

            }

            for row in records

        ],

        "count": len(records),

    }