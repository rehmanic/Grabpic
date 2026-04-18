# 📸 Grabpic HTTP API Reference

The Grabpic API handles identity extraction, clustering, and retrieval via a RESTful JSON/Multipart interface.

You can view the interactive Swagger/OpenAPI documentation by running the app and navigating to:  
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🛑 Error Handling
Standard errors are returned as JSON with the appropriate HTTP status code (4xx, 5xx) in the following format:
```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human readable error description."
  }
}
```

---

## 📡 Endpoints

### 1. Health Check
Check if the API and database are alive and healthy.
- **Method:** `GET`
- **Path:** `/health`
- **Response:** `200 OK`
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### 2. Batch Ingest / Scan
Crawl the configured `STORAGE_ROOT` (or a specific sub-directory) and automatically extract faces from all supported images, mapping them to `grab_id`s.
- **Method:** `POST`
- **Path:** `/v1/ingest/scan`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "root": "/data/storage/lfw" // Optional: defaults to the STORAGE_ROOT environment variable
}
```
- **Response:** `200 OK`
```json
{
  "scanned_files": 13233,
  "processed": 13233,
  "skipped": 0,
  "faces_detected": 15420,
  "errors": []
}
```

---

### 3. Upload & Index Single Image
Upload a single image file to the storage server, immediately extracting any faces inside it and indexing them into the database.
- **Method:** `POST`
- **Path:** `/v1/ingest/upload`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: The binary image file (e.g., JPEG, PNG)
- **Response:** `200 OK`
```json
{
  "image_id": 42,
  "path": "/data/storage/uploads/abcdef123.jpg",
  "faces_detected": 2,
  "grab_ids": [
    "uuid-for-person-1",
    "uuid-for-person-2"
  ]
}
```

---

### 4. Selfie Authentication
Submit a selfie image to act as a secure authentication token. The system finds the nearest matching identity cluster and returns the user's secure `grab_id`.
- **Method:** `POST`
- **Path:** `/v1/auth/selfie`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: The binary selfie image file.
- **Response:** `200 OK`
```json
{
  "grab_id": "8a83421d-...",
  "similarity": 0.85 
}
```
*(Throws `400 Bad Request` with `NO_FACE_FOUND` if no face is in the image, or `401 Unauthorized` with `IDENTITY_NOT_FOUND` if the face doesn't match known users.)*

---

### 5. Fetch User's Photos
Given an authenticated `grab_id`, retrieve all images where that specific user was detected.
- **Method:** `GET`
- **Path:** `/v1/grab/{grab_id}/images`
- **Response:** `200 OK`
```json
{
  "grab_id": "8a83421d-...",
  "total": 2,
  "images": [
    {
      "image_id": 105,
      "path": "/data/storage/marathon/runner_123.jpg",
      "content_hash": "hash_string"
    },
    {
      "image_id": 412,
      "path": "/data/storage/finish_line/group_shot.jpg",
      "content_hash": "hash_string"
    }
  ]
}
```
