from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..core.security import oauth2_scheme
from ..core.config import get_settings
from ..db.base import get_db
from ..models.user import User
from ..models.questionnaire import Questionnaire, UserResponse
from ..services.temp_questionnaire_service import get_all_questionnaires
from ..services.matching_service import MatchingService
from ..schemas.questionnaire import UserResponseCreate

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

@router.get("/test")
async def test_endpoint():
    """Test endpoint qui retourne juste du JSON"""
    return JSONResponse(content={"message": "test successful", "data": [{"id": 1, "title": "Test"}]})

@router.get("/questionnaires-test")
async def test_questionnaires_endpoint(db: Session = Depends(get_db)):
    """Test endpoint pour questionnaires sans authentification"""
    try:
        # Utilisation du service simplifié
        all_questionnaires = get_all_questionnaires(db)
        
        # Construction manuelle de la réponse
        result = []
        for q in all_questionnaires:
            result.append({
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "category": q.category,
                "weight": q.weight,
                "questions": q.questions,  # JSON brut de la DB
                "created_at": q.created_at.isoformat(),
                "updated_at": q.updated_at.isoformat() if q.updated_at else None
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)

@router.get("/test-completion")
async def test_completion_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint pour vérifier si on peut détecter les questionnaires complétés"""
    try:
        # Récupérer les questionnaires
        all_questionnaires = get_all_questionnaires(db)
        
        result = []
        for q in all_questionnaires:
            # Vérifier si l'utilisateur a déjà répondu à ce questionnaire
            user_response = db.query(UserResponse).filter(
                UserResponse.user_id == current_user.id,
                UserResponse.questionnaire_id == q.id
            ).first()
            
            is_completed = user_response is not None
            print(f"TEST: Questionnaire {q.id} ({q.title}): User {current_user.id} completed = {is_completed}")
            
            result.append({
                "id": q.id,
                "title": q.title,
                "is_completed": is_completed
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)

@router.get("/questionnaires")
async def list_questionnaires(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint principal pour récupérer les questionnaires"""
    try:
        # Utilisation du service simplifié
        all_questionnaires = get_all_questionnaires(db)
        
        # Filtrage simple
        questionnaires = all_questionnaires
        if category:
            questionnaires = [q for q in all_questionnaires if q.category == category]
        
        # Pagination simple
        questionnaires = questionnaires[skip:skip+limit]
        
        # Construction manuelle de la réponse avec statut de completion
        result = []
        for q in questionnaires:
            # Vérifier si l'utilisateur a déjà répondu à ce questionnaire
            user_response = db.query(UserResponse).filter(
                UserResponse.user_id == current_user.id,
                UserResponse.questionnaire_id == q.id
            ).first()
            
            is_completed = user_response is not None
            
            print(f"Questionnaire {q.id} ({q.title}): User {current_user.id} completed = {is_completed}")
            if user_response:
                print(f"Found response ID {user_response.id} for user {current_user.id} and questionnaire {q.id}")
            
            result.append({
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "category": q.category,
                "weight": q.weight,
                "is_completed": is_completed,
                "questions": q.questions,  # JSON brut de la DB
                "created_at": q.created_at.isoformat(),
                "updated_at": q.updated_at.isoformat() if q.updated_at else None
            })
        
        print(f"Returning {len(result)} questionnaires for user {current_user.id}")
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)

