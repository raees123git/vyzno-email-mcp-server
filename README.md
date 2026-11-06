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

In a separate terminal, check tool discovery:

```powershell
uv run python server-check.py
```

## Tools

- **`create_draft`**: Creates and saves a new email draft.
- **`update_draft`**: Updates an existing saved draft.
- **`send_email`**: Sends an existing saved draft.
- **`trash_email`**: Moves one email message to the Trash folder.
- **`restore_email`**: Restores one email message from Trash.
- **`trash_thread`**: Moves an entire conversation to the Trash folder.
- **`restore_thread`**: Restores an entire conversation from Trash.
- **`permanently_delete_thread`**: Permanently deletes an entire trashed conversation.
- **`list_threads`**: Lists and searches conversations across mailbox folders.
- **`get_thread`**: Retrieves a complete conversation and its messages.
- **`get_draft`**: Retrieves one draft by its exact draft ID.
- **`delete_draft`**: Permanently deletes one saved draft.
## Flow

```text
MCP client -> MCP tool -> Vyzno -> texinity-mail
```
