import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np

# Override env vars before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test_grabpic.db"
os.environ["STORAGE_ROOT"] = "/tmp/grabpic_test_storage"

from app.main import app
from app.database import Base, get_db
from app.deps import configure_face_engine
from app.services.face_engine import DetectedFace

# Set up test database
engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MockFaceEngine:
    """A mock face engine that always returns a single fixed face embedding."""
    def extract_from_bgr(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        if image_bgr is None or image_bgr.size == 0:
            return []
        
        # Return a 512-D normalized vector of ones to simulate a face
        emb = np.ones(512, dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        
        return [
            DetectedFace(
                embedding=emb,
                bbox={"x1": 0.0, "y1": 0.0, "x2": 100.0, "y2": 100.0}
            )
        ]

@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_grabpic.db"):
        os.remove("./test_grabpic.db")

@pytest.fixture
def db_session(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    configure_face_engine(MockFaceEngine())
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
