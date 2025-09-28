from sqlalchemy.orm import Session
from ..models.questionnaire import Questionnaire

def init_questionnaires(db: Session):
    """Initialise la base de données avec des questionnaires par défaut"""
    # Ne fait rien - les questionnaires sont ajoutés via des scripts SQL
    pass
