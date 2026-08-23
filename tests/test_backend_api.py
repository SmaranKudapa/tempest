import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(bind=engine)

        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_health_check(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_creates_and_returns_latest_reading(self) -> None:
        payload = {"temp_c": 23.4, "humidity": 41.0, "source": "test-sensor"}

        create_response = self.client.post("/readings", json=payload)
        latest_response = self.client.get("/readings/latest")

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(latest_response.status_code, 200)
        self.assertEqual(latest_response.json()["temp_c"], 23.4)
        self.assertEqual(latest_response.json()["humidity"], 41.0)
        self.assertEqual(latest_response.json()["source"], "test-sensor")

    def test_rejects_invalid_reading(self) -> None:
        response = self.client.post(
            "/readings",
            json={"temp_c": 23.4, "humidity": 140.0, "source": "test-sensor"},
        )

        self.assertEqual(response.status_code, 422)

    def test_latest_reading_returns_404_when_empty(self) -> None:
        response = self.client.get("/readings/latest")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
