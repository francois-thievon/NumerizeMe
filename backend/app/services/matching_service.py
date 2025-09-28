from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.user import User
from ..models.questionnaire import UserResponse
from ..models.match import Match
import json
from collections import Counter
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class MatchingService:
    
    @staticmethod
    def calculate_jaccard_similarity(responses1: List[Dict], responses2: List[Dict]) -> float:
        """
        Calcule l'indice de Jaccard entre deux ensembles de réponses
        Ne considère que les questionnaires auxquels les deux utilisateurs ont répondu
        """
        print("=== DEBUT calculate_jaccard_similarity ===")
        try:
            if not responses1 or not responses2:
                print("Pas de réponses - retour 0.0")
                return 0.0
            
            # Identifier les questionnaires auxquels les deux utilisateurs ont répondu
            questionnaires_user1 = set(r['questionnaire_id'] for r in responses1)
            questionnaires_user2 = set(r['questionnaire_id'] for r in responses2)
            common_questionnaires = questionnaires_user1.intersection(questionnaires_user2)
            
            logger.info(f"=== CALCUL JACCARD DEBUG ===")
            print(f"=== CALCUL JACCARD DEBUG ===")
            logger.info(f"Questionnaires user1: {sorted(questionnaires_user1)}")
            print(f"Questionnaires user1: {sorted(questionnaires_user1)}")
            logger.info(f"Questionnaires user2: {sorted(questionnaires_user2)}")
            print(f"Questionnaires user2: {sorted(questionnaires_user2)}")
            logger.info(f"Questionnaires communs: {sorted(common_questionnaires)}")
            print(f"Questionnaires communs: {sorted(common_questionnaires)}")
            
            if not common_questionnaires:
                logger.info("Aucun questionnaire en commun - similarité = 0")
                print("Aucun questionnaire en commun - similarité = 0")
                logger.info(f"=== FIN DEBUG ===")
                print(f"=== FIN DEBUG ===")
                return 0.0
            
            # Convertir les réponses en ensembles de (questionnaire_id, question_id, réponse)
            # mais seulement pour les questionnaires communs
            set1 = set()
            set2 = set()
            
            try:
                for response in responses1:
                    questionnaire_id = response['questionnaire_id']
                    if questionnaire_id in common_questionnaires:
                        answers = response['answers']
                        
                        for answer in answers:
                            question_id = answer['question_id']
                            choice = answer['chosen_option']
                            set1.add((questionnaire_id, question_id, choice))
            except Exception as e:
                logger.error(f"Error processing responses1: {e}")
                print(f"Error processing responses1: {e}")
                raise
            
            try:
                for response in responses2:
                    questionnaire_id = response['questionnaire_id']
                    if questionnaire_id in common_questionnaires:
                        answers = response['answers']
                        
                        for answer in answers:
                            question_id = answer['question_id']
                            choice = answer['chosen_option']
                            set2.add((questionnaire_id, question_id, choice))
            except Exception as e:
                logger.error(f"Error processing responses2: {e}")
                print(f"Error processing responses2: {e}")
                raise
            
            # Calcul de l'indice de Jaccard
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            # AJOUT: Logs détaillés pour le debugging
            print(f"=== DEBUG MATCHING ===")
            print(f"Set 1 ({len(set1)} éléments): {sorted(set1)}")
            print(f"Set 2 ({len(set2)} éléments): {sorted(set2)}")
            print(f"Intersection ({intersection} éléments): {sorted(set1.intersection(set2))}")
            print(f"Union ({union} éléments): {sorted(set1.union(set2))}")
            similarity = intersection / union if union > 0 else 0.0
            print(f"Similarité calculée: {intersection}/{union} = {similarity:.4f} ({similarity*100:.1f}%)")
            print(f"=== FIN DEBUG ===")
            
            if union == 0:
                print("Union = 0, retour 0.0")
                return 0.0
            
            print(f"Retour similarity: {similarity}")
            return similarity
            
        except Exception as e:
            print(f"ERREUR dans calculate_jaccard_similarity: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    @staticmethod
    def find_matches_for_user(db: Session, user_id: int, min_similarity: float = 0.3) -> List[Dict]:
        """
        Trouve tous les matchs possibles pour un utilisateur
        """
        logger.error(f"=== DEBUT find_matches_for_user pour user_id: {user_id} ===")
        
        # Récupérer les réponses de l'utilisateur
        user_responses = db.query(UserResponse).filter(UserResponse.user_id == user_id).all()
        logger.error(f"Trouvé {len(user_responses) if user_responses else 0} réponses pour user {user_id}")
        
        if not user_responses:
            return []
        
        user_responses_data = []
        for response in user_responses:
            user_responses_data.append({
                'questionnaire_id': response.questionnaire_id,
                'answers': response.answers
            })
        
        # Récupérer tous les autres utilisateurs qui ont des réponses
        other_users = db.query(User).join(UserResponse).filter(User.id != user_id).distinct().all()
        
        matches = []
        
        for other_user in other_users:
            # Récupérer les réponses de l'autre utilisateur
            other_responses = db.query(UserResponse).filter(UserResponse.user_id == other_user.id).all()
            
            other_responses_data = []
            for response in other_responses:
                other_responses_data.append({
                    'questionnaire_id': response.questionnaire_id,
                    'answers': response.answers
                })
            
            # Calculer la similarité
            logger.error(f"AVANT APPEL calculate_jaccard_similarity pour users {user_id} et {other_user.id}")
            similarity = MatchingService.calculate_jaccard_similarity(user_responses_data, other_responses_data)
            logger.error(f"APRES APPEL calculate_jaccard_similarity - résultat: {similarity}")
            
            if similarity >= min_similarity:
                matches.append({
                    'user': other_user,
                    'similarity_score': similarity
                })
        
        # Trier par score de similarité décroissant
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return matches
    
    @staticmethod
    def create_or_update_match(db: Session, user1_id: int, user2_id: int, similarity_score: float) -> Match:
        """
        Crée ou met à jour un match entre deux utilisateurs
        """
        # S'assurer que user1_id < user2_id pour éviter les doublons
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        # Vérifier si le match existe déjà
        existing_match = db.query(Match).filter(
            and_(Match.user1_id == user1_id, Match.user2_id == user2_id)
        ).first()
        
        if existing_match:
            existing_match.similarity_score = similarity_score
            db.commit()
            db.refresh(existing_match)
            return existing_match
        else:
            new_match = Match(
                user1_id=user1_id,
                user2_id=user2_id,
                similarity_score=similarity_score
            )
            db.add(new_match)
            db.commit()
            db.refresh(new_match)
            return new_match
    
    @staticmethod
    def get_user_matches(db: Session, user_id: int) -> List[Dict]:
        """
        Récupère tous les matchs d'un utilisateur avec les informations des autres utilisateurs
        """
        matches = db.query(Match).filter(
            or_(Match.user1_id == user_id, Match.user2_id == user_id)
        ).order_by(Match.similarity_score.desc()).all()
        
        result = []
        for match in matches:
            # Déterminer qui est l'autre utilisateur
            other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
            other_user = db.query(User).filter(User.id == other_user_id).first()
            
            if other_user:
                # Temporairement, ne pas compter les messages non lus pour éviter l'erreur SQL
                unread_count = 0
                
                result.append({
                    'match_id': match.id,
                    'user': {
                        'id': other_user.id,
                        'username': other_user.username,
                        'first_name': other_user.first_name,
                        'last_name': other_user.last_name,
                        'age': other_user.age,
                        'city': other_user.city,
                        'bio': other_user.bio
                    },
                    'similarity_score': match.similarity_score,
                    'unread_messages': unread_count,
                    'created_at': match.created_at
                })
        
        return result
    
    @staticmethod
    def recalculate_all_matches(db: Session):
        """
        Recalcule tous les matchs pour tous les utilisateurs
        """
        # Supprimer tous les matchs existants
        db.query(Match).delete()
        db.commit()
        
        # Récupérer tous les utilisateurs qui ont des réponses
        users_with_responses = db.query(User).join(UserResponse).distinct().all()
        
        # Calculer les matchs pour chaque paire d'utilisateurs
        processed_pairs = set()
        
        for i, user1 in enumerate(users_with_responses):
            for user2 in users_with_responses[i+1:]:
                pair = tuple(sorted([user1.id, user2.id]))
                if pair in processed_pairs:
                    continue
                
                processed_pairs.add(pair)
                
                # Récupérer les réponses
                user1_responses = db.query(UserResponse).filter(UserResponse.user_id == user1.id).all()
                user2_responses = db.query(UserResponse).filter(UserResponse.user_id == user2.id).all()
                
                user1_data = [{'questionnaire_id': r.questionnaire_id, 'answers': r.answers} for r in user1_responses]
                user2_data = [{'questionnaire_id': r.questionnaire_id, 'answers': r.answers} for r in user2_responses]
                
                similarity = MatchingService.calculate_jaccard_similarity(user1_data, user2_data)
                
                if similarity >= 0.1:  # Seuil minimum plus bas pour le calcul global
                    MatchingService.create_or_update_match(db, user1.id, user2.id, similarity)
