from fastapi import APIRouter, Depends, HTTPException, Request  # ← Request imported here
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.views.auth_views import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user,
    oauth2_scheme, revoke_token, revoke_all_tokens, normalize_email
)
from app.services.rate_limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
@limiter.limit("5/hour")
def signup(request: Request, req: SignupRequest, db: Session = Depends(get_db)):  # ← request: Request added
    email = normalize_email(req.email)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(email=email,
                hashed_password=hash_password(req.password),
                full_name=req.full_name)
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):    # ← request: Request added
    user = db.query(User).filter(User.email == normalize_email(req.email)).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    return TokenResponse(access_token=create_access_token(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=204)
def logout(token: str = Depends(oauth2_scheme),
           db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    revoke_token(db, token)


@router.post("/logout-all", status_code=204)
def logout_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    revoke_all_tokens(db, user)