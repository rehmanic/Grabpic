"""
Router for image ingestion, including folder scanning and individual uploads.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.deps import DbSession, FaceEngineDep, SettingsDep
from app.exceptions import bad_request
from app.schemas import IngestScanRequest, IngestScanResponse, IngestUploadResponse
from app.services.ingest import ingest_image_path, iter_image_files

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])


def _ensure_under_storage(root: Path, storage_root: Path) -> Path:
    """Verifies that the provided path is within the designated storage root."""
    root_res = root.resolve()
    base = storage_root.resolve()
    try:
        root_res.relative_to(base)
    except ValueError as exc:
        raise bad_request(
            "INVALID_ROOT",
            "Provided root must be inside STORAGE_ROOT for safety.",
        ) from exc
    return root_res


@router.post("/scan", response_model=IngestScanResponse)
def ingest_scan(
    body: IngestScanRequest,
    db: DbSession,
    settings: SettingsDep,
    engine: FaceEngineDep,
) -> IngestScanResponse:
    """Scan a directory for images and index them into the system."""
    storage = Path(settings.storage_root)
    storage.mkdir(parents=True, exist_ok=True)
    root = Path(body.root) if body.root else storage
    root = _ensure_under_storage(root, storage)

    files = iter_image_files(root)
    processed = 0
    skipped = 0
    faces_detected = 0
    errors: list[str] = []

    for fp in files:
        try:
            _image_id, n_faces, _grab_ids, was_new = ingest_image_path(db, engine, fp)
            if was_new:
                processed += 1
                faces_detected += n_faces
            else:
                skipped += 1
        except ValueError as e:
            skipped += 1
            errors.append(str(e))
        except Exception as e:  # noqa: BLE001
            skipped += 1
            errors.append(f"{fp}: {e.__class__.__name__}:{e}")

    db.commit()
    return IngestScanResponse(
        scanned_files=len(files),
        processed=processed,
        skipped=skipped,
        faces_detected=faces_detected,
        errors=errors[:50],
    )


@router.post("/upload", response_model=IngestUploadResponse)
async def ingest_upload(
    db: DbSession,
    settings: SettingsDep,
    engine: FaceEngineDep,
    file: UploadFile = File(..., description="Raw image bytes (JPEG/PNG/WebP)."),
) -> IngestUploadResponse:
    storage = Path(settings.storage_root)
    upload_dir = storage / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "image").suffix or ".bin"
    dest = upload_dir / f"{uuid.uuid4().hex}{suffix}"
    content = await file.read()
    if not content:
        raise bad_request("EMPTY_FILE", "Uploaded file is empty.")
    dest.write_bytes(content)

    try:
        image_id, n_faces, grab_ids, was_new = ingest_image_path(db, engine, dest)
    except ValueError as e:
        dest.unlink(missing_ok=True)
        raise bad_request("UNREADABLE_IMAGE", str(e)) from e

    if not was_new or image_id is None:
        db.rollback()
        raise bad_request("DUPLICATE_PATH", "This file path was already indexed.")

    db.commit()
    return IngestUploadResponse(
        image_id=image_id,
        path=str(dest.resolve()),
        faces_detected=n_faces,
        grab_ids=grab_ids,
    )
