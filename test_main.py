import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists,create_database

from config.db import get_db, Base
from main import app

engine = create_engine("mysql+pymysql://root:root@localhost:3306/test_urlshortener_app")

if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


TEST_JWT_TOKEN=""
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_EMAIL = "testemail"
TEST_USERNAME_WRONG = "wronguser"
TEST_PASSWORD_WRONG = "wrongpassword"
TEST_URL = "www.testurl.com"
TEST_SHORT_URL = ""


def test_register(client, setup_db):
    response = client.post("/auth", json={"username": TEST_USERNAME, "password": TEST_PASSWORD, "email": TEST_EMAIL})
    assert response.status_code == 200


def test_register_existing_user(client, setup_db):
    response = client.post("/auth", json={"username": TEST_USERNAME, "password": TEST_PASSWORD, "email": TEST_EMAIL})
    assert response.status_code == 400


def test_login(client, setup_db):
    response = client.post("/auth/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]
    global TEST_JWT_TOKEN
    TEST_JWT_TOKEN = token


def test_login_wrong_username(client, setup_db):
    response = client.post("/auth/token", data={"username": TEST_USERNAME_WRONG, "password": TEST_PASSWORD})
    assert response.status_code == 401


def test_login_wrong_password(client, setup_db):
    response = client.post("/auth/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD_WRONG})
    assert response.status_code == 401


def test_create_short_url(client, setup_db):
    response = client.post("/url", params={"url": TEST_URL}, headers={"Authorization": f"Bearer {TEST_JWT_TOKEN}"})
    assert response.status_code == 200
    global TEST_SHORT_URL
    TEST_SHORT_URL = response.json()


def test_redirect_original_url(client, setup_db):
    global TEST_SHORT_URL
    short_url = TEST_SHORT_URL.replace("localhost:8000", "")
    response = client.get(short_url, follow_redirects=False)
    assert response.status_code == 307


def test_get_statistics(client, setup_db):
    global TEST_SHORT_URL
    response = client.get("/url/statistic", params={"short_url": TEST_SHORT_URL}, headers={"Authorization": f"Bearer {TEST_JWT_TOKEN}"})
    assert response.status_code == 200