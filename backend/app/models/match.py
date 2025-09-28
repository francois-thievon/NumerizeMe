from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)  # Score de similarité (0-1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")

# Classe Message temporairement désactivée pour résoudre le problème de match_id
# class Message(Base):
#     __tablename__ = "messages"
#
#     id = Column(Integer, primary_key=True, index=True)
#     sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     content = Column(String, nullable=False)
#     is_read = Column(Boolean, default=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     # Relations
#     sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
#     receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
