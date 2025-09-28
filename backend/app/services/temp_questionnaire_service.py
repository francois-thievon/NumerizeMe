from sqlalchemy.orm import Session
from ..models.questionnaire import Questionnaire

def get_all_questionnaires(db: Session):
    """Fonction simple pour récupérer tous les questionnaires"""
    return db.query(Questionnaire).all()
