# MCP Server Email

A FastMCP server that exposes tools to create drafts and send emails through Vyzno.

## Setup

Requires Python 3.11+ and uv.

Install dependencies from the project folder:

```powershell
uv sync
```

Create a `.env` file:

```dotenv
VYZNO_BASE_URL=https://api.vyzno.io
```

The MCP client must provide these HTTP headers for tool calls:

- `Vyzno-Cookie`: the user's Vyzno cookie header.
- `Vyzno-CSRF-Token`: the user's CSRF token.
- `Vyzno-Mailbox-Id`: the mailbox ID.

Keep credentials private.

## Run

```powershell
uv run python -m mcp_server_email.server
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`.

This check lists tools without creating or sending emails.

## Tools

- `create_draft`: saves an email as a draft.
- `send_email`: creates a draft, reads its ID, and calls the send endpoint.

## Flow

```text
MCP client -> MCP tool -> Vyzno -> texinity-mail
```

Sending calls `POST /v1/mailboxes/:mailboxId/drafts`, then `POST /v1/mailboxes/:mailboxId/drafts/:draftId/send`.
