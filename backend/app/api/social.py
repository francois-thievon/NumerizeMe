from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt
from ..core.security import oauth2_scheme
from ..core.config import get_settings
from ..db.base import get_db
from ..models.user import User
from ..schemas.social import MessageCreate, Message, Match
from ..services.social_service import (
    send_message,
    get_messages,
    get_matches,
    calculate_compatibility
)

settings = get_settings()

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

@router.post("/messages", response_model=Message)
async def create_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return send_message(db, message, current_user.id)

@router.get("/messages/{user_id}", response_model=List[Message])
async def get_conversation(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_messages(db, current_user.id, user_id)

@router.get("/matches", response_model=List[Match])
async def get_user_matches(
    min_score: float = 0.5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_matches(db, current_user.id, min_score)

@router.post("/matches/calculate")
async def update_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalcule les scores de compatibilité avec les autres utilisateurs"""
    await calculate_compatibility(db, current_user.id)
    return {"message": "Compatibility scores updated successfully"}
