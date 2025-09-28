from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base

# Table d'association pour les matchs entre utilisateurs
user_matches = Table('user_matches',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('matched_user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('compatibility_score', Float),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# Table pour les messages entre utilisateurs - temporairement désactivée
# class Message(Base):
#     __tablename__ = "messages"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     sender_id = Column(Integer, ForeignKey("users.id"))
#     receiver_id = Column(Integer, ForeignKey("users.id"))
#     content = Column(String)
#     is_read = Column(Boolean, default=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     sender = relationship("User", foreign_keys=[sender_id])
#     receiver = relationship("User", foreign_keys=[receiver_id])
