# Grabpic HTTP API (summary)

Run the stack with Docker (`docker compose up --build -d`), then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness / version |
| `POST` | `/v1/ingest/scan` | Walk `STORAGE_ROOT` (or JSON `root` under it) and index images |
| `POST` | `/v1/ingest/upload` | Upload one image file into storage and index it |
| `POST` | `/v1/auth/selfie` | Selfie image → nearest `grab_id` (authorizer) |
| `GET` | `/v1/grab/{grab_id}/images` | List stored image paths for that `grab_id` |

Errors use JSON: `{"error":{"code":"...","message":"..."}}`.
