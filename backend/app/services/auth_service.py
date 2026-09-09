from datetime import datetime, timedelta
from uuid import uuid4
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.token import RevokedToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user: User) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "jti": str(uuid4()),     # unique id → individually revocable
        "iat": now,              # issued-at → global cutoff checks
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(401, "Could not validate credentials",
                                 headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id, jti, iat = payload.get("sub"), payload.get("jti"), payload.get("iat")
        if user_id is None:
            raise unauthorized
    except JWTError:
        raise unauthorized

    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise unauthorized

    # ── server-side revocation ──────────────────────────────────────
    if jti and db.query(RevokedToken.id).filter_by(jti=jti).first():
        raise unauthorized                                  # this token was logged out
    if user.tokens_revoked_before:
        issued = datetime.utcfromtimestamp(iat) if isinstance(iat, (int, float)) else None
        if issued is None or issued < user.tokens_revoked_before:
            raise unauthorized                              # predates "logout everywhere"
    return user


def revoke_token(db: Session, token: str) -> None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return
    jti, exp = payload.get("jti"), payload.get("exp")
    if not jti or not exp:
        return
    if not db.query(RevokedToken.id).filter_by(jti=jti).first():
        db.add(RevokedToken(jti=jti, expires_at=datetime.utcfromtimestamp(exp)))
        db.commit()


def revoke_all_tokens(db: Session, user: User) -> None:
    user.tokens_revoked_before = datetime.utcnow()
    db.commit()


def purge_revoked_tokens(db: Session) -> int:
    n = db.query(RevokedToken).filter(RevokedToken.expires_at < datetime.utcnow()).delete()
    db.commit()
    return n