from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
from ..core.security import get_password_hash, verify_password, create_access_token, pwd_context
from ..db.base import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, User as UserSchema

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to register user with email: {user.email} and username: {user.username}")
        
        # Vérification si l'email existe déjà
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Vérification si le nom d'utilisateur existe déjà
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already taken: {user.username}")
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Création du nouvel utilisateur
        logger.info("Creating new user")
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User successfully created with id: {db_user.id}")
            return db_user
        except Exception as e:
            logger.error(f"Database error during user registration: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Internal server error during user creation")
            
    except HTTPException as he:
        # Remonter les erreurs HTTP telles quelles
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for email: {user_data.email}")
        
        # Vérification de l'existence de l'utilisateur
        user = db.query(User).filter(User.email == user_data.email).first()
        
        if not user:
            logger.warning(f"Login attempt failed: User not found with email {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Vérification du mot de passe
        if not pwd_context.verify(user_data.password, user.hashed_password):
            logger.warning(f"Login attempt failed: Invalid password for user {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Si tout est correct, créer le token
        logger.info(f"Login successful for user: {user_data.email}")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(days=1)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
