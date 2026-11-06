from typing import Any
from html import escape
from pydantic import UUID4
from fastmcp.exceptions import ToolError
from fastmcp.tools import tool
from mcp_server_email.schemas.drafts import CreateDraft, UpdateDraft
from mcp_server_email.schemas.threads import ListThreadsInput
from mcp_server_email.client.vyzno import vyzno_request


@tool()
async def create_draft( draft: CreateDraft ) -> dict[str, Any]:
    """
    Create and save an email draft in the user's Vyzno mailbox.

    Requirements:
    - The user must provide a subject or message body, or both.
    - If only the body is provided, generate a concise, relevant subject based on the message content.
    - If the subject is provided, preserve the user's intended subject.
    - If the user provides a recipient email address, include it. Otherwise, leave the recipient list empty.
    - Do not invent recipient email addresses or missing message content from your own knowledge.
    - If neither a subject nor message content is provided, ask the user for more information before calling this tool. Subject or message content (any of them) is required to create a draft.
    """

    payload = draft.model_dump(mode="json", by_alias=True)

    if draft.body_text is not None:
        html_body = escape(draft.body_text)
        html_body = html_body.replace("\n", "<br>")
        payload["bodyHtml"] = f"<p>{html_body}</p>"
    else:
        payload["bodyHtml"] = None

    
    return await vyzno_request(
        method="POST",
        path="/drafts",
        payload=payload,
    )


@tool()
async def get_draft(draft_id: UUID4) -> dict[str, Any]:
    """
    Retrieve one draft by its exact, already-known draft ID.

    Use this only when:
    - The exact draft ID was returned by create_draft, list_threads/get_thread, or a previous verified operation.
    - You need to inspect the draft before sending, updating, or deleting it.
    - call it only after first calling list_threads/get_thread to find the draft ID, or after creating a draft with create_draft.

    Do not use this tool to:
    - Find the latest draft.
    - Search or list drafts.
    - Guess or invent a draft ID.
    - Pass a thread ID in place of a draft ID.

    Requirements:
    - Use an existing draft ID from a verified tool response.
    - Never invent or guess a draft ID.
    - This tool only retrieves draft information.
    - Do not modify, send, or delete the draft.
    

    For latest/last-N draft requests, call list_threads with folder="drafts" first, then resolve the actual draft message IDs.
    This tool is read-only and does not send, update, or delete anything. 
    """

    return await vyzno_request(
        method="GET",
        path=f"/drafts/{draft_id}",
    )





@tool()
async def update_draft(
    draft_id: UUID4,
    changes: UpdateDraft,
) -> dict[str, Any]:
    """
    Update an existing email draft in the user's Vyzno mailbox.

    Use this tool when the user wants to:
    - Add or change recipient email addresses.
    - Change the email subject.
    - Edit or rewrite the email body.
    - Refine an existing draft through follow-up instructions.

    Requirements:
    - Use the draft ID returned by a previous draft operation.
    - Never invent a draft ID or recipient address. pass the draft id as you received after creating a draft.
    - Update the existing draft instead of creating a new one.
    - Preserve existing fields unless the user requests changes.
    - When changing the body, provide the complete revised text.
    - This tool updates and saves the draft; it does not send it.
    """

    payload = changes.model_dump(
        mode="json",
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )

    if not payload:
        raise ToolError("No draft changes were provided.")

    if changes.body_text is not None:
        text = changes.body_text.replace("\r\n", "\n").replace("\r", "\n")
        html_body = escape(text).replace("\n", "<br>")
        payload["bodyHtml"] = f"<p>{html_body}</p>"

    return await vyzno_request(
        method="PATCH",
        path=f"/drafts/{draft_id}",
        payload=payload,
    )


@tool()
async def delete_draft(draft_id: UUID4) -> dict[str, Any]:
    """
    Delete an existing saved email draft from the user's Vyzno mailbox.

    Use this tool when the user wants to delete a saved draft.

    Requirements:
    - Use the existing draft ID from a previous tool response or another verified source.
    - Draft ID is given by get_thread tool. First call list_threads with folder="drafts" to get the thread_id, then call get_thread with that thread_id to retrieve the draft_id, and finally call delete_draft with the exact draft_id.
    - Never invent a draft ID.
    - Never use a thread ID or message ID as a draft ID.
    - Only report success when the backend confirms deletion.
    - this draft is only for deleting saved drafts, not sent, received, or other email types.
    """

    await vyzno_request(
        method="DELETE",
        path=f"/drafts/{draft_id}",
    )

    return {
        "deleted": True,
        "draft_id": str(draft_id),
    }





@tool()
async def send_email(draft_id: UUID4) -> dict[str, Any]:
    """
    Send an existing email draft from the user's Vyzno mailbox.

    Usage:
    - For a new email, first call create_draft to create
      the email, then call send_email using the returned draft ID.
    - For an already saved draft, use its existing draft ID
      and call send_email directly.
    - Never create another draft if one already exists
      for the email the user wants to send.

    Requirements:
    - Send only after the user explicitly confirms.
    - Never invent a draft ID.
    - Never send without a valid recipient.
    - Do not automatically retry an uncertain send.
    """

    try:
        result = await vyzno_request(
            method="POST",
            path=f"/drafts/{draft_id}/send",
            timeout=90.0,
        )

    except ToolError as exc:
        raise ToolError(
            f"Sending could not be confirmed for draft {draft_id}. "
            "Check its status before retrying."
        ) from exc

    return result


