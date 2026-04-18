from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class IngestScanRequest(BaseModel):
    root: str | None = Field(
        default=None,
        description="Optional directory to scan; defaults to STORAGE_ROOT from environment.",
    )


class IngestScanResponse(BaseModel):
    scanned_files: int = Field(description="Number of image files discovered under the root.")
    processed: int = Field(description="Images newly indexed in this run.")
    skipped: int = Field(description="Images skipped (already indexed or unreadable).")
    faces_detected: int = Field(description="Total face detections persisted across processed images.")
    errors: list[str] = Field(default_factory=list, description="Non-fatal per-file errors.")


class IngestUploadResponse(BaseModel):
    image_id: int
    path: str
    faces_detected: int
    grab_ids: list[str]


class SelfieAuthResponse(BaseModel):
    grab_id: str
    similarity: float = Field(description="Cosine similarity against the matched identity centroid.")


class ImageItem(BaseModel):
    image_id: int
    path: str
    content_hash: str


class GrabImagesResponse(BaseModel):
    grab_id: str
    images: list[ImageItem]
    total: int


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
