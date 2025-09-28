from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from ..models.match import Match, Message
from ..models.user import User

class MessageService:
    
    @staticmethod
    def send_message(db: Session, match_id: int, sender_id: int, content: str) -> Message:
        """
        Envoie un message dans une conversation
        """
        # Vérifier que l'utilisateur fait partie du match
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match or (match.user1_id != sender_id and match.user2_id != sender_id):
            raise ValueError("Utilisateur non autorisé pour ce match")
        
        message = Message(
            match_id=match_id,
            sender_id=sender_id,
            content=content,
            is_read=False
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation(db: Session, match_id: int, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Récupère les messages d'une conversation
        """
        # Vérifier que l'utilisateur fait partie du match
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match or (match.user1_id != user_id and match.user2_id != user_id):
            raise ValueError("Utilisateur non autorisé pour ce match")
        
        messages = db.query(Message).filter(
            Message.match_id == match_id
        ).order_by(desc(Message.created_at)).limit(limit).all()
        
        # Marquer les messages reçus comme lus
        unread_messages = db.query(Message).filter(
            and_(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.commit()
        
        # Formater les messages pour la réponse
        result = []
        for message in reversed(messages):  # Inverser pour avoir l'ordre chronologique
            sender = db.query(User).filter(User.id == message.sender_id).first()
            result.append({
                'id': message.id,
                'content': message.content,
                'sender': {
                    'id': sender.id,
                    'username': sender.username,
                    'first_name': sender.first_name,
                    'last_name': sender.last_name
                },
                'is_own_message': message.sender_id == user_id,
                'created_at': message.created_at,
                'is_read': message.is_read
            })
        
        return result
    
    @staticmethod
    def get_unread_message_count(db: Session, user_id: int) -> int:
        """
        Compte le nombre total de messages non lus pour un utilisateur
        """
        # Récupérer tous les matchs de l'utilisateur
        user_matches = db.query(Match).filter(
            (Match.user1_id == user_id) | (Match.user2_id == user_id)
        ).all()
        
        total_unread = 0
        for match in user_matches:
            unread_count = db.query(Message).filter(
                and_(
                    Message.match_id == match.id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            ).count()
            total_unread += unread_count
        
        return total_unread
    
    @staticmethod
    def mark_conversation_as_read(db: Session, match_id: int, user_id: int):
        """
        Marque tous les messages d'une conversation comme lus
        """
        # Vérifier que l'utilisateur fait partie du match
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match or (match.user1_id != user_id and match.user2_id != user_id):
            raise ValueError("Utilisateur non autorisé pour ce match")
        
        unread_messages = db.query(Message).filter(
            and_(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.commit()
