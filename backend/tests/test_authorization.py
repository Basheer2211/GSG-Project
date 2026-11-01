"""Authentication, role guard and ownership checks over HTTP (NFR-016)."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.application.authorization import ensure_can_access
from app.core.config import settings
from app.core.dependencies import CurrentUser, get_user_repository, require_permission
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.permissions import Permission
from app.main import app
from tests.conftest import auth_header


# Test-only routes that exercise the guards the way real endpoints will.
@app.get("/_test/review-queue")
def _review_queue(
    user: Annotated[User, Depends(require_permission(Permission.REVIEW_QUEUE))]
):
    return {"ok": True}


@app.get("/_test/dashboard")
def _dashboard(
    user: Annotated[User, Depends(require_permission(Permission.DASHBOARD_VIEW))]
):
    return {"ok": True}


@app.get("/_test/candidates/{owner_id}/profile")
def _candidate_profile(owner_id: int, user: CurrentUser):
    ensure_can_access(user, owner_id)
    return {"ok": True}


@pytest.fixture
def client(user_repo):
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def _token(**overrides) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": "1", "iat": now, "exp": now + timedelta(minutes=5), "type": "access"}
    payload.update(overrides)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# --- get_current_user -------------------------------------------------------

def test_me_returns_current_user(client, make_user):
    user = make_user(UserRole.CANDIDATE)
    response = client.get("/api/v1/auth/me", headers=auth_header(user))
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == user.user_id
    assert body["role"] == "candidate"
    assert "password_hash" not in body


def test_missing_token_is_401(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("token", [
    "not-a-jwt",
    _token(exp=datetime.now(timezone.utc) - timedelta(minutes=1)),   # expired
    _token(type="refresh"),                                          # wrong type
    _token(sub="abc"),                                               # bad subject
    jwt.encode({"sub": "1", "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
                "type": "access"}, "wrong-secret-wrong-secret-wrong-secret",
               algorithm="HS256"),                                   # wrong signature
], ids=["garbage", "expired", "wrong-type", "bad-sub", "wrong-signature"])
def test_invalid_token_is_401(client, make_user, token):
    make_user(UserRole.CANDIDATE)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_token_for_deleted_user_is_401(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {_token(sub='999')}"})
    assert response.status_code == 401


# --- role guard -------------------------------------------------------------

@pytest.mark.parametrize("role, path, expected", [
    (UserRole.CANDIDATE, "/_test/review-queue", 403),
    (UserRole.REVIEWER, "/_test/review-queue", 200),
    (UserRole.ADMINISTRATOR, "/_test/review-queue", 200),   # admin inherits reviewer
    (UserRole.CANDIDATE, "/_test/dashboard", 403),
    (UserRole.REVIEWER, "/_test/dashboard", 403),
    (UserRole.ADMINISTRATOR, "/_test/dashboard", 200),
])
def test_role_guard(client, make_user, role, path, expected):
    user = make_user(role)
    assert client.get(path, headers=auth_header(user)).status_code == expected


def test_role_guard_requires_login(client):
    assert client.get("/_test/review-queue").status_code == 401


# --- ownership --------------------------------------------------------------

def test_candidate_can_access_own_data(client, make_user):
    me = make_user(UserRole.CANDIDATE)
    response = client.get(f"/_test/candidates/{me.user_id}/profile", headers=auth_header(me))
    assert response.status_code == 200


def test_candidate_cannot_access_other_candidates_data(client, make_user):
    me = make_user(UserRole.CANDIDATE)
    other = make_user(UserRole.CANDIDATE)
    response = client.get(f"/_test/candidates/{other.user_id}/profile", headers=auth_header(me))
    assert response.status_code == 403


def test_reviewer_cannot_access_candidate_data_directly(client, make_user):
    reviewer = make_user(UserRole.REVIEWER)
    candidate = make_user(UserRole.CANDIDATE)
    response = client.get(f"/_test/candidates/{candidate.user_id}/profile", headers=auth_header(reviewer))
    assert response.status_code == 403


def test_administrator_can_access_any_candidates_data(client, make_user):
    admin = make_user(UserRole.ADMINISTRATOR)
    candidate = make_user(UserRole.CANDIDATE)
    response = client.get(f"/_test/candidates/{candidate.user_id}/profile", headers=auth_header(admin))
    assert response.status_code == 200
