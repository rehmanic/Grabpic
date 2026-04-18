"""
Router for authentication-related endpoints, primarily selfie-as-a-key logic.
"""
from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.deps import DbSession, FaceEngineDep
from app.exceptions import not_found, unprocessable
from app.schemas import SelfieAuthResponse
from app.services.face_engine import read_image_bgr_from_bytes
from app.services.identity import best_identity_match

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/selfie", response_model=SelfieAuthResponse)
async def selfie_auth(
    db: DbSession,
    engine: FaceEngineDep,
    file: UploadFile = File(..., description="Selfie image used as the search token."),
) -> SelfieAuthResponse:
    """
    Authenticate a user based on a selfie image.
    Extracts face embeddings and matches against known identities.
    """
    content = await file.read()
    if not content:
        raise unprocessable("EMPTY_FILE", "Uploaded file is empty.")

    bgr = read_image_bgr_from_bytes(content)
    if bgr is None:
        raise unprocessable("UNREADABLE_IMAGE", "Could not decode an image from the upload.")

    faces = engine.extract_from_bgr(bgr)
    if not faces:
        raise unprocessable("NO_FACE", "No face detected in the selfie.")

    emb = faces[0].embedding
    match = best_identity_match(db, emb)
    if match is None:
        raise not_found(
            "NO_MATCH",
            "No known grab_id matched this selfie above the configured threshold.",
        )
    grab_id, similarity = match
    return SelfieAuthResponse(grab_id=grab_id, similarity=similarity)
