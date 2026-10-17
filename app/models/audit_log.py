from datetime import datetime

from sqlalchemy import DateTime, Index, JSON, String, Text

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class AuditLog(Base):

    __tablename__ = "audit_logs"

    __table_args__ = (

        Index("ix_audit_logs_created_at", "created_at"),

        Index("ix_audit_logs_actor", "actor"),

        Index("ix_audit_logs_action", "action"),

    )

    id: Mapped[int] = mapped_column(primary_key=True)

    event_id: Mapped[str] = mapped_column(

        String(100),

        unique=True,

        nullable=False,

    )

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        nullable=False,

    )

    actor: Mapped[str] = mapped_column(

        String(150),

        nullable=False,

    )

    action: Mapped[str] = mapped_column(

        String(150),

        nullable=False,

    )

    resource_type: Mapped[str] = mapped_column(

        String(100),

        nullable=False,

    )

    resource_id: Mapped[str | None] = mapped_column(

        String(200),

        nullable=True,

    )

    outcome: Mapped[str] = mapped_column(

        String(30),

        nullable=False,

    )

    request_id: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True,

    )

    details: Mapped[dict] = mapped_column(

        JSON,

        nullable=False,

        default=dict,

    )

    error_summary: Mapped[str | None] = mapped_column(

        Text,

        nullable=True,

    )