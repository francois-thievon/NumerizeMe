from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.base import get_db
from ..services.matching_service import MatchingService
from ..schemas.match import MatchResponse
from ..core.security import get_current_user
from ..models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/matches", response_model=List[MatchResponse])
async def get_user_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les matchs de l'utilisateur connecté
    """
    try:
        matches = MatchingService.get_user_matches(db, current_user.id)
        return matches
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des matchs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des matchs")

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
