from datetime import datetime

from sqlalchemy import (

    DateTime,

    Index,

    JSON,

    String,

    UniqueConstraint,

)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class NetworkEvent(Base):

    __tablename__ = "network_events"

    __table_args__ = (

        UniqueConstraint(

            "source",

            "event_id",

            name="uq_network_event_source_event_id",

        ),

        Index("ix_network_events_observed_at", "observed_at"),

        Index("ix_network_events_event_type", "event_type"),

    )

    id: Mapped[int] = mapped_column(primary_key=True)

    source: Mapped[str] = mapped_column(

        String(100),

        nullable=False,

    )

    event_id: Mapped[str] = mapped_column(

        String(200),

        nullable=False,

    )

    event_type: Mapped[str] = mapped_column(

        String(100),

        nullable=False,

    )

    observed_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        nullable=False,

    )

    received_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        nullable=False,

    )

    payload: Mapped[dict] = mapped_column(

        JSON,

        nullable=False,

    )