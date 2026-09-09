from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_id: int | None = None          # None = root


class RenameRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class MoveRequest(BaseModel):
    parent_id: int | None = None          # None = root


class ShareRequest(BaseModel):
    email: EmailStr


class ShareResponse(BaseModel):
    shared_emails: list[str]


class FolderOption(BaseModel):
    id: int | None
    name: str


class ItemResponse(BaseModel):
    id: int
    name: str
    is_folder: bool
    size: int
    parent_id: int | None
    created_at: datetime
    updated_at: datetime
    shared_emails: list[str] = []
    owner_email: str | None = None        # populated in "Shared with me" view


class DownloadResponse(BaseModel):
    url: str
    filename: str