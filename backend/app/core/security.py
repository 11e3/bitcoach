"""In-memory credential manager.

API Keys are stored in server memory only:
- Never written to disk or database
- Cleared on server restart
- Per-session isolation via session tokens
- Auto-expiry after inactivity
"""

import secrets
import time
from dataclasses import dataclass, field

from app.core.upbit_client import UpbitClient, UpbitCredentials

# Session expires after 1 hour of inactivity
SESSION_TTL_SECONDS = 3600


@dataclass
class Session:
    client: UpbitClient
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

    def touch(self):
        self.last_accessed = time.time()

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.last_accessed) > SESSION_TTL_SECONDS


class CredentialManager:
    """Manages in-memory sessions with Upbit API credentials.

    Security guarantees:
    - Credentials exist only in RAM
    - Session tokens are cryptographically random
    - Expired sessions are automatically cleaned
    - Server restart clears all credentials
    """

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(self, credentials: UpbitCredentials) -> str:
        """Create a new session with API credentials. Returns session token."""
        self._cleanup_expired()

        token = secrets.token_urlsafe(32)
        client = UpbitClient(credentials)
        self._sessions[token] = Session(client=client)
        return token

    def get_client(self, token: str) -> UpbitClient | None:
        """Get Upbit client for a session. Returns None if expired/invalid."""
        session = self._sessions.get(token)
        if session is None:
            return None

        if session.is_expired:
            self._remove_session(token)
            return None

        session.touch()
        return session.client

    async def remove_session(self, token: str):
        """Explicitly remove a session (logout)."""
        await self._remove_session(token)

    async def _remove_session(self, token: str):
        session = self._sessions.pop(token, None)
        if session:
            await session.client.close()

    def _cleanup_expired(self):
        """Remove expired sessions."""
        expired = [t for t, s in self._sessions.items() if s.is_expired]
        for token in expired:
            session = self._sessions.pop(token, None)
            # Can't await in sync context — client will be GC'd

    @property
    def active_sessions(self) -> int:
        return len(self._sessions)


# Singleton instance
credential_manager = CredentialManager()
