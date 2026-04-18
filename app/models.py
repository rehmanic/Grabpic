from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


def _json_type():
    return JSON().with_variant(JSONB(), "postgresql")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GrabIdentity(Base):
    __tablename__ = "grab_identities"

    grab_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    centroid_embedding: Mapped[list] = mapped_column(_json_type(), nullable=False)
    face_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    image_faces: Mapped[list["ImageFace"]] = relationship(back_populates="identity")


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    faces: Mapped[list["ImageFace"]] = relationship(back_populates="image")


class ImageFace(Base):
    __tablename__ = "image_faces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    grab_id: Mapped[str] = mapped_column(ForeignKey("grab_identities.grab_id", ondelete="CASCADE"), nullable=False)
    bbox: Mapped[dict | None] = mapped_column(_json_type(), nullable=True)
    embedding: Mapped[list | None] = mapped_column(_json_type(), nullable=True)

    image: Mapped["Image"] = relationship(back_populates="faces")
    identity: Mapped["GrabIdentity"] = relationship(back_populates="image_faces")
