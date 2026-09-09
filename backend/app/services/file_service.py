import os
from datetime import datetime,timedelta
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.item import Item, ItemShare
from app.models.user import User
from app.services import s3_service

UPLOAD_PENDING_MINUTES = 60
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


def init_upload(db, user, parent_id, filename, size, content_type, conflict_action):
    """Phase 1: validate, reserve final name, return a presigned PUT URL."""
    _validate_parent(db, parent_id, user)
    if not filename or not size or size <= 0:
        raise HTTPException(400, "Invalid file metadata")
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds the 50 MB limit")

    existing = db.query(Item).filter(
        Item.parent_id == parent_id, Item.owner_id == user.id, Item.name == filename,
        Item.deleted_at.is_(None), Item.upload_status == "ready").first()
    if existing and existing.is_folder:
        raise HTTPException(400, "A folder with this name already exists")
    if existing and conflict_action is None:
        raise HTTPException(409, "File already exists")

    replaces_id = None
    if existing and conflict_action == "rename":
        filename = unique_name(db, parent_id, filename, user.id)
    elif existing and conflict_action == "replace":
        replaces_id = existing.id

    ext = os.path.splitext(filename)[1]
    s3_key = f"users/{user.id}/{uuid4().hex}{ext}"
    item = Item(name=filename, is_folder=False, size=size, s3_key=s3_key,
                parent_id=parent_id, owner_id=user.id,
                upload_status="pending", replaces_id=replaces_id)
    db.add(item); db.commit(); db.refresh(item)

    return {
        "item_id": item.id,
        "upload_url": s3_service.presigned_put_url(s3_key, content_type or "application/octet-stream"),
        "key": s3_key,
        "final_name": filename,
    }


def confirm_upload(db, user, item_id):
    """Phase 2: verify bytes landed in S3, finalize row, clean up replaced file."""
    item = _owned_item(db, item_id, user)
    if item.upload_status != "pending":
        raise HTTPException(409, "Upload already confirmed")

    actual = s3_service.head_object_size(item.s3_key)
    if actual is None:
        raise HTTPException(400, "Upload not received by S3 — please retry")
    if actual > MAX_UPLOAD_BYTES:                      # client lied about size
        s3_service.delete_file(item.s3_key)
        db.delete(item); db.commit()
        raise HTTPException(413, "File exceeds the 50 MB limit")

    item.size = actual
    item.upload_status = "ready"
    if item.replaces_id:
        old = db.get(Item, item.replaces_id)
        if old:
            if old.s3_key:
                s3_service.delete_file(old.s3_key)
            db.delete(old)
        item.replaces_id = None
    db.commit(); db.refresh(item)
    return serialize(item, user)


def purge_abandoned_uploads(db: Session) -> int:
    """Clients that vanished mid-upload leave pending rows — reap them."""
    cutoff = datetime.utcnow() - timedelta(minutes=UPLOAD_PENDING_MINUTES)
    stale = db.query(Item).filter(Item.upload_status == "pending", Item.created_at < cutoff).all()
    for it in stale:
        if it.s3_key:
            s3_service.delete_file(it.s3_key)
        db.delete(it)
    if stale:
        db.commit()
    return len(stale)
# ───────────────────────── helpers ─────────────────────────

def _owned_item(db: Session, item_id: int, user: User) -> Item:
    item = db.get(Item, item_id)
    if not item or item.owner_id != user.id or item.deleted_at:
        raise HTTPException(404, "Item not found")
    return item


def unique_name(db: Session, parent_id, name: str, owner_id: int, exclude_id=None) -> str:
    """Returns `name`, or `name (1)`, `name (2)`… if it already exists."""
    def exists(candidate: str) -> bool:
        q = db.query(Item).filter(
            Item.parent_id == parent_id, Item.owner_id == owner_id,
            Item.name == candidate, Item.deleted_at.is_(None))
        if exclude_id:
            q = q.filter(Item.id != exclude_id)
        return q.first() is not None

    if not exists(name):
        return name
    base, ext = os.path.splitext(name)
    counter = 1
    while exists(f"{base} ({counter}){ext}"):
        counter += 1
    return f"{base} ({counter}){ext}"


def serialize(item: Item, user: User) -> dict:
    return {
        "id": item.id, "name": item.name, "is_folder": item.is_folder,
        "size": item.size, "parent_id": item.parent_id,
        "created_at": item.created_at, "updated_at": item.updated_at,
        "shared_emails": [s.shared_email for s in item.shares],
        "owner_email": item.owner.email if item.owner_id != user.id else None,
    }


def _sorted(query, sort_by: str):
    if sort_by == "date":
        return query.order_by(Item.is_folder.desc(), Item.updated_at.desc())
    return query.order_by(Item.is_folder.desc(), Item.name.asc())


def _descendants(db: Session, item: Item, trashed_only: bool = False) -> list[Item]:
    q = db.query(Item).filter(Item.parent_id == item.id)
    if trashed_only:
        q = q.filter(Item.deleted_at.isnot(None))
    else:
        q = q.filter(Item.deleted_at.is_(None))
    out = []
    for child in q.all():
        out.append(child)
        out.extend(_descendants(db, child, trashed_only))
    return out


