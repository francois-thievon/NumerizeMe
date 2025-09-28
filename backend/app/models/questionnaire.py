from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..db.base import Base

class QuestionType(enum.Enum):
    TEXT = "text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"

class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    category = Column(String, index=True)  # Pour grouper les questionnaires par thème
    questions = Column(JSON)  # Stocke la liste des questions et leurs options
    weight = Column(Integer, default=1)  # Poids du questionnaire dans le calcul de compatibilité
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    responses = relationship("UserResponse", back_populates="questionnaire")

class UserResponse(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))
    answers = Column(JSON)  # Stocke les réponses de l'utilisateur
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="questionnaire_responses")
    questionnaire = relationship("Questionnaire", back_populates="responses")
