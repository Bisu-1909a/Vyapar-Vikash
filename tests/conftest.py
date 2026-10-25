import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "backend"), os.path.join(ROOT, "database"), os.path.join(ROOT, "api")):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """App backed by a fresh database: TEST_DATABASE_URL (e.g. Postgres) or a temp SQLite file."""
    from database import orm

    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        os.environ["DATABASE_URL"] = test_url
        orm.reset_engine()
        orm.Base.metadata.drop_all(orm.get_engine())
        with orm.get_engine().begin() as conn:
            conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    else:
        os.environ.pop("DATABASE_URL", None)
        os.environ["DATABASE_PATH"] = str(tmp_path_factory.mktemp("db") / "test.sqlite3")
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ.pop("LLM_API_KEY", None)
    orm.reset_engine()

    from database.models import init_db
    from backend.app import create_app

    init_db()
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_client(app):
    """Client signed in as a fresh user."""
    import uuid
    c = app.test_client()
    email = f"u{uuid.uuid4().hex[:8]}@example.com"
    r = c.post("/api/register", json={"name": "Test User", "email": email, "password": "secret123"})
    assert r.status_code in (200, 201), r.get_json()
    c.user = r.get_json()["user"]
    return c


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    from api import ai_api
    ai_api._limiter._hits.clear()
    yield