def _validate_parent(db: Session, parent_id, user: User):
    if parent_id is None:
        return
    parent = db.get(Item, parent_id)
    if not parent or not parent.is_folder or parent.owner_id != user.id or parent.deleted_at:
        raise HTTPException(404, "Parent folder not found")


# ───────────────────────── queries ─────────────────────────


def list_folder(db: Session, user: User, parent_id, search: str, sort_by: str) -> list[dict]:
    if parent_id is None:
        q = db.query(Item).filter(
            Item.owner_id == user.id, Item.parent_id.is_(None), Item.deleted_at.is_(None))
    else:
        parent = db.get(Item, parent_id)
        if not parent or not parent.is_folder or parent.deleted_at:
            raise HTTPException(404, "Folder not found")
        if not can_access(db, parent, user):
            raise HTTPException(403, "Access denied")
        # Children of a shared folder belong to the owner — don't filter by owner here
        q = db.query(Item).filter(Item.parent_id == parent_id, Item.deleted_at.is_(None))
    if search:
        q = q.filter(Item.name.ilike(f"%{search}%"))
    return [serialize(i, user) for i in _sorted(q, sort_by).all()]

def list_shared(db: Session, user: User) -> list[dict]:
    rows = (db.query(Item)
            .join(ItemShare, ItemShare.item_id == Item.id)
            .filter(ItemShare.shared_email == user.email, Item.deleted_at.is_(None))
            .order_by(Item.updated_at.desc()).all())
    return [serialize(i, user) for i in rows]


def list_recent(db: Session, user: User, limit: int = 30) -> list[dict]:
    rows = (db.query(Item)
            .filter(Item.owner_id == user.id, Item.is_folder.is_(False), Item.deleted_at.is_(None))
            .order_by(Item.updated_at.desc()).limit(limit).all())
    return [serialize(i, user) for i in rows]


def list_trash(db: Session, user: User) -> list[dict]:
    items = db.query(Item).filter(Item.owner_id == user.id, Item.deleted_at.isnot(None)).all()
    trashed_ids = {i.id for i in items}
    top = [i for i in items if i.parent_id is None or i.parent_id not in trashed_ids]
    return [serialize(i, user) for i in sorted(top, key=lambda x: x.deleted_at, reverse=True)]


# ───────────────────────── mutations ─────────────────────────

def create_folder(db: Session, user: User, name: str, parent_id) -> dict:
    _validate_parent(db, parent_id, user)
    folder = Item(name=unique_name(db, parent_id, name, user.id),
                  is_folder=True, parent_id=parent_id, owner_id=user.id)
    db.add(folder); db.commit(); db.refresh(folder)
    return serialize(folder, user)


def save_upload(db: Session, user: User, parent_id, filename: str,
                content: bytes, conflict_action: str | None) -> dict:
    _validate_parent(db, parent_id, user)

    existing = db.query(Item).filter(
        Item.parent_id == parent_id, Item.owner_id == user.id,
        Item.name == filename, Item.deleted_at.is_(None)).first()
    if existing and existing.is_folder:
        raise HTTPException(400, "A folder with this name already exists")
    if existing and conflict_action is None:
        raise HTTPException(409, "File already exists")

    if existing and conflict_action == "rename":
        filename = unique_name(db, parent_id, filename, user.id)
    if existing and conflict_action == "replace":
        s3_service.delete_file(existing.s3_key)

    ext = os.path.splitext(filename)[1]
    s3_key = f"users/{user.id}/{uuid4().hex}{ext}"   # UUID key → rename/move never touch S3
    s3_service.upload_file(content, s3_key)

    if existing and conflict_action == "replace":
        existing.size = len(content)
        existing.s3_key = s3_key
        existing.updated_at = datetime.utcnow()
        item = existing
    else:
        item = Item(name=filename, is_folder=False, size=len(content),
                    s3_key=s3_key, parent_id=parent_id, owner_id=user.id)
        db.add(item)
    db.commit(); db.refresh(item)
    return serialize(item, user)


def rename_item(db: Session, item_id: int, new_name: str, user: User) -> dict:
    item = _owned_item(db, item_id, user)
    clash = db.query(Item).filter(
        Item.parent_id == item.parent_id, Item.owner_id == user.id,
        Item.name == new_name, Item.id != item.id, Item.deleted_at.is_(None)).first()
    if clash:
        raise HTTPException(409, "An item with this name already exists here")
    item.name = new_name
    item.updated_at = datetime.utcnow()
    db.commit(); db.refresh(item)
    return serialize(item, user)


def move_item(db: Session, item_id: int, new_parent_id, user: User) -> dict:
    item = _owned_item(db, item_id, user)
    _validate_parent(db, new_parent_id, user)

    if new_parent_id is not None and item.is_folder:
        cursor = db.get(Item, new_parent_id)
        while cursor:                                   # cycle prevention
            if cursor.id == item.id:
                raise HTTPException(400, "Cannot move a folder into itself or a subfolder")
            cursor = db.get(Item, cursor.parent_id) if cursor.parent_id else None

    item.name = unique_name(db, new_parent_id, item.name, user.id, exclude_id=item.id)
    item.parent_id = new_parent_id
    item.updated_at = datetime.utcnow()
    db.commit(); db.refresh(item)
    return serialize(item, user)


