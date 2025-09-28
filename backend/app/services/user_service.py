from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from ..models.user import User
from ..models.questionnaire import UserResponse
from ..schemas.user import UserUpdate
import io

def get_user_profile(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Compter les questionnaires répondus
    questionnaire_count = db.query(UserResponse).filter(
        UserResponse.user_id == user_id
    ).count()
    
    # Compter les matchs avec le nouveau modèle
    from ..models.match import Match
    match_count = db.query(Match).filter(
        (Match.user1_id == user_id) |
        (Match.user2_id == user_id)
    ).count()
    
    return {
        **user.__dict__,
        "questionnaire_count": questionnaire_count,
        "match_count": match_count
    }

def update_user_profile(db: Session, user_id: int, user_update: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return get_user_profile(db, user_id)

async def store_profile_picture(db: Session, user_id: int, picture: UploadFile):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Lire et stocker l'image
    contents = await picture.read()
    user.profile_picture = contents
    
    db.commit()
    return True
