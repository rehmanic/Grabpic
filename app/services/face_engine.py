"""
Service for facial detection and embedding extraction using InsightFace.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Protocol

import cv2
import numpy as np


@dataclass
class DetectedFace:
    """Represents a face detected within an image, including its embedding and bounding box."""
    embedding: np.ndarray
    bbox: dict[str, float]


class FaceEngineProtocol(Protocol):
    """Protocol defining the interface for face extraction engines."""
    def extract_from_bgr(self, image_bgr: np.ndarray) -> list[DetectedFace]: ...


class InsightFaceEngine:
    """Wraps InsightFace buffalo_l (512-D embeddings, L2-normalized)."""

    def __init__(self, model_name: str, insightface_root: str | None = None) -> None:
        """Initializes the InsightFace model with the specified model name and root path."""
        from insightface.app import FaceAnalysis

        root = os.path.expanduser(insightface_root or "~/.insightface")
        self._app = FaceAnalysis(
            name=model_name,
            root=root,
            providers=["CPUExecutionProvider"],
        )
        self._app.prepare(ctx_id=-1, det_size=(640, 640))

    def extract_from_bgr(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        if image_bgr is None or image_bgr.size == 0:
            return []
        faces = self._app.get(image_bgr)
        faces = sorted(
            faces,
            key=lambda f: float((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])),
            reverse=True,
        )
        out: list[DetectedFace] = []
        for f in faces:
            emb = np.asarray(f.normed_embedding, dtype=np.float32)
            bbox = {
                "x1": float(f.bbox[0]),
                "y1": float(f.bbox[1]),
                "x2": float(f.bbox[2]),
                "y2": float(f.bbox[3]),
            }
            out.append(DetectedFace(embedding=emb, bbox=bbox))
        return out


def read_image_bgr(path: str) -> np.ndarray | None:
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def read_image_bgr_from_bytes(content: bytes) -> np.ndarray | None:
    buf = np.frombuffer(content, dtype=np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)