def copy_item(db: Session, item_id: int, user: User) -> dict:
    item = _owned_item(db, item_id, user)
    if item.is_folder:
        raise HTTPException(400, "Folder copy is not supported yet")
    new_name = unique_name(db, item.parent_id, item.name, user.id)
    ext = os.path.splitext(item.name)[1]
    new_key = f"users/{user.id}/{uuid4().hex}{ext}"
    s3_service.copy_file(item.s3_key, new_key)
    copy = Item(name=new_name, is_folder=False, size=item.size,
                s3_key=new_key, parent_id=item.parent_id, owner_id=user.id)
    db.add(copy); db.commit(); db.refresh(copy)
    return serialize(copy, user)


def soft_delete(db: Session, item_id: int, user: User) -> None:
    item = _owned_item(db, item_id, user)
    now = datetime.utcnow()
    for target in [item] + _descendants(db, item):
        target.deleted_at = now
    db.commit()


def restore(db: Session, item_id: int, user: User) -> None:
    item = db.get(Item, item_id)
    if not item or item.owner_id != user.id or not item.deleted_at:
        raise HTTPException(404, "Item not found in trash")
    for target in [item] + _descendants(db, item, trashed_only=True):
        target.deleted_at = None
    db.commit()


def hard_delete(db: Session, item_id: int, user: User) -> None:
    item = db.get(Item, item_id)
    if not item or item.owner_id != user.id:
        raise HTTPException(404, "Item not found")
    targets = [item] + _descendants(db, item)
    for target in targets:
        if not target.is_folder and target.s3_key:
            s3_service.delete_file(target.s3_key)
        db.delete(target)
    db.commit()


# ───────────────────────── sharing & access ─────────────────────────

def share_item(db: Session, item_id: int, email: str, user: User) -> list[str]:
    item = _owned_item(db, item_id, user)
    if email.lower() == user.email.lower():
        raise HTTPException(400, "You cannot share an item with yourself")
    if not db.query(ItemShare).filter_by(item_id=item.id, shared_email=email).first():
        db.add(ItemShare(item_id=item.id, shared_email=email))
        db.commit()
    return [s.shared_email for s in item.shares]


def unshare_item(db: Session, item_id: int, email: str, user: User) -> list[str]:
    item = _owned_item(db, item_id, user)
    db.query(ItemShare).filter_by(item_id=item.id, shared_email=email).delete()
    db.commit()
    return [s.shared_email for s in item.shares]


def can_access(db: Session, item: Item, user: User) -> bool:
    """Owner, OR shared directly, OR shared via any parent folder."""
    if item.owner_id == user.id:
        return True
    cursor = item
    while cursor:
        if db.query(ItemShare).filter_by(item_id=cursor.id, shared_email=user.email).first():
            return True
        cursor = db.get(Item, cursor.parent_id) if cursor.parent_id else None
    return False

# ───────────────────────── move-modal helper ─────────────────────────

def folder_options(db: Session, user: User, exclude_id: int | None) -> list[dict]:
    options = [{"id": None, "name": "My Files (root)"}]
    excluded = set()
    if exclude_id:
        root = db.get(Item, exclude_id)
        if root:
            excluded = {root.id} | {d.id for d in _descendants(db, root)}

    folders = db.query(Item).filter(
        Item.owner_id == user.id, Item.is_folder.is_(True), Item.deleted_at.is_(None)).all()

    def path_of(item: Item) -> str:
        parts, cursor = [], item
        while cursor:
            parts.append(cursor.name)
            cursor = db.get(Item, cursor.parent_id) if cursor.parent_id else None
        return " / ".join(reversed(parts))

    for f in sorted(folders, key=path_of):
        if f.id not in excluded:
            options.append({"id": f.id, "name": path_of(f)})
    return options

TRASH_RETENTION_DAYS = 30   # S3 + DB purge after this long in Trash


def purge_expired_trash(db: Session) -> int:
    """Background cleanup: remove trash older than retention from S3 AND DB."""
    cutoff = datetime.utcnow() - timedelta(days=TRASH_RETENTION_DAYS)
    expired = db.query(Item).filter(
        Item.deleted_at.isnot(None), Item.deleted_at < cutoff).all()
    if not expired:
        return 0
    for item in expired:
        if not item.is_folder and item.s3_key:
            s3_service.delete_file(item.s3_key)      # bytes leave AWS here
    for item in expired:
        db.delete(item)                              # cascades to item_shares
    db.commit()
    return len(expired)


def empty_trash(db: Session, user: User) -> int:
    """User-triggered: permanently delete everything in my trash (S3 + DB)."""
    trashed = db.query(Item).filter(
        Item.owner_id == user.id, Item.deleted_at.isnot(None)).all()
    for item in trashed:
        if not item.is_folder and item.s3_key:
            s3_service.delete_file(item.s3_key)
    for item in trashed:
        db.delete(item)
    db.commit()
    return len(trashed)