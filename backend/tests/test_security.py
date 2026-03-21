"""Tests for credential manager."""

import time

import pytest

from app.core.security import CredentialManager, Session, SESSION_TTL_SECONDS
from app.core.upbit_client import UpbitCredentials


@pytest.fixture
def manager():
    return CredentialManager()


@pytest.fixture
def creds():
    return UpbitCredentials(access_key="test-access", secret_key="test-secret")


def test_create_session(manager, creds):
    token = manager.create_session(creds)
    assert isinstance(token, str)
    assert len(token) > 20  # cryptographically random
    assert manager.active_sessions == 1


def test_get_client(manager, creds):
    token = manager.create_session(creds)
    client = manager.get_client(token)
    assert client is not None


def test_get_client_invalid_token(manager):
    client = manager.get_client("nonexistent-token")
    assert client is None


def test_get_client_touches_session(manager, creds):
    token = manager.create_session(creds)
    session = manager._sessions[token]
    old_accessed = session.last_accessed

    time.sleep(0.01)
    manager.get_client(token)

    assert session.last_accessed > old_accessed


@pytest.mark.asyncio
async def test_remove_session(manager, creds):
    token = manager.create_session(creds)
    assert manager.active_sessions == 1

    await manager.remove_session(token)
    assert manager.active_sessions == 0
    assert manager.get_client(token) is None


def test_session_expiry():
    session = Session(
        client=None,
        last_accessed=time.time() - SESSION_TTL_SECONDS - 1,
    )
    assert session.is_expired


def test_session_not_expired():
    session = Session(client=None)
    assert not session.is_expired


def test_multiple_sessions(manager, creds):
    t1 = manager.create_session(creds)
    t2 = manager.create_session(creds)
    assert t1 != t2
    assert manager.active_sessions == 2


def test_cleanup_expired(manager, creds):
    token = manager.create_session(creds)
    # Manually expire
    manager._sessions[token].last_accessed = time.time() - SESSION_TTL_SECONDS - 1

    # Creating a new session triggers cleanup
    manager.create_session(creds)
    assert manager.active_sessions == 1  # Expired one removed