@router.get("/questionnaires/{questionnaire_id}")
async def get_questionnaire_by_id(
    questionnaire_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer un questionnaire spécifique"""
    try:
        questionnaire = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()
        if not questionnaire:
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        
        result = {
            "id": questionnaire.id,
            "title": questionnaire.title,
            "description": questionnaire.description,
            "category": questionnaire.category,
            "weight": questionnaire.weight,
            "questions": questionnaire.questions,
            "created_at": questionnaire.created_at.isoformat(),
            "updated_at": questionnaire.updated_at.isoformat() if questionnaire.updated_at else None
        }
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)

@router.post("/responses")
async def submit_response(
    response_data: UserResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soumettre une réponse à un questionnaire"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Submitting response for user {current_user.id}, questionnaire {response_data.questionnaire_id}")
        logger.info(f"Response data: {response_data}")
        
        # Vérifier si le questionnaire existe
        questionnaire = db.query(Questionnaire).filter(Questionnaire.id == response_data.questionnaire_id).first()
        if not questionnaire:
            logger.error(f"Questionnaire {response_data.questionnaire_id} not found")
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        
        logger.info(f"Questionnaire found: {questionnaire.title}")
        
        # Vérifier si l'utilisateur a déjà répondu à ce questionnaire
        existing_response = db.query(UserResponse).filter(
            UserResponse.user_id == current_user.id,
            UserResponse.questionnaire_id == response_data.questionnaire_id
        ).first()
        
        if existing_response:
            logger.info(f"Updating existing response {existing_response.id}")
            # Mettre à jour la réponse existante
            existing_response.answers = [answer.dict() for answer in response_data.answers]
            db.commit()
            db.refresh(existing_response)
            
            # Déclencher le recalcul des matchs après mise à jour
            try:
                logger.info(f"Recalculating matches for user {current_user.id} after response update")
                
                # IMPORTANT: Forcer une nouvelle session pour éviter les problèmes de cache
                db.expunge_all()  # Vider le cache de la session
                
                # Recalculer les matchs pour cet utilisateur
                potential_matches = MatchingService.find_matches_for_user(db, current_user.id)
                logger.info(f"Found {len(potential_matches)} potential matches to update")
                
                for match_info in potential_matches:
                    updated_match = MatchingService.create_or_update_match(
                        db, 
                        current_user.id, 
                        match_info['user'].id, 
                        match_info['similarity_score']
                    )
                    logger.info(f"Updated match with user {match_info['user'].id}: score = {match_info['similarity_score']}")
                
                logger.info("Matches recalculated successfully")
            except Exception as match_error:
                logger.warning(f"Error recalculating matches: {match_error}")
                # Ne pas faire échouer la réponse si le recalcul échoue
            
            result = {
                "id": existing_response.id,
                "user_id": existing_response.user_id,
                "questionnaire_id": existing_response.questionnaire_id,
                "answers": existing_response.answers,
                "created_at": existing_response.created_at.isoformat()
            }
        else:
            logger.info("Creating new response")
            # Créer une nouvelle réponse
            db_response = UserResponse(
                user_id=current_user.id,
                questionnaire_id=response_data.questionnaire_id,
                answers=[answer.dict() for answer in response_data.answers]
            )
            db.add(db_response)
            db.commit()
            db.refresh(db_response)
            
            # Déclencher le recalcul des matchs après nouvelle réponse
            try:
                logger.info(f"Calculating matches for user {current_user.id} after new response")
                
                # IMPORTANT: Forcer une nouvelle session pour éviter les problèmes de cache
                db.expunge_all()  # Vider le cache de la session
                
                # Recalculer les matchs pour cet utilisateur
                potential_matches = MatchingService.find_matches_for_user(db, current_user.id)
                logger.info(f"Found {len(potential_matches)} potential matches to create")
                
                for match_info in potential_matches:
                    new_match = MatchingService.create_or_update_match(
                        db, 
                        current_user.id, 
                        match_info['user'].id, 
                        match_info['similarity_score']
                    )
                    logger.info(f"Created match with user {match_info['user'].id}: score = {match_info['similarity_score']}")
                
                logger.info("Matches calculated successfully")
            except Exception as match_error:
                logger.warning(f"Error calculating matches: {match_error}")
                # Ne pas faire échouer la réponse si le calcul échoue
            
            result = {
                "id": db_response.id,
                "user_id": db_response.user_id,
                "questionnaire_id": db_response.questionnaire_id,
                "answers": db_response.answers,
                "created_at": db_response.created_at.isoformat()
            }
        
        logger.info(f"Response saved successfully: {result}")
        return JSONResponse(content=result, status_code=201)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)

@router.get("/responses/me")
async def get_my_responses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les réponses de l'utilisateur connecté"""
    try:
        responses = db.query(UserResponse).filter(UserResponse.user_id == current_user.id).all()
        
        result = []
        for response in responses:
            result.append({
                "id": response.id,
                "user_id": response.user_id,
                "questionnaire_id": response.questionnaire_id,
                "answers": response.answers,
                "created_at": response.created_at.isoformat()
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return JSONResponse(content=error_details, status_code=500)
