"""
Service for identity management, clustering embeddings into stable grab_ids.
"""
from __future__ import annotations

import uuid

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import GrabIdentity


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates the cosine similarity between two vectors."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _centroid_to_numpy(centroid: list) -> np.ndarray:
    """Converts a stored centroid list to a NumPy array."""
    return np.asarray(centroid, dtype=np.float32)


def assign_grab_id_for_embedding(db: Session, embedding: np.ndarray) -> str:
    """Merge with closest existing identity above threshold, else mint a new grab_id."""
    settings = get_settings()
    rows = db.scalars(select(GrabIdentity)).all()
    best_id: str | None = None
    best_sim = -1.0
    for row in rows:
        c = _centroid_to_numpy(row.centroid_embedding)
        sim = cosine_similarity(embedding, c)
        if sim > best_sim:
            best_sim = sim
            best_id = row.grab_id

    if best_id is not None and best_sim >= settings.match_threshold:
        row = db.get(GrabIdentity, best_id)
        assert row is not None
        n = int(row.face_count)
        old = _centroid_to_numpy(row.centroid_embedding)
        new_centroid = (old * n + embedding) / (n + 1)
        row.centroid_embedding = new_centroid.astype(float).tolist()
        row.face_count = n + 1
        db.add(row)
        return best_id

    gid = str(uuid.uuid4())
    identity = GrabIdentity(
        grab_id=gid,
        centroid_embedding=embedding.astype(float).tolist(),
        face_count=1,
    )
    db.add(identity)
    return gid


def best_identity_match(db: Session, embedding: np.ndarray) -> tuple[str, float] | None:
    settings = get_settings()
    rows = db.scalars(select(GrabIdentity)).all()
    best_id: str | None = None
    best_sim = -1.0
    for row in rows:
        c = _centroid_to_numpy(row.centroid_embedding)
        sim = cosine_similarity(embedding, c)
        if sim > best_sim:
            best_sim = sim
            best_id = row.grab_id
    if best_id is None:
        return None
    if best_sim < settings.selfie_auth_threshold:
        return None
    return best_id, best_sim