@tool()
async def trash_email(message_id: UUID4,  thread_id: UUID4) -> dict[str, Any]:
    """
    Move one email message to the mailbox Trash folder.

    Use this tool when the user asks to delete, trash, or remove one email from the inbox, sent folder, or another mailbox folder.

    Requirements:
    - Use the exact message ID from list_threads response.
    - You will get message_id by calling list_threads tool. 
    - This moves the message to Trash; it does not permanently delete it.
    - This tool only moves one single email message to trash, not an entire thread or multiple messages.
    """

    await vyzno_request(
        method="PATCH",
        path=f"/messages/{message_id}",
        payload={"trashed": True},
    )

    return {
    "trashed": True,
    "message_id": str(message_id),
    "thread_id": str(thread_id),
    }


@tool()
async def restore_email(message_id: UUID4) -> dict[str, Any]:
    """
    Restore one email message from Trash.

    Use the exact message ID from list_threads(folder="trash").
    This restores only one message, not the entire conversation.
    """

    await vyzno_request(
        method="PATCH",
        path=f"/messages/{message_id}",
        payload={"trashed": False},
    )

    return {
        "restored": True,
        "message_id": str(message_id),
    }




@tool()
async def list_threads(
    filters: ListThreadsInput,
) -> dict[str, Any]:
    """
    Search, filter, and retrieve a paginated list of email
    conversation threads from the user's Vyzno mailbox.

    Use this tool to:
    - List recent email conversations.
    - Retrieve conversations from inbox, sent, drafts,
      starred, spam, or trash folders.
    - Search conversations using keywords or search text.
    - Find relevant conversations before reading, summarizing, or replying to them.
    - Identify unread, starred, or attachment-containing threads among the returned results.
    - Retrieve additional pages of conversations using a cursor.

    Each thread summary includes:
    - Thread ID and latest message ID.
    - Subject, sender, and preview.
    - Last message date and time.
    - Read and starred status.
    - Message and attachment counts.
    - Associated labels.

    Results are paginated. Use nextCursor to fetch additional
    pages when hasNextPage is true.

    This tool only retrieves thread summaries, not full message bodies. Use get_thread to read a conversation's full content.
    This tool cannot send, modify, or delete emails.
    """


    params = filters.model_dump(
        mode="json",
        exclude_none=True,
    )

    return await vyzno_request(
        method="GET",
        path="/threads",
        params=params,
    )



@tool()
async def get_thread(thread_id: UUID4) -> dict[str, Any]:
    """
    Retrieve the complete email conversation from the user's Vyzno mailbox.

    Use this tool to:
    - Read the full content of an email conversation.
    - Summarize an individual email or entire thread.
    - Answer questions about messages in a conversation.
    - Understand conversation context before replying.

    Requirements:
    - Use a valid thread ID obtained from list_threads or the currently selected email context.
    - Never invent a thread ID.
    - Do not modify, delete, or send any emails.

    Returns the thread details and its messages, including their available bodies and metadata.
    """

    return await vyzno_request(
        method="GET",
        path=f"/threads/{thread_id}",
    )


@tool()
async def trash_thread(thread_id: UUID4) -> dict[str, Any]:
    """
    Move an entire email conversation to Trash.

    Use only when the user asks to trash or delete the whole conversation.
    Do not use for a single email; use trash_email instead.
    Do not use for drafts; use delete_draft instead.
    This tool moves the entire thread to Trash, not just one message.
    """

    await vyzno_request(
        method="PATCH",
        path=f"/threads/{thread_id}",
        payload={"trashed": True},
    )

    return {
        "trashed": True,
        "thread_id": str(thread_id),
    }


@tool()
async def restore_thread(thread_id: UUID4) -> dict[str, Any]:
    """
    Restore an entire email conversation from Trash.

    Use the exact thread ID from list_threads(folder="trash").
    This restores every message in the conversation.
    """

    await vyzno_request(
        method="PATCH",
        path=f"/threads/{thread_id}",
        payload={"trashed": False},
    )

    return {
        "restored": True,
        "thread_id": str(thread_id),
    }


@tool()
async def permanently_delete_thread(thread_id: UUID4) -> dict[str, Any]:
    """
    Permanently delete an entire email conversation.

    Use only when the user explicitly asks to permanently delete a conversation from the Trash folder.

    Requirements:
    - Use the exact thread ID from list_threads(folder="trash").
    - The entire thread must already be in Trash.
    - This permanently deletes the whole conversation.
    - Do not use this for one message; individual permanent message deletion is not supported.
    - This action cannot be undone.
    """

    await vyzno_request(
        method="DELETE",
        path=f"/threads/{thread_id}",
    )

    return {
        "permanently_deleted": True,
        "thread_id": str(thread_id),
    }