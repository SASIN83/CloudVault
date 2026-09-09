from fastapi import APIRouter, Depends, UploadFile, Query, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.item import Item
from app.views.file_views import (FolderCreate, RenameRequest, MoveRequest, ShareRequest,
                                  ShareResponse, FolderOption, ItemResponse, DownloadResponse,
                                  UploadInitRequest, UploadInitResponse)
from app.services import file_service, s3_service
from app.services.auth_service import get_current_user
from app.services.rate_limiter import limiter

router = APIRouter(prefix="/api/files", tags=["Files"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


# ══════════ STATIC ROUTES — MUST stay ABOVE /{parent_id} & /{item_id} ══════════

@router.post("/folders", response_model=ItemResponse, status_code=201)
def create_folder(request: Request, payload: FolderCreate, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    return file_service.create_folder(db, user, payload.name, payload.parent_id)


@router.get("/shared", response_model=list[ItemResponse])
def shared_with_me(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.list_shared(db, user)


@router.get("/recent", response_model=list[ItemResponse])
def recent(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.list_recent(db, user)


@router.get("/trash", response_model=list[ItemResponse])
def trash(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.list_trash(db, user)


@router.delete("/trash", status_code=204)
@limiter.limit("60/hour")
def empty_trash(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_service.empty_trash(db, user)


@router.get("/folder-options", response_model=list[FolderOption])
def folder_options(request: Request, exclude: int | None = Query(default=None),
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.folder_options(db, user, exclude)


# ══════════ PARAMETERIZED ROUTES ══════════

@router.post("/upload-init", response_model=UploadInitResponse, status_code=201)
@limiter.limit("60/hour")
def upload_init(request: Request, payload: UploadInitRequest,
                db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.init_upload(db, user, payload.parent_id, payload.filename,
                                    payload.size, payload.content_type, payload.conflict_action)


@router.post("/upload-confirm/{item_id}", response_model=ItemResponse)
@limiter.limit("120/hour")
def upload_confirm(request: Request, item_id: int,
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.confirm_upload(db, user, item_id)


@router.get("/{parent_id}", response_model=list[ItemResponse])
def list_folder(request: Request, parent_id: int,
                search: str = Query(default=""),
                sort_by: str = Query(default="name", pattern="^(name|date)$"),
                db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.list_folder(db, user, None if parent_id == 0 else parent_id, search, sort_by)


@router.post("/upload/{parent_id}", response_model=ItemResponse, status_code=201)
@limiter.limit("60/hour")
async def upload_file(request: Request, parent_id: int, file: UploadFile,
                      conflict_action: str | None = Query(default=None, pattern="^(replace|rename)$"),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds the 50 MB limit")
    return file_service.save_upload(db, user, None if parent_id == 0 else parent_id,
                                    file.filename, content, conflict_action)


@router.post("/{item_id}/rename", response_model=ItemResponse)
@limiter.limit("60/hour")
def rename(request: Request, item_id: int, payload: RenameRequest,
           db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.rename_item(db, item_id, payload.name, user)


@router.post("/{item_id}/move", response_model=ItemResponse)
@limiter.limit("60/hour")
def move(request: Request, item_id: int, payload: MoveRequest,
         db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.move_item(db, item_id, payload.parent_id, user)


@router.post("/{item_id}/copy", response_model=ItemResponse, status_code=201)
@limiter.limit("60/hour")
def copy(request: Request, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return file_service.copy_item(db, item_id, user)


@router.delete("/{item_id}", status_code=204)
@limiter.limit("60/hour")
def to_trash(request: Request, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_service.soft_delete(db, item_id, user)


@router.post("/{item_id}/restore", status_code=204)
@limiter.limit("60/hour")
def restore(request: Request, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_service.restore(db, item_id, user)


@router.delete("/{item_id}/permanent", status_code=204)
@limiter.limit("60/hour")
def delete_forever(request: Request, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_service.hard_delete(db, item_id, user)


@router.post("/{item_id}/share", response_model=ShareResponse)
@limiter.limit("60/hour")
def share(request: Request, item_id: int, payload: ShareRequest,
          db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"shared_emails": file_service.share_item(db, item_id, payload.email, user)}


@router.delete("/{item_id}/share/{email}", response_model=ShareResponse)
@limiter.limit("60/hour")
def unshare(request: Request, item_id: int, email: str,
            db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"shared_emails": file_service.unshare_item(db, item_id, email, user)}


@router.get("/{item_id}/download", response_model=DownloadResponse)
@limiter.limit("60/hour")
def download(request: Request, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item or item.is_folder or item.deleted_at:
        raise HTTPException(404, "File not found")
    
    if getattr(item, "upload_status", "ready") != "ready":
        raise HTTPException(409, "Upload not finalized")
    if not file_service.can_access(db, item, user):
        raise HTTPException(403, "Access denied")
    return {"url": s3_service.presigned_download_url(item.s3_key, item.name), "filename": item.name}