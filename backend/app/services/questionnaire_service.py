from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from ..models.questionnaire import Questionnaire, UserResponse
from ..schemas.questionnaire import QuestionnaireCreate, UserResponseCreate

def create_questionnaire(db: Session, questionnaire: QuestionnaireCreate):
    db_questionnaire = Questionnaire(**questionnaire.model_dump())
    db.add(db_questionnaire)
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire

def get_questionnaires(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
):
    query = db.query(Questionnaire)
    if category:
        query = query.filter(Questionnaire.category == category)
    return query.offset(skip).limit(limit).all()

def get_questionnaire(db: Session, questionnaire_id: int):
    return db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()

def submit_response(
    db: Session,
    response: UserResponseCreate,
    user_id: int
):
    # Vérifier si le questionnaire existe
    questionnaire = get_questionnaire(db, response.questionnaire_id)
    if not questionnaire:
        raise HTTPException(
            status_code=404,
            detail="Questionnaire not found"
        )
    
    # Vérifier si l'utilisateur a déjà répondu à ce questionnaire
    existing_response = db.query(UserResponse).filter(
        UserResponse.user_id == user_id,
        UserResponse.questionnaire_id == response.questionnaire_id
    ).first()
    
    if existing_response:
        # Mettre à jour la réponse existante
        existing_response.answers = response.answers
        db.commit()
        db.refresh(existing_response)
        return existing_response
    else:
        # Créer une nouvelle réponse
        db_response = UserResponse(
            user_id=user_id,
            questionnaire_id=response.questionnaire_id,
            answers=response.answers
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response

def get_user_responses(db: Session, user_id: int):
    return db.query(UserResponse).filter(
        UserResponse.user_id == user_id
    ).all()
