# 📸 Grabpic — Intelligent Identity & Retrieval Engine

**Grabpic** is a high-performance image processing backend designed for large-scale events (like marathons). It crawls your storage, uses facial recognition to automatically index people and assign them a unique `grab_id`, and provides a secure **"Selfie-as-a-Key"** retrieval system for users to fetch their photos.

Built for the **Vyrothon 2026** Hackathon! 🚀

---

## ✨ Features

- **Automated Discovery & Indexing:** Crawls storage and extracts faces using state-of-the-art AI (InsightFace `buffalo_l`).
- **Identity Grouping:** Automatically groups multiple occurrences of the same person under a unified `grab_id`.
- **Multi-face Support:** A single image with multiple people will map to multiple identities seamlessly.
- **Selfie Authentication:** Users just upload a selfie. The system compares it against known identities and returns a securely linked `grab_id`.
- **Data Extraction:** Fast endpoint to retrieve all images for an authenticated user.

---

## 🚀 Quickstart (Docker Setup - Recommended)

The easiest way to get everything running (API, Postgres Database, and volumes) is using Docker Compose. 

### 1. Clone & Configure
```bash
git clone https://github.com/rehmanic/Grabpic.git
cd Grabpic

# Create the environment file from the example
cp .env.example .env
```

### 2. Build and Run
```bash
docker compose up --build -d
```
*Note: The first run might take 5-10 minutes as it installs dependencies, compiles C++ extensions for facial recognition, and downloads the ONNX weights.*

### 3. Verify Health
Once the containers are up, verify the API is running:
```bash
curl -sS http://127.0.0.1:8000/health
```

### 4. Interactive Docs
Go to your browser to view the interactive API documentation (Swagger UI):
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 How to Test the API

You can use the Swagger UI above, or run these `curl` commands directly.

### Step 1: Ingesting Data
You can upload an image directly to the system:
```bash
curl -sS -X POST http://127.0.0.1:8000/v1/ingest/upload \
  -F 'file=@/path/to/photo.jpg'
```

*Alternatively, scan an entire storage directory (e.g., if you loaded a dataset):*
```bash
curl -sS -X POST http://127.0.0.1:8000/v1/ingest/scan \
  -H 'Content-Type: application/json' \
  -d '{"root": "/data/storage"}'
```

### Step 2: Authenticate with a Selfie ("Selfie-as-a-Key")
Pass a selfie of the user. The system compares it to known centroids and returns a `grab_id`.
```bash
curl -sS -X POST http://127.0.0.1:8000/v1/auth/selfie \
  -F 'file=@/path/to/selfie.jpg'
```

### Step 3: Fetch User's Images
Using the `grab_id` returned from Step 2, fetch all photos they are in:
```bash
GRAB_ID='<paste-from-selfie-response>'
curl -sS "http://127.0.0.1:8000/v1/grab/${GRAB_ID}/images"
```

---

## 📦 Loading the LFW Dataset (Optional)

If you want to test with a massive dataset, Grabpic can automatically pull and index the **Labeled Faces in the Wild** (LFW) dataset from Kaggle.

1. Ensure your `~/.kaggle/kaggle.json` exists locally, or uncomment it in `docker-compose.yml`.
2. Run the download script **inside** the API container:
```bash
docker compose exec api python scripts/download_lfw.py --symlink-into /data/storage/lfw
```
3. Ingest the dataset:
```bash
curl -sS -X POST http://127.0.0.1:8000/v1/ingest/scan \
  -H 'Content-Type: application/json' \
  -d '{"root": "/data/storage/lfw"}'
```

---

## ⚙️ Configuration Variables

The system is highly configurable via the `.env` file:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy Connection URL (Postgres or SQLite). |
| `STORAGE_ROOT` | Root directory crawled by the ingest service. |
| `INSIGHTFACE_ROOT` | Where InsightFace stores its ONNX weights (default: `/data/insightface`). |
| `MATCH_THRESHOLD` | Cosine similarity threshold to merge a newly found face into an existing `grab_id`. |
| `SELFIE_AUTH_THRESHOLD` | Minimum similarity score to authorize a selfie login. |

---

## 🛠️ Project Structure

- `Dockerfile` & `docker-compose.yml` — Full stack orchestration.
- `app/` — Core FastAPI application code.
- `scripts/` — Utility scripts (like downloading datasets).
- `docs/` — Requirements and architecture documentation.

---

## 🛑 Stopping the System

Stop containers while keeping your database and image data:
```bash
docker compose down
```

To completely wipe all containers **and** data volumes (Postgres + uploaded images + model caches):
```bash
docker compose down -v
```
