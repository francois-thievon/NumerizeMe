from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from typing import List
from ..db.base import get_db
from ..services.matching_service import MatchingService
from ..schemas.match import MatchResponse
from ..core.security import get_current_user
from ..models.user import User
from ..models.match import Match
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test-simple")
async def test_simple():
    """
    Test simple sans dépendances
    """
    return {"message": "Test OK"}

@router.get("/list-matches")
async def list_user_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les matchs d'un utilisateur - Version simple sans ORM complexe
    """
    try:
        # Requête SQL très simple pour récupérer les matchs
        sql = text("""
            SELECT 
                m.id as match_id,
                m.similarity_score,
                m.created_at,
                CASE 
                    WHEN m.user1_id = :user_id THEN m.user2_id
                    ELSE m.user1_id
                END as other_user_id
            FROM matches m 
            WHERE m.user1_id = :user_id OR m.user2_id = :user_id
            ORDER BY m.similarity_score DESC
        """)
        
        matches = db.execute(sql, {"user_id": current_user.id}).fetchall()
        
        result = []
        for match in matches:
            # Récupérer les infos de l'autre utilisateur avec une requête séparée
            user_sql = text("""
                SELECT id, username, first_name, last_name, age, city, bio 
                FROM users 
                WHERE id = :user_id
            """)
            user_data = db.execute(user_sql, {"user_id": match.other_user_id}).fetchone()
            
            if user_data:
                result.append({
                    "match_id": match.match_id,
                    "user": {
                        "id": user_data.id,
                        "username": user_data.username,
                        "first_name": user_data.first_name,
                        "last_name": user_data.last_name,
                        "age": user_data.age,
                        "city": user_data.city,
                        "bio": user_data.bio
                    },
                    "similarity_score": float(match.similarity_score),
                    "unread_messages": 0,
                    "created_at": match.created_at.isoformat() if match.created_at else None
                })
        
        logger.info(f"Found {len(result)} matches for user {current_user.id}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matchs: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des matchs: {str(e)}")

@router.get("/stats")
async def get_matching_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques de matching de l'utilisateur - Version simplifiée
    """
    try:
        # Compter les matchs de l'utilisateur
        sql = text("""
            SELECT COUNT(*) as total_matches,
                   MAX(similarity_score) as top_similarity
            FROM matches 
            WHERE user1_id = :user_id OR user2_id = :user_id
        """)
        
        result = db.execute(sql, {"user_id": current_user.id}).fetchone()
        
        return {
            "total_matches": result.total_matches or 0,
            "unread_messages": 0,  # Temporairement désactivé
            "top_similarity": float(result.top_similarity) if result.top_similarity else None
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    """
    Test de connexion à la base de données sans authentification
    """
    try:
        # Test simple de count sur les matchs
        sql = text("SELECT COUNT(*) as count FROM matches")
        result = db.execute(sql).fetchone()
        return {"message": f"Base de données OK - {result.count} matchs total"}
    except Exception as e:
        logger.error(f"Erreur de test DB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur DB: {str(e)}")

@router.post("/calculate-matches")
async def calculate_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calcule les nouveaux matchs pour l'utilisateur connecté
    """
    try:
        logger.info(f"Starting calculate_matches for user: {current_user.email}")
        
        # Récupérer les matchs potentiels
        potential_matches = MatchingService.find_matches_for_user(db, current_user.id)
        logger.info(f"Found {len(potential_matches)} potential matches")
        
        # Créer ou mettre à jour les matchs en base
        new_matches_count = 0
        for match_info in potential_matches:
            match_record = MatchingService.create_or_update_match(
                db, 
                current_user.id, 
                match_info['user'].id, 
                match_info['similarity_score']
            )
            new_matches_count += 1
        
        logger.info(f"Created/updated {new_matches_count} matches")
        return {"message": f"{new_matches_count} nouveaux matchs calculés", "matches_count": new_matches_count}
    except Exception as e:
        logger.error(f"Erreur lors du calcul des matchs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des matchs")

@router.post("/recalculate-all-matches")
async def recalculate_all_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recalcule tous les matchs pour tous les utilisateurs (admin only pour l'instant)
    """
    try:
        MatchingService.recalculate_all_matches(db)
        logger.info("Recalcul global des matchs terminé")
        return {"message": "Tous les matchs ont été recalculés"}
    except Exception as e:
        logger.error(f"Erreur lors du recalcul global: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du recalcul des matchs")

# Endpoints de messagerie basiques
@router.post("/conversation/{match_id}/message")
async def send_message(
    match_id: int,
    message_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envoie un message dans une conversation - Version simplifiée
    """
    try:
        # Vérifier que le match existe et que l'utilisateur en fait partie
        match_sql = text("""
            SELECT user1_id, user2_id 
            FROM matches 
            WHERE id = :match_id AND (user1_id = :user_id OR user2_id = :user_id)
        """)
        match_result = db.execute(match_sql, {"match_id": match_id, "user_id": current_user.id}).fetchone()
        
        if not match_result:
            raise HTTPException(status_code=403, detail="Accès refusé à cette conversation")
        
        # Déterminer qui est le destinataire
        receiver_id = match_result.user2_id if match_result.user1_id == current_user.id else match_result.user1_id
        
        # Insérer le message dans la base
        content = message_data.get('content', '')
        if not content:
            raise HTTPException(status_code=400, detail="Le contenu du message ne peut pas être vide")
        
        insert_sql = text("""
            INSERT INTO messages (sender_id, receiver_id, content, is_read, created_at)
            VALUES (:sender_id, :receiver_id, :content, false, NOW())
            RETURNING id, sender_id, receiver_id, content, is_read, created_at
        """)
        
        result = db.execute(insert_sql, {
            "sender_id": current_user.id,
            "receiver_id": receiver_id,
            "content": content
        }).fetchone()
        
        db.commit()
        
        # Retourner le message créé
        return {
            "id": result.id,
            "content": result.content,
            "sender": {
                "id": current_user.id,
                "username": current_user.username,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name
            },
            "is_own_message": True,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "is_read": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'envoi du message: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du message")

@router.get("/conversation/{match_id}")
async def get_conversation(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère la conversation d'un match - Version simplifiée
    """
    try:
        # Vérifier que le match existe et que l'utilisateur en fait partie
        match_sql = text("""
            SELECT user1_id, user2_id 
            FROM matches 
            WHERE id = :match_id AND (user1_id = :user_id OR user2_id = :user_id)
        """)
        match_result = db.execute(match_sql, {"match_id": match_id, "user_id": current_user.id}).fetchone()
        
        if not match_result:
            raise HTTPException(status_code=403, detail="Accès refusé à cette conversation")
        
        # Récupérer les messages de la conversation
        messages_sql = text("""
            SELECT m.id, m.sender_id, m.receiver_id, m.content, m.is_read, m.created_at,
                   u.username, u.first_name, u.last_name
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            WHERE (m.sender_id = :user1_id AND m.receiver_id = :user2_id)
               OR (m.sender_id = :user2_id AND m.receiver_id = :user1_id)
            ORDER BY m.created_at ASC
            LIMIT 50
        """)
        
        messages = db.execute(messages_sql, {
            "user1_id": match_result.user1_id,
            "user2_id": match_result.user2_id
        }).fetchall()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "content": msg.content,
                "sender": {
                    "id": msg.sender_id,
                    "username": msg.username,
                    "first_name": msg.first_name,
                    "last_name": msg.last_name
                },
                "is_own_message": msg.sender_id == current_user.id,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "is_read": msg.is_read
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la conversation: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de la conversation")

@router.post("/conversation/{match_id}/mark-read")
async def mark_conversation_as_read(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marque tous les messages d'une conversation comme lus
    """
    try:
        # Vérifier que le match existe et que l'utilisateur en fait partie
        match_sql = text("""
            SELECT user1_id, user2_id 
            FROM matches 
            WHERE id = :match_id AND (user1_id = :user_id OR user2_id = :user_id)
        """)
        match_result = db.execute(match_sql, {"match_id": match_id, "user_id": current_user.id}).fetchone()
        
        if not match_result:
            raise HTTPException(status_code=403, detail="Accès refusé à cette conversation")
        
        # Déterminer qui est l'autre utilisateur
        other_user_id = match_result.user2_id if match_result.user1_id == current_user.id else match_result.user1_id
        
        # Marquer comme lus tous les messages reçus de l'autre utilisateur
        update_sql = text("""
            UPDATE messages 
            SET is_read = true 
            WHERE sender_id = :other_user_id 
              AND receiver_id = :current_user_id 
              AND is_read = false
        """)
        
        result = db.execute(update_sql, {
            "other_user_id": other_user_id,
            "current_user_id": current_user.id
        })
        
        db.commit()
        
        return {"message": "Messages marqués comme lus", "updated_count": result.rowcount}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du marquage comme lu: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du marquage comme lu")
