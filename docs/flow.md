# Grabpic Architecture & Application Flow

This document details the exact flow of the main functionalities, detailing the files, libraries, and logic used under the hood. This acts as a reference for hackathon judging and team explanations.

## Core Tech Stack
- **Web Framework:** FastAPI (Python)
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Facial Recognition:** InsightFace (`buffalo_l` model running on ONNX Runtime via CPU)
- **Image Processing:** OpenCV (`cv2`) and NumPy

---

## Use Case 1: Image Discovery & Ingestion

**Triggered via:** `POST /v1/ingest/scan` or `POST /v1/ingest/upload`  
**Relevant Files:** `app/routers/ingest.py`, `app/services/ingest.py`, `app/services/face_engine.py`, `app/services/identity.py`

### Step-by-Step Flow:
1. **File Hashing & Deduplication:** 
   In `app/services/ingest.py`, the image file is hashed using SHA-256. If the hash or path already exists in the `Image` table (`app/models.py`), it skips processing to prevent duplicates.
2. **Face Extraction:**
   The image is passed to `InsightFaceEngine.extract_from_bgr()` in `app/services/face_engine.py`. InsightFace runs its `buffalo_l` model to detect bounding boxes and extract a 512-dimensional L2-normalized embedding for each face in the image.
3. **Identity Clustering:**
   For each detected face, the embedding is passed to `assign_grab_id_for_embedding` in `app/services/identity.py`. 
   - It computes the **Cosine Similarity** between the new embedding and the `centroid_embedding` of all existing identities in the `GrabIdentity` table.
   - If the similarity exceeds the `MATCH_THRESHOLD` (e.g. 0.35), it links the face to the existing `grab_id` and recalculates the identity's centroid (averaging the vectors).
   - If no match is found, it mints a fresh UUID `grab_id`.
4. **Database Persistence:**
   The `Image`, `GrabIdentity` and the junction table `ImageFace` are inserted/updated into PostgreSQL via SQLAlchemy.

---

## Use Case 2: Selfie Authentication

**Triggered via:** `POST /v1/auth/selfie`  
**Relevant Files:** `app/routers/auth.py`, `app/services/face_engine.py`, `app/services/identity.py`

### Step-by-Step Flow:
1. **Selfie Extraction:**
   The user uploads a selfie. `app/routers/auth.py` reads the binary data into OpenCV memory.
2. **Face Verification:**
   The `FaceEngineProtocol` extracts the face embedding. If there are multiple faces or zero faces, it throws a `400 Bad Request`.
3. **Identity Matching:**
   The single embedding is passed to `best_identity_match()` in `app/services/identity.py`. 
   - It performs Cosine Similarity against all `GrabIdentity` rows.
   - It requires the similarity to be higher than `SELFIE_AUTH_THRESHOLD` (e.g. 0.32).
4. **Authorizer Returned:**
   If a match is found, the system returns the matched `grab_id` which acts as the user's secure token. If no match is found, it throws a `401 Unauthorized` (`IDENTITY_NOT_FOUND`).

---

## Use Case 3: Fetching User's Images

**Triggered via:** `GET /v1/grab/{grab_id}/images`  
**Relevant Files:** `app/routers/images.py`, `app/models.py`

### Step-by-Step Flow:
1. **Querying:**
   The router `app/routers/images.py` receives the authenticated `grab_id`.
2. **Database Join:**
   It queries the `ImageFace` table, joining with the `Image` table where the `grab_id` matches.
3. **Response Output:**
   It returns the list of image records (including the `image_id`, `path`, and `content_hash`), allowing the client to retrieve or display all photos featuring the user.
