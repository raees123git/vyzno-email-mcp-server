from typing import Any
import httpx
from fastmcp.exceptions import ToolError
from uuid import uuid4

from mcp_server_email.auth import (
    user_mailbox_id,
    vyzno_auth_headers,
)
from mcp_server_email.config import Settings


async def vyzno_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:

    settings = Settings()
    mailbox_id = user_mailbox_id()
    idempotency_key = str(uuid4())

    headers = vyzno_auth_headers(settings)

    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    try:
        async with httpx.AsyncClient(
            base_url=str(settings.vyzno_base_url),
            headers=headers,
            timeout=timeout,
            follow_redirects=False,
        ) as client:
            response = await client.request(
                method,
                f"/v1/mailboxes/{mailbox_id}{path}",
                params=params,
                json=payload,
            )

            response.raise_for_status()

            if response.status_code == 204:
                return {}

            result = response.json()

            if not isinstance(result, dict):
                raise ToolError("Unexpected Vyzno response.")

            return result

    except httpx.HTTPStatusError as exc:
        raise ToolError(
            f"Vyzno returned HTTP {exc.response.status_code}."
        ) from None

    except httpx.RequestError:
        raise ToolError(
            "Unable to complete the Vyzno request. "
            "For write operations, the result may be unknown."
        ) from None

