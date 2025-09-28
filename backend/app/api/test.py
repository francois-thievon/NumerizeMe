from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..services.matching_service import MatchingService
from ..models.user import User
from ..models.questionnaire import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/test-matching")
async def test_matching_system(db: Session = Depends(get_db)):
    """
    Endpoint de test pour le système de matching
    """
    try:
        # Créer des données de test
        logger.info("=== TEST DU SYSTÈME DE MATCHING ===")
        
        # 1. Vérifier les utilisateurs existants
        users = db.query(User).all()
        logger.info(f"Nombre d'utilisateurs en base: {len(users)}")
        
        # 2. Vérifier les réponses existantes
        responses = db.query(UserResponse).all()
        logger.info(f"Nombre de réponses en base: {len(responses)}")
        
        # 3. Créer des réponses de test pour FrysT (user_id: 4)
        user_4_responses = db.query(UserResponse).filter(UserResponse.user_id == 4).all()
        if user_4_responses:
            logger.info(f"Utilisateur 4 a {len(user_4_responses)} réponses")
            
            # Calculer les matchs pour cet utilisateur
            matches = MatchingService.find_matches_for_user(db, 4)
            logger.info(f"Matchs trouvés pour l'utilisateur 4: {len(matches)}")
            
            # Créer les matchs en base
            for match_data in matches:
                MatchingService.create_or_update_match(
                    db, 
                    4, 
                    match_data['user'].id, 
                    match_data['similarity_score']
                )
            
            return {
                "message": "Test de matching réussi",
                "users_count": len(users),
                "responses_count": len(responses),
                "matches_found": len(matches),
                "user_4_responses": len(user_4_responses)
            }
        else:
            return {
                "message": "Utilisateur 4 n'a pas de réponses",
                "users_count": len(users),
                "responses_count": len(responses)
            }
            
    except Exception as e:
        logger.error(f"Erreur pendant le test: {e}")
        return {"error": str(e)}
