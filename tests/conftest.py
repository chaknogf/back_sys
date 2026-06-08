import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.database import get_db, engine, SessionLocal
from core.security import hash_password
from modules.users.models import UserModel
from main import app


@pytest.fixture(scope="session")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


TEST_USER = {
    "username": "test_integration",
    "password": "TestPass123!",
    "nombre": "Test User Integration",
    "email": "test_integration@hospital.com",
    "role": "admin",
    "estado": "A",
}


@pytest.fixture(scope="module")
def auth_headers(db_session):
    user = db_session.query(UserModel).filter(
        UserModel.username == TEST_USER["username"]
    ).first()
    if not user:
        user = UserModel(
            username=TEST_USER["username"],
            password=hash_password(TEST_USER["password"]),
            nombre=TEST_USER["nombre"],
            email=TEST_USER["email"],
            role=TEST_USER["role"],
            estado=TEST_USER["estado"],
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    response = TestClient(app).post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def pytest_sessionfinish(session):
    try:
        db = SessionLocal()
        try:
            from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
            user = db.query(UserModel).filter(
                UserModel.username == TEST_USER["username"]
            ).first()
            if user:
                db.query(ConstanciaNacimientoModel).filter(
                    ConstanciaNacimientoModel.registrador_id == user.id
                ).delete(synchronize_session=False)
                db.query(UserModel).filter(
                    UserModel.username == TEST_USER["username"]
                ).delete()
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Cleanup warning: {e}")
