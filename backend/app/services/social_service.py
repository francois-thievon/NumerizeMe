from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_, or_
from typing import List
from ..models.social import Message, user_matches
from ..models.user import User
from ..models.questionnaire import UserResponse, Questionnaire
from ..schemas.social import MessageCreate
import numpy as np

def send_message(db: Session, message: MessageCreate, sender_id: int):
    # Vérifier si le destinataire existe
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Créer le message
    db_message = Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, user_id: int, other_user_id: int):
    return db.query(Message).filter(
        or_(
            and_(
                Message.sender_id == user_id,
                Message.receiver_id == other_user_id
            ),
            and_(
                Message.sender_id == other_user_id,
                Message.receiver_id == user_id
            )
        )
    ).order_by(Message.created_at.asc()).all()

def calculate_compatibility_score(user1_responses: List[UserResponse], user2_responses: List[UserResponse]):
    score = 0
    total_weight = 0
    
    # Créer des dictionnaires pour un accès facile aux réponses
    user1_answers = {r.questionnaire_id: r.answers for r in user1_responses}
    user2_answers = {r.questionnaire_id: r.answers for r in user2_responses}
    
    # Calculer le score pour chaque questionnaire commun
    common_questionnaires = set(user1_answers.keys()) & set(user2_answers.keys())
    
    for q_id in common_questionnaires:
        questionnaire = db.query(Questionnaire).get(q_id)
        weight = questionnaire.weight
        total_weight += weight
        
        answers1 = user1_answers[q_id]
        answers2 = user2_answers[q_id]
        
        # Calculer la similarité des réponses
        matching_answers = 0
        total_questions = len(questionnaire.questions)
        
        for question in questionnaire.questions:
            q_id = str(question["id"])
            if q_id in answers1 and q_id in answers2:
                if question["type"] == "SCALE":
                    # Pour les échelles, calculer la proximité des réponses
                    diff = abs(answers1[q_id] - answers2[q_id])
                    max_diff = question["max_scale"] - question["min_scale"]
                    matching_answers += 1 - (diff / max_diff)
                else:
                    # Pour les autres types de questions, vérifier l'égalité
                    if answers1[q_id] == answers2[q_id]:
                        matching_answers += 1
        
        question_score = matching_answers / total_questions
        score += question_score * weight
    
    if total_weight == 0:
        return 0
    
    return score / total_weight

async def calculate_compatibility(db: Session, user_id: int):
    # Récupérer les réponses de l'utilisateur
    user_responses = db.query(UserResponse).filter(
        UserResponse.user_id == user_id
    ).all()
    
    if not user_responses:
        return
    
    # Récupérer tous les autres utilisateurs actifs
    other_users = db.query(User).filter(
        User.id != user_id,
        User.is_active == True
    ).all()
    
    # Calculer la compatibilité avec chaque utilisateur
    for other_user in other_users:
        other_user_responses = db.query(UserResponse).filter(
            UserResponse.user_id == other_user.id
        ).all()
        
        if other_user_responses:
            score = calculate_compatibility_score(user_responses, other_user_responses)
            
            # Mettre à jour ou créer l'entrée dans la table des matchs
            match = db.query(user_matches).filter(
                or_(
                    and_(
                        user_matches.c.user_id == user_id,
                        user_matches.c.matched_user_id == other_user.id
                    ),
                    and_(
                        user_matches.c.user_id == other_user.id,
                        user_matches.c.matched_user_id == user_id
                    )
                )
            ).first()
            
            if match:
                # Mettre à jour le score existant
                db.execute(
                    user_matches.update().where(
                        and_(
                            user_matches.c.user_id == user_id,
                            user_matches.c.matched_user_id == other_user.id
                        )
                    ).values(compatibility_score=score)
                )
            else:
                # Créer une nouvelle entrée
                db.execute(
                    user_matches.insert().values(
                        user_id=user_id,
                        matched_user_id=other_user.id,
                        compatibility_score=score
                    )
                )
    
    db.commit()

def get_matches(db: Session, user_id: int, min_score: float = 0.5):
    # Récupérer les matchs où l'utilisateur est impliqué
    matches = db.query(user_matches, User).join(
        User,
        or_(
            and_(
                user_matches.c.matched_user_id == User.id,
                user_matches.c.user_id == user_id
            ),
            and_(
                user_matches.c.user_id == User.id,
                user_matches.c.matched_user_id == user_id
            )
        )
    ).filter(
        user_matches.c.compatibility_score >= min_score
    ).order_by(
        user_matches.c.compatibility_score.desc()
    ).all()
    
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "compatibility_score": match.compatibility_score,
            "created_at": match.created_at
        }
        for match, user in matches
    ]
