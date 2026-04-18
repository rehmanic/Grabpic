"""
Router for retrieving image metadata linked to specific identities.
"""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.deps import DbSession
from app.models import Image, ImageFace
from app.schemas import GrabImagesResponse, ImageItem

router = APIRouter(prefix="/v1", tags=["images"])


@router.get("/grab/{grab_id}/images", response_model=GrabImagesResponse)
def list_images_for_grab(grab_id: str, db: DbSession) -> GrabImagesResponse:
    """List all image metadata associated with a specific grab_id identity."""
    stmt = (
        select(Image)
        .join(ImageFace, ImageFace.image_id == Image.id)
        .where(ImageFace.grab_id == grab_id)
        .distinct()
    )
    rows = db.scalars(stmt).all()
    items = [
        ImageItem(image_id=r.id, path=r.path, content_hash=r.content_hash) for r in rows
    ]
    return GrabImagesResponse(grab_id=grab_id, images=items, total=len(items))
