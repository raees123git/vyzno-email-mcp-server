from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)


class CreateDraft(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        hide_input_in_errors=True,
    )

    type: Literal["new"] = "new"

    to: list[EmailStr] = Field(
        default_factory=list,
        max_length=100,
        description="Recipient email addresses. Leave empty if not provided."
    )
    subject: str | None = Field(
        default=None,
        max_length=998,
        description=(
        "Email subject. Preserve the user's subject if provided. "
        "If only a message body is given, generate a relevant subject."
        )
    )
    body_text: str | None = Field(
        default=None,
        alias="bodyText",
        max_length=1_000_000,
        description=(
        "Plain-text email body. Use the message provided by the user. "
        )
    )


    @model_validator(mode="after")
    def require_content(self) -> Self:
        has_content = bool(
            (self.subject or "").strip()
            or (self.body_text or "").strip()
        )

        if not has_content:
            raise ValueError(
                "Provide a subject, or message content."
            )

        return self



class UpdateDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    to: list[EmailStr] | None = Field(
        default=None,
        max_length=100,
        description="Updated recipient email addresses.",
    )

    subject: str | None = Field(
        default=None,
        max_length=998,
        description="Updated email subject.",
    )

    body_text: str | None = Field(
        default=None,
        alias="bodyText",
        max_length=1_000_000,
        description="Complete updated plain-text email body.",
    )
    