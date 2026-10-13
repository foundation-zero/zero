from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ModulePersistenceBase(SQLModel):
    __table_args__ = {"schema": "thrs"}


class ModulePersistence(ModulePersistenceBase, table=True):
    """Last known control configuration of a module, one row per module."""

    __tablename__ = "module_persistence"  # type: ignore
    module_name: str = Field(primary_key=True)
    parameters: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    manual_control_values: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    automation_mode: str = Field(default="manual")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
