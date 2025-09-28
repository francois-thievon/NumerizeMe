from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class BinaryQuestion(BaseModel):
    """Question binaire simplifiée : choix entre 2 options seulement"""
    id: int
    text: str = Field(..., description="Le texte de la question (ex: 'Pizza vs Sushis')")
    option_a: str = Field(..., description="Première option (ex: 'Pizza')")
    option_b: str = Field(..., description="Deuxième option (ex: 'Sushis')")

class QuestionnaireBase(BaseModel):
    title: str
    description: str
    category: str
    weight: int = 1
    questions: List[BinaryQuestion] = Field(..., description="Liste des questions binaires")

class QuestionnaireCreate(QuestionnaireBase):
    pass

class QuestionnaireResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    weight: int
    questions: List[BinaryQuestion]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BinaryAnswer(BaseModel):
    """Réponse à une question binaire"""
    question_id: int
    chosen_option: str = Field(..., description="L'option choisie (option_a ou option_b)")

class UserResponseBase(BaseModel):
    questionnaire_id: int
    answers: List[BinaryAnswer] = Field(..., description="Liste des réponses binaires")

class UserResponseCreate(UserResponseBase):
    pass

class UserResponseResponse(BaseModel):
    id: int
    user_id: int
    questionnaire_id: int
    answers: List[BinaryAnswer]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
