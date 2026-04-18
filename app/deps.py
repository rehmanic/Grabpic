"""
FastAPI dependencies for database sessions, settings, and facial recognition engine injection.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.services.face_engine import FaceEngineProtocol, InsightFaceEngine

_face_engine: FaceEngineProtocol | None = None


def configure_face_engine(engine: FaceEngineProtocol | None) -> None:
    """Test hook: replace the lazy InsightFace singleton with a mock instance."""
    global _face_engine
    _face_engine = engine


def get_face_engine() -> FaceEngineProtocol:
    """Dependency generator that initializes and returns a singleton instance of the facial recognition engine."""
    global _face_engine
    if _face_engine is None:
        settings = get_settings()
        _face_engine = InsightFaceEngine(settings.insightface_model, settings.insightface_root)
    assert _face_engine is not None
    return _face_engine


def get_settings_dep() -> Settings:
    """Dependency generator that yields the application configuration settings."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
DbSession = Annotated[Session, Depends(get_db)]
FaceEngineDep = Annotated[FaceEngineProtocol, Depends(get_face_engine)]
