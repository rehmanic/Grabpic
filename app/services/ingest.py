from __future__ import annotations

import hashlib
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Image, ImageFace
from app.services.face_engine import FaceEngineProtocol, read_image_bgr
from app.services.identity import assign_grab_id_for_embedding

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_image_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    out: list[Path] = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in IMAGE_EXTENSIONS:
                out.append(p)
    return sorted(out)


def ingest_image_path(
    db: Session, engine: FaceEngineProtocol, path: Path
) -> tuple[int | None, int, list[str], bool]:
    """
    Returns (image_id, faces_count, grab_ids, was_new_image).
    If path already indexed, returns (None, 0, [], False) without reprocessing.
    """
    path_str = str(path.resolve())
    existing = db.scalar(select(Image).where(Image.path == path_str))
    if existing is not None:
        return None, 0, [], False

    content_hash = _file_sha256(path)
    bgr = read_image_bgr(path_str)
    if bgr is None:
        raise ValueError(f"unreadable_image:{path_str}")

    detected = engine.extract_from_bgr(bgr)
    img_row = Image(path=path_str, content_hash=content_hash)
    db.add(img_row)
    db.flush()

    grab_ids: list[str] = []
    for face in detected:
        gid = assign_grab_id_for_embedding(db, face.embedding)
        grab_ids.append(gid)
        db.add(
            ImageFace(
                image_id=img_row.id,
                grab_id=gid,
                bbox=face.bbox,
                embedding=face.embedding.astype(float).tolist(),
            )
        )
    db.flush()
    return img_row.id, len(detected), grab_ids, True
