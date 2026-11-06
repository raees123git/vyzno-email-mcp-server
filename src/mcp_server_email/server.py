from fastmcp import FastMCP

from mcp_server_email.config import Settings
from mcp_server_email.tools.drafts import (
    create_draft,
    update_draft,
    send_email,
    trash_email,
    list_threads,
    get_thread,
    delete_draft,
    get_draft,
    trash_thread,
    permanently_delete_thread,
    restore_email,
    restore_thread,
)

mcp = FastMCP("Vyzno Mail", mask_error_details=True)

mcp.add_tool(create_draft)
mcp.add_tool(update_draft)
mcp.add_tool(send_email)
mcp.add_tool(trash_email)
mcp.add_tool(list_threads)
mcp.add_tool(get_thread)
mcp.add_tool(delete_draft)
mcp.add_tool(get_draft)
mcp.add_tool(trash_thread)
mcp.add_tool(permanently_delete_thread)
mcp.add_tool(restore_email)
mcp.add_tool(restore_thread)

if __name__ == "__main__":
    settings = Settings()

    mcp.run(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )