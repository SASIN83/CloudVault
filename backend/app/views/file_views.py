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

class UploadInitRequest(BaseModel):
    parent_id: int | None = None
    filename: str = Field(min_length=1, max_length=255)
    size: int = Field(gt=0)
    content_type: str | None = None
    conflict_action: str | None = Field(default=None, pattern="^(replace|rename)$")


class UploadInitResponse(BaseModel):
    item_id: int
    upload_url: str
    key: str
    final_name: str