from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, UUID4

class ListThreadsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    folder: Literal[
        "inbox",
        "sent",
        "drafts",
        "starred",
        "spam",
        "trash",
    ] | None = Field(
        default="inbox",
        description="Mailbox folder to retrieve threads from.",
    )
    
    search: str | None = Field(
        default=None,
        max_length=200,
        description="Search text for finding email conversations.",
    )

    cursor: str | None = Field(
        default=None,
        max_length=500,
        description="Pagination cursor from a previous response.",
    )

    limit: int = Field(
        default=15,
        ge=1,
        le=100,
        description="Maximum number of threads to retrieve.",
    )