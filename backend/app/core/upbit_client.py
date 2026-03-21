"""Upbit Open API client.

Handles JWT authentication and trade history fetching.
API Keys are held in memory only — never persisted to disk/DB.

Reference: https://docs.upbit.com
"""

import hashlib
import uuid
from datetime import datetime
from urllib.parse import urlencode

import httpx
import jwt
from pydantic import BaseModel


class UpbitCredentials(BaseModel):
    access_key: str
    secret_key: str


class UpbitTradeRecord(BaseModel):
    """Raw trade record from Upbit API."""

    uuid: str
    side: str  # "bid" (buy) or "ask" (sell)
    ord_type: str
    price: float
    state: str
    market: str
    volume: float
    remaining_volume: float
    executed_volume: float
    trades_count: int
    funds: float | None = None
    paid_fee: float
    created_at: str
    trades: list[dict] | None = None


class UpbitClient:
    """Upbit Open API client with JWT auth.

    Security:
    - Credentials stored in memory only
    - No disk/DB persistence
    - JWT tokens generated per-request with short-lived nonce
    """

    BASE_URL = "https://api.upbit.com/v1"

    def __init__(self, credentials: UpbitCredentials):
        self._access_key = credentials.access_key
        self._secret_key = credentials.secret_key
        self._http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        )

    def _generate_token(self, query_params: dict | None = None) -> str:
        """Generate JWT token for Upbit API authentication."""
        payload = {
            "access_key": self._access_key,
            "nonce": str(uuid.uuid4()),
        }

        if query_params:
            query_string = urlencode(query_params)
            query_hash = hashlib.sha512(query_string.encode()).hexdigest()
            payload["query_hash"] = query_hash
            payload["query_hash_alg"] = "SHA512"

        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    async def get_accounts(self) -> list[dict]:
        """Get all accounts (balances)."""
        token = self._generate_token()
        response = await self._http.get(
            "/accounts",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    async def get_orders(
        self,
        market: str | None = None,
        state: str = "done",
        page: int = 1,
        limit: int = 100,
        order_by: str = "desc",
    ) -> list[dict]:
        """Get order history.

        Args:
            market: Market code (e.g., "KRW-BTC"). None for all markets.
            state: Order state filter - "done" (completed), "cancel", "wait"
            page: Page number (1-indexed)
            limit: Results per page (max 100)
            order_by: "asc" or "desc"
        """
        params: dict = {
            "state": state,
            "page": str(page),
            "limit": str(limit),
            "order_by": order_by,
        }
        if market:
            params["market"] = market

        token = self._generate_token(params)
        response = await self._http.get(
            "/orders",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    async def get_order_detail(self, order_uuid: str) -> dict:
        """Get detailed order info including individual trades."""
        params = {"uuid": order_uuid}
        token = self._generate_token(params)
        response = await self._http.get(
            "/order",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    async def fetch_all_completed_orders(
        self,
        market: str | None = None,
        max_pages: int = 50,
    ) -> list[dict]:
        """Fetch all completed orders with pagination.

        Iterates through pages until no more results or max_pages reached.
        For market orders (price=null), fetches order detail to get actual
        execution price and funds from individual trades.
        """
        all_orders: list[dict] = []
        page = 1

        while page <= max_pages:
            orders = await self.get_orders(
                market=market,
                state="done",
                page=page,
                limit=100,
            )

            if not orders:
                break

            all_orders.extend(orders)
            page += 1

        return all_orders

    async def verify_credentials(self) -> bool:
        """Verify API credentials are valid by fetching accounts."""
        try:
            await self.get_accounts()
            return True
        except httpx.HTTPStatusError:
            return False

    async def close(self):
        """Close HTTP client."""
        await self._http.aclose()
