from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from ..core.security import oauth2_scheme
from ..core.config import get_settings
from ..db.base import get_db
from ..models.user import User
from ..models.questionnaire import UserResponse
from ..schemas.user import UserProfile, UserUpdate
from ..services.user_service import update_user_profile, get_user_profile, store_profile_picture

settings = get_settings()

router = APIRouter()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

router = APIRouter()

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_profile(db, current_user.id)

@router.put("/me", response_model=UserProfile)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_user_profile(db, current_user.id, user_update)

@router.post("/me/picture")
async def upload_profile_picture(
    picture: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not picture.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File uploaded is not an image"
        )
    await store_profile_picture(db, current_user.id, picture)
    return {"message": "Profile picture updated successfully"}
