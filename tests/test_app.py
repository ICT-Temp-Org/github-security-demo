"""
Tests for the GHAS Demo Blog – benign behaviour only.

These tests cover the safe, read-only blog routes (/  and  /post/<id>).
They do NOT exercise the intentionally vulnerable demo endpoints.

The test fixture uses a temporary SQLite database so that each test run
starts from a clean, known state without touching the development database.
"""

import pytest

import app as app_module
from app import app, init_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    Provide a Flask test client backed by a fresh temporary database.

    monkeypatch replaces the module-level DB_PATH so that both init_db()
    and the per-request get_db() helper connect to the same temp file.
    """
    db_path = str(tmp_path / "test_blog.db")
    monkeypatch.setattr(app_module, "DB_PATH", db_path)

    init_db()

    app.config["TESTING"] = True
    app.config["DEBUG"] = False

    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


# ── Blog listing ──────────────────────────────────────────────────────────────


def test_index_returns_200(client):
    """GET / returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_lists_posts(client):
    """GET / lists all seeded blog posts."""
    response = client.get("/")
    data = response.data.decode("utf-8")

    # All four seeded post titles must appear in the listing.
    assert "Welcome to the GHAS Demo Blog" in data
    assert "Understanding CodeQL Code Scanning" in data
    assert "Keeping Dependencies Up to Date with Dependabot" in data
    assert "Preventing Secret Leakage with Secret Scanning" in data


def test_index_html_content_type(client):
    """GET / responds with HTML."""
    response = client.get("/")
    assert "text/html" in response.content_type


# ── Post detail ───────────────────────────────────────────────────────────────


def test_post_detail_returns_200(client):
    """GET /post/1 returns HTTP 200 for the first seeded post."""
    response = client.get("/post/1")
    assert response.status_code == 200


def test_post_detail_shows_title_and_body(client):
    """GET /post/1 renders the post title and body text."""
    response = client.get("/post/1")
    data = response.data.decode("utf-8")
    assert "Welcome to the GHAS Demo Blog" in data
    assert "demonstration application for GitHub Advanced Security" in data


def test_post_detail_shows_author(client):
    """GET /post/1 renders the author name."""
    response = client.get("/post/1")
    data = response.data.decode("utf-8")
    assert "Demo Author" in data


def test_post_detail_second_post(client):
    """GET /post/2 returns HTTP 200 for the second seeded post."""
    response = client.get("/post/2")
    assert response.status_code == 200
    data = response.data.decode("utf-8")
    assert "Understanding CodeQL Code Scanning" in data


# ── Missing post ──────────────────────────────────────────────────────────────


def test_missing_post_returns_404(client):
    """GET /post/<nonexistent-id> returns HTTP 404."""
    response = client.get("/post/99999")
    assert response.status_code == 404


def test_missing_post_large_id(client):
    """GET /post/0 returns HTTP 404 (no post with id 0 in SQLite AUTOINCREMENT)."""
    response = client.get("/post/0")
    assert response.status_code == 404
